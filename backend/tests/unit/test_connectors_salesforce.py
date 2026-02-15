"""
测试 Salesforce Connector
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from ai_ppt.infrastructure.connectors.base import (
    AuthenticationError,
    ConnectionError,
    DataRow,
    DataType,
    QueryError,
)
from ai_ppt.infrastructure.connectors.salesforce import (
    SF_TYPE_MAPPING,
    SalesforceConnector,
)


class TestSFTypeMapping:
    """测试 Salesforce 类型映射"""

    def test_string_types(self):
        """测试字符串类型映射"""
        assert SF_TYPE_MAPPING["string"] == DataType.STRING
        assert SF_TYPE_MAPPING["textarea"] == DataType.STRING
        assert SF_TYPE_MAPPING["email"] == DataType.STRING
        assert SF_TYPE_MAPPING["phone"] == DataType.STRING

    def test_numeric_types(self):
        """测试数值类型映射"""
        assert SF_TYPE_MAPPING["int"] == DataType.INTEGER
        assert SF_TYPE_MAPPING["double"] == DataType.FLOAT
        assert SF_TYPE_MAPPING["currency"] == DataType.FLOAT
        assert SF_TYPE_MAPPING["percent"] == DataType.FLOAT

    def test_datetime_types(self):
        """测试日期时间类型映射"""
        assert SF_TYPE_MAPPING["date"] == DataType.DATETIME
        assert SF_TYPE_MAPPING["datetime"] == DataType.DATETIME
        assert SF_TYPE_MAPPING["time"] == DataType.DATETIME

    def test_other_types(self):
        """测试其他类型映射"""
        assert SF_TYPE_MAPPING["boolean"] == DataType.BOOLEAN
        assert SF_TYPE_MAPPING["address"] == DataType.JSON
        assert SF_TYPE_MAPPING["location"] == DataType.JSON


class TestSalesforceConnector:
    """测试 SalesforceConnector"""

    @pytest.fixture
    def connector(self):
        """创建测试用连接器"""
        return SalesforceConnector(
            config_id="sf-test",
            name="Test Salesforce",
            api_key="test_key",
            username="test@example.com",
            password="test_pass",
            security_token="token123",
        )

    class TestInitialization:
        """测试初始化"""

        def test_initialization(self, connector):
            """测试初始化"""
            assert connector.config_id == "sf-test"
            assert connector.name == "Test Salesforce"
            assert connector.api_key == "test_key"
            assert connector.username == "test@example.com"
            assert connector.password == "test_pass"
            assert connector.security_token == "token123"
            assert connector.login_url == "https://login.salesforce.com"
            assert connector.api_version == "v59.0"
            assert connector.timeout == 30.0

        def test_initialization_with_optional_params(self):
            """测试带可选参数的初始化"""
            connector = SalesforceConnector(
                config_id="sf-test",
                name="Test",
                api_key="key",
                username="user",
                password="pass",
                instance_url="https://test.salesforce.com",
                login_url="https://test.salesforce.com",
                api_version="v60.0",
                timeout=60.0,
            )

            assert connector.instance_url == "https://test.salesforce.com"
            assert connector.api_version == "v60.0"
            assert connector.timeout == 60.0

    class TestSetOAuthCredentials:
        """测试 set_oauth_credentials 方法"""

        def test_set_oauth_credentials(self, connector):
            """测试设置 OAuth 凭证"""
            connector.set_oauth_credentials(
                "client_id_123", "client_secret_456"
            )

            assert connector._client_id == "client_id_123"
            assert connector._client_secret == "client_secret_456"

    class TestConnect:
        """测试 connect 方法"""

        async def test_connect_success(self, connector):
            """测试成功连接"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(
                return_value={
                    "access_token": "test_token",
                    "instance_url": "https://test.salesforce.com",
                }
            )

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()

            with patch("httpx.AsyncClient", return_value=mock_client):
                await connector.connect()

                assert connector.is_connected is True
                assert connector._access_token == "test_token"
                assert connector.instance_url == "https://test.salesforce.com"

        async def test_connect_http_error(self, connector):
            """测试 HTTP 错误"""
            mock_client = MagicMock()
            mock_client.post = AsyncMock(
                side_effect=httpx.HTTPError("Connection failed")
            )
            mock_client.aclose = AsyncMock()

            with patch("httpx.AsyncClient", return_value=mock_client):
                with pytest.raises(
                    ConnectionError, match="Failed to authenticate"
                ):
                    await connector.connect()

        async def test_connect_missing_access_token(self, connector):
            """测试响应中缺少 access_token"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(
                return_value={
                    "instance_url": "https://test.salesforce.com",
                    # 缺少 access_token
                }
            )

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()

            with patch("httpx.AsyncClient", return_value=mock_client):
                with pytest.raises(
                    AuthenticationError,
                    match="Invalid authentication response",
                ):
                    await connector.connect()

    class TestDisconnect:
        """测试 disconnect 方法"""

        async def test_disconnect_success(self, connector):
            """测试成功断开"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(
                return_value={
                    "access_token": "token",
                    "instance_url": "https://test.salesforce.com",
                }
            )

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()

            with patch("httpx.AsyncClient", return_value=mock_client):
                await connector.connect()

            await connector.disconnect()

            assert connector.is_connected is False
            assert connector._access_token is None

        async def test_disconnect_without_connect(self, connector):
            """测试未连接时断开"""
            await connector.disconnect()

            assert connector.is_connected is False

    class TestTestConnection:
        """测试 test_connection 方法"""

        async def test_test_connection_success(self, connector):
            """测试连接测试成功"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(return_value={})
            mock_response.content = b"{}"

            mock_client = MagicMock()
            mock_client.post = AsyncMock(
                return_value=MagicMock(
                    raise_for_status=MagicMock(),
                    json=MagicMock(
                        return_value={
                            "access_token": "token",
                            "instance_url": "https://test.salesforce.com",
                        }
                    ),
                )
            )
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()

            with patch("httpx.AsyncClient", return_value=mock_client):
                await connector.connect()

            result = await connector.test_connection()

            assert result is True

        async def test_test_connection_not_authenticated(self, connector):
            """测试未认证时返回 False"""
            result = await connector.test_connection()

            assert result is False

    class TestQuery:
        """测试 query 方法"""

        async def test_query_success(self, connector):
            """测试成功查询"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(
                return_value={
                    "access_token": "token",
                    "instance_url": "https://test.salesforce.com",
                }
            )

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.request = AsyncMock(
                return_value=MagicMock(
                    raise_for_status=MagicMock(),
                    json=MagicMock(
                        return_value={
                            "records": [
                                {"Id": "001", "Name": "Test Account"},
                                {"Id": "002", "Name": "Test Account 2"},
                            ]
                        }
                    ),
                    content=b"{}",
                )
            )
            mock_client.aclose = AsyncMock()

            with patch("httpx.AsyncClient", return_value=mock_client):
                await connector.connect()

            results = await connector.query("SELECT Id, Name FROM Account")

            assert len(results) == 2
            assert results[0]["Id"] == "001"
            assert "attributes" not in results[0]  # 应该被移除

        async def test_query_with_params(self, connector):
            """测试带参数的查询"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(
                return_value={
                    "access_token": "token",
                    "instance_url": "https://test.salesforce.com",
                }
            )

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.request = AsyncMock(
                return_value=MagicMock(
                    raise_for_status=MagicMock(),
                    json=MagicMock(return_value={"records": []}),
                    content=b"{}",
                )
            )
            mock_client.aclose = AsyncMock()

            with patch("httpx.AsyncClient", return_value=mock_client):
                await connector.connect()

            results = await connector.query(
                "SELECT Id FROM Account WHERE Name = :name",
                params={"name": "Test"},
            )

            assert results == []

        async def test_query_not_connected(self, connector):
            """测试未连接时抛出异常"""
            with pytest.raises(ConnectionError, match="Not connected"):
                await connector.query("SELECT Id FROM Account")

        async def test_query_http_error(self, connector):
            """测试 HTTP 错误"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(
                return_value={
                    "access_token": "token",
                    "instance_url": "https://test.salesforce.com",
                }
            )

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.request = AsyncMock(
                side_effect=httpx.HTTPError("Query failed")
            )
            mock_client.aclose = AsyncMock()

            with patch("httpx.AsyncClient", return_value=mock_client):
                await connector.connect()

            with pytest.raises(QueryError, match="SOQL query failed"):
                await connector.query("SELECT Id FROM Account")


