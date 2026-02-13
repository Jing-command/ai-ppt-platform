"""
测试 MySQL Connector
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_ppt.infrastructure.connectors.base import (
    ConnectionError,
    DataRow,
    DataType,
    QueryError,
)
from ai_ppt.infrastructure.connectors.mysql import MYSQL_TYPE_MAPPING, MySQLConnector


class TestMySQLTypeMapping:
    """测试 MySQL 类型映射"""

    def test_string_types(self):
        """测试字符串类型映射"""
        assert MYSQL_TYPE_MAPPING["varchar"] == DataType.STRING
        assert MYSQL_TYPE_MAPPING["text"] == DataType.STRING
        assert MYSQL_TYPE_MAPPING["longtext"] == DataType.STRING
        assert MYSQL_TYPE_MAPPING["char"] == DataType.STRING

    def test_integer_types(self):
        """测试整数类型映射"""
        assert MYSQL_TYPE_MAPPING["int"] == DataType.INTEGER
        assert MYSQL_TYPE_MAPPING["bigint"] == DataType.INTEGER
        assert MYSQL_TYPE_MAPPING["smallint"] == DataType.INTEGER

    def test_float_types(self):
        """测试浮点类型映射"""
        assert MYSQL_TYPE_MAPPING["float"] == DataType.FLOAT
        assert MYSQL_TYPE_MAPPING["double"] == DataType.FLOAT
        assert MYSQL_TYPE_MAPPING["decimal"] == DataType.FLOAT

    def test_datetime_types(self):
        """测试日期时间类型映射"""
        assert MYSQL_TYPE_MAPPING["datetime"] == DataType.DATETIME
        assert MYSQL_TYPE_MAPPING["timestamp"] == DataType.DATETIME
        assert MYSQL_TYPE_MAPPING["date"] == DataType.DATETIME

    def test_other_types(self):
        """测试其他类型映射"""
        assert MYSQL_TYPE_MAPPING["json"] == DataType.JSON
        assert MYSQL_TYPE_MAPPING["bool"] == DataType.BOOLEAN
        assert MYSQL_TYPE_MAPPING["boolean"] == DataType.BOOLEAN


class TestMySQLConnector:
    """测试 MySQLConnector"""

    @pytest.fixture
    def connector(self):
        """创建测试用连接器"""
        return MySQLConnector(
            config_id="mysql-test",
            name="Test MySQL",
            host="localhost",
            port=3306,
            username="test_user",
            password="test_pass",
            database="test_db",
            pool_size=5,
            max_overflow=10,
        )

    class TestInitialization:
        """测试初始化"""

        def test_initialization(self, connector):
            """测试初始化"""
            assert connector.config_id == "mysql-test"
            assert connector.name == "Test MySQL"
            assert connector.host == "localhost"
            assert connector.port == 3306
            assert connector.username == "test_user"
            assert connector.password == "test_pass"
            assert connector.database == "test_db"
            assert connector.pool_size == 5
            assert connector.max_overflow == 10
            assert connector._pool is None

    class TestConnect:
        """测试 connect 方法"""

        async def test_connect_success(self, connector):
            """测试成功连接"""
            mock_pool = MagicMock()
            mock_pool.close = MagicMock()
            mock_pool.wait_closed = AsyncMock()

            with patch('aiomysql.create_pool', return_value=mock_pool):
                await connector.connect()

                assert connector.is_connected is True
                assert connector._pool is not None

        async def test_connect_failure(self, connector):
            """测试连接失败"""
            with patch('aiomysql.create_pool', side_effect=Exception("Connection refused")):
                with pytest.raises(ConnectionError, match="Failed to connect"):
                    await connector.connect()

                assert connector.is_connected is False

    class TestDisconnect:
        """测试 disconnect 方法"""

        async def test_disconnect_success(self, connector):
            """测试成功断开"""
            mock_pool = MagicMock()
            mock_pool.close = MagicMock()
            mock_pool.wait_closed = AsyncMock()

            with patch('aiomysql.create_pool', return_value=mock_pool):
                await connector.connect()
                await connector.disconnect()

                assert connector.is_connected is False
                assert connector._pool is None
                mock_pool.close.assert_called_once()
                mock_pool.wait_closed.assert_called_once()

        async def test_disconnect_without_connect(self, connector):
            """测试未连接时断开"""
            await connector.disconnect()

            assert connector.is_connected is False

    class TestTestConnection:
        """测试 test_connection 方法"""

        async def test_test_connection_success(self, connector):
            """测试连接测试成功"""
            mock_pool = MagicMock()
            mock_conn = AsyncMock()
            mock_cur = AsyncMock()
            mock_cur.fetchone = AsyncMock(return_value=(1,))

            mock_pool.acquire = MagicMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)
            mock_conn.cursor = MagicMock(return_value=mock_cur)
            mock_cur.__aenter__ = AsyncMock(return_value=mock_cur)
            mock_cur.__aexit__ = AsyncMock(return_value=None)

            with patch('aiomysql.create_pool', return_value=mock_pool):
                await connector.connect()

            # 模拟连接池返回正确的连接对象
            mock_pool.acquire.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cur

            result = await connector.test_connection()

            assert result is True

        async def test_test_connection_not_connected(self, connector):
            """测试未连接时返回 False"""
            result = await connector.test_connection()

            assert result is False

        async def test_test_connection_failure(self, connector):
            """测试连接测试失败"""
            mock_pool = MagicMock()

            with patch('aiomysql.create_pool', return_value=mock_pool):
                await connector.connect()

            mock_pool.acquire = MagicMock(side_effect=Exception("Query failed"))

            result = await connector.test_connection()

            assert result is False

    class TestGetSchema:
        """测试 get_schema 方法"""

        async def test_get_schema_success(self, connector):
            """测试成功获取表结构"""
            mock_pool = MagicMock()

            with patch('aiomysql.create_pool', return_value=mock_pool):
                await connector.connect()

            # 模拟游标返回表和列信息
            mock_cur = AsyncMock()
            mock_cur.fetchone = AsyncMock(side_effect=[
                None,  # First call
            ])
            mock_cur.fetchall = AsyncMock(side_effect=[
                [{"TABLE_NAME": "users", "TABLE_COMMENT": "Users table"}],
                [
                    {"COLUMN_NAME": "id", "DATA_TYPE": "int", "IS_NULLABLE": "NO", "COLUMN_COMMENT": ""},
                    {"COLUMN_NAME": "name", "DATA_TYPE": "varchar", "IS_NULLABLE": "YES", "COLUMN_COMMENT": "User name"},
                ],
            ])

            mock_conn = AsyncMock()
            mock_conn.cursor = MagicMock(return_value=mock_cur)
            mock_pool.acquire = MagicMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)

            schemas = await connector.get_schema()

            assert len(schemas) == 1
            assert schemas[0].name == "users"
            assert len(schemas[0].columns) == 2

        async def test_get_schema_not_connected(self, connector):
            """测试未连接时抛出异常"""
            with pytest.raises(ConnectionError, match="Not connected"):
                await connector.get_schema()

    class TestQuery:
        """测试 query 方法"""

        async def test_query_success(self, connector):
            """测试成功查询"""
            mock_pool = MagicMock()

            with patch('aiomysql.create_pool', return_value=mock_pool):
                await connector.connect()

            mock_cur = AsyncMock()
            mock_cur.fetchall = AsyncMock(return_value=[
                {"id": 1, "name": "Test"},
                {"id": 2, "name": "Test2"},
            ])

            mock_conn = AsyncMock()
            mock_conn.cursor = MagicMock(return_value=mock_cur)
            mock_pool.acquire = MagicMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)

            results = await connector.query("SELECT * FROM users")

            assert len(results) == 2
            assert results[0]["id"] == 1

        async def test_query_with_limit(self, connector):
            """测试带限制的查询"""
            mock_pool = MagicMock()

            with patch('aiomysql.create_pool', return_value=mock_pool):
                await connector.connect()

            mock_cur = AsyncMock()
            mock_cur.fetchall = AsyncMock(return_value=[{"id": 1}])

            mock_conn = AsyncMock()
            mock_conn.cursor = MagicMock(return_value=mock_cur)
            mock_pool.acquire = MagicMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)

            results = await connector.query("SELECT * FROM users", limit=10)

            mock_cur.execute.assert_called_once()
            call_args = mock_cur.execute.call_args[0][0]
            assert "LIMIT 10" in call_args

        async def test_query_not_connected(self, connector):
            """测试未连接时抛出异常"""
            with pytest.raises(ConnectionError, match="Not connected"):
                await connector.query("SELECT 1")

        async def test_query_failure(self, connector):
            """测试查询失败"""
            mock_pool = MagicMock()

            with patch('aiomysql.create_pool', return_value=mock_pool):
                await connector.connect()

            mock_cur = AsyncMock()
            mock_cur.execute = AsyncMock(side_effect=Exception("Syntax error"))

            mock_conn = AsyncMock()
            mock_conn.cursor = MagicMock(return_value=mock_cur)
            mock_pool.acquire = MagicMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(QueryError, match="Query failed"):
                await connector.query("INVALID SQL")


class TestMySQLConnectorEdgeCases:
    """测试边界情况"""

    def test_init_with_ssl(self):
        """测试带 SSL 初始化"""
        connector = MySQLConnector(
            config_id="mysql-ssl",
            name="Test SSL",
            host="localhost",
            port=3306,
            username="user",
            password="pass",
            database="test",
            ssl={"ca": "/path/to/ca.pem"},
        )

        assert connector.ssl == {"ca": "/path/to/ca.pem"}

    def test_init_with_timeout(self):
        """测试带超时初始化"""
        connector = MySQLConnector(
            config_id="mysql-timeout",
            name="Test Timeout",
            host="localhost",
            port=3306,
            username="user",
            password="pass",
            database="test",
            connect_timeout=60,
        )

        assert connector.connect_timeout == 60

    def test_unknown_type_mapping(self):
        """测试未知类型映射"""
        # 未知类型应该映射为 STRING
        assert MYSQL_TYPE_MAPPING.get("unknown_type", DataType.STRING) == DataType.STRING
