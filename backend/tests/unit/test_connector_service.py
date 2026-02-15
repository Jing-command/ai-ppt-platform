"""
连接器服务单元测试
"""

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_ppt.api.v1.schemas.connector import ConnectorCreate, ConnectorUpdate
from ai_ppt.application.services.connector_service import (
    ConnectorNameExistsError,
    ConnectorNotFoundError,
    ConnectorService,
)
from ai_ppt.domain.models.connector import Connector, ConnectorStatus


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    session = AsyncMock()
    return session


@pytest.fixture
def mock_repository():
    """模拟连接器仓储"""
    repo = AsyncMock()
    return repo


@pytest.fixture
def connector_service(mock_db_session, mock_repository):
    """创建连接器服务实例"""
    return ConnectorService(mock_db_session, mock_repository)


@pytest.fixture
def sample_connector():
    """示例连接器"""
    return Connector(
        id=uuid.uuid4(),
        name="Test MySQL",
        type="mysql",
        user_id=uuid.uuid4(),
        config={
            "host": "localhost",
            "port": 3306,
            "database": "test_db",
            "username": "user",
            "password": "pass",
        },
    )


class TestConnectorServiceCreate:
    """测试创建连接器"""

    async def test_create_connector_success(
        self, connector_service, mock_repository
    ):
        """测试成功创建连接器"""
        user_id = uuid.uuid4()
        data = ConnectorCreate(
            name="MySQL Connection",
            type="mysql",
            config={"host": "localhost", "port": 3306},
            description="Test connection",
        )

        # 模拟名称不存在
        mock_repository.name_exists.return_value = False

        # 模拟创建成功
        created_connector = Connector(
            id=uuid.uuid4(),
            name=data.name,
            type=data.type,
            user_id=user_id,
            config=data.config,
        )
        mock_repository.create.return_value = created_connector

        result = await connector_service.create_connector(data, user_id)

        assert result.name == "MySQL Connection"
        assert result.type == "mysql"
        mock_repository.name_exists.assert_called_once_with(
            user_id, "MySQL Connection"
        )
        mock_repository.create.assert_called_once()

    async def test_create_connector_name_exists(
        self, connector_service, mock_repository
    ):
        """测试名称已存在的连接器创建"""
        user_id = uuid.uuid4()
        data = ConnectorCreate(
            name="Existing Name",
            type="mysql",
            config={},
        )

        # 模拟名称已存在
        mock_repository.name_exists.return_value = True

        with pytest.raises(ConnectorNameExistsError) as exc_info:
            await connector_service.create_connector(data, user_id)

        assert "Existing Name" in str(exc_info.value)
        mock_repository.create.assert_not_called()


