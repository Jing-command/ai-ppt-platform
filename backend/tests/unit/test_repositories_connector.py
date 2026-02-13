"""
测试 Connector Repository
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.domain.models.connector import Connector, ConnectorType
from ai_ppt.infrastructure.repositories.connector import ConnectorRepository


@pytest.fixture
def mock_session():
    """创建模拟的异步会话"""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = MagicMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session):
    """创建测试用的仓储实例"""
    return ConnectorRepository(mock_session)


@pytest.fixture
def sample_connector():
    """创建示例连接器"""
    connector = MagicMock(spec=Connector)
    connector.id = uuid.uuid4()
    connector.user_id = uuid.uuid4()
    connector.name = "Test MySQL"
    connector.type = ConnectorType.MYSQL
    connector.config = {"host": "localhost", "port": 3306}
    connector.is_active = True
    return connector


class TestConnectorRepository:
    """测试 ConnectorRepository"""

    class TestGetByUser:
        """测试 get_by_user 方法"""

        async def test_get_by_user_success(
            self, repository, mock_session, sample_connector
        ):
            """测试成功获取用户连接器列表"""
            user_id = sample_connector.user_id

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [sample_connector]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_user(user_id)

            assert len(result) == 1
            assert result[0] == sample_connector

        async def test_get_by_user_empty_result(self, repository, mock_session):
            """测试用户无连接器"""
            user_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = []
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_user(user_id)

            assert result == []

        async def test_get_by_user_with_type_filter(
            self, repository, mock_session, sample_connector
        ):
            """测试带类型过滤的查询"""
            user_id = sample_connector.user_id

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [sample_connector]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_user(user_id, connector_type="mysql")

            assert len(result) == 1

        async def test_get_by_user_with_pagination(self, repository, mock_session):
            """测试分页参数"""
            user_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = []
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_user(user_id, skip=10, limit=5)

            assert result == []

    class TestGetByUserAndName:
        """测试 get_by_user_and_name 方法"""

        async def test_get_by_user_and_name_success(
            self, repository, mock_session, sample_connector
        ):
            """测试成功获取指定名称的连接器"""
            user_id = sample_connector.user_id
            name = sample_connector.name

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = sample_connector
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_user_and_name(user_id, name)

            assert result == sample_connector

        async def test_get_by_user_and_name_not_found(self, repository, mock_session):
            """测试获取不存在的连接器"""
            user_id = uuid.uuid4()
            name = "NonExistent"

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_user_and_name(user_id, name)

            assert result is None

    class TestCountByUser:
        """测试 count_by_user 方法"""

        async def test_count_by_user_success(self, repository, mock_session):
            """测试成功统计用户连接器数量"""
            user_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one.return_value = 5
            mock_session.execute.return_value = mock_result

            result = await repository.count_by_user(user_id)

            assert result == 5

        async def test_count_by_user_with_type_filter(self, repository, mock_session):
            """测试带类型过滤的统计"""
            user_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one.return_value = 2
            mock_session.execute.return_value = mock_result

            result = await repository.count_by_user(user_id, connector_type="mysql")

            assert result == 2

        async def test_count_by_user_zero(self, repository, mock_session):
            """测试用户无连接器"""
            user_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one.return_value = 0
            mock_session.execute.return_value = mock_result

            result = await repository.count_by_user(user_id)

            assert result == 0

    class TestNameExists:
        """测试 name_exists 方法"""

        async def test_name_exists_true(self, repository, mock_session):
            """测试名称已存在"""
            user_id = uuid.uuid4()
            name = "Existing Name"

            mock_result = MagicMock()
            mock_result.scalar_one.return_value = 1
            mock_session.execute.return_value = mock_result

            result = await repository.name_exists(user_id, name)

            assert result is True

        async def test_name_exists_false(self, repository, mock_session):
            """测试名称不存在"""
            user_id = uuid.uuid4()
            name = "New Name"

            mock_result = MagicMock()
            mock_result.scalar_one.return_value = 0
            mock_session.execute.return_value = mock_result

            result = await repository.name_exists(user_id, name)

            assert result is False

        async def test_name_exists_exclude_id(self, repository, mock_session):
            """测试排除特定 ID 后的名称存在性检查"""
            user_id = uuid.uuid4()
            name = "Existing Name"
            exclude_id = uuid.uuid4()

            mock_result = MagicMock()
            mock_result.scalar_one.return_value = 1
            mock_session.execute.return_value = mock_result

            result = await repository.name_exists(user_id, name, exclude_id=exclude_id)

            assert result is True

    class TestInheritance:
        """测试继承自 BaseRepository 的方法"""

        async def test_get_by_id_inherited(
            self, repository, mock_session, sample_connector
        ):
            """测试继承的 get_by_id 方法"""
            connector_id = sample_connector.id

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = sample_connector
            mock_session.execute.return_value = mock_result

            result = await repository.get_by_id(connector_id)

            assert result == sample_connector

        async def test_create_inherited(
            self, repository, mock_session, sample_connector
        ):
            """测试继承的 create 方法"""
            result = await repository.create(sample_connector)

            assert result == sample_connector
            mock_session.add.assert_called_once_with(sample_connector)


class TestConnectorRepositoryEdgeCases:
    """测试边界情况"""

    async def test_repository_initialization(self, mock_session):
        """测试仓储初始化"""
        repo = ConnectorRepository(mock_session)

        assert repo._session == mock_session
        assert repo._model_class == Connector

    async def test_get_by_user_with_negative_skip(self, repository, mock_session):
        """测试负数的 skip 参数"""
        user_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_user(user_id, skip=-1)

        assert result == []

    async def test_count_by_user_large_result(self, repository, mock_session):
        """测试统计大量结果"""
        user_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1000000
        mock_session.execute.return_value = mock_result

        result = await repository.count_by_user(user_id)

        assert result == 1000000
