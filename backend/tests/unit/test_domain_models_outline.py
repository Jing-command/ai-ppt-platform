"""
测试 Outline 领域模型方法
"""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from ai_ppt.domain.models.outline import (
    Outline,
    OutlineBackground,
    OutlineBackgroundType,
    OutlinePage,
    OutlinePageType,
    OutlineStatus,
)


class TestOutlinePage:
    """测试 OutlinePage 类"""

    def test_init_default_values(self):
        """测试默认初始化值"""
        page = OutlinePage(
            id="page-1",
            page_number=1,
            title="Test Page",
        )

        assert page.id == "page-1"
        assert page.page_number == 1
        assert page.title == "Test Page"
        assert page.content is None
        assert page.page_type == "content"
        assert page.layout is None
        assert page.notes is None
        assert page.image_prompt is None

    def test_to_dict(self):
        """测试转换为字典"""
        page = OutlinePage(
            id="page-1",
            page_number=1,
            title="Test Page",
            content="Test content",
            page_type="title",
            layout="center",
            notes="Test notes",
            image_prompt="Test prompt",
        )

        result = page.to_dict()

        assert result["id"] == "page-1"
        assert result["pageNumber"] == 1
        assert result["title"] == "Test Page"
        assert result["content"] == "Test content"
        assert result["pageType"] == "title"
        assert result["layout"] == "center"
        assert result["notes"] == "Test notes"
        assert result["imagePrompt"] == "Test prompt"

    def test_from_dict_with_camel_case(self):
        """测试从驼峰命名字典创建"""
        data = {
            "id": "page-1",
            "pageNumber": 2,
            "title": "Test",
            "content": "Content",
            "pageType": "content",
            "layout": "left",
            "notes": "Notes",
            "imagePrompt": "Prompt",
        }

        page = OutlinePage.from_dict(data)

        assert page.page_number == 2
        assert page.page_type == "content"
        assert page.image_prompt == "Prompt"

    def test_from_dict_with_snake_case(self):
        """测试从蛇形命名字典创建"""
        data = {
            "id": "page-1",
            "page_number": 3,
            "title": "Test",
            "page_type": "section",
            "image_prompt": "Snake Case Prompt",
        }

        page = OutlinePage.from_dict(data)

        assert page.page_number == 3
        assert page.page_type == "section"
        assert page.image_prompt == "Snake Case Prompt"

    def test_from_dict_generates_id_if_missing(self):
        """测试缺少 ID 时自动生成"""
        data = {
            "pageNumber": 1,
            "title": "Test",
        }

        page = OutlinePage.from_dict(data)

        assert page.id is not None
        assert len(page.id) > 0


class TestOutlineBackground:
    """测试 OutlineBackground 类"""

    def test_init_default_values(self):
        """测试默认初始化值"""
        bg = OutlineBackground()

        assert bg.type == "ai"
        assert bg.prompt is None
        assert bg.url is None
        assert bg.color is None
        assert bg.opacity == 1.0
        assert bg.blur == 0.0

    def test_init_custom_values(self):
        """测试自定义初始化值"""
        bg = OutlineBackground(
            type="solid",
            prompt="Test prompt",
            url="http://example.com/bg.jpg",
            color="#ffffff",
            opacity=0.8,
            blur=2.0,
        )

        assert bg.type == "solid"
        assert bg.prompt == "Test prompt"
        assert bg.url == "http://example.com/bg.jpg"
        assert bg.color == "#ffffff"
        assert bg.opacity == 0.8
        assert bg.blur == 2.0

    def test_to_dict(self):
        """测试转换为字典"""
        bg = OutlineBackground(
            type="upload",
            url="http://example.com/image.jpg",
            opacity=0.5,
        )

        result = bg.to_dict()

        assert result["type"] == "upload"
        assert result["url"] == "http://example.com/image.jpg"
        assert result["opacity"] == 0.5
        assert result["prompt"] is None

    def test_from_dict_with_data(self):
        """测试从字典创建"""
        data = {
            "type": "solid",
            "color": "#000000",
            "opacity": 0.9,
            "blur": 1.0,
        }

        bg = OutlineBackground.from_dict(data)

        assert bg.type == "solid"
        assert bg.color == "#000000"
        assert bg.opacity == 0.9
        assert bg.blur == 1.0

    def test_from_dict_with_none(self):
        """测试从 None 创建"""
        bg = OutlineBackground.from_dict(None)

        assert bg is None

    def test_from_dict_empty_returns_none(self):
        """测试从空字典返回 None（空字典是 falsy）"""
        bg = OutlineBackground.from_dict({})

        # 空字典被视为 falsy，所以返回 None
        assert bg is None

    def test_from_dict_with_minimal_data(self):
        """测试从最小数据字典创建使用默认值"""
        bg = OutlineBackground.from_dict({"type": "ai"})

        assert bg is not None
        assert bg.type == "ai"
        assert bg.opacity == 1.0
        assert bg.blur == 0.0


class TestOutlineInit:
    """测试 Outline 初始化"""

    def test_init_with_minimal_params(self):
        """测试最小参数初始化"""
        user_id = uuid.uuid4()

        outline = Outline(
            title="Test Outline",
            user_id=user_id,
        )

        assert outline.title == "Test Outline"
        assert outline.user_id == user_id
        assert outline.pages == []
        assert outline.total_slides == 0
        assert outline.status == OutlineStatus.DRAFT.value

    def test_init_calculates_total_slides(self):
        """测试初始化时计算总页数"""
        user_id = uuid.uuid4()
        pages = [{"id": "1"}, {"id": "2"}, {"id": "3"}]

        outline = Outline(
            title="Test",
            user_id=user_id,
            pages=pages,
        )

        assert outline.total_slides == 3

    def test_init_with_custom_status(self):
        """测试自定义状态初始化"""
        user_id = uuid.uuid4()

        outline = Outline(
            title="Test",
            user_id=user_id,
            status=OutlineStatus.COMPLETED.value,
        )

        assert outline.status == OutlineStatus.COMPLETED.value


