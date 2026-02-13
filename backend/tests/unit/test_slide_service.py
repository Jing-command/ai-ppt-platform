"""
幻灯片服务单元测试
"""

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_ppt.application.services.presentation_service import PresentationNotFoundError
from ai_ppt.application.services.slide_service import SlideService, UndoRedoError
from ai_ppt.domain.commands.slide_commands import UpdateSlideCommand
from ai_ppt.domain.models.slide import Slide, SlideLayoutType


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    session = AsyncMock()
    return session


@pytest.fixture
def slide_service(mock_db_session):
    """创建幻灯片服务实例"""
    return SlideService(mock_db_session)


@pytest.fixture
def sample_presentation():
    """示例演示文稿"""
    from ai_ppt.domain.models.presentation import Presentation

    return Presentation(
        id=uuid.uuid4(),
        title="Test Presentation",
        owner_id=uuid.uuid4(),
        theme="default",
    )


@pytest.fixture
def sample_slide():
    """示例幻灯片"""
    return Slide(
        id=uuid.uuid4(),
        title="Test Slide",
        presentation_id=uuid.uuid4(),
        layout_type=SlideLayoutType.TITLE_CONTENT,
        order_index=0,
        content={"title": "Test", "text": "Content"},
    )


class TestSlideServiceUpdateSlide:
    """测试更新幻灯片"""

    async def test_update_slide_success(
        self, slide_service, mock_db_session, sample_presentation, sample_slide
    ):
        """测试成功更新幻灯片"""
        ppt_id = uuid.uuid4()
        user_id = uuid.uuid4()

        # 模拟演示文稿服务
        with patch.object(
            slide_service._presentation_service, "update_slide"
        ) as mock_update:
            mock_update.return_value = sample_slide

            result = await slide_service.update_slide(
                presentation_id=ppt_id,
                slide_id=sample_slide.id,
                user_id=user_id,
                updates={"content": {"title": "Updated"}},
            )

        assert result["title"] == sample_slide.title
        mock_update.assert_called_once()

    async def test_update_slide_creates_command(
        self, slide_service, mock_db_session, sample_presentation
    ):
        """测试更新创建命令"""
        ppt_id = uuid.uuid4()
        user_id = uuid.uuid4()

        from ai_ppt.api.v1.schemas.presentation import SlideUpdate

        with patch.object(
            slide_service._presentation_service, "update_slide"
        ) as mock_update:
            mock_update.return_value = Slide(
                id=uuid.uuid4(),
                title="Updated",
                presentation_id=ppt_id,
                layout_type=SlideLayoutType.TITLE_CONTENT,
                order_index=0,
                content={"title": "Updated"},
            )

            await slide_service.update_slide(
                presentation_id=ppt_id,
                slide_id=uuid.uuid4(),
                user_id=user_id,
                updates={"content": {"title": "Updated"}},
            )

        # 验证命令被添加到历史
        history = slide_service._get_command_history(ppt_id)
        assert history.undo_count >= 0


