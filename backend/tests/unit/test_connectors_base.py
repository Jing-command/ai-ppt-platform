"""
测试 Connector Base
"""

from typing import Any, AsyncIterator, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_ppt.infrastructure.connectors.base import (
    AuthenticationError,
    ColumnSchema,
    ConnectionError,
    ConnectorError,
    DataConnector,
    DataRow,
    DataType,
    QueryError,
    TableSchema,
)


class TestDataType:
    """测试 DataType 枚举"""

    def test_data_type_values(self):
        """测试数据类型值"""
        assert DataType.STRING.value == "string"
        assert DataType.INTEGER.value == "integer"
        assert DataType.FLOAT.value == "float"
        assert DataType.BOOLEAN.value == "boolean"
        assert DataType.DATETIME.value == "datetime"
        assert DataType.JSON.value == "json"


class TestColumnSchema:
    """测试 ColumnSchema"""

    def test_column_schema_creation(self):
        """测试列模式创建"""
        column = ColumnSchema(
            name="id",
            data_type=DataType.INTEGER,
            nullable=False,
            description="Primary key",
        )

        assert column.name == "id"
        assert column.data_type == DataType.INTEGER
        assert column.nullable is False
        assert column.description == "Primary key"

    def test_column_schema_defaults(self):
        """测试默认值"""
        column = ColumnSchema(
            name="name",
            data_type=DataType.STRING,
        )

        assert column.nullable is True
        assert column.description is None


class TestTableSchema:
    """测试 TableSchema"""

    def test_table_schema_creation(self):
        """测试表模式创建"""
        columns = [
            ColumnSchema(name="id", data_type=DataType.INTEGER, nullable=False),
            ColumnSchema(name="name", data_type=DataType.STRING),
        ]
        table = TableSchema(
            name="users",
            columns=columns,
            description="User table",
        )

        assert table.name == "users"
        assert len(table.columns) == 2
        assert table.description == "User table"


class TestDataRow:
    """测试 DataRow"""

    def test_data_row_creation(self):
        """测试数据行创建"""
        row = DataRow(data={"id": 1, "name": "Test"})

        assert row.data == {"id": 1, "name": "Test"}

    def test_data_row_get(self):
        """测试 get 方法"""
        row = DataRow(data={"id": 1, "name": "Test"})

        assert row.get("id") == 1
        assert row.get("name") == "Test"
        assert row.get("missing") is None
        assert row.get("missing", "default") == "default"

    def test_data_row_getitem(self):
        """测试 __getitem__ 方法"""
        row = DataRow(data={"id": 1, "name": "Test"})

        assert row["id"] == 1
        assert row["name"] == "Test"

        with pytest.raises(KeyError):
            row["missing"]

    def test_data_row_contains(self):
        """测试 __contains__ 方法"""
        row = DataRow(data={"id": 1, "name": "Test"})

        assert "id" in row
        assert "name" in row
        assert "missing" not in row

    def test_data_row_repr(self):
        """测试 __repr__ 方法"""
        row = DataRow(data={"id": 1})

        repr_str = repr(row)

        assert "DataRow" in repr_str
        assert "id" in repr_str


class TestConnectorExceptions:
    """测试连接器异常"""

    def test_connector_error(self):
        """测试 ConnectorError"""
        exc = ConnectorError("Connection failed")

        assert str(exc) == "Connection failed"

    def test_connection_error(self):
        """测试 ConnectionError"""
        exc = ConnectionError("Cannot connect")

        assert str(exc) == "Cannot connect"
        assert isinstance(exc, ConnectorError)

    def test_query_error(self):
        """测试 QueryError"""
        exc = QueryError("Invalid query", query="SELECT * FROM")

        assert str(exc) == "Invalid query"
        assert exc.query == "SELECT * FROM"
        assert isinstance(exc, ConnectorError)

    def test_query_error_without_query(self):
        """测试不带查询的 QueryError"""
        exc = QueryError("Query failed")

        assert exc.query is None

    def test_authentication_error(self):
        """测试 AuthenticationError"""
        exc = AuthenticationError("Invalid credentials")

        assert str(exc) == "Invalid credentials"
        assert isinstance(exc, ConnectorError)


class MockDataConnector(DataConnector):
    """测试用数据连接器"""

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def test_connection(self) -> bool:
        return self._connected

    async def get_schema(self) -> List[TableSchema]:
        return []

    async def query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[DataRow]:
        return []

    async def query_stream(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        batch_size: int = 1000,
    ) -> AsyncIterator[DataRow]:
        return
        yield


class TestDataConnector:
    """测试 DataConnector 基类"""

    class TestInitialization:
        """测试初始化"""

        def test_initialization(self):
            """测试初始化"""
            connector = MockDataConnector(config_id="test-1", name="Test Connector")

            assert connector.config_id == "test-1"
            assert connector.name == "Test Connector"
            assert connector.is_connected is False

    class TestIsConnected:
        """测试 is_connected 属性"""

        async def test_is_connected_after_connect(self):
            """测试连接后状态"""
            connector = MockDataConnector(config_id="test", name="Test")

            await connector.connect()

            assert connector.is_connected is True

        async def test_is_connected_after_disconnect(self):
            """测试断开后状态"""
            connector = MockDataConnector(config_id="test", name="Test")
            await connector.connect()

            await connector.disconnect()

            assert connector.is_connected is False

    class TestContextManager:
        """测试异步上下文管理器"""

        async def test_async_context_manager(self):
            """测试异步上下文管理器"""
            connector = MockDataConnector(config_id="test", name="Test")

            async with connector as conn:
                assert conn.is_connected is True

            assert connector.is_connected is False

        async def test_async_context_manager_with_exception(self):
            """测试上下文管理器中发生异常"""
            connector = MockDataConnector(config_id="test", name="Test")

            with pytest.raises(ValueError, match="Test error"):
                async with connector:
                    raise ValueError("Test error")

            assert connector.is_connected is False


class TestDataConnectorEdgeCases:
    """测试边界情况"""

    def test_empty_config_id(self):
        """测试空配置 ID"""
        connector = MockDataConnector(config_id="", name="Test")

        assert connector.config_id == ""

    def test_empty_name(self):
        """测试空名称"""
        connector = MockDataConnector(config_id="test", name="")

        assert connector.name == ""

    def test_data_row_empty_data(self):
        """测试空数据行"""
        row = DataRow(data={})

        assert row.data == {}
        assert "key" not in row
        assert row.get("key") is None
