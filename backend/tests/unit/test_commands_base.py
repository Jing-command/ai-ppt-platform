"""
测试 Command 基类
"""

import uuid
from datetime import datetime
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_ppt.domain.commands.base import (
    Command,
    CommandException,
    CommandExecutionError,
    CommandFactory,
    CommandMetadata,
    CommandUndoError,
)


class MockCommand(Command):
    """测试用命令类"""

    def __init__(self, data: str = "test"):
        super().__init__()
        self.data = data
        self.executed = False
        self.undone = False

    @property
    def command_type(self) -> str:
        return "MockCommand"

    async def execute(self) -> None:
        self.executed = True
        self.mark_executed()

    async def undo(self) -> None:
        self.undone = True
        self.mark_undone()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.command_type,
            "id": str(self.id),
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockCommand":
        cmd = cls(data=data.get("data", "test"))
        cmd._id = uuid.UUID(data["id"])
        return cmd


class TestCommand:
    """测试 Command 基类"""

    class TestInitialization:
        """测试初始化"""

        def test_command_initialization(self):
            """测试命令初始化"""
            cmd = MockCommand()

            assert cmd.id is not None
            assert isinstance(cmd.id, uuid.UUID)
            assert cmd.executed_at is None
            assert cmd.undone_at is None
            assert cmd.data == "test"

        def test_command_with_custom_data(self):
            """测试带自定义数据的初始化"""
            cmd = MockCommand(data="custom")

            assert cmd.data == "custom"

    class TestMarkExecuted:
        """测试 mark_executed 方法"""

        def test_mark_executed(self):
            """测试标记已执行"""
            cmd = MockCommand()

            cmd.mark_executed()

            assert cmd.executed_at is not None
            assert isinstance(cmd.executed_at, datetime)

        def test_mark_executed_overwrite(self):
            """测试重复标记执行"""
            cmd = MockCommand()

            with patch(
                "ai_ppt.domain.commands.base.datetime"
            ) as mock_datetime:
                first_time = datetime(2024, 1, 1, 12, 0, 0)
                second_time = datetime(2024, 1, 1, 12, 0, 1)

                mock_datetime.utcnow.return_value = first_time
                cmd.mark_executed()
                assert cmd.executed_at == first_time

                mock_datetime.utcnow.return_value = second_time
                cmd.mark_executed()

                assert cmd.executed_at == second_time
                assert cmd.executed_at > first_time

    class TestMarkUndone:
        """测试 mark_undone 方法"""

        def test_mark_undone(self):
            """测试标记已撤销"""
            cmd = MockCommand()

            cmd.mark_undone()

            assert cmd.undone_at is not None
            assert isinstance(cmd.undone_at, datetime)

    class TestExecuteAndUndo:
        """测试 execute 和 undo 方法"""

        async def test_execute(self):
            """测试执行命令"""
            cmd = MockCommand()

            await cmd.execute()

            assert cmd.executed is True
            assert cmd.executed_at is not None

        async def test_undo(self):
            """测试撤销命令"""
            cmd = MockCommand()
            await cmd.execute()

            await cmd.undo()

            assert cmd.undone is True
            assert cmd.undone_at is not None

    class TestToDict:
        """测试 to_dict 方法"""

        def test_to_dict(self):
            """测试序列化"""
            cmd = MockCommand(data="test_data")

            data = cmd.to_dict()

            assert data["type"] == "MockCommand"
            assert data["id"] == str(cmd.id)
            assert data["data"] == "test_data"

    class TestFromDict:
        """测试 from_dict 方法"""

        def test_from_dict(self):
            """测试反序列化"""
            original_id = uuid.uuid4()
            data = {
                "type": "MockCommand",
                "id": str(original_id),
                "data": "restored_data",
            }

            cmd = MockCommand.from_dict(data)

            assert cmd.id == original_id
            assert cmd.data == "restored_data"


class TestCommandMetadata:
    """测试 CommandMetadata"""

    class TestInitialization:
        """测试初始化"""

        def test_default_initialization(self):
            """测试默认初始化"""
            target_id = uuid.uuid4()
            metadata = CommandMetadata(
                command_type="TestCommand",
                target_id=target_id,
                target_type="Slide",
            )

            assert metadata.command_type == "TestCommand"
            assert metadata.target_id == target_id
            assert metadata.target_type == "Slide"
            assert metadata.id is not None
            assert metadata.created_at is not None
            assert metadata.executed_at is None
            assert metadata.undone_at is None
            assert metadata.payload == {}

        def test_full_initialization(self):
            """测试完整初始化"""
            target_id = uuid.uuid4()
            executed_at = datetime.utcnow()
            metadata = CommandMetadata(
                command_type="TestCommand",
                target_id=target_id,
                target_type="Slide",
                executed_at=executed_at,
                payload={"key": "value"},
            )

            assert metadata.executed_at == executed_at
            assert metadata.payload == {"key": "value"}

    class TestToDict:
        """测试 to_dict 方法"""

        def test_to_dict_with_all_fields(self):
            """测试完整序列化"""
            target_id = uuid.uuid4()
            executed_at = datetime.utcnow()
            metadata = CommandMetadata(
                command_type="TestCommand",
                target_id=target_id,
                target_type="Slide",
                executed_at=executed_at,
                payload={"key": "value"},
            )

            data = metadata.to_dict()

            assert data["command_type"] == "TestCommand"
            assert data["target_id"] == str(target_id)
            assert data["target_type"] == "Slide"
            assert data["executed_at"] == executed_at.isoformat()
            assert data["payload"] == {"key": "value"}

        def test_to_dict_with_none_fields(self):
            """测试含 None 字段的序列化"""
            target_id = uuid.uuid4()
            metadata = CommandMetadata(
                command_type="TestCommand",
                target_id=target_id,
                target_type="Slide",
            )

            data = metadata.to_dict()

            assert data["executed_at"] is None
            assert data["undone_at"] is None

    class TestFromDict:
        """测试 from_dict 方法"""

        def test_from_dict(self):
            """测试反序列化"""
            id_val = uuid.uuid4()
            target_id = uuid.uuid4()
            created_at = datetime.utcnow()
            executed_at = datetime.utcnow()

            data = {
                "id": str(id_val),
                "command_type": "TestCommand",
                "target_id": str(target_id),
                "target_type": "Slide",
                "created_at": created_at.isoformat(),
                "executed_at": executed_at.isoformat(),
                "undone_at": None,
                "payload": {"key": "value"},
            }

            metadata = CommandMetadata.from_dict(data)

            assert metadata.id == id_val
            assert metadata.command_type == "TestCommand"
            assert metadata.target_id == target_id
            assert metadata.created_at == created_at
            assert metadata.executed_at == executed_at
            assert metadata.payload == {"key": "value"}

        def test_from_dict_without_optional_fields(self):
            """测试不含可选字段的反序列化"""
            data = {
                "id": str(uuid.uuid4()),
                "command_type": "TestCommand",
                "target_id": str(uuid.uuid4()),
                "target_type": "Slide",
                "created_at": datetime.utcnow().isoformat(),
            }

            metadata = CommandMetadata.from_dict(data)

            assert metadata.payload == {}


