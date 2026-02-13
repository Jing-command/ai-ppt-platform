"""
Connector 仓储接口
"""

from abc import abstractmethod
from uuid import UUID

from ai_ppt.domain.models.connector import Connector
from ai_ppt.domain.repositories.base import IRepository


class IConnectorRepository(IRepository[Connector]):
    """连接器仓储接口"""

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        connector_type: str | None = None,
    ) -> list[Connector]:
        """
        获取指定用户的连接器列表

        Args:
            user_id: 用户 ID
            skip: 分页偏移量
            limit: 分页大小
            connector_type: 可选，按类型过滤

        Returns:
            连接器列表
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_and_name(
        self,
        user_id: UUID,
        name: str,
    ) -> Connector | None:
        """
        根据用户 ID 和名称获取连接器

        Args:
            user_id: 用户 ID
            name: 连接器名称

        Returns:
            连接器实体，如果不存在则返回 None
        """
        raise NotImplementedError

    @abstractmethod
    async def count_by_user(
        self,
        user_id: UUID,
        connector_type: str | None = None,
    ) -> int:
        """
        统计用户的连接器数量

        Args:
            user_id: 用户 ID
            connector_type: 可选，按类型过滤

        Returns:
            连接器数量
        """
        raise NotImplementedError

    @abstractmethod
    async def name_exists(
        self,
        user_id: UUID,
        name: str,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        检查名称是否已存在

        Args:
            user_id: 用户 ID
            name: 连接器名称
            exclude_id: 可选，排除指定 ID 的连接器

        Returns:
            如果名称已存在则返回 True
        """
        raise NotImplementedError
