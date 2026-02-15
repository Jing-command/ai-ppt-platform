"""
数据连接器抽象接口
定义统一的数据源连接和查询接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional


class DataType(Enum):
    """支持的数据类型"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    JSON = "json"


@dataclass(frozen=True)
class ColumnSchema:
    """列/字段模式"""

    name: str
    data_type: DataType
    nullable: bool = True
    description: Optional[str] = None


@dataclass(frozen=True)
class TableSchema:
    """表/对象模式"""

    name: str
    columns: List[ColumnSchema]
    description: Optional[str] = None


@dataclass
class DataRow:
    """数据行"""

    data: Dict[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __repr__(self) -> str:
        return f"DataRow({self.data})"


class ConnectorError(Exception):
    """连接器错误基类"""


class ConnectionError(ConnectorError):
    """连接错误"""


class QueryError(ConnectorError):
    """查询错误"""

    def __init__(self, message: str, query: Optional[str] = None) -> None:
        super().__init__(message)
        self.query = query


class AuthenticationError(ConnectorError):
    """认证错误"""


class DataConnector(ABC):
    """
    数据连接器抽象基类

    所有数据源连接器必须实现此接口
    """

    def __init__(self, config_id: str, name: str) -> None:
        self.config_id = config_id
        self.name = name
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected

    @abstractmethod
    async def connect(self) -> None:
        """建立连接"""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接"""
        raise NotImplementedError

    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接是否可用"""
        raise NotImplementedError

    @abstractmethod
    async def get_schema(self) -> List[TableSchema]:
        """获取数据源结构（表/对象列表）"""
        raise NotImplementedError

    @abstractmethod
    async def query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[DataRow]:
        """
        执行查询

        Args:
            query: 查询语句（SQL 或特定查询语法）
            params: 查询参数
            limit: 结果数量限制

        Returns:
            查询结果列表
        """
        raise NotImplementedError

    @abstractmethod
    def query_stream(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        batch_size: int = 1000,
    ) -> AsyncIterator[DataRow]:
        """
        流式查询（用于大数据量）

        Args:
            query: 查询语句
            params: 查询参数
            batch_size: 每批次数量

        Yields:
            数据行
        """
        raise NotImplementedError

    async def __aenter__(self) -> "DataConnector":
        """异步上下文管理器入口"""
        await self.connect()
        return self

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """异步上下文管理器出口"""
        await self.disconnect()


class DataConnectorFactory(ABC):
    """
    连接器工厂接口

    根据配置创建对应的连接器实例
    """

    @abstractmethod
    async def create_connector(
        self,
        config_id: str,
    ) -> DataConnector:
        """创建连接器实例"""
        raise NotImplementedError
