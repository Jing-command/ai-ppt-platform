"""
测试 Presentation 领域模型方法
"""

import uuid
from unittest.mock import MagicMock

import pytest

from ai_ppt.domain.models.presentation import Presentation, PresentationStatus


class TestPresentationInit:
    """测试 Presentation 初始化"""

    def test_init_with_all_params(self):
        """测试完整参数初始化"""
        test_id = uuid.uuid4()
        owner_id = uuid.uuid4()
        outline_id = uuid.uuid4()

        presentation = Presentation(
            title="Test Presentation",
            owner_id=owner_id,
            description="Test Description",
            theme="modern",
            id=test_id,
            outline_id=outline_id,
            status=PresentationStatus.PUBLISHED,
        )

        assert presentation.id == test_id
        assert presentation.title == "Test Presentation"
        assert presentation.owner_id == owner_id
        assert presentation.description == "Test Description"
        assert presentation.theme == "modern"
        assert presentation.outline_id == outline_id
        assert presentation.status == PresentationStatus.PUBLISHED

    def test_init_with_minimal_params(self):
        """测试最小参数初始化"""
        owner_id = uuid.uuid4()

        presentation = Presentation(
            title="Minimal Presentation",
            owner_id=owner_id,
        )

        assert presentation.title == "Minimal Presentation"
        assert presentation.owner_id == owner_id
        assert presentation.theme == "default"
        # id should be None when not provided (SQLAlchemy sets it on persist)
        assert presentation.id is None

    def test_init_without_optional_params(self):
        """测试不传入可选参数"""
        owner_id = uuid.uuid4()

        presentation = Presentation(
            title="Test",
            owner_id=owner_id,
        )

        # These are set by SQLAlchemy defaults on persist, not in __init__
        assert presentation.status is None  # Will be set by SQLAlchemy default on persist
        assert presentation.id is None  # Will be set by SQLAlchemy default on persist


class TestPresentationUpdateTitle:
    """测试更新标题方法"""

    def test_update_title_success(self):
        """测试成功更新标题"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Old Title",
            owner_id=owner_id,
        )

        presentation.update_title("New Title")

        assert presentation.title == "New Title"

    def test_update_title_strips_whitespace(self):
        """测试更新标题时去除首尾空格"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Old",
            owner_id=owner_id,
        )

        presentation.update_title("  New Title  ")

        assert presentation.title == "New Title"

    def test_update_title_empty_raises_error(self):
        """测试空标题抛出错误"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Valid Title",
            owner_id=owner_id,
        )

        with pytest.raises(ValueError, match="Title cannot be empty"):
            presentation.update_title("")

    def test_update_title_whitespace_only_raises_error(self):
        """测试仅包含空格的标题抛出错误"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Valid Title",
            owner_id=owner_id,
        )

        with pytest.raises(ValueError, match="Title cannot be empty"):
            presentation.update_title("   ")


class TestPresentationPublish:
    """测试发布方法"""

    def test_publish_success(self):
        """测试成功发布"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Test",
            owner_id=owner_id,
            status=PresentationStatus.DRAFT,
        )

        presentation.publish()

        assert presentation.status == PresentationStatus.PUBLISHED

    def test_publish_archived_raises_error(self):
        """测试已归档的演示文稿不能发布"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Test",
            owner_id=owner_id,
            status=PresentationStatus.ARCHIVED,
        )

        with pytest.raises(ValueError, match="Cannot publish archived presentation"):
            presentation.publish()

    def test_publish_already_published(self):
        """测试已发布的演示文稿再次发布"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Test",
            owner_id=owner_id,
            status=PresentationStatus.PUBLISHED,
        )

        # 不应该抛出错误，状态保持不变
        presentation.publish()
        assert presentation.status == PresentationStatus.PUBLISHED


class TestPresentationArchive:
    """测试归档方法"""

    def test_archive_success(self):
        """测试成功归档"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Test",
            owner_id=owner_id,
            status=PresentationStatus.DRAFT,
        )

        presentation.archive()

        assert presentation.status == PresentationStatus.ARCHIVED

    def test_archive_from_published(self):
        """测试从已发布状态归档"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Test",
            owner_id=owner_id,
            status=PresentationStatus.PUBLISHED,
        )

        presentation.archive()

        assert presentation.status == PresentationStatus.ARCHIVED


class TestPresentationIncrementView:
    """测试增加浏览次数方法"""

    def test_increment_view(self):
        """测试增加浏览次数"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Test",
            owner_id=owner_id,
        )
        # Initialize view_count manually (normally set by SQLAlchemy default)
        presentation.view_count = 0

        presentation.increment_view()

        assert presentation.view_count == 1

    def test_increment_view_multiple_times(self):
        """测试多次增加浏览次数"""
        owner_id = uuid.uuid4()
        presentation = Presentation(
            title="Test",
            owner_id=owner_id,
        )
        # Initialize view_count manually
        presentation.view_count = 0

        presentation.increment_view()
        presentation.increment_view()
        presentation.increment_view()

        assert presentation.view_count == 3


class TestPresentationStatusEnum:
    """测试 PresentationStatus 枚举"""

    def test_status_values(self):
        """测试状态枚举值"""
        assert PresentationStatus.DRAFT.value == "draft"
        assert PresentationStatus.REVIEW.value == "review"
        assert PresentationStatus.PUBLISHED.value == "published"
        assert PresentationStatus.ARCHIVED.value == "archived"

    def test_status_string_comparison(self):
        """测试状态字符串比较"""
        assert PresentationStatus.DRAFT == "draft"
        assert PresentationStatus.PUBLISHED == "published"
