"""
连接器应用服务
处理连接器的 CRUD 操作和连接测试
"""

import time
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.api.v1.schemas.connector import (
    ConnectorCreate,
    ConnectorTestResponse,
    ConnectorUpdate,
)
from ai_ppt.domain.models.connector import Connector, ConnectorStatus
from ai_ppt.domain.repositories.connector import IConnectorRepository
from ai_ppt.infrastructure.connectors.factory import ConnectorFactory
from ai_ppt.infrastructure.repositories.connector import ConnectorRepository


class ConnectorServiceError(Exception):
    """连接器服务错误基类"""


class ConnectorNotFoundError(ConnectorServiceError):
    """连接器不存在错误"""


class ConnectorNameExistsError(ConnectorServiceError):
    """连接器名称已存在错误"""


class ConnectorTestError(ConnectorServiceError):
    """连接测试错误"""


class ConnectorService:
    """
    连接器应用服务

    协调连接器的 CRUD 操作：
    1. 创建连接器配置
    2. 获取连接器列表和详情
    3. 更新连接器配置
    4. 删除连接器
    5. 测试数据源连接

    使用示例:
        >>> service = ConnectorService(db_session)
        >>> connector = await service.create_connector(
        ...     data=ConnectorCreate(
        ...         name="MySQL", type="mysql", config={...}
        ...     ),
        ...     user_id=user_id,
        ... )
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: IConnectorRepository | None = None,
    ) -> None:
        """
        初始化连接器服务

        Args:
            session: SQLAlchemy 异步会话
            repository: 可选，仓储实例
        """
        self._session = session
        self._repository = repository or ConnectorRepository(session)

    async def create_connector(
        self,
        data: ConnectorCreate,
        user_id: UUID,
    ) -> Connector:
        """
        创建连接器

        Args:
            data: 连接器创建数据
            user_id: 用户 ID

        Returns:
            创建的连接器实体

        Raises:
            ConnectorNameExistsError: 名称已存在
        """
        # 检查名称是否已存在
        exists = await self._repository.name_exists(user_id, data.name)
        if exists:
            raise ConnectorNameExistsError(
                f"Connector with name '{data.name}' already exists"
            )

        # 创建连接器实体
        connector = Connector(
            name=data.name,
            type=data.type,
            user_id=user_id,
            config=data.config,
            description=data.description,
        )

        # 保存到数据库
        created = await self._repository.create(connector)
        return created

    async def get_connector(
        self,
        connector_id: UUID,
        user_id: UUID,
    ) -> Connector:
        """
        获取连接器详情

        Args:
            connector_id: 连接器 ID
            user_id: 用户 ID

        Returns:
            连接器实体

        Raises:
            ConnectorNotFoundError: 连接器不存在
        """
        connector = await self._repository.get_by_id(connector_id)

        if not connector or connector.user_id != user_id:
            raise ConnectorNotFoundError(
                f"Connector with id '{connector_id}' not found"
            )

        return connector

    async def get_connectors(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        connector_type: str | None = None,
    ) -> tuple[list[Connector], int]:
        """
        获取连接器列表

        Args:
            user_id: 用户 ID
            skip: 分页偏移
            limit: 分页大小
            connector_type: 可选，按类型过滤

        Returns:
            (连接器列表, 总数)
        """
        connectors = await self._repository.get_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            connector_type=connector_type,
        )
        total = await self._repository.count_by_user(
            user_id=user_id,
            connector_type=connector_type,
        )
        return connectors, total

    async def update_connector(
        self,
        connector_id: UUID,
        data: ConnectorUpdate,
        user_id: UUID,
    ) -> Connector:
        """
        更新连接器

        Args:
            connector_id: 连接器 ID
            data: 更新数据
            user_id: 用户 ID

        Returns:
            更新后的连接器实体

        Raises:
            ConnectorNotFoundError: 连接器不存在
            ConnectorNameExistsError: 名称已存在
        """
        # 获取连接器
        connector = await self.get_connector(connector_id, user_id)

        # 检查名称是否冲突
        if data.name and data.name != connector.name:
            exists = await self._repository.name_exists(
                user_id, data.name, exclude_id=connector_id
            )
            if exists:
                raise ConnectorNameExistsError(
                    f"Connector with name '{data.name}' already exists"
                )
            connector.name = data.name

        # 更新字段
        if data.description is not None:
            connector.description = data.description

        if data.config is not None:
            connector.update_config(data.config)
            # 更新配置后重置状态
            connector.update_status(ConnectorStatus.DISCONNECTED)

        if data.is_active is not None:
            if data.is_active:
                connector.activate()
            else:
                connector.deactivate()

        # 保存到数据库
        updated = await self._repository.update(connector)
        return updated

    async def delete_connector(
        self,
        connector_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        删除连接器

        Args:
            connector_id: 连接器 ID
            user_id: 用户 ID

        Returns:
            是否删除成功

        Raises:
            ConnectorNotFoundError: 连接器不存在
        """
        # 验证连接器存在且属于当前用户
        await self.get_connector(connector_id, user_id)

        # 删除连接器
        success = await self._repository.delete(connector_id)
        return success

    async def test_connector(
        self,
        connector_id: UUID,
        user_id: UUID | None = None,
        test_config: dict[str, Any] | None = None,
    ) -> ConnectorTestResponse:
        """
        测试连接器

        Args:
            connector_id: 连接器 ID
            user_id: 可选，用户 ID（用于验证所有权）
            test_config: 可选，临时配置用于测试

        Returns:
            测试结果

        Raises:
            ConnectorNotFoundError: 连接器不存在
            ConnectorTestError: 测试失败
        """
        # 获取连接器
        connector = await self._repository.get_by_id(connector_id)

        if not connector:
            raise ConnectorNotFoundError(
                f"Connector with id '{connector_id}' not found"
            )

        # 验证所有权
        if user_id and connector.user_id != user_id:
            raise ConnectorNotFoundError(
                f"Connector with id '{connector_id}' not found"
            )

        # 使用临时配置或保存的配置
        config = test_config or connector.config

        try:
            # 创建连接器实例
            data_connector = ConnectorFactory.create_connector(
                connector_type=connector.type,
                config_id=str(connector_id),
                name=connector.name,
                config=config,
            )

            # 测试连接
            start_time = time.time()
            success = await data_connector.test_connection()
            latency_ms = int((time.time() - start_time) * 1000)

            # 更新连接器测试状态
            connector.mark_as_tested(success)
            await self._repository.update(connector)

            if success:
                return ConnectorTestResponse(
                    success=True,
                    message="Connection successful",
                    latencyMs=latency_ms,
                    serverVersion=getattr(
                        data_connector, "server_version", None
                    ),
                    errorDetails=None,
                )
            else:
                return ConnectorTestResponse(
                    success=False,
                    message="Connection failed",
                    latencyMs=latency_ms,
                    errorDetails="Unable to establish connection",
                    serverVersion=None,
                )

        except Exception as e:
            # 更新连接器状态为错误
            connector.update_status(ConnectorStatus.ERROR)
            await self._repository.update(connector)

            return ConnectorTestResponse(
                success=False,
                message=f"Connection test failed: {str(e)}",
                errorDetails=str(e),
                latencyMs=None,
                serverVersion=None,
            )


def get_connector_service(session: AsyncSession) -> ConnectorService:
    """
    获取连接器服务实例的便捷函数

    Args:
        session: SQLAlchemy 异步会话

    Returns:
        ConnectorService 实例
    """
    return ConnectorService(session)
