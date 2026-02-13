"""
测试 Command History
"""

import uuid
from typing import Any, Dict
from unittest.mock import AsyncMock

import pytest

from ai_ppt.domain.commands.base import Command
from ai_ppt.domain.commands.command_history import (
    CommandHistory,
    PresentationCommandHistory,
)


class MockCommand(Command):
    """测试用命令类"""

    def __init__(self, name: str = "test"):
        super().__init__()
        self.name = name
        self._can_execute = True
        self._can_undo = True

    @property
    def command_type(self) -> str:
        return "MockCommand"

    async def execute(self) -> None:
        if not self._can_execute:
            raise Exception("Cannot execute")
        self.mark_executed()

    async def undo(self) -> None:
        if not self._can_undo:
            raise Exception("Cannot undo")
        self.mark_undone()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.command_type,
            "id": str(self.id),
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockCommand":
        cmd = cls(name=data.get("name", "test"))
        cmd._id = uuid.UUID(data["id"])
        return cmd


class MockCommandFactory:
    """测试用命令工厂"""

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Command:
        if data.get("type") == "MockCommand":
            return MockCommand.from_dict(data)
        raise ValueError(f"Unknown command type: {data.get('type')}")


class TestCommandHistory:
    """测试 CommandHistory"""

    class TestInitialization:
        """测试初始化"""

        def test_default_initialization(self):
            """测试默认初始化"""
            history = CommandHistory()

            assert history.max_history == 50
            assert history.current_position == -1
            assert history.history_size == 0
            assert history.can_undo is False
            assert history.can_redo is False

        def test_custom_initialization(self):
            """测试自定义最大历史数"""
            history = CommandHistory(max_history=100)

            assert history.max_history == 100

        def test_zero_max_history(self):
            """测试 max_history 为 0 时使用默认值"""
            history = CommandHistory(max_history=0)

            assert history.max_history == 1  # 被设置为 max(1, 0)

        def test_negative_max_history(self):
            """测试负数 max_history"""
            history = CommandHistory(max_history=-5)

            assert history.max_history == 1  # 被设置为 max(1, -5)

    class TestExecute:
        """测试 execute 方法"""

        async def test_execute_single_command(self):
            """测试执行单个命令"""
            history = CommandHistory()
            cmd = MockCommand()

            await history.execute(cmd)

            assert history.current_position == 0
            assert history.can_undo is True
            assert history.can_redo is False
            assert cmd.executed_at is not None

        async def test_execute_multiple_commands(self):
            """测试执行多个命令"""
            history = CommandHistory()
            cmd1 = MockCommand()
            cmd2 = MockCommand()

            await history.execute(cmd1)
            await history.execute(cmd2)

            assert history.current_position == 1
            assert history.history_size == 2

        async def test_execute_clears_redo_stack(self):
            """测试执行新命令清除重做栈"""
            history = CommandHistory()
            cmd1 = MockCommand()
            cmd2 = MockCommand()
            cmd3 = MockCommand()

            await history.execute(cmd1)
            await history.execute(cmd2)
            await history.undo()
            await history.execute(cmd3)

            assert history.current_position == 1
            assert history.history_size == 2  # cmd3 替换了 cmd2 的位置

        async def test_execute_with_error(self):
            """测试执行出错时抛出异常"""
            history = CommandHistory()
            cmd = MockCommand()
            cmd._can_execute = False

            with pytest.raises(Exception, match="Cannot execute"):
                await history.execute(cmd)

            assert history.history_size == 0

    class TestUndo:
        """测试 undo 方法"""

        async def test_undo_single_command(self):
            """测试撤销单个命令"""
            history = CommandHistory()
            cmd = MockCommand()
            await history.execute(cmd)

            result = await history.undo()

            assert result == cmd
            assert history.current_position == -1
            assert history.can_undo is False
            assert cmd.undone_at is not None

        async def test_undo_empty_history(self):
            """测试撤销空历史"""
            history = CommandHistory()

            result = await history.undo()

            assert result is None

        async def test_undo_at_start(self):
            """测试在起始位置撤销"""
            history = CommandHistory()
            cmd = MockCommand()
            await history.execute(cmd)
            await history.undo()

            result = await history.undo()

            assert result is None

        async def test_undo_with_error(self):
            """测试撤销出错时抛出异常"""
            history = CommandHistory()
            cmd = MockCommand()
            cmd._can_undo = False
            await history.execute(cmd)

            with pytest.raises(Exception, match="Cannot undo"):
                await history.undo()

        async def test_undo_multiple_commands(self):
            """测试撤销多个命令"""
            history = CommandHistory()
            cmd1 = MockCommand()
            cmd2 = MockCommand()
            await history.execute(cmd1)
            await history.execute(cmd2)

            result = await history.undo()

            assert result == cmd2
            assert history.current_position == 0
            assert history.can_redo is True

    class TestRedo:
        """测试 redo 方法"""

        async def test_redo_single_command(self):
            """测试重做单个命令"""
            history = CommandHistory()
            cmd = MockCommand()
            await history.execute(cmd)
            await history.undo()

            result = await history.redo()

            assert result == cmd
            assert history.current_position == 0
            assert history.can_redo is False

        async def test_redo_empty_history(self):
            """测试重做空历史"""
            history = CommandHistory()

            result = await history.redo()

            assert result is None

        async def test_redo_at_end(self):
            """测试在末尾重做"""
            history = CommandHistory()
            cmd = MockCommand()
            await history.execute(cmd)

            result = await history.redo()

            assert result is None

        async def test_redo_with_error(self):
            """测试重做出错时抛出异常"""
            history = CommandHistory()
            cmd = MockCommand()
            await history.execute(cmd)
            cmd._can_execute = False  # 重做时调用 execute
            await history.undo()

            with pytest.raises(Exception, match="Cannot execute"):
                await history.redo()

    class TestUndoMany:
        """测试 undo_many 方法"""

        async def test_undo_many_commands(self):
            """测试撤销多个命令"""
            history = CommandHistory()
            cmds = [MockCommand() for _ in range(5)]
            for cmd in cmds:
                await history.execute(cmd)

            undone = await history.undo_many(3)

            assert len(undone) == 3
            assert history.current_position == 1

        async def test_undo_more_than_available(self):
            """测试撤销超过可用数量的命令"""
            history = CommandHistory()
            cmds = [MockCommand() for _ in range(3)]
            for cmd in cmds:
                await history.execute(cmd)

            undone = await history.undo_many(10)

            assert len(undone) == 3
            assert history.current_position == -1

        async def test_undo_zero(self):
            """测试撤销 0 个命令"""
            history = CommandHistory()
            cmd = MockCommand()
            await history.execute(cmd)

            undone = await history.undo_many(0)

            assert len(undone) == 0
            assert history.current_position == 0

    class TestRedoMany:
        """测试 redo_many 方法"""

        async def test_redo_many_commands(self):
            """测试重做多个命令"""
            history = CommandHistory()
            cmds = [MockCommand() for _ in range(5)]
            for cmd in cmds:
                await history.execute(cmd)
            for _ in range(5):
                await history.undo()

            redone = await history.redo_many(3)

            assert len(redone) == 3
            assert history.current_position == 2

        async def test_redo_more_than_available(self):
            """测试重做超过可用数量的命令"""
            history = CommandHistory()
            cmds = [MockCommand() for _ in range(3)]
            for cmd in cmds:
                await history.execute(cmd)
            for _ in range(3):
                await history.undo()

            redone = await history.redo_many(10)

            assert len(redone) == 3
            assert history.current_position == 2

    class TestGetCommandAt:
        """测试 get_command_at 方法"""

        async def test_get_command_at_valid_index(self):
            """测试获取有效索引的命令"""
            history = CommandHistory()
            cmd = MockCommand()
            await history.execute(cmd)

            result = history.get_command_at(0)

            assert result == cmd

        async def test_get_command_at_invalid_index(self):
            """测试获取无效索引的命令"""
            history = CommandHistory()

            result = history.get_command_at(0)

            assert result is None

        async def test_get_command_at_negative_index(self):
            """测试获取负数索引的命令"""
            history = CommandHistory()
            cmd = MockCommand()
            await history.execute(cmd)

            result = history.get_command_at(-1)

            assert result is None

        async def test_get_command_at_out_of_range(self):
            """测试获取超出范围的索引"""
            history = CommandHistory()
            cmd = MockCommand()
            await history.execute(cmd)

            result = history.get_command_at(10)

            assert result is None

    class TestGetCurrentCommand:
        """测试 get_current_command 方法"""

        async def test_get_current_command_with_commands(self):
            """测试获取当前命令"""
            history = CommandHistory()
            cmd = MockCommand()
            await history.execute(cmd)

            result = history.get_current_command()

            assert result == cmd

        async def test_get_current_command_empty(self):
            """测试空历史时获取当前命令"""
            history = CommandHistory()

            result = history.get_current_command()

            assert result is None

        async def test_get_current_command_after_undo(self):
            """测试撤销后获取当前命令"""
            history = CommandHistory()
            cmd1 = MockCommand()
            cmd2 = MockCommand()
            await history.execute(cmd1)
            await history.execute(cmd2)
            await history.undo()

            result = history.get_current_command()

            assert result == cmd1

    class TestClear:
        """测试 clear 方法"""

        async def test_clear_history(self):
            """测试清除历史"""
            history = CommandHistory()
            for _ in range(5):
                await history.execute(MockCommand())

            history.clear()

            assert history.history_size == 0
            assert history.current_position == -1
            assert history.can_undo is False
            assert history.can_redo is False

        async def test_clear_empty_history(self):
            """测试清除空历史"""
            history = CommandHistory()

            history.clear()  # 不应抛出异常

            assert history.history_size == 0

    class TestGetHistorySummary:
        """测试 get_history_summary 方法"""

        async def test_get_history_summary(self):
            """测试获取历史摘要"""
            history = CommandHistory()
            cmd = MockCommand(name="test_cmd")
            await history.execute(cmd)

            summary = history.get_history_summary()

            assert len(summary) == 1
            assert summary[0]["type"] == "MockCommand"
            assert summary[0]["index"] == 0
            assert summary[0]["is_current"] is True
            assert summary[0]["can_undo"] is True

        async def test_get_history_summary_after_undo(self):
            """测试撤销后获取历史摘要"""
            history = CommandHistory()
            cmd1 = MockCommand(name="cmd1")
            cmd2 = MockCommand(name="cmd2")
            await history.execute(cmd1)
            await history.execute(cmd2)
            await history.undo()

            summary = history.get_history_summary()

            assert len(summary) == 2
            assert summary[0]["is_current"] is True
            assert summary[1]["is_current"] is False

    class TestToDict:
        """测试 to_dict 方法"""

        async def test_to_dict(self):
            """测试序列化"""
            history = CommandHistory(max_history=100)
            cmd = MockCommand()
            await history.execute(cmd)

            data = history.to_dict()

            assert data["max_history"] == 100
            assert data["current_index"] == 0
            assert len(data["commands"]) == 1
            assert data["commands"][0]["type"] == "MockCommand"

    class TestFromDict:
        """测试 from_dict 方法"""

        async def test_from_dict(self):
            """测试反序列化"""
            cmd_id = str(uuid.uuid4())
            data = {
                "max_history": 100,
                "current_index": 0,
                "commands": [
                    {"type": "MockCommand", "id": cmd_id, "name": "restored"},
                ],
            }

            history = CommandHistory.from_dict(data, MockCommandFactory)

            assert history.max_history == 100
            assert history.current_position == 0
            assert history.history_size == 1

        async def test_from_dict_without_factory(self):
            """测试不使用工厂的反序列化"""
            data = {
                "max_history": 50,
                "current_index": -1,
                "commands": [],
            }

            history = CommandHistory.from_dict(data)

            assert history.max_history == 50
            assert history.history_size == 0

        async def test_from_dict_with_unknown_command(self):
            """测试含未知命令的反序列化"""
            data = {
                "max_history": 50,
                "current_index": 0,
                "commands": [
                    {"type": "UnknownCommand", "id": str(uuid.uuid4())},
                ],
            }

            history = CommandHistory.from_dict(data, MockCommandFactory)

            assert history.history_size == 0  # 未知命令被跳过

    class TestProperties:
        """测试属性"""

        async def test_undo_count(self):
            """测试 undo_count 属性"""
            history = CommandHistory()
            await history.execute(MockCommand())
            await history.execute(MockCommand())

            assert history.undo_count == 2

        async def test_redo_count(self):
            """测试 redo_count 属性"""
            history = CommandHistory()
            await history.execute(MockCommand())
            await history.execute(MockCommand())
            await history.undo()

            assert history.redo_count == 1