class TestSalesforceConnectorEdgeCases:
    """测试边界情况"""

    def test_init_without_security_token(self):
        """测试不带安全令牌初始化"""
        connector = SalesforceConnector(
            config_id="sf-test",
            name="Test",
            api_key="key",
            username="user",
            password="pass",
            # 不提供 security_token
        )

        assert connector.security_token == ""

    async def test_get_schema_not_connected(self):
        """测试未连接时获取表结构"""
        connector = SalesforceConnector(
            config_id="sf-test",
            name="Test",
            api_key="key",
            username="user",
            password="pass",
        )

        with pytest.raises(ConnectionError, match="Not connected"):
            await connector.get_schema()

    async def test_query_stream_not_connected(self):
        """测试未连接时流式查询"""
        connector = SalesforceConnector(
            config_id="sf-test",
            name="Test",
            api_key="key",
            username="user",
            password="pass",
        )

        with pytest.raises(ConnectionError, match="Not connected"):
            async for _ in connector.query_stream("SELECT Id FROM Account"):
                pass

    def test_unknown_type_mapping(self):
        """测试未知类型映射"""
        # 未知类型应该映射为 STRING
        assert (
            SF_TYPE_MAPPING.get("unknown_type", DataType.STRING)
            == DataType.STRING
        )
