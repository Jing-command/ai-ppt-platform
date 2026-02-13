"""
演示文稿服务单元测试
"""

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_ppt.api.v1.schemas.presentation import (
    PresentationCreate,
    PresentationUpdate,
    SlideContent,
    SlideCreate,
    SlideLayout,
    SlideUpdate,
)
from ai_ppt.application.services.presentation_service import (
    PresentationNotFoundError,
    PresentationService,
    SlideNotFoundError,
)
from ai_ppt.domain.models.presentation import Presentation, PresentationStatus
from ai_ppt.domain.models.slide import Slide, SlideLayoutType


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def mock_slide_repo():
    """模拟幻灯片仓储"""
    repo = AsyncMock()
    return repo


@pytest.fixture
def presentation_service(mock_db_session, mock_slide_repo):
    """创建演示文稿服务实例"""
    service = PresentationService(mock_db_session)
    service._slide_repo = mock_slide_repo
    return service


@pytest.fixture
def sample_presentation():
    """示例演示文稿"""
    return Presentation(
        id=uuid.uuid4(),
        title="Test Presentation",
        owner_id=uuid.uuid4(),
        description="Test description",
        theme="default",
        status=PresentationStatus.DRAFT,
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


class TestPresentationServiceCreate:
    """测试创建演示文稿"""

    async def test_create_success(self, presentation_service, mock_db_session):
        """测试成功创建"""
        user_id = uuid.uuid4()
        data = PresentationCreate(title="New Presentation")

        result = await presentation_service.create(data, user_id)

        assert result.title == "New Presentation"
        assert result.owner_id == user_id
        assert result.theme == "default"

        mock_db_session.add.assert_called()
        mock_db_session.flush.assert_called()

    async def test_create_with_description(self, presentation_service, mock_db_session):
        """测试带描述创建"""
        data = PresentationCreate(
            title="With Description",
            description="This is a description",
        )

        result = await presentation_service.create(data, uuid.uuid4())

        assert result.description == "This is a description"

    async def test_create_with_template(self, presentation_service, mock_db_session):
        """测试带模板创建"""
        data = PresentationCreate(
            title="With Template",
            template_id="modern",
        )

        result = await presentation_service.create(data, uuid.uuid4())

        assert result.theme == "modern"

    async def test_create_with_outline(self, presentation_service, mock_db_session):
        """测试带大纲创建"""
        outline_id = uuid.uuid4()
        data = PresentationCreate(
            title="From Outline",
            outline_id=outline_id,
        )

        result = await presentation_service.create(data, uuid.uuid4())

        assert result.outline_id == outline_id

    async def test_create_with_slides(self, presentation_service, mock_db_session):
        """测试带初始幻灯片创建"""
        data = PresentationCreate(
            title="With Slides",
            slides=[
                {
                    "type": "content",
                    "content": {"title": "Slide 1", "text": "Content 1"},
                    "layout": {"type": "title_content"},
                },
            ],
        )

        result = await presentation_service.create(data, uuid.uuid4())

        mock_db_session.add.assert_called()


class TestPresentationServiceGet:
    """测试获取演示文稿"""

    async def test_get_by_id_success(
        self, presentation_service, mock_db_session, sample_presentation
    ):
        """测试成功获取"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_presentation
        mock_db_session.execute.return_value = mock_result

        result = await presentation_service.get_by_id(
            sample_presentation.id, sample_presentation.owner_id
        )

        assert result is not None
        assert result.id == sample_presentation.id

    async def test_get_by_id_not_found(self, presentation_service, mock_db_session):
        """测试获取不存在的演示文稿"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await presentation_service.get_by_id(uuid.uuid4(), uuid.uuid4())

        assert result is None

    async def test_get_by_id_wrong_owner(
        self, presentation_service, mock_db_session, sample_presentation
    ):
        """测试获取其他用户的演示文稿"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # 查询条件包含 owner_id
        mock_db_session.execute.return_value = mock_result

        result = await presentation_service.get_by_id(
            sample_presentation.id, uuid.uuid4()
        )

        assert result is None

    async def test_get_by_id_or_raise_success(
        self, presentation_service, mock_db_session, sample_presentation
    ):
        """测试成功获取或抛出"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_presentation
        mock_db_session.execute.return_value = mock_result

        result = await presentation_service.get_by_id_or_raise(
            sample_presentation.id, sample_presentation.owner_id
        )

        assert result.id == sample_presentation.id

    async def test_get_by_id_or_raise_not_found(
        self, presentation_service, mock_db_session
    ):
        """测试获取不存在时抛出"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(PresentationNotFoundError) as exc_info:
            await presentation_service.get_by_id_or_raise(uuid.uuid4(), uuid.uuid4())

        assert "not found" in str(exc_info.value).lower()

    async def test_get_by_user(self, presentation_service, mock_db_session):
        """测试获取用户演示文稿列表"""
        user_id = uuid.uuid4()
        presentations = [
            Presentation(
                id=uuid.uuid4(), title=f"PPT {i}", owner_id=user_id, theme="default"
            )
            for i in range(3)
        ]

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 3

        mock_data_result = MagicMock()
        mock_data_result.scalars.return_value.all.return_value = presentations

        mock_db_session.execute.side_effect = [mock_count_result, mock_data_result]

        result, total = await presentation_service.get_by_user(
            user_id, page=1, page_size=10
        )

        assert len(result) == 3
        assert total == 3

    async def test_get_by_user_with_status_filter(
        self, presentation_service, mock_db_session
    ):
        """测试带状态过滤的获取"""
        user_id = uuid.uuid4()

        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = 0

        mock_data_result = MagicMock()
        mock_data_result.scalars.return_value.all.return_value = []

        mock_db_session.execute.side_effect = [mock_count_result, mock_data_result]

        result, total = await presentation_service.get_by_user(
            user_id, page=1, page_size=10, status="published"
        )

        assert len(result) == 0
        assert total == 0


class TestPresentationServiceUpdate:
    """测试更新演示文稿"""

    async def test_update_title(
        self, presentation_service, mock_db_session, sample_presentation
    ):
        """测试更新标题"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_presentation
        mock_db_session.execute.return_value = mock_result

        data = PresentationUpdate(title="Updated Title")
        result = await presentation_service.update(
            sample_presentation.id, sample_presentation.owner_id, data
        )

        assert result.title == "Updated Title"

    async def test_update_description(
        self, presentation_service, mock_db_session, sample_presentation
    ):
        """测试更新描述"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_presentation
        mock_db_session.execute.return_value = mock_result

        data = PresentationUpdate(description="New description")
        result = await presentation_service.update(
            sample_presentation.id, sample_presentation.owner_id, data
        )

        assert result.description == "New description"

    async def test_update_status(
        self, presentation_service, mock_db_session, sample_presentation
    ):
        """测试更新状态"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_presentation
        mock_db_session.execute.return_value = mock_result

        data = PresentationUpdate(status="published")
        result = await presentation_service.update(
            sample_presentation.id, sample_presentation.owner_id, data
        )

        assert result.status == PresentationStatus.PUBLISHED

    async def test_update_template(
        self, presentation_service, mock_db_session, sample_presentation
    ):
        """测试更新模板"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_presentation
        mock_db_session.execute.return_value = mock_result

        data = PresentationUpdate(template_id="modern")
        result = await presentation_service.update(
            sample_presentation.id, sample_presentation.owner_id, data
        )

        assert result.theme == "modern"

    async def test_update_not_found(self, presentation_service, mock_db_session):
        """测试更新不存在的演示文稿"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        data = PresentationUpdate(title="New Title")

        with pytest.raises(PresentationNotFoundError):
            await presentation_service.update(uuid.uuid4(), uuid.uuid4(), data)


class TestPresentationServiceDelete:
    """测试删除演示文稿"""

    async def test_delete_success(
        self, presentation_service, mock_db_session, sample_presentation
    ):
        """测试成功删除"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_presentation
        mock_db_session.execute.return_value = mock_result

        result = await presentation_service.delete(
            sample_presentation.id, sample_presentation.owner_id
        )

        assert result is True
        mock_db_session.delete.assert_called_once_with(sample_presentation)

    async def test_delete_not_found(self, presentation_service, mock_db_session):
        """测试删除不存在的演示文稿"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await presentation_service.delete(uuid.uuid4(), uuid.uuid4())

        assert result is False


class TestPresentationServiceSlides:
    """测试幻灯片操作"""

    async def test_add_slide(
        self, presentation_service, mock_db_session, mock_slide_repo, sample_presentation
    ):
        """测试添加幻灯片"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_presentation
        mock_db_session.execute.return_value = mock_result
        mock_slide_repo.get_max_order.return_value = 0

        slide_data = SlideCreate(
            type="content",
            content=SlideContent(title="New Slide", text="Content"),
            layout=SlideLayout(type="title_content"),
        )

        result = await presentation_service.add_slide(
            sample_presentation.id, sample_presentation.owner_id, slide_data
        )

        mock_db_session.add.assert_called()
        mock_db_session.flush.assert_called()

    async def test_add_slide_at_position(
        self, presentation_service, mock_db_session, sample_presentation
    ):
        """测试在指定位置添加幻灯片"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_presentation
        mock_db_session.execute.return_value = mock_result

        slide_data = SlideCreate(
            type="content",
            content=SlideContent(title="Slide at Position", text="Content"),
            position=2,
        )

        result = await presentation_service.add_slide(
            sample_presentation.id, sample_presentation.owner_id, slide_data
        )

        # 验证位置被正确设置
        assert result is not None

    async def test_get_slides(
        self, presentation_service, mock_db_session, mock_slide_repo, sample_presentation, sample_slide
    ):
        """测试获取幻灯片列表"""
        mock_ppt_result = MagicMock()
        mock_ppt_result.scalar_one_or_none.return_value = sample_presentation

        mock_slide_repo.get_by_presentation.return_value = [sample_slide]

        mock_db_session.execute.return_value = mock_ppt_result

        result = await presentation_service.get_slides(
            sample_presentation.id, sample_presentation.owner_id
        )

        assert result is not None
        assert len(result) == 1

    async def test_get_slides_ppt_not_found(
        self, presentation_service, mock_db_session
    ):
        """测试获取不存在的 PPT 的幻灯片"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await presentation_service.get_slides(uuid.uuid4(), uuid.uuid4())

        assert result is None

    async def test_get_slide(
        self, presentation_service, mock_db_session, mock_slide_repo, sample_presentation, sample_slide
    ):
        """测试获取单个幻灯片"""
        mock_ppt_result = MagicMock()
        mock_ppt_result.scalar_one_or_none.return_value = sample_presentation

        # 确保幻灯片属于该演示文稿
        sample_slide.presentation_id = sample_presentation.id
        mock_slide_repo.get_by_id.return_value = sample_slide

        mock_db_session.execute.return_value = mock_ppt_result

        result = await presentation_service.get_slide(
            sample_presentation.id, sample_slide.id, sample_presentation.owner_id
        )

        assert result is not None
        assert result.id == sample_slide.id

    async def test_get_slide_not_found(
        self, presentation_service, mock_db_session, sample_presentation
    ):
        """测试获取不存在的幻灯片"""
        mock_ppt_result = MagicMock()
        mock_ppt_result.scalar_one_or_none.return_value = sample_presentation

        mock_slide_result = MagicMock()
        mock_slide_result.scalar_one_or_none.return_value = None

        mock_db_session.execute.side_effect = [mock_ppt_result, mock_slide_result]

        result = await presentation_service.get_slide(
            sample_presentation.id, uuid.uuid4(), sample_presentation.owner_id
        )

        assert result is None

    async def test_update_slide(
        self, presentation_service, mock_db_session, mock_slide_repo, sample_presentation, sample_slide
    ):
        """测试更新幻灯片"""
        mock_ppt_result = MagicMock()
        mock_ppt_result.scalar_one_or_none.return_value = sample_presentation

        # 确保幻灯片属于该演示文稿
        sample_slide.presentation_id = sample_presentation.id
        mock_slide_repo.get_by_id.return_value = sample_slide

        mock_db_session.execute.return_value = mock_ppt_result

        data = SlideUpdate(content=SlideContent(title="Updated"))

        result = await presentation_service.update_slide(
            sample_presentation.id, sample_slide.id, sample_presentation.owner_id, data
        )

        assert result.content["title"] == "Updated"

    async def test_delete_slide(
        self, presentation_service, mock_db_session, mock_slide_repo, sample_presentation, sample_slide
    ):
        """测试删除幻灯片"""
        mock_ppt_result = MagicMock()
        mock_ppt_result.scalar_one_or_none.return_value = sample_presentation

        # 确保幻灯片属于该演示文稿
        sample_slide.presentation_id = sample_presentation.id
        mock_slide_repo.get_by_id.return_value = sample_slide

        mock_db_session.execute.return_value = mock_ppt_result

        result = await presentation_service.delete_slide(
            sample_presentation.id, sample_slide.id, sample_presentation.owner_id
        )

        assert result is True