class TestPresentationCommandHistory:
    """测试 PresentationCommandHistory"""

    class TestInitialization:
        """测试初始化"""

        def test_initialization(self):
            """测试初始化"""
            presentation_id = uuid.uuid4()
            history = PresentationCommandHistory(presentation_id)

            assert history.presentation_id == presentation_id
            assert history.can_undo is False
            assert history.can_redo is False

    class TestDelegation:
        """测试委托方法"""

        async def test_execute_delegation(self):
            """测试 execute 委托"""
            history = PresentationCommandHistory(uuid.uuid4())
            cmd = MockCommand()

            await history.execute(cmd)

            assert history.can_undo is True

        async def test_undo_delegation(self):
            """测试 undo 委托"""
            history = PresentationCommandHistory(uuid.uuid4())
            cmd = MockCommand()
            await history.execute(cmd)

            result = await history.undo()

            assert result == cmd

        async def test_redo_delegation(self):
            """测试 redo 委托"""
            history = PresentationCommandHistory(uuid.uuid4())
            cmd = MockCommand()
            await history.execute(cmd)
            await history.undo()

            result = await history.redo()

            assert result == cmd

    class TestSerialization:
        """测试序列化"""

        async def test_to_dict(self):
            """测试序列化"""
            presentation_id = uuid.uuid4()
            history = PresentationCommandHistory(presentation_id)
            await history.execute(MockCommand())

            data = history.to_dict()

            assert data["presentation_id"] == str(presentation_id)
            assert "history" in data

        async def test_from_dict(self):
            """测试反序列化"""
            presentation_id = uuid.uuid4()
            cmd_id = str(uuid.uuid4())
            data = {
                "presentation_id": str(presentation_id),
                "history": {
                    "max_history": 50,
                    "current_index": 0,
                    "commands": [
                        {"type": "MockCommand", "id": cmd_id, "name": "test"},
                    ],
                },
            }

            history = PresentationCommandHistory.from_dict(data, MockCommandFactory)

            assert history.presentation_id == presentation_id
            assert history.can_undo is True
