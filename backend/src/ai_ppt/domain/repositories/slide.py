"""
Slide 仓储接口
"""

from abc import abstractmethod
from uuid import UUID

from ai_ppt.domain.models.slide import Slide
from ai_ppt.domain.repositories.base import IRepository


class ISlideRepository(IRepository[Slide]):
    """幻灯片仓储接口"""

    @abstractmethod
    async def get_by_presentation(
        self,
        presentation_id: UUID,
    ) -> list[Slide]:
        """
        获取指定演示文稿的所有幻灯片

        Args:
            presentation_id: 演示文稿 ID

        Returns:
            幻灯片列表，按 order_index 排序
        """
        raise NotImplementedError

    @abstractmethod
    async def get_max_order(self, presentation_id: UUID) -> int:
        """
        获取指定演示文稿的最大排序索引

        Args:
            presentation_id: 演示文稿 ID

        Returns:
            最大排序索引，如果没有幻灯片则返回 0
        """
        raise NotImplementedError

    @abstractmethod
    async def reorder_slides(
        self,
        presentation_id: UUID,
        slide_orders: dict[UUID, int],
    ) -> None:
        """
        批量重新排序幻灯片

        Args:
            presentation_id: 演示文稿 ID
            slide_orders: 幻灯片 ID 到新排序索引的映射
        """
        raise NotImplementedError
