"""
测试 Slide Commands
"""

import uuid
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_ppt.domain.commands.slide_commands import (
    CreateSlideCommand,
    DeleteSlideCommand,
    MoveSlideCommand,
    UpdateSlideCommand,
)
from ai_ppt.domain.models.slide import SlideLayoutType


@pytest.fixture
def mock_slide_repository():
    """创建模拟的幻灯片仓储"""
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.reorder_slides = AsyncMock()
    return repo


@pytest.fixture
def sample_slide():
    """创建示例幻灯片"""
    slide = MagicMock()
    slide.id = uuid.uuid4()
    slide.presentation_id = uuid.uuid4()
    slide.title = "Test Slide"
    slide.subtitle = "Test Subtitle"
    slide.layout_type = SlideLayoutType.TITLE_CONTENT
    slide.content = {"text": "Content"}
    slide.notes = "Notes"
    slide.background_color = "#ffffff"
    slide.text_color = "#000000"
    slide.font_family = "Arial"
    slide.order_index = 1
    slide.version = 1
    slide.move_to = MagicMock()
    return slide


class TestCreateSlideCommand:
    """测试 CreateSlideCommand"""

    class TestInitialization:
        """测试初始化"""

        def test_default_initialization(self):
            """测试默认初始化"""
            presentation_id = uuid.uuid4()
            cmd = CreateSlideCommand(
                presentation_id=presentation_id,
                title="Test Slide",
            )

            assert cmd.presentation_id == presentation_id
            assert cmd.title == "Test Slide"
            assert cmd.layout_type == "title_content"
            assert cmd.content == {}
            assert cmd.order_index is None
            assert cmd.command_type == "CreateSlideCommand"

        def test_full_initialization(self):
            """测试完整初始化"""
            presentation_id = uuid.uuid4()
            cmd = CreateSlideCommand(
                presentation_id=presentation_id,
                title="Test Slide",
                layout_type="title_only",
                content={"text": "Hello"},
                order_index=2,
            )

            assert cmd.layout_type == "title_only"
            assert cmd.content == {"text": "Hello"}
            assert cmd.order_index == 2

    class TestExecute:
        """测试 execute 方法"""

        async def test_execute_success(self, mock_slide_repository, sample_slide):
            """测试成功执行创建"""
            presentation_id = uuid.uuid4()
            cmd = CreateSlideCommand(
                presentation_id=presentation_id,
                title="New Slide",
                layout_type="title_content",
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.create.return_value = sample_slide

            await cmd.execute()

            assert cmd._created_slide_id == sample_slide.id
            assert cmd.executed_at is not None
            mock_slide_repository.create.assert_called_once()

        async def test_execute_without_repository(self):
            """测试缺少仓储时抛出异常"""
            cmd = CreateSlideCommand(
                presentation_id=uuid.uuid4(),
                title="Test",
            )

            with pytest.raises(ValueError, match="Slide repository is required"):
                await cmd.execute()

    class TestUndo:
        """测试 undo 方法"""

        async def test_undo_success(self, mock_slide_repository, sample_slide):
            """测试成功撤销创建"""
            cmd = CreateSlideCommand(
                presentation_id=uuid.uuid4(),
                title="New Slide",
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.create.return_value = sample_slide

            await cmd.execute()
            await cmd.undo()

            assert cmd.undone_at is not None
            mock_slide_repository.delete.assert_called_once_with(sample_slide.id)

        async def test_undo_without_repository(self):
            """测试缺少仓储时抛出异常"""
            cmd = CreateSlideCommand(
                presentation_id=uuid.uuid4(),
                title="Test",
            )
            cmd._created_slide_id = uuid.uuid4()

            with pytest.raises(ValueError, match="Slide repository is required"):
                await cmd.undo()

        async def test_undo_without_created_slide(self, mock_slide_repository):
            """测试未创建幻灯片时撤销"""
            cmd = CreateSlideCommand(
                presentation_id=uuid.uuid4(),
                title="Test",
                slide_repository=mock_slide_repository,
            )

            await cmd.undo()

            mock_slide_repository.delete.assert_not_called()

    class TestSerialization:
        """测试序列化"""

        def test_to_dict(self, mock_slide_repository, sample_slide):
            """测试序列化"""
            presentation_id = uuid.uuid4()
            cmd = CreateSlideCommand(
                presentation_id=presentation_id,
                title="Test Slide",
                layout_type="title_content",
                content={"text": "Hello"},
                order_index=1,
                slide_repository=mock_slide_repository,
            )
            cmd._created_slide_id = sample_slide.id

            data = cmd.to_dict()

            assert data["type"] == "CreateSlideCommand"
            assert data["presentation_id"] == str(presentation_id)
            assert data["title"] == "Test Slide"
            assert data["layout_type"] == "title_content"
            assert data["content"] == {"text": "Hello"}
            assert data["order_index"] == 1
            assert data["created_slide_id"] == str(sample_slide.id)

        def test_from_dict(self):
            """测试反序列化"""
            presentation_id = uuid.uuid4()
            cmd_id = uuid.uuid4()
            slide_id = uuid.uuid4()

            data = {
                "type": "CreateSlideCommand",
                "id": str(cmd_id),
                "presentation_id": str(presentation_id),
                "title": "Test Slide",
                "layout_type": "title_content",
                "content": {"text": "Hello"},
                "order_index": 1,
                "created_slide_id": str(slide_id),
            }

            cmd = CreateSlideCommand.from_dict(data)

            assert cmd.id == cmd_id
            assert cmd.presentation_id == presentation_id
            assert cmd.title == "Test Slide"
            assert cmd._created_slide_id == slide_id


class TestUpdateSlideCommand:
    """测试 UpdateSlideCommand"""

    class TestInitialization:
        """测试初始化"""

        def test_initialization(self):
            """测试初始化"""
            slide_id = uuid.uuid4()
            updates = {"title": "Updated Title"}
            cmd = UpdateSlideCommand(
                slide_id=slide_id,
                updates=updates,
            )

            assert cmd.slide_id == slide_id
            assert cmd.updates == updates
            assert cmd.command_type == "UpdateSlideCommand"

    class TestExecute:
        """测试 execute 方法"""

        async def test_execute_success(self, mock_slide_repository, sample_slide):
            """测试成功执行更新"""
            cmd = UpdateSlideCommand(
                slide_id=sample_slide.id,
                updates={"title": "Updated Title"},
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.get_by_id.return_value = sample_slide

            await cmd.execute()

            assert sample_slide.title == "Updated Title"
            assert cmd._previous_data is not None
            assert cmd._previous_data["title"] == "Test Slide"
            mock_slide_repository.update.assert_called_once()
            assert cmd.executed_at is not None

        async def test_execute_all_fields(self, mock_slide_repository, sample_slide):
            """测试更新所有字段"""
            cmd = UpdateSlideCommand(
                slide_id=sample_slide.id,
                updates={
                    "title": "New Title",
                    "subtitle": "New Subtitle",
                    "layout_type": "title_only",
                    "content": {"new": "content"},
                    "notes": "New Notes",
                    "background_color": "#000000",
                    "text_color": "#ffffff",
                    "font_family": "Times New Roman",
                },
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.get_by_id.return_value = sample_slide

            await cmd.execute()

            assert sample_slide.title == "New Title"
            assert sample_slide.subtitle == "New Subtitle"
            assert sample_slide.notes == "New Notes"
            mock_slide_repository.update.assert_called_once()

        async def test_execute_without_repository(self):
            """测试缺少仓储时抛出异常"""
            cmd = UpdateSlideCommand(
                slide_id=uuid.uuid4(),
                updates={"title": "Test"},
            )

            with pytest.raises(ValueError, match="Slide repository is required"):
                await cmd.execute()

        async def test_execute_slide_not_found(self, mock_slide_repository):
            """测试幻灯片不存在时抛出异常"""
            cmd = UpdateSlideCommand(
                slide_id=uuid.uuid4(),
                updates={"title": "Test"},
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.get_by_id.return_value = None

            with pytest.raises(ValueError, match="Slide .* not found"):
                await cmd.execute()

    class TestUndo:
        """测试 undo 方法"""

        async def test_undo_success(self, mock_slide_repository, sample_slide):
            """测试成功撤销更新"""
            cmd = UpdateSlideCommand(
                slide_id=sample_slide.id,
                updates={"title": "Updated Title"},
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.get_by_id.return_value = sample_slide

            await cmd.execute()
            original_title = sample_slide.title
            sample_slide.title = "Updated Title"
            await cmd.undo()

            assert sample_slide.title == "Test Slide"  # 恢复原值
            assert cmd.undone_at is not None

        async def test_undo_without_repository(self):
            """测试缺少仓储时抛出异常"""
            cmd = UpdateSlideCommand(
                slide_id=uuid.uuid4(),
                updates={"title": "Test"},
            )
            cmd._previous_data = {"title": "Old Title"}

            with pytest.raises(ValueError, match="Slide repository is required"):
                await cmd.undo()

        async def test_undo_without_previous_data(self, mock_slide_repository):
            """测试无先前数据时抛出异常"""
            cmd = UpdateSlideCommand(
                slide_id=uuid.uuid4(),
                updates={"title": "Test"},
                slide_repository=mock_slide_repository,
            )

            with pytest.raises(ValueError, match="No previous data to restore"):
                await cmd.undo()

        async def test_undo_slide_not_found(self, mock_slide_repository):
            """测试幻灯片不存在时抛出异常"""
            cmd = UpdateSlideCommand(
                slide_id=uuid.uuid4(),
                updates={"title": "Test"},
                slide_repository=mock_slide_repository,
            )
            cmd._previous_data = {"title": "Old Title"}
            mock_slide_repository.get_by_id.return_value = None

            with pytest.raises(ValueError, match="Slide .* not found"):
                await cmd.undo()

    class TestSerialization:
        """测试序列化"""

        def test_to_dict(self):
            """测试序列化"""
            slide_id = uuid.uuid4()
            cmd = UpdateSlideCommand(
                slide_id=slide_id,
                updates={"title": "Updated"},
            )
            cmd._previous_data = {"title": "Original"}

            data = cmd.to_dict()

            assert data["type"] == "UpdateSlideCommand"
            assert data["slide_id"] == str(slide_id)
            assert data["updates"] == {"title": "Updated"}
            assert data["previous_data"] == {"title": "Original"}

        def test_from_dict(self):
            """测试反序列化"""
            slide_id = uuid.uuid4()
            cmd_id = uuid.uuid4()

            data = {
                "type": "UpdateSlideCommand",
                "id": str(cmd_id),
                "slide_id": str(slide_id),
                "updates": {"title": "Updated"},
                "previous_data": {"title": "Original"},
            }

            cmd = UpdateSlideCommand.from_dict(data)

            assert cmd.id == cmd_id
            assert cmd.slide_id == slide_id
            assert cmd.updates == {"title": "Updated"}
            assert cmd._previous_data == {"title": "Original"}


class TestDeleteSlideCommand:
    """测试 DeleteSlideCommand"""

    class TestInitialization:
        """测试初始化"""

        def test_initialization(self):
            """测试初始化"""
            slide_id = uuid.uuid4()
            cmd = DeleteSlideCommand(slide_id=slide_id)

            assert cmd.slide_id == slide_id
            assert cmd.command_type == "DeleteSlideCommand"

    class TestExecute:
        """测试 execute 方法"""

        async def test_execute_success(self, mock_slide_repository, sample_slide):
            """测试成功执行删除"""
            cmd = DeleteSlideCommand(
                slide_id=sample_slide.id,
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.get_by_id.return_value = sample_slide

            await cmd.execute()

            assert cmd._deleted_data is not None
            assert cmd._deleted_data["title"] == sample_slide.title
            assert cmd._deleted_data["id"] == sample_slide.id
            mock_slide_repository.delete.assert_called_once_with(sample_slide.id)
            assert cmd.executed_at is not None

        async def test_execute_without_repository(self):
            """测试缺少仓储时抛出异常"""
            cmd = DeleteSlideCommand(slide_id=uuid.uuid4())

            with pytest.raises(ValueError, match="Slide repository is required"):
                await cmd.execute()

        async def test_execute_slide_not_found(self, mock_slide_repository):
            """测试幻灯片不存在时抛出异常"""
            cmd = DeleteSlideCommand(
                slide_id=uuid.uuid4(),
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.get_by_id.return_value = None

            with pytest.raises(ValueError, match="Slide .* not found"):
                await cmd.execute()

    class TestUndo:
        """测试 undo 方法"""

        async def test_undo_success(self, mock_slide_repository, sample_slide):
            """测试成功撤销删除"""
            cmd = DeleteSlideCommand(
                slide_id=sample_slide.id,
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.get_by_id.return_value = sample_slide

            await cmd.execute()
            await cmd.undo()

            mock_slide_repository.create.assert_called_once()
            created_slide = mock_slide_repository.create.call_args[0][0]
            assert created_slide.title == sample_slide.title
            assert cmd.undone_at is not None

        async def test_undo_without_repository(self):
            """测试缺少仓储时抛出异常"""
            cmd = DeleteSlideCommand(slide_id=uuid.uuid4())
            cmd._deleted_data = {"title": "Old Slide"}

            with pytest.raises(ValueError, match="Slide repository is required"):
                await cmd.undo()

        async def test_undo_without_deleted_data(self, mock_slide_repository):
            """测试无删除数据时抛出异常"""
            cmd = DeleteSlideCommand(
                slide_id=uuid.uuid4(),
                slide_repository=mock_slide_repository,
            )

            with pytest.raises(ValueError, match="No deleted data to restore"):
                await cmd.undo()

    class TestSerialization:
        """测试序列化"""

        def test_to_dict(self, mock_slide_repository, sample_slide):
            """测试序列化"""
            cmd = DeleteSlideCommand(
                slide_id=sample_slide.id,
                slide_repository=mock_slide_repository,
            )
            cmd._deleted_data = {
                "id": sample_slide.id,
                "title": sample_slide.title,
                "presentation_id": sample_slide.presentation_id,
                "layout_type": sample_slide.layout_type,
                "content": sample_slide.content,
            }

            data = cmd.to_dict()

            assert data["type"] == "DeleteSlideCommand"
            assert data["slide_id"] == str(sample_slide.id)
            assert data["deleted_data"]["title"] == sample_slide.title

        def test_from_dict(self):
            """测试反序列化"""
            slide_id = uuid.uuid4()
            cmd_id = uuid.uuid4()

            data = {
                "type": "DeleteSlideCommand",
                "id": str(cmd_id),
                "slide_id": str(slide_id),
                "deleted_data": {"title": "Deleted Slide"},
            }

            cmd = DeleteSlideCommand.from_dict(data)

            assert cmd.id == cmd_id
            assert cmd.slide_id == slide_id
            assert cmd._deleted_data == {"title": "Deleted Slide"}


class TestMoveSlideCommand:
    """测试 MoveSlideCommand"""

    class TestInitialization:
        """测试初始化"""

        def test_initialization(self):
            """测试初始化"""
            slide_id = uuid.uuid4()
            cmd = MoveSlideCommand(
                slide_id=slide_id,
                new_order=5,
            )

            assert cmd.slide_id == slide_id
            assert cmd.new_order == 5
            assert cmd.command_type == "MoveSlideCommand"

    class TestExecute:
        """测试 execute 方法"""

        async def test_execute_success(self, mock_slide_repository, sample_slide):
            """测试成功执行移动"""
            cmd = MoveSlideCommand(
                slide_id=sample_slide.id,
                new_order=5,
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.get_by_id.return_value = sample_slide
            sample_slide.presentation_id = uuid.uuid4()

            await cmd.execute()

            assert cmd._previous_order == 1  # 原始顺序
            sample_slide.move_to.assert_called_once_with(5)
            mock_slide_repository.update.assert_called_once()
            mock_slide_repository.reorder_slides.assert_called_once()
            assert cmd.executed_at is not None

        async def test_execute_without_repository(self):
            """测试缺少仓储时抛出异常"""
            cmd = MoveSlideCommand(
                slide_id=uuid.uuid4(),
                new_order=5,
            )

            with pytest.raises(ValueError, match="Slide repository is required"):
                await cmd.execute()

        async def test_execute_slide_not_found(self, mock_slide_repository):
            """测试幻灯片不存在时抛出异常"""
            cmd = MoveSlideCommand(
                slide_id=uuid.uuid4(),
                new_order=5,
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.get_by_id.return_value = None

            with pytest.raises(ValueError, match="Slide .* not found"):
                await cmd.execute()

    class TestUndo:
        """测试 undo 方法"""

        async def test_undo_success(self, mock_slide_repository, sample_slide):
            """测试成功撤销移动"""
            cmd = MoveSlideCommand(
                slide_id=sample_slide.id,
                new_order=5,
                slide_repository=mock_slide_repository,
            )
            mock_slide_repository.get_by_id.return_value = sample_slide
            sample_slide.presentation_id = uuid.uuid4()

            await cmd.execute()
            sample_slide.move_to.reset_mock()
            await cmd.undo()

            sample_slide.move_to.assert_called_once_with(1)  # 恢复原始顺序
            assert cmd.undone_at is not None

        async def test_undo_without_repository(self):
            """测试缺少仓储时抛出异常"""
            cmd = MoveSlideCommand(
                slide_id=uuid.uuid4(),
                new_order=5,
            )
            cmd._previous_order = 1

            with pytest.raises(ValueError, match="Slide repository is required"):
                await cmd.undo()

        async def test_undo_without_previous_order(self, mock_slide_repository):
            """测试无先前顺序时抛出异常"""
            cmd = MoveSlideCommand(
                slide_id=uuid.uuid4(),
                new_order=5,
                slide_repository=mock_slide_repository,
            )

            with pytest.raises(ValueError, match="No previous order to restore"):
                await cmd.undo()

        async def test_undo_slide_not_found(self, mock_slide_repository):
            """测试幻灯片不存在时抛出异常"""
            cmd = MoveSlideCommand(
                slide_id=uuid.uuid4(),
                new_order=5,
                slide_repository=mock_slide_repository,
            )
            cmd._previous_order = 1
            mock_slide_repository.get_by_id.return_value = None

            with pytest.raises(ValueError, match="Slide .* not found"):
                await cmd.undo()

    class TestSerialization:
        """测试序列化"""

        def test_to_dict(self):
            """测试序列化"""
            slide_id = uuid.uuid4()
            cmd = MoveSlideCommand(
                slide_id=slide_id,
                new_order=5,
            )
            cmd._previous_order = 1

            data = cmd.to_dict()

            assert data["type"] == "MoveSlideCommand"
            assert data["slide_id"] == str(slide_id)
            assert data["new_order"] == 5
            assert data["previous_order"] == 1

        def test_from_dict(self):
            """测试反序列化"""
            slide_id = uuid.uuid4()
            cmd_id = uuid.uuid4()

            data = {
                "type": "MoveSlideCommand",
                "id": str(cmd_id),
                "slide_id": str(slide_id),
                "new_order": 5,
                "previous_order": 1,
            }

            cmd = MoveSlideCommand.from_dict(data)

            assert cmd.id == cmd_id
            assert cmd.slide_id == slide_id
            assert cmd.new_order == 5
            assert cmd._previous_order == 1


class TestSlideCommandsEdgeCases:
    """测试边界情况"""

    async def test_create_slide_with_empty_content(
        self, mock_slide_repository, sample_slide
    ):
        """测试创建空内容幻灯片"""
        cmd = CreateSlideCommand(
            presentation_id=uuid.uuid4(),
            title="Empty Slide",
            content={},
            slide_repository=mock_slide_repository,
        )
        mock_slide_repository.create.return_value = sample_slide

        await cmd.execute()

        assert cmd._created_slide_id is not None

    async def test_update_slide_partial_fields(
        self, mock_slide_repository, sample_slide
    ):
        """测试部分字段更新"""
        cmd = UpdateSlideCommand(
            slide_id=sample_slide.id,
            updates={"title": "Only Title"},
            slide_repository=mock_slide_repository,
        )
        mock_slide_repository.get_by_id.return_value = sample_slide

        await cmd.execute()

        assert sample_slide.title == "Only Title"
        # 其他字段应该保持不变

    async def test_move_slide_to_same_position(
        self, mock_slide_repository, sample_slide
    ):
        """测试移动到相同位置"""
        cmd = MoveSlideCommand(
            slide_id=sample_slide.id,
            new_order=1,  # 和当前位置相同
            slide_repository=mock_slide_repository,
        )
        mock_slide_repository.get_by_id.return_value = sample_slide
        sample_slide.presentation_id = uuid.uuid4()

        await cmd.execute()

        assert cmd._previous_order == 1
        sample_slide.move_to.assert_called_once_with(1)