class TestOutlineGetPages:
    """测试获取页面列表方法"""

    def test_get_pages_from_json(self):
        """测试从 JSON 解析页面"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
            pages=[
                {"id": "page-1", "pageNumber": 1, "title": "Page 1"},
                {"id": "page-2", "pageNumber": 2, "title": "Page 2"},
            ],
        )

        pages = outline.get_pages()

        assert len(pages) == 2
        assert isinstance(pages[0], OutlinePage)
        assert pages[0].title == "Page 1"

    def test_get_pages_caches_result(self):
        """测试页面缓存"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
            pages=[{"id": "page-1", "pageNumber": 1, "title": "Page 1"}],
        )

        pages1 = outline.get_pages()
        pages2 = outline.get_pages()

        # 应该是同一个缓存对象
        assert pages1 is pages2

    def test_get_pages_empty(self):
        """测试空页面列表"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
        )

        pages = outline.get_pages()

        assert pages == []


class TestOutlineSetPages:
    """测试设置页面列表方法"""

    def test_set_pages_updates_json(self):
        """测试设置页面更新 JSON"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
        )

        pages = [
            OutlinePage(id="page-1", page_number=1, title="New Page"),
        ]
        outline.set_pages(pages)

        assert len(outline.pages) == 1
        assert outline.pages[0]["title"] == "New Page"
        assert outline.total_slides == 1


class TestOutlineGetBackground:
    """测试获取背景方法"""

    def test_get_background_from_dict(self):
        """测试从字典解析背景"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
            background={"type": "solid", "color": "#ffffff"},
        )

        bg = outline.get_background()

        assert isinstance(bg, OutlineBackground)
        assert bg.type == "solid"
        assert bg.color == "#ffffff"

    def test_get_background_caches_result(self):
        """测试背景缓存"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
            background={"type": "ai"},
        )

        bg1 = outline.get_background()
        bg2 = outline.get_background()

        assert bg1 is bg2

    def test_get_background_none(self):
        """测试无背景时返回 None"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
        )

        bg = outline.get_background()

        assert bg is None


class TestOutlineSetBackground:
    """测试设置背景方法"""

    def test_set_background_updates_dict(self):
        """测试设置背景更新字典"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
        )

        bg = OutlineBackground(type="solid", color="#000000")
        outline.set_background(bg)

        assert outline.background["type"] == "solid"
        assert outline.background["color"] == "#000000"

    def test_set_background_to_none(self):
        """测试设置背景为 None"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
            background={"type": "ai"},
        )

        outline.set_background(None)

        assert outline.background is None


class TestOutlineAddPage:
    """测试添加页面方法"""

    def test_add_page_appends_to_list(self):
        """测试添加页面追加到列表"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
            pages=[{"id": "page-1", "pageNumber": 1, "title": "Page 1"}],
        )

        new_page = OutlinePage(id="page-2", page_number=2, title="Page 2")
        outline.add_page(new_page)

        pages = outline.get_pages()
        assert len(pages) == 2
        assert pages[1].title == "Page 2"


class TestOutlineMarkAsGenerating:
    """测试标记为生成中"""

    def test_mark_as_generating(self):
        """测试标记为生成中状态"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
            status=OutlineStatus.DRAFT.value,
        )

        outline.mark_as_generating()

        assert outline.status == OutlineStatus.GENERATING.value


class TestOutlineMarkAsCompleted:
    """测试标记为已完成"""

    def test_mark_as_completed(self):
        """测试标记为已完成状态"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
            status=OutlineStatus.GENERATING.value,
        )

        outline.mark_as_completed()

        assert outline.status == OutlineStatus.COMPLETED.value
        assert outline.generated_at is not None


class TestOutlineMarkAsArchived:
    """测试标记为已归档"""

    def test_mark_as_archived(self):
        """测试标记为已归档状态"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
            status=OutlineStatus.COMPLETED.value,
        )

        outline.mark_as_archived()

        assert outline.status == OutlineStatus.ARCHIVED.value


class TestOutlineUpdatePagesFromDict:
    """测试从字典更新页面"""

    def test_update_pages_from_dict(self):
        """测试从字典列表更新页面"""
        user_id = uuid.uuid4()
        outline = Outline(
            title="Test",
            user_id=user_id,
        )

        pages_data = [
            {"id": "p1", "pageNumber": 1, "title": "Updated Page 1"},
            {"id": "p2", "pageNumber": 2, "title": "Updated Page 2"},
        ]
        outline.update_pages_from_dict(pages_data)

        pages = outline.get_pages()
        assert len(pages) == 2
        assert pages[0].title == "Updated Page 1"
        assert outline.total_slides == 2


class TestOutlineStatusEnum:
    """测试 OutlineStatus 枚举"""

    def test_status_values(self):
        """测试状态枚举值"""
        assert OutlineStatus.DRAFT.value == "draft"
        assert OutlineStatus.GENERATING.value == "generating"
        assert OutlineStatus.COMPLETED.value == "completed"
        assert OutlineStatus.ARCHIVED.value == "archived"
