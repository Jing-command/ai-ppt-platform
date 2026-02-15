"""
测试 Repository 基类
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import Column, DateTime, Select, String
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.domain.models.base import Base
from ai_ppt.domain.repositories.base import EntityNotFoundError
from ai_ppt.infrastructure.repositories.base import BaseRepository


class MockModel(Base):
    """测试用模型类"""

    __tablename__ = "mock_models"

    id = Column(String, primary_key=True)
    name = Column(String, default="test")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, id=None, name="test"):
        self.id = str(id or uuid.uuid4())
        self.name = name
        self.created_at = datetime.utcnow()


@pytest.fixture
def mock_session():
    """创建模拟的异步会话"""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """创建测试用的仓储实例"""
    return BaseRepository(mock_session, MockModel)


class TestBaseRepository:
    """测试 BaseRepository"""

    class TestGetById:
        """测试 get_by_id 方法"""

        async def test_get_by_id_success(self, repository, mock_session):
            """测试成功获取实体"""
            entity_id = uuid.uuid4()
            mock_entity = MockModel(id=entity_id, name="Test Entity")

            # 模拟查询结果
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_entity
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_id(entity_id)

            assert result == mock_entity
            mock_session.execute.assert_called_once()

        async def test_get_by_id_not_found(self, repository, mock_session):
            """测试获取不存在的实体"""
            entity_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_id(entity_id)

            assert result is None

        async def test_get_by_id_with_str_uuid(self, repository, mock_session):
            """测试使用字符串 UUID"""
            entity_id = str(uuid.uuid4())
            mock_entity = MockModel(id=uuid.UUID(entity_id))

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_entity
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_id(uuid.UUID(entity_id))

            assert result == mock_entity

    class TestGetByIdOrRaise:
        """测试 get_by_id_or_raise 方法"""

        async def test_get_by_id_or_raise_success(
            self, repository, mock_session
        ):
            """测试成功获取实体"""
            entity_id = uuid.uuid4()
            mock_entity = MockModel(id=entity_id, name="Test")

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_entity
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_id_or_raise(entity_id)

            assert result == mock_entity

        async def test_get_by_id_or_raise_not_found(
            self, repository, mock_session
        ):
            """测试实体不存在时抛出异常"""
            entity_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            with pytest.raises(EntityNotFoundError) as exc_info:
                await repository.get_by_id_or_raise(entity_id)

            assert str(entity_id) in str(exc_info.value)
            assert "MockModel" in str(exc_info.value)

    class TestGetAll:
        """测试 get_all 方法"""

        async def test_get_all_default_pagination(
            self, repository, mock_session
        ):
            """测试默认分页"""
            mock_entities = [
                MockModel(name="Entity1"),
                MockModel(name="Entity2"),
            ]

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = mock_entities
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_all()

            assert len(result) == 2
            assert result == mock_entities

        async def test_get_all_with_custom_pagination(
            self, repository, mock_session
        ):
            """测试自定义分页"""
            mock_entities = [MockModel(name="Entity1")]

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = mock_entities
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_all(skip=10, limit=5)

            assert len(result) == 1

        async def test_get_all_empty_result(self, repository, mock_session):
            """测试空结果"""
            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = []
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_all()

            assert result == []

    class TestCreate:
        """测试 create 方法"""

        async def test_create_success(self, repository, mock_session):
            """测试成功创建实体"""
            entity = MockModel(name="New Entity")

            result = await repository.create(entity)

            assert result == entity
            mock_session.add.assert_called_once_with(entity)
            mock_session.flush.assert_called_once()
            mock_session.refresh.assert_called_once_with(entity)

        async def test_create_with_flush_error(self, repository, mock_session):
            """测试 flush 时出错"""
            entity = MockModel()
            mock_session.flush.side_effect = Exception("Flush error")

            with pytest.raises(Exception, match="Flush error"):
                await repository.create(entity)

    class TestUpdate:
        """测试 update 方法"""

        async def test_update_success(self, repository, mock_session):
            """测试成功更新实体"""
            entity = MockModel(name="Updated Entity")

            result = await repository.update(entity)

            assert result == entity
            mock_session.add.assert_called_once_with(entity)
            mock_session.flush.assert_called_once()
            mock_session.refresh.assert_called_once_with(entity)

    class TestDelete:
        """测试 delete 方法"""

        async def test_delete_success(self, repository, mock_session):
            """测试成功删除实体"""
            entity_id = uuid.uuid4()
            mock_entity = MockModel(id=entity_id)

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_entity
            mock_session.execute.return_value = mock_result

            result = await repository.delete(entity_id)

            assert result is True
            mock_session.delete.assert_called_once_with(mock_entity)
            mock_session.flush.assert_called_once()

        async def test_delete_not_found(self, repository, mock_session):
            """测试删除不存在的实体"""
            entity_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            result = await repository.delete(entity_id)

            assert result is False
            mock_session.delete.assert_not_called()

    class TestExists:
        """测试 exists 方法"""

        async def test_exists_true(self, repository, mock_session):
            """测试实体存在"""
            entity_id = uuid.uuid4()
            mock_entity = MockModel(id=entity_id)

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_entity
            mock_session.execute.return_value = mock_result

            result = await repository.exists(entity_id)

            assert result is True

        async def test_exists_false(self, repository, mock_session):
            """测试实体不存在"""
            entity_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            result = await repository.exists(entity_id)

            assert result is False


class TestBaseRepositoryEdgeCases:
    """测试边界情况"""

    async def test_repository_initialization(self, mock_session):
        """测试仓储初始化"""
        repo = BaseRepository(mock_session, MockModel)

        assert repo._session == mock_session
        assert repo._model_class == MockModel

    async def test_get_all_with_zero_limit(self, repository, mock_session):
        """测试 limit 为 0"""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_all(limit=0)

        assert result == []

    async def test_delete_with_flush_error(self, repository, mock_session):
        """测试删除时 flush 出错"""
        entity_id = uuid.uuid4()
        mock_entity = MockModel(id=entity_id)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_entity
        mock_session.execute.return_value = mock_result
        mock_session.flush.side_effect = Exception("Flush error")

        with pytest.raises(Exception, match="Flush error"):
            await repository.delete(entity_id)
