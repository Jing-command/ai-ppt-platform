"""
测试 Connector Factory
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_ppt.infrastructure.connectors.base import DataConnector
from ai_ppt.infrastructure.connectors.factory import (
    ConnectorFactory,
    ConnectorType,
)
from ai_ppt.infrastructure.connectors.mysql import MySQLConnector
from ai_ppt.infrastructure.connectors.salesforce import SalesforceConnector


class TestConnectorType:
    """测试 ConnectorType 常量"""

    def test_connector_type_values(self):
        """测试连接器类型常量"""
        assert ConnectorType.MYSQL == "mysql"
        assert ConnectorType.SALESFORCE == "salesforce"
        assert ConnectorType.POSTGRESQL == "postgresql"


class TestConnectorFactory:
    """测试 ConnectorFactory"""

    class TestRegister:
        """测试 register 方法"""

        def test_register_new_connector(self):
            """测试注册新连接器类型"""

            class MockConnector(DataConnector):
                async def connect(self):
                    pass

                async def disconnect(self):
                    pass

                async def test_connection(self):
                    return True

                async def get_schema(self):
                    return []

                async def query(self, query, params=None, limit=None):
                    return []

                async def query_stream(
                    self, query, params=None, batch_size=1000
                ):
                    return
                    yield

            ConnectorFactory.register("mock", MockConnector)

            assert "mock" in ConnectorFactory._connectors
            assert ConnectorFactory._connectors["mock"] == MockConnector

        def test_register_overwrite(self):
            """测试覆盖注册"""

            class MockConnector1(DataConnector):
                async def connect(self):
                    pass

                async def disconnect(self):
                    pass

                async def test_connection(self):
                    return True

                async def get_schema(self):
                    return []

                async def query(self, query, params=None, limit=None):
                    return []

                async def query_stream(
                    self, query, params=None, batch_size=1000
                ):
                    return
                    yield

            class MockConnector2(DataConnector):
                async def connect(self):
                    pass

                async def disconnect(self):
                    pass

                async def test_connection(self):
                    return True

                async def get_schema(self):
                    return []

                async def query(self, query, params=None, limit=None):
                    return []

                async def query_stream(
                    self, query, params=None, batch_size=1000
                ):
                    return
                    yield

            ConnectorFactory.register("test_type", MockConnector1)
            ConnectorFactory.register("test_type", MockConnector2)

            assert ConnectorFactory._connectors["test_type"] == MockConnector2

    class TestUnregister:
        """测试 unregister 方法"""

        def test_unregister_existing(self):
            """测试注销存在的连接器类型"""

            class MockConnector(DataConnector):
                async def connect(self):
                    pass

                async def disconnect(self):
                    pass

                async def test_connection(self):
                    return True

                async def get_schema(self):
                    return []

                async def query(self, query, params=None, limit=None):
                    return []

                async def query_stream(
                    self, query, params=None, batch_size=1000
                ):
                    return
                    yield

            ConnectorFactory.register("to_remove", MockConnector)
            ConnectorFactory.unregister("to_remove")

            assert "to_remove" not in ConnectorFactory._connectors

        def test_unregister_nonexistent(self):
            """测试注销不存在的连接器类型"""
            # 不应抛出异常
            ConnectorFactory.unregister("nonexistent")

    class TestGetSupportedTypes:
        """测试 get_supported_types 方法"""

        def test_get_supported_types(self):
            """测试获取支持的类型"""
            types = ConnectorFactory.get_supported_types()

            assert "mysql" in types
            assert "salesforce" in types
            assert "postgresql" in types

    class TestCreateConnector:
        """测试 create_connector 方法"""

        def test_create_mysql_connector(self):
            """测试创建 MySQL 连接器"""
            config = {
                "host": "localhost",
                "port": 3306,
                "database": "test_db",
                "username": "user",
                "password": "pass",
                "pool_size": 10,
                "max_overflow": 20,
            }

            connector = ConnectorFactory.create_connector(
                connector_type=ConnectorType.MYSQL,
                config_id="mysql-1",
                name="Test MySQL",
                config=config,
            )

            assert isinstance(connector, MySQLConnector)
            assert connector.config_id == "mysql-1"
            assert connector.name == "Test MySQL"
            assert connector.host == "localhost"
            assert connector.port == 3306

        def test_create_mysql_with_defaults(self):
            """测试创建 MySQL 连接器使用默认值"""
            config = {
                "host": "localhost",
                "username": "user",
                "password": "pass",
                "database": "test",
            }

            connector = ConnectorFactory.create_connector(
                connector_type=ConnectorType.MYSQL,
                config_id="mysql-1",
                name="Test",
                config=config,
            )

            assert connector.port == 3306  # 默认值
            assert connector.pool_size == 5  # 默认值

        def test_create_salesforce_connector(self):
            """测试创建 Salesforce 连接器"""
            config = {
                "api_key": "test_key",
                "username": "test@example.com",
                "password": "password",
                "security_token": "token123",
            }

            connector = ConnectorFactory.create_connector(
                connector_type=ConnectorType.SALESFORCE,
                config_id="sf-1",
                name="Test Salesforce",
                config=config,
            )

            assert isinstance(connector, SalesforceConnector)
            assert connector.config_id == "sf-1"
            assert connector.api_key == "test_key"
            assert connector.username == "test@example.com"

        def test_create_salesforce_with_oauth(self):
            """测试创建带 OAuth 的 Salesforce 连接器"""
            config = {
                "api_key": "test_key",
                "username": "test@example.com",
                "password": "password",
                "client_id": "client_id_123",
                "client_secret": "client_secret_456",
            }

            connector = ConnectorFactory.create_connector(
                connector_type=ConnectorType.SALESFORCE,
                config_id="sf-1",
                name="Test Salesforce",
                config=config,
            )

            assert connector._client_id == "client_id_123"
            assert connector._client_secret == "client_secret_456"

        def test_create_unsupported_type(self):
            """测试创建不支持的连接器类型"""
            with pytest.raises(ValueError, match="Unsupported connector type"):
                ConnectorFactory.create_connector(
                    connector_type="unsupported",
                    config_id="test",
                    name="Test",
                    config={},
                )

        def test_create_postgresql_not_implemented(self):
            """测试创建未实现的 PostgreSQL 连接器"""
            with pytest.raises(
                NotImplementedError, match="not yet implemented"
            ):
                ConnectorFactory.create_connector(
                    connector_type=ConnectorType.POSTGRESQL,
                    config_id="pg-1",
                    name="Test PostgreSQL",
                    config={},
                )

    class TestCreateAndConnect:
        """测试 create_and_connect 方法"""

        async def test_create_and_connect(self):
            """测试创建并连接"""
            config = {
                "host": "localhost",
                "username": "user",
                "password": "pass",
                "database": "test",
            }

            with patch.object(
                MySQLConnector, "connect", new_callable=AsyncMock
            ) as mock_connect:
                connector = await ConnectorFactory.create_and_connect(
                    connector_type=ConnectorType.MYSQL,
                    config_id="mysql-1",
                    name="Test",
                    config=config,
                )

                assert isinstance(connector, MySQLConnector)
                mock_connect.assert_called_once()


class TestConnectorFactoryEdgeCases:
    """测试边界情况"""

    def test_mysql_config_with_ssl(self):
        """测试 MySQL 配置带 SSL"""
        config = {
            "host": "localhost",
            "username": "user",
            "password": "pass",
            "database": "test",
            "ssl": {"ca": "/path/to/ca.pem"},
        }

        connector = ConnectorFactory.create_connector(
            connector_type=ConnectorType.MYSQL,
            config_id="mysql-ssl",
            name="Test SSL",
            config=config,
        )

        assert connector.ssl == {"ca": "/path/to/ca.pem"}

    def test_salesforce_with_optional_params(self):
        """测试 Salesforce 带可选参数"""
        config = {
            "api_key": "key",
            "username": "user",
            "password": "pass",
            "instance_url": "https://test.salesforce.com",
            "login_url": "https://test.salesforce.com",
            "api_version": "v60.0",
            "timeout": 60.0,
        }

        connector = ConnectorFactory.create_connector(
            connector_type=ConnectorType.SALESFORCE,
            config_id="sf-1",
            name="Test",
            config=config,
        )

        assert connector.instance_url == "https://test.salesforce.com"
        assert connector.login_url == "https://test.salesforce.com"
        assert connector.api_version == "v60.0"
        assert connector.timeout == 60.0

    def test_empty_config(self):
        """测试空配置"""
        connector = ConnectorFactory.create_connector(
            connector_type=ConnectorType.MYSQL,
            config_id="empty",
            name="Empty",
            config={},
        )

        assert isinstance(connector, MySQLConnector)
        assert connector.host == "localhost"  # 默认值
        assert connector.port == 3306  # 默认值