class TestCommandFactory:
    """测试 CommandFactory"""

    class TestRegister:
        """测试 register 方法"""

        def test_register_command(self):
            """测试注册命令类型"""
            CommandFactory.register("MockCommand", MockCommand)

            assert "MockCommand" in CommandFactory._registry

        def test_register_overwrite(self):
            """测试覆盖注册"""
            CommandFactory.register("MockCommand", MockCommand)
            CommandFactory.register("MockCommand", MockCommand)

            assert CommandFactory._registry["MockCommand"] == MockCommand

    class TestUnregister:
        """测试 unregister 方法"""

        def test_unregister_command(self):
            """测试注销命令类型"""
            CommandFactory.register("TestUnregister", MockCommand)

            CommandFactory.unregister("TestUnregister")

            assert "TestUnregister" not in CommandFactory._registry

        def test_unregister_nonexistent(self):
            """测试注销不存在的命令类型"""
            # 不应抛出异常
            CommandFactory.unregister("NonExistent")

    class TestCreate:
        """测试 create 方法"""

        def test_create_command(self):
            """测试创建命令实例"""
            CommandFactory.register("MockCommand", MockCommand)
            cmd_id = uuid.uuid4()
            data = {
                "type": "MockCommand",
                "id": str(cmd_id),
                "data": "created_data",
            }

            cmd = CommandFactory.create(data)

            assert isinstance(cmd, MockCommand)
            assert cmd.id == cmd_id
            assert cmd.data == "created_data"

        def test_create_missing_type(self):
            """测试缺少 type 字段"""
            with pytest.raises(ValueError, match="must contain 'type' field"):
                CommandFactory.create({"id": str(uuid.uuid4())})

        def test_create_unknown_type(self):
            """测试未知的命令类型"""
            with pytest.raises(ValueError, match="Unknown command type"):
                CommandFactory.create({"type": "UnknownCommand"})


class TestCommandExceptions:
    """测试 Command 异常类"""

    def test_command_exception(self):
        """测试 CommandException"""
        exc = CommandException("Test error")

        assert str(exc) == "Test error"

    def test_command_execution_error(self):
        """测试 CommandExecutionError"""
        cmd = MockCommand()
        exc = CommandExecutionError("Execution failed", command=cmd)

        assert str(exc) == "Execution failed"
        assert exc.command == cmd

    def test_command_execution_error_without_command(self):
        """测试不带命令的 CommandExecutionError"""
        exc = CommandExecutionError("Execution failed")

        assert str(exc) == "Execution failed"
        assert exc.command is None

    def test_command_undo_error(self):
        """测试 CommandUndoError"""
        cmd = MockCommand()
        exc = CommandUndoError("Undo failed", command=cmd)

        assert str(exc) == "Undo failed"
        assert exc.command == cmd


class TestCommandEdgeCases:
    """测试边界情况"""

    def test_command_id_unique(self):
        """测试命令 ID 唯一性"""
        cmd1 = MockCommand()
        cmd2 = MockCommand()

        assert cmd1.id != cmd2.id

    async def test_command_execute_exception(self):
        """测试执行时抛出异常"""

        class FailingCommand(Command):
            @property
            def command_type(self) -> str:
                return "FailingCommand"

            async def execute(self) -> None:
                raise ValueError("Execute failed")

            async def undo(self) -> None:
                pass

            def to_dict(self) -> Dict[str, Any]:
                return {"type": self.command_type}

            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "FailingCommand":
                return cls()

        cmd = FailingCommand()

        with pytest.raises(ValueError, match="Execute failed"):
            await cmd.execute()

    async def test_command_undo_exception(self):
        """测试撤销时抛出异常"""

        class FailingUndoCommand(Command):
            @property
            def command_type(self) -> str:
                return "FailingUndoCommand"

            async def execute(self) -> None:
                self.mark_executed()

            async def undo(self) -> None:
                raise ValueError("Undo failed")

            def to_dict(self) -> Dict[str, Any]:
                return {"type": self.command_type}

            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "FailingUndoCommand":
                return cls()

        cmd = FailingUndoCommand()
        await cmd.execute()

        with pytest.raises(ValueError, match="Undo failed"):
            await cmd.undo()