class TestConnectorServiceGet:
    """测试获取连接器"""

    async def test_get_connector_success(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试成功获取连接器"""
        mock_repository.get_by_id.return_value = sample_connector

        result = await connector_service.get_connector(
            sample_connector.id, sample_connector.user_id
        )

        assert result.id == sample_connector.id
        assert result.name == sample_connector.name

    async def test_get_connector_not_found(
        self, connector_service, mock_repository
    ):
        """测试获取不存在的连接器"""
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ConnectorNotFoundError) as exc_info:
            await connector_service.get_connector(uuid.uuid4(), uuid.uuid4())

        assert "not found" in str(exc_info.value).lower()

    async def test_get_connector_wrong_user(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试获取其他用户的连接器"""
        mock_repository.get_by_id.return_value = sample_connector

        wrong_user_id = uuid.uuid4()

        with pytest.raises(ConnectorNotFoundError):
            await connector_service.get_connector(
                sample_connector.id, wrong_user_id
            )

    async def test_get_connectors_list(
        self, connector_service, mock_repository
    ):
        """测试获取连接器列表"""
        user_id = uuid.uuid4()
        connectors = [
            Connector(
                id=uuid.uuid4(),
                name=f"Connector {i}",
                type="mysql",
                user_id=user_id,
                config={},
            )
            for i in range(3)
        ]

        mock_repository.get_by_user.return_value = connectors
        mock_repository.count_by_user.return_value = 3

        result, total = await connector_service.get_connectors(
            user_id=user_id, skip=0, limit=10
        )

        assert len(result) == 3
        assert total == 3
        mock_repository.get_by_user.assert_called_once_with(
            user_id=user_id, skip=0, limit=10, connector_type=None
        )

    async def test_get_connectors_with_type_filter(
        self, connector_service, mock_repository
    ):
        """测试带类型过滤的连接器列表"""
        user_id = uuid.uuid4()

        mock_repository.get_by_user.return_value = []
        mock_repository.count_by_user.return_value = 0

        await connector_service.get_connectors(
            user_id=user_id, skip=0, limit=10, connector_type="postgresql"
        )

        mock_repository.get_by_user.assert_called_once_with(
            user_id=user_id, skip=0, limit=10, connector_type="postgresql"
        )


class TestConnectorServiceUpdate:
    """测试更新连接器"""

    async def test_update_connector_success(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试成功更新连接器"""
        mock_repository.get_by_id.return_value = sample_connector
        mock_repository.name_exists.return_value = False  # 名称不冲突
        mock_repository.update.return_value = sample_connector

        data = ConnectorUpdate(
            name="Updated Name", description="New description"
        )

        result = await connector_service.update_connector(
            sample_connector.id, data, sample_connector.user_id
        )

        assert result.name == "Updated Name"
        mock_repository.update.assert_called_once()

    async def test_update_connector_name_conflict(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试更新时名称冲突"""
        mock_repository.get_by_id.return_value = sample_connector
        mock_repository.name_exists.return_value = True

        data = ConnectorUpdate(name="Existing Name")

        with pytest.raises(ConnectorNameExistsError):
            await connector_service.update_connector(
                sample_connector.id, data, sample_connector.user_id
            )

    async def test_update_connector_not_found(
        self, connector_service, mock_repository
    ):
        """测试更新不存在的连接器"""
        mock_repository.get_by_id.return_value = None

        data = ConnectorUpdate(name="New Name")

        with pytest.raises(ConnectorNotFoundError):
            await connector_service.update_connector(
                uuid.uuid4(), data, uuid.uuid4()
            )

    async def test_update_connector_activate(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试激活连接器"""
        sample_connector.deactivate()
        mock_repository.get_by_id.return_value = sample_connector
        mock_repository.update.return_value = sample_connector

        data = ConnectorUpdate(is_active=True)

        result = await connector_service.update_connector(
            sample_connector.id, data, sample_connector.user_id
        )

        assert result.is_active is True

    async def test_update_connector_deactivate(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试停用连接器"""
        mock_repository.get_by_id.return_value = sample_connector
        mock_repository.update.return_value = sample_connector

        data = ConnectorUpdate(is_active=False)

        result = await connector_service.update_connector(
            sample_connector.id, data, sample_connector.user_id
        )

        assert result.is_active is False


class TestConnectorServiceDelete:
    """测试删除连接器"""

    async def test_delete_connector_success(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试成功删除连接器"""
        mock_repository.get_by_id.return_value = sample_connector
        mock_repository.delete.return_value = True

        result = await connector_service.delete_connector(
            sample_connector.id, sample_connector.user_id
        )

        assert result is True
        mock_repository.delete.assert_called_once_with(sample_connector.id)

    async def test_delete_connector_not_found(
        self, connector_service, mock_repository
    ):
        """测试删除不存在的连接器"""
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ConnectorNotFoundError):
            await connector_service.delete_connector(
                uuid.uuid4(), uuid.uuid4()
            )


class TestConnectorServiceTest:
    """测试连接器连接测试"""

    async def test_test_connector_success(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试成功连接测试"""
        mock_repository.get_by_id.return_value = sample_connector
        mock_repository.update.return_value = sample_connector

        # 模拟连接器工厂和连接
        with patch(
            "ai_ppt.application.services.connector_service.ConnectorFactory"
        ) as mock_factory:
            mock_connector = AsyncMock()
            mock_connector.test_connection.return_value = True
            mock_connector.server_version = "8.0.0"  # 设置为字符串
            mock_factory.create_connector.return_value = mock_connector

            result = await connector_service.test_connector(
                sample_connector.id, sample_connector.user_id
            )

        assert result.success is True
        assert result.message == "Connection successful"

    async def test_test_connector_failure(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试连接失败"""
        mock_repository.get_by_id.return_value = sample_connector
        mock_repository.update.return_value = sample_connector

        with patch(
            "ai_ppt.application.services.connector_service.ConnectorFactory"
        ) as mock_factory:
            mock_connector = AsyncMock()
            mock_connector.test_connection.return_value = False
            mock_factory.create_connector.return_value = mock_connector

            result = await connector_service.test_connector(
                sample_connector.id, sample_connector.user_id
            )

        assert result.success is False

    async def test_test_connector_with_temp_config(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试使用临时配置连接"""
        mock_repository.get_by_id.return_value = sample_connector
        mock_repository.update.return_value = sample_connector

        temp_config = {"host": "other-host", "port": 3307}

        with patch(
            "ai_ppt.application.services.connector_service.ConnectorFactory"
        ) as mock_factory:
            mock_connector = AsyncMock()
            mock_connector.test_connection.return_value = True
            mock_factory.create_connector.return_value = mock_connector

            await connector_service.test_connector(
                sample_connector.id,
                sample_connector.user_id,
                test_config=temp_config,
            )

        # 验证使用了临时配置
        call_kwargs = mock_factory.create_connector.call_args[1]
        assert call_kwargs["config"] == temp_config

    async def test_test_connector_not_found(
        self, connector_service, mock_repository
    ):
        """测试不存在连接器的连接测试"""
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ConnectorNotFoundError):
            await connector_service.test_connector(uuid.uuid4(), uuid.uuid4())

    async def test_test_connector_exception(
        self, connector_service, mock_repository, sample_connector
    ):
        """测试连接测试异常"""
        mock_repository.get_by_id.return_value = sample_connector
        mock_repository.update.return_value = sample_connector

        with patch(
            "ai_ppt.application.services.connector_service.ConnectorFactory"
        ) as mock_factory:
            mock_factory.create_connector.side_effect = Exception(
                "Connection error"
            )

            result = await connector_service.test_connector(
                sample_connector.id, sample_connector.user_id
            )

        assert result.success is False
        assert "Connection error" in result.message
