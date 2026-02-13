"""
大纲服务单元测试
"""

import uuid
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_ppt.api.v1.schemas.outline import OutlinePage
from ai_ppt.domain.models.outline import (
    Outline,
    OutlineBackground,
)
from ai_ppt.domain.models.outline import OutlinePage as DomainOutlinePage
from ai_ppt.domain.models.outline import (
    OutlineStatus,
)
from ai_ppt.services.outline_service import (
    OutlineNotFoundError,
    OutlinePermissionError,
    OutlineService,
)


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def outline_service(mock_db_session):
    """创建大纲服务实例"""
    return OutlineService(mock_db_session)


@pytest.fixture
def sample_outline():
    """示例大纲"""
    return Outline(
        id=uuid.uuid4(),
        title="Test Outline",
        user_id=uuid.uuid4(),
        description="Test description",
        pages=[
            {
                "id": "page-1",
                "pageNumber": 1,
                "title": "Page 1",
                "content": "Content 1",
                "pageType": "title",
            },
            {
                "id": "page-2",
                "pageNumber": 2,
                "title": "Page 2",
                "content": "Content 2",
                "pageType": "content",
            },
        ],
        status=OutlineStatus.DRAFT.value,
    )


class TestOutlineServiceGetById:
    """测试获取大纲"""

    async def test_get_by_id_success(self, outline_service, mock_db_session, sample_outline):
        """测试成功获取大纲"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_outline
        mock_db_session.execute.return_value = mock_result

        result = await outline_service.get_by_id(sample_outline.id)

        assert result is not None
        assert result.id == sample_outline.id
        assert result.title == sample_outline.title

    async def test_get_by_id_not_found(self, outline_service, mock_db_session):
        """测试获取不存在的大纲"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await outline_service.get_by_id(uuid.uuid4())

        assert result is None

    async def test_get_by_id_with_user_permission(
        self, outline_service, mock_db_session, sample_outline
    ):
        """测试带用户权限的获取"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_outline
        mock_db_session.execute.return_value = mock_result

        result = await outline_service.get_by_id(sample_outline.id, user_id=sample_outline.user_id)

        assert result is not None

    async def test_get_by_id_wrong_user(self, outline_service, mock_db_session, sample_outline):
        """测试获取其他用户的大纲"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_outline
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(OutlinePermissionError) as exc_info:
            await outline_service.get_by_id(sample_outline.id, user_id=uuid.uuid4())

        assert "无权访问" in str(exc_info.value)

    async def test_get_by_id_or_raise_success(
        self, outline_service, mock_db_session, sample_outline
    ):
        """测试成功获取或抛出"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_outline
        mock_db_session.execute.return_value = mock_result

        result = await outline_service.get_by_id_or_raise(sample_outline.id)

        assert result.id == sample_outline.id

    async def test_get_by_id_or_raise_not_found(self, outline_service, mock_db_session):
        """测试获取不存在时抛出"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(OutlineNotFoundError) as exc_info:
            await outline_service.get_by_id_or_raise(uuid.uuid4())

        assert "不存在" in str(exc_info.value)


class TestOutlineServiceGetByUser:
    """测试获取用户大纲列表"""

    async def test_get_by_user_success(self, outline_service, mock_db_session):
        """测试成功获取用户大纲列表"""
        user_id = uuid.uuid4()
        outlines = [Outline(title=f"Outline {i}", user_id=user_id, pages=[]) for i in range(3)]

        # 模拟总数查询
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 3

        # 模拟数据查询
        mock_data_result = MagicMock()
        mock_data_result.scalars.return_value.all.return_value = outlines

        mock_db_session.execute.side_effect = [mock_count_result, mock_data_result]

        result, total = await outline_service.get_by_user(user_id, page=1, page_size=10)

        assert len(result) == 3
        assert total == 3

    async def test_get_by_user_with_status_filter(self, outline_service, mock_db_session):
        """测试带状态过滤的获取"""
        user_id = uuid.uuid4()

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0

        mock_data_result = MagicMock()
        mock_data_result.scalars.return_value.all.return_value = []

        mock_db_session.execute.side_effect = [mock_count_result, mock_data_result]

        result, total = await outline_service.get_by_user(
            user_id, page=1, page_size=10, status="completed"
        )

        assert len(result) == 0
        assert total == 0


