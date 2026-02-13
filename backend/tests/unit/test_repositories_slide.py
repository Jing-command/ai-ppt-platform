"""
测试 Slide Repository
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.domain.models.slide import Slide, SlideLayoutType
from ai_ppt.infrastructure.repositories.slide import SlideRepository


@pytest.fixture
def mock_session():
    """创建模拟的异步会话"""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    return session


@pytest.fixture
def repository(mock_session):
    """创建测试用的仓储实例"""
    return SlideRepository(mock_session)


@pytest.fixture
def sample_slide():
    """创建示例幻灯片"""
    slide = MagicMock(spec=Slide)
    slide.id = uuid.uuid4()
    slide.presentation_id = uuid.uuid4()
    slide.title = "Test Slide"
    slide.subtitle = "Test Subtitle"
    slide.layout_type = SlideLayoutType.TITLE_CONTENT
    slide.content = {"text": "Test content"}
    slide.order_index = 1
    return slide


class TestSlideRepository:
    """测试 SlideRepository"""

    class TestGetByPresentation:
        """测试 get_by_presentation 方法"""

        async def test_get_by_presentation_success(
            self, repository, mock_session, sample_slide
        ):
            """测试成功获取演示文稿的幻灯片"""
            presentation_id = sample_slide.presentation_id

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [sample_slide]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_presentation(presentation_id)

            assert len(result) == 1
            assert result[0] == sample_slide

        async def test_get_by_presentation_empty(self, repository, mock_session):
            """测试演示文稿无幻灯片"""
            presentation_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = []
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_presentation(presentation_id)

            assert result == []

        async def test_get_by_presentation_ordered(self, repository, mock_session):
            """测试幻灯片按顺序返回"""
            presentation_id = uuid.uuid4()

            slide1 = MagicMock(spec=Slide, order_index=1)
            slide2 = MagicMock(spec=Slide, order_index=2)
            slide3 = MagicMock(spec=Slide, order_index=3)

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [slide1, slide2, slide3]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_presentation(presentation_id)

            assert len(result) == 3

    class TestGetMaxOrder:
        """测试 get_max_order 方法"""

        async def test_get_max_order_success(self, repository, mock_session):
            """测试成功获取最大排序索引"""
            presentation_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = 5
            mock_session.execute.return_value = mock_result

            result = await repository.get_max_order(presentation_id)

            assert result == 5

        async def test_get_max_order_none(self, repository, mock_session):
            """测试无幻灯片时返回 0"""
            presentation_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            result = await repository.get_max_order(presentation_id)

            assert result == 0

        async def test_get_max_order_zero(self, repository, mock_session):
            """测试最大索引为 0"""
            presentation_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = 0
            mock_session.execute.return_value = mock_result

            result = await repository.get_max_order(presentation_id)

            assert result == 0

    class TestReorderSlides:
        """测试 reorder_slides 方法"""

        async def test_reorder_slides_success(self, repository, mock_session):
            """测试成功重新排序幻灯片"""
            presentation_id = uuid.uuid4()
            slide_orders = {
                uuid.uuid4(): 0,
                uuid.uuid4(): 1,
                uuid.uuid4(): 2,
            }

            mock_session.execute.return_value = MagicMock()

            result = await repository.reorder_slides(presentation_id, slide_orders)

            assert result is None
            assert mock_session.execute.call_count == 3
            mock_session.flush.assert_called_once()

        async def test_reorder_slides_empty(self, repository, mock_session):
            """测试空排序列表"""
            presentation_id = uuid.uuid4()
            slide_orders = {}

            await repository.reorder_slides(presentation_id, slide_orders)

            mock_session.execute.assert_not_called()
            mock_session.flush.assert_called_once()

        async def test_reorder_slides_single_slide(self, repository, mock_session):
            """测试单幻灯片排序"""
            presentation_id = uuid.uuid4()
            slide_orders = {uuid.uuid4(): 0}

            mock_session.execute.return_value = MagicMock()

            await repository.reorder_slides(presentation_id, slide_orders)

            mock_session.execute.assert_called_once()
            mock_session.flush.assert_called_once()

    class TestDeleteByPresentation:
        """测试 delete_by_presentation 方法"""

        async def test_delete_by_presentation_success(self, repository, mock_session):
            """测试成功删除演示文稿的所有幻灯片"""
            presentation_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.rowcount = 3
            mock_session.execute.return_value = mock_result

            result = await repository.delete_by_presentation(presentation_id)

            assert result == 3
            mock_session.flush.assert_called_once()

        async def test_delete_by_presentation_none(self, repository, mock_session):
            """测试删除 0 张幻灯片"""
            presentation_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.rowcount = 0
            mock_session.execute.return_value = mock_result

            result = await repository.delete_by_presentation(presentation_id)

            assert result == 0

        async def test_delete_by_presentation_rowcount_none(
            self, repository, mock_session
        ):
            """测试 rowcount 为 None 的情况"""
            presentation_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.rowcount = None
            mock_session.execute.return_value = mock_result

            result = await repository.delete_by_presentation(presentation_id)

            assert result == 0

    class TestInheritance:
        """测试继承自 BaseRepository 的方法"""

        async def test_get_by_id_inherited(
            self, repository, mock_session, sample_slide
        ):
            """测试继承的 get_by_id 方法"""
            slide_id = sample_slide.id

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = sample_slide
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_id(slide_id)

            assert result == sample_slide

        async def test_create_inherited(self, repository, mock_session, sample_slide):
            """测试继承的 create 方法"""
            result = await repository.create(sample_slide)

            assert result == sample_slide
            mock_session.add.assert_called_once_with(sample_slide)

        async def test_update_inherited(self, repository, mock_session, sample_slide):
            """测试继承的 update 方法"""
            result = await repository.update(sample_slide)

            assert result == sample_slide
            mock_session.add.assert_called_once_with(sample_slide)


class TestSlideRepositoryEdgeCases:
    """测试边界情况"""

    async def test_repository_initialization(self, mock_session):
        """测试仓储初始化"""
        repo = SlideRepository(mock_session)

        assert repo._session == mock_session
        assert repo._model_class == Slide

    async def test_get_max_order_negative(self, repository, mock_session):
        """测试最大索引为负数（异常情况）"""
        presentation_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = -1
        mock_session.execute.return_value = mock_result

        result = await repository.get_max_order(presentation_id)

        assert result == -1

    async def test_reorder_slides_large_batch(self, repository, mock_session):
        """测试大批量排序"""
        presentation_id = uuid.uuid4()
        slide_orders = {uuid.uuid4(): i for i in range(100)}

        mock_session.execute.return_value = MagicMock()

        await repository.reorder_slides(presentation_id, slide_orders)

        assert mock_session.execute.call_count == 100

    async def test_delete_by_presentation_large_result(self, repository, mock_session):
        """测试删除大量幻灯片"""
        presentation_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 10000
        mock_session.execute.return_value = mock_result

        result = await repository.delete_by_presentation(presentation_id)

        assert result == 10000
