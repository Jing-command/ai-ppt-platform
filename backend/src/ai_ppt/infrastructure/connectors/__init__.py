"""
数据连接器模块

提供统一的数据源连接和查询接口
支持 MySQL、Salesforce 等数据源
"""

# 基类和数据类型
from ai_ppt.infrastructure.connectors.base import (
    AuthenticationError,
    ColumnSchema,
    ConnectionError,
    ConnectorError,
    DataConnector,
    DataConnectorFactory,
    DataRow,
    DataType,
    QueryError,
    TableSchema,
)

# 工厂类
from ai_ppt.infrastructure.connectors.factory import ConnectorFactory, ConnectorType

# 具体连接器实现
from ai_ppt.infrastructure.connectors.mysql import MySQLConnector
from ai_ppt.infrastructure.connectors.salesforce import SalesforceConnector

__all__ = [
    # 基类
    "DataConnector",
    "DataConnectorFactory",
    "DataRow",
    "DataType",
    "ColumnSchema",
    "TableSchema",
    "ConnectorError",
    "ConnectionError",
    "QueryError",
    "AuthenticationError",
    # 连接器实现
    "MySQLConnector",
    "SalesforceConnector",
    # 工厂
    "ConnectorFactory",
    "ConnectorType",
]