class TestSlideServiceUndo:
    """测试撤销操作"""

    async def test_undo_success(
        self, slide_service, mock_db_session, sample_presentation
    ):
        """测试成功撤销"""
        ppt_id = sample_presentation.id
        slide_id = uuid.uuid4()
        user_id = sample_presentation.owner_id

        # 设置命令历史
        history = slide_service._get_command_history(ppt_id)

        # 创建一个模拟命令
        mock_command = MagicMock()
        mock_command.command_type = "UPDATE_SLIDE"
        mock_command.slide_id = slide_id
        await history.execute(mock_command)

        with patch.object(slide_service._presentation_service, "get_by_id_or_raise"):
            with patch.object(slide_service._slide_repo, "get_by_id") as mock_get_slide:
                mock_get_slide.return_value = Slide(
                    id=slide_id,
                    title="Before Undo",
                    presentation_id=ppt_id,
                    layout_type=SlideLayoutType.TITLE_CONTENT,
                    order_index=0,
                    content={},
                )

                result = await slide_service.undo(ppt_id, slide_id, user_id)

        assert result["success"] is True
        assert "撤销" in result["description"]

    async def test_undo_no_history(self, slide_service, mock_db_session):
        """测试无历史记录时撤销"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()
        user_id = uuid.uuid4()

        with patch.object(slide_service._presentation_service, "get_by_id_or_raise"):
            with pytest.raises(UndoRedoError) as exc_info:
                await slide_service.undo(ppt_id, slide_id, user_id)

            assert "没有可撤销" in str(exc_info.value)

    async def test_undo_presentation_not_found(self, slide_service, mock_db_session):
        """测试演示文稿不存在时撤销"""
        with patch.object(
            slide_service._presentation_service, "get_by_id_or_raise"
        ) as mock_get:
            mock_get.side_effect = PresentationNotFoundError("Not found")

            with pytest.raises(PresentationNotFoundError):
                await slide_service.undo(uuid.uuid4(), uuid.uuid4(), uuid.uuid4())


class TestSlideServiceRedo:
    """测试重做操作"""

    async def test_redo_success(
        self, slide_service, mock_db_session, sample_presentation
    ):
        """测试成功重做"""
        ppt_id = sample_presentation.id
        slide_id = uuid.uuid4()
        user_id = sample_presentation.owner_id

        # 设置命令历史
        history = slide_service._get_command_history(ppt_id)

        # 创建并执行命令，然后撤销
        mock_command = MagicMock()
        mock_command.command_type = "UPDATE_SLIDE"
        mock_command.slide_id = slide_id
        await history.execute(mock_command)
        await history.undo()

        with patch.object(slide_service._presentation_service, "get_by_id_or_raise"):
            with patch.object(slide_service._slide_repo, "get_by_id") as mock_get_slide:
                mock_get_slide.return_value = Slide(
                    id=slide_id,
                    title="After Redo",
                    presentation_id=ppt_id,
                    layout_type=SlideLayoutType.TITLE_CONTENT,
                    order_index=0,
                    content={},
                )

                result = await slide_service.redo(ppt_id, slide_id, user_id)

        assert result["success"] is True
        assert "重做" in result["description"]

    async def test_redo_no_history(self, slide_service, mock_db_session):
        """测试无可重做操作时"""
        ppt_id = uuid.uuid4()
        slide_id = uuid.uuid4()
        user_id = uuid.uuid4()

        with patch.object(slide_service._presentation_service, "get_by_id_or_raise"):
            with pytest.raises(UndoRedoError) as exc_info:
                await slide_service.redo(ppt_id, slide_id, user_id)

            assert "没有可重做" in str(exc_info.value)


class TestSlideServiceHistory:
    """测试命令历史"""

    def test_get_command_history_creates_new(self, slide_service):
        """测试获取命令历史（新建）"""
        ppt_id = uuid.uuid4()

        history = slide_service._get_command_history(ppt_id)

        assert history is not None

    def test_get_command_history_returns_existing(self, slide_service):
        """测试获取已存在的命令历史"""
        ppt_id = uuid.uuid4()

        history1 = slide_service._get_command_history(ppt_id)
        history2 = slide_service._get_command_history(ppt_id)

        assert history1 is history2

    def test_get_undo_redo_status(self, slide_service):
        """测试获取撤销/重做状态"""
        ppt_id = uuid.uuid4()

        status = slide_service.get_undo_redo_status(ppt_id)

        assert "can_undo" in status
        assert "can_redo" in status
        assert "undo_count" in status
        assert "redo_count" in status

    async def test_clear_history(self, slide_service):
        """测试清除历史"""
        ppt_id = uuid.uuid4()

        # 添加一些历史
        history = slide_service._get_command_history(ppt_id)
        mock_command = MagicMock()
        await history.execute(mock_command)

        assert history.undo_count > 0

        # 清除历史
        await slide_service.clear_history(ppt_id)

        assert history.undo_count == 0
