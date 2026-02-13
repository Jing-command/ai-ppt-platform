"""
数据连接器工厂
根据配置动态创建对应类型的连接器
"""
from typing import Any, Dict, Type

from ai_ppt.infrastructure.connectors.base import DataConnector
from ai_ppt.infrastructure.connectors.mysql import MySQLConnector
from ai_ppt.infrastructure.connectors.salesforce import SalesforceConnector


class ConnectorType:
    """连接器类型常量"""
    MYSQL = "mysql"
    SALESFORCE = "salesforce"
    POSTGRESQL = "postgresql"


class ConnectorFactory:
    """
    连接器工厂
    
    根据配置创建对应的连接器实例
    支持注册自定义连接器类型
    """
    
    _connectors: Dict[str, Type[DataConnector]] = {
        ConnectorType.MYSQL: MySQLConnector,
        ConnectorType.SALESFORCE: SalesforceConnector,
        # PostgreSQL 连接器占位，可后续实现
        # ConnectorType.POSTGRESQL: PostgreSQLConnector,
    }
    
    @classmethod
    def register(
        cls,
        connector_type: str,
        connector_class: Type[DataConnector],
    ) -> None:
        """
        注册新的连接器类型
        
        Args:
            connector_type: 连接器类型标识
            connector_class: 连接器类
        """
        cls._connectors[connector_type] = connector_class
    
    @classmethod
    def unregister(cls, connector_type: str) -> None:
        """
        注销连接器类型
        
        Args:
            connector_type: 连接器类型标识
        """
        if connector_type in cls._connectors:
            del cls._connectors[connector_type]
    
    @classmethod
    def get_supported_types(cls) -> list[str]:
        """获取所有支持的连接器类型"""
        return list(cls._connectors.keys())
    
    @classmethod
    def create_connector(
        cls,
        connector_type: str,
        config_id: str,
        name: str,
        config: Dict[str, Any],
    ) -> DataConnector:
        """
        根据配置创建连接器
        
        Args:
            connector_type: 连接器类型（mysql, salesforce, postgresql）
            config_id: 配置 ID
            name: 连接器名称
            config: 连接器配置字典
            
        Returns:
            配置好的连接器实例
            
        Raises:
            ValueError: 不支持的连接器类型
        """
        connector_class = cls._connectors.get(connector_type)
        if not connector_class:
            raise ValueError(
                f"Unsupported connector type: {connector_type}. "
                f"Supported types: {', '.join(cls.get_supported_types())}"
            )
        
        # 根据连接器类型提取配置参数
        if connector_type == ConnectorType.MYSQL:
            return MySQLConnector(
                config_id=config_id,
                name=name,
                host=config.get("host", "localhost"),
                port=config.get("port", 3306),
                username=config.get("username", ""),
                password=config.get("password", ""),
                database=config.get("database", ""),
                pool_size=config.get("pool_size", 5),
                max_overflow=config.get("max_overflow", 10),
                ssl=config.get("ssl"),
                connect_timeout=config.get("connect_timeout", 30),
            )
        
        elif connector_type == ConnectorType.SALESFORCE:
            connector = SalesforceConnector(
                config_id=config_id,
                name=name,
                api_key=config.get("api_key", ""),
                username=config.get("username", ""),
                password=config.get("password", ""),
                security_token=config.get("security_token"),
                instance_url=config.get("instance_url"),
                login_url=config.get("login_url", "https://login.salesforce.com"),
                api_version=config.get("api_version", "v59.0"),
                timeout=config.get("timeout", 30.0),
            )
            # 如果提供了 OAuth 凭证，设置 OAuth 凭证
            if config.get("client_id") and config.get("client_secret"):
                connector.set_oauth_credentials(
                    config["client_id"],
                    config["client_secret"]
                )
            return connector
        
        elif connector_type == ConnectorType.POSTGRESQL:
            # PostgreSQL 连接器占位实现
            raise NotImplementedError(
                "PostgreSQL connector is not yet implemented. "
                "Please implement PostgreSQLConnector class."
            )
        
        else:
            raise ValueError(f"Unknown connector type: {connector_type}")
    
    @classmethod
    async def create_and_connect(
        cls,
        connector_type: str,
        config_id: str,
        name: str,
        config: Dict[str, Any],
    ) -> DataConnector:
        """
        创建连接器并建立连接
        
        这是便捷方法，创建连接器后立即调用 connect()
        
        Args:
            connector_type: 连接器类型
            config_id: 配置 ID
            name: 连接器名称
            config: 连接器配置字典
            
        Returns:
            已连接的连接器实例
        """
        connector = cls.create_connector(
            connector_type=connector_type,
            config_id=config_id,
            name=name,
            config=config,
        )
        await connector.connect()
        return connector