class TestOutlineServiceCreate:
    """测试创建大纲"""

    async def test_create_success(self, outline_service, mock_db_session):
        """测试成功创建大纲"""
        user_id = uuid.uuid4()

        result = await outline_service.create(
            user_id=user_id,
            title="New Outline",
            description="Description",
            pages=[
                {
                    "id": "page-1",
                    "pageNumber": 1,
                    "title": "Page 1",
                    "pageType": "title",
                }
            ],
        )

        assert result.title == "New Outline"
        assert result.user_id == user_id
        assert result.total_slides == 1
        assert result.status == OutlineStatus.DRAFT.value

        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()

    async def test_create_minimal(self, outline_service, mock_db_session):
        """测试最小化创建"""
        user_id = uuid.uuid4()

        result = await outline_service.create(
            user_id=user_id,
            title="Simple Outline",
        )

        assert result.title == "Simple Outline"
        assert result.pages == []
        assert result.total_slides == 0

    async def test_create_with_background(self, outline_service, mock_db_session):
        """测试带背景创建"""
        user_id = uuid.uuid4()
        background = {"type": "ai", "prompt": "Blue gradient"}

        result = await outline_service.create(
            user_id=user_id,
            title="Outline with Background",
            background=background,
        )

        assert result.background == background

    async def test_create_from_schema(self, outline_service, mock_db_session):
        """测试从 Schema 创建"""
        user_id = uuid.uuid4()
        data = {
            "title": "Schema Outline",
            "description": "From schema",
            "pages": [
                OutlinePage(page_number=1, title="Page 1", page_type="title"),
            ],
            "background": {"type": "ai", "prompt": "Background"},
        }

        result = await outline_service.create_from_schema(user_id, data)

        assert result.title == "Schema Outline"
        assert result.total_slides == 1


class TestOutlineServiceUpdate:
    """测试更新大纲"""

    async def test_update_success(self, outline_service, mock_db_session, sample_outline):
        """测试成功更新大纲"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_outline
        mock_db_session.execute.return_value = mock_result

        result = await outline_service.update(
            outline_id=sample_outline.id,
            user_id=sample_outline.user_id,
            data={"title": "Updated Title"},
        )

        assert result.title == "Updated Title"
        mock_db_session.flush.assert_called_once()

    async def test_update_pages(self, outline_service, mock_db_session, sample_outline):
        """测试更新大纲页面"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_outline
        mock_db_session.execute.return_value = mock_result

        new_pages = [
            {
                "id": "page-3",
                "pageNumber": 1,
                "title": "New Page",
                "pageType": "content",
            },
        ]

        result = await outline_service.update(
            outline_id=sample_outline.id,
            user_id=sample_outline.user_id,
            data={"pages": new_pages},
        )

        assert result.pages == new_pages
        assert result.total_slides == 1

    async def test_update_background(self, outline_service, mock_db_session, sample_outline):
        """测试更新背景"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_outline
        mock_db_session.execute.return_value = mock_result

        new_background = {"type": "solid", "color": "#ffffff"}

        result = await outline_service.update(
            outline_id=sample_outline.id,
            user_id=sample_outline.user_id,
            data={"background": new_background},
        )

        assert result.background == new_background

    async def test_update_status(self, outline_service, mock_db_session, sample_outline):
        """测试更新状态"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_outline
        mock_db_session.execute.return_value = mock_result

        result = await outline_service.update(
            outline_id=sample_outline.id,
            user_id=sample_outline.user_id,
            data={"status": "archived"},
        )

        assert result.status == "archived"


class TestOutlineServiceDelete:
    """测试删除大纲"""

    async def test_delete_success(self, outline_service, mock_db_session, sample_outline):
        """测试成功删除"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_outline
        mock_db_session.execute.return_value = mock_result

        result = await outline_service.delete(sample_outline.id, sample_outline.user_id)

        assert result is True
        mock_db_session.delete.assert_called_once_with(sample_outline)
        mock_db_session.flush.assert_called_once()

    async def test_delete_not_found(self, outline_service, mock_db_session):
        """测试删除不存在的大纲"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(OutlineNotFoundError):
            await outline_service.delete(uuid.uuid4(), uuid.uuid4())


