"""
测试 Outline Repository
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.domain.models.outline import Outline, OutlineStatus
from ai_ppt.infrastructure.repositories.outline import OutlineRepository


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
    return OutlineRepository(mock_session)


@pytest.fixture
def sample_outline():
    """创建示例大纲"""
    outline = MagicMock(spec=Outline)
    outline.id = uuid.uuid4()
    outline.user_id = uuid.uuid4()
    outline.title = "Test Outline"
    outline.description = "Test description"
    outline.pages = [
        {"id": "page-1", "title": "Page 1", "content": "Content 1"},
        {"id": "page-2", "title": "Page 2", "content": "Content 2"},
    ]
    outline.status = OutlineStatus.DRAFT
    outline.created_at = datetime.utcnow()
    outline.updated_at = datetime.utcnow()
    return outline


class TestOutlineRepository:
    """测试 OutlineRepository"""

    class TestGetByOwner:
        """测试 get_by_owner 方法"""

        async def test_get_by_owner_success(
            self, repository, mock_session, sample_outline
        ):
            """测试成功获取用户大纲列表"""
            owner_id = sample_outline.user_id

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [sample_outline]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_owner(owner_id)

            assert len(result) == 1
            assert result[0] == sample_outline

        async def test_get_by_owner_empty_result(self, repository, mock_session):
            """测试用户无大纲"""
            owner_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = []
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_owner(owner_id)

            assert result == []

        async def test_get_by_owner_with_pagination(
            self, repository, mock_session, sample_outline
        ):
            """测试分页参数"""
            owner_id = sample_outline.user_id

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [sample_outline]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_owner(owner_id, skip=0, limit=10)

            assert len(result) == 1

    class TestGetReadyOutlines:
        """测试 get_ready_outlines 方法"""

        async def test_get_ready_outlines_success(
            self, repository, mock_session, sample_outline
        ):
            """测试成功获取就绪状态的大纲"""
            owner_id = sample_outline.user_id
            sample_outline.status = OutlineStatus.COMPLETED

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [sample_outline]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_ready_outlines(owner_id)

            assert len(result) == 1
            assert result[0].status == OutlineStatus.COMPLETED

        async def test_get_ready_outlines_empty(self, repository, mock_session):
            """测试无就绪状态大纲"""
            owner_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = []
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_ready_outlines(owner_id)

            assert result == []

        async def test_get_ready_outlines_with_pagination(
            self, repository, mock_session, sample_outline
        ):
            """测试带分页的获取"""
            owner_id = sample_outline.user_id
            sample_outline.status = OutlineStatus.COMPLETED

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [sample_outline]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_ready_outlines(owner_id, skip=5, limit=3)

            assert len(result) == 1

    class TestSearchByTitle:
        """测试 search_by_title 方法"""

        async def test_search_by_title_success(
            self, repository, mock_session, sample_outline
        ):
            """测试成功按标题搜索"""
            owner_id = sample_outline.user_id
            keyword = "Test"

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [sample_outline]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.search_by_title(owner_id, keyword)

            assert len(result) == 1
            assert result[0] == sample_outline

        async def test_search_by_title_no_results(self, repository, mock_session):
            """测试搜索无结果"""
            owner_id = uuid.uuid4()
            keyword = "NonExistent"

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = []
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.search_by_title(owner_id, keyword)

            assert result == []

        async def test_search_by_title_with_pagination(
            self, repository, mock_session, sample_outline
        ):
            """测试带分页的搜索"""
            owner_id = sample_outline.user_id
            keyword = "Test"

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [sample_outline]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.search_by_title(
                owner_id, keyword, skip=0, limit=5
            )

            assert len(result) == 1

        async def test_search_by_title_case_insensitive(
            self, repository, mock_session, sample_outline
        ):
            """测试搜索大小写不敏感"""
            owner_id = sample_outline.user_id
            keyword = "test"  # 小写
            sample_outline.title = "TEST OUTLINE"  # 大写

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [sample_outline]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.search_by_title(owner_id, keyword)

            assert len(result) == 1

    class TestInheritance:
        """测试继承自 BaseRepository 的方法"""

        async def test_get_by_id_inherited(
            self, repository, mock_session, sample_outline
        ):
            """测试继承的 get_by_id 方法"""
            outline_id = sample_outline.id

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = sample_outline
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_id(outline_id)

            assert result == sample_outline

        async def test_create_inherited(self, repository, mock_session, sample_outline):
            """测试继承的 create 方法"""
            result = await repository.create(sample_outline)

            assert result == sample_outline
            mock_session.add.assert_called_once_with(sample_outline)

        async def test_delete_inherited(self, repository, mock_session, sample_outline):
            """测试继承的 delete 方法"""
            outline_id = sample_outline.id

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = sample_outline
            mock_session.execute.return_value = mock_result

            result = await repository.delete(outline_id)

            assert result is True
            mock_session.delete.assert_called_once_with(sample_outline)


class TestOutlineRepositoryEdgeCases:
    """测试边界情况"""

    async def test_repository_initialization(self, mock_session):
        """测试仓储初始化"""
        repo = OutlineRepository(mock_session)

        assert repo._session == mock_session
        assert repo._model_class == Outline

    async def test_search_by_title_empty_keyword(self, repository, mock_session):
        """测试空关键词搜索"""
        owner_id = uuid.uuid4()
        keyword = ""

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.search_by_title(owner_id, keyword)

        assert result == []

    async def test_get_by_owner_large_limit(self, repository, mock_session):
        """测试大 limit 值"""
        owner_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_owner(owner_id, limit=10000)

        assert result == []
