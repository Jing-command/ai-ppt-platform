"""
Outline 仓储接口
"""

from abc import abstractmethod
from uuid import UUID

from ai_ppt.domain.models.outline import Outline
from ai_ppt.domain.repositories.base import IRepository


class IOutlineRepository(IRepository[Outline]):
    """大纲仓储接口"""

    @abstractmethod
    async def get_by_owner(
        self,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Outline]:
        """
        获取指定用户的所有大纲

        Args:
            owner_id: 用户 ID
            skip: 分页偏移量
            limit: 分页大小

        Returns:
            大纲列表
        """
        raise NotImplementedError

    @abstractmethod
    async def get_ready_outlines(
        self,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Outline]:
        """
        获取指定用户的就绪状态大纲

        Args:
            owner_id: 用户 ID
            skip: 分页偏移量
            limit: 分页大小

        Returns:
            就绪状态的大纲列表
        """
        raise NotImplementedError

    @abstractmethod
    async def search_by_title(
        self,
        owner_id: UUID,
        keyword: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Outline]:
        """
        按标题搜索大纲

        Args:
            owner_id: 用户 ID
            keyword: 搜索关键词
            skip: 分页偏移量
            limit: 分页大小

        Returns:
            匹配的大纲列表
        """
        raise NotImplementedError