class TestOutlineServiceGenerate:
    """测试 AI 生成大纲"""

    async def test_generate_success(self, outline_service, mock_db_session):
        """测试成功生成大纲"""
        user_id = uuid.uuid4()

        # 模拟生成服务
        mock_generation_result = {
            "title": "Generated Outline",
            "description": "AI generated description",
            "pages": [
                {
                    "id": "page-1",
                    "pageNumber": 1,
                    "title": "Page 1",
                    "pageType": "title",
                },
                {
                    "id": "page-2",
                    "pageNumber": 2,
                    "title": "Page 2",
                    "pageType": "content",
                },
            ],
            "background": {"type": "ai", "prompt": "Generated background"},
        }

        mock_generation_service = AsyncMock()
        mock_generation_service.generate_outline.return_value = mock_generation_result
        mock_generation_service.close = AsyncMock()

        outline_service._generation_service = mock_generation_service

        result = await outline_service.generate(
            user_id=user_id,
            prompt="Create a presentation about AI",
            num_slides=5,
            language="en",
            style="business",
        )

        assert result.title == "Generated Outline"
        assert result.status == OutlineStatus.COMPLETED.value
        assert len(result.pages) == 2
        assert result.total_slides == 2

        mock_generation_service.generate_outline.assert_called_once()
        mock_generation_service.close.assert_called_once()

    async def test_generate_creates_generation_service(self, outline_service, mock_db_session):
        """测试自动生成服务实例"""
        user_id = uuid.uuid4()

        with patch("ai_ppt.services.outline_service.OutlineGenerationService") as mock_gen_class:
            mock_instance = AsyncMock()
            mock_instance.generate_outline.return_value = {
                "title": "Test",
                "pages": [],
            }
            mock_instance.close = AsyncMock()
            mock_gen_class.return_value = mock_instance

            await outline_service.generate(
                user_id=user_id,
                prompt="Test prompt",
            )

            mock_gen_class.assert_called_once()

    async def test_generate_with_context_data(self, outline_service, mock_db_session):
        """测试带上下文数据的生成"""
        user_id = uuid.uuid4()
        context_data = {"key": "value", "numbers": [1, 2, 3]}

        mock_generation_service = AsyncMock()
        mock_generation_service.generate_outline.return_value = {
            "title": "Test",
            "pages": [],
        }
        mock_generation_service.close = AsyncMock()

        outline_service._generation_service = mock_generation_service

        await outline_service.generate(
            user_id=user_id,
            prompt="Test prompt",
            context_data=context_data,
        )

        # 验证 context_data 被传递给生成服务
        call_kwargs = mock_generation_service.generate_outline.call_args[1]
        assert call_kwargs["context_data"] == context_data

    async def test_generate_with_connector_id(self, outline_service, mock_db_session):
        """测试带连接器 ID 的生成"""
        user_id = uuid.uuid4()
        connector_id = uuid.uuid4()

        mock_generation_service = AsyncMock()
        mock_generation_service.generate_outline.return_value = {
            "title": "Test",
            "pages": [],
        }
        mock_generation_service.close = AsyncMock()

        outline_service._generation_service = mock_generation_service

        result = await outline_service.generate(
            user_id=user_id,
            prompt="Test prompt",
            connector_id=connector_id,
        )

        # 验证 connector_id 被记录到 ai_parameters
        assert result.ai_parameters is not None
        assert result.ai_parameters["connector_id"] == str(connector_id)

    async def test_generate_failure(self, outline_service, mock_db_session):
        """测试生成失败"""
        user_id = uuid.uuid4()

        mock_generation_service = AsyncMock()
        mock_generation_service.generate_outline.side_effect = Exception("Generation failed")
        mock_generation_service.close = AsyncMock()

        outline_service._generation_service = mock_generation_service

        with pytest.raises(Exception) as exc_info:
            await outline_service.generate(
                user_id=user_id,
                prompt="Test prompt",
            )

        assert "Generation failed" in str(exc_info.value)
        mock_generation_service.close.assert_called_once()


class TestOutlineDomainPage:
    """测试大纲领域页面模型"""

    def test_outline_page_to_dict(self):
        """测试页面转字典"""
        page = DomainOutlinePage(
            id="page-1",
            page_number=1,
            title="Test Page",
            content="Content",
            page_type="title",
            image_prompt="Blue background",
        )

        result = page.to_dict()

        assert result["id"] == "page-1"
        assert result["pageNumber"] == 1
        assert result["imagePrompt"] == "Blue background"

    def test_outline_page_from_dict(self):
        """测试从字典创建页面"""
        data = {
            "id": "page-2",
            "pageNumber": 2,
            "title": "Another Page",
            "content": "More content",
            "pageType": "content",
        }

        page = DomainOutlinePage.from_dict(data)

        assert page.id == "page-2"
        assert page.page_number == 2
        assert page.page_type == "content"

    def test_outline_page_from_dict_aliases(self):
        """测试从字典创建页面（使用别名）"""
        data = {
            "page_number": 3,
            "page_type": "section",
            "image_prompt": "Prompt",
        }

        page = DomainOutlinePage.from_dict(data)

        assert page.page_number == 3
        assert page.page_type == "section"
        assert page.image_prompt == "Prompt"

    def test_outline_background_to_dict(self):
        """测试背景转字典"""
        bg = OutlineBackground(
            type="ai",
            prompt="Blue gradient",
            opacity=0.8,
            blur=5.0,
        )

        result = bg.to_dict()

        assert result["type"] == "ai"
        assert result["opacity"] == 0.8
        assert result["blur"] == 5.0

    def test_outline_background_from_dict(self):
        """测试从字典创建背景"""
        data = {"type": "solid", "color": "#ffffff", "opacity": 0.9}

        bg = OutlineBackground.from_dict(data)

        assert bg.type == "solid"
        assert bg.color == "#ffffff"
        assert bg.opacity == 0.9

    def test_outline_background_from_dict_none(self):
        """测试从 None 创建背景"""
        bg = OutlineBackground.from_dict(None)

        assert bg is None
