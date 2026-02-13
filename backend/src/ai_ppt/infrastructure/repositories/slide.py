"""
Slide 仓储实现
"""

from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.domain.models.slide import Slide
from ai_ppt.domain.repositories.slide import ISlideRepository
from ai_ppt.infrastructure.repositories.base import BaseRepository


class SlideRepository(BaseRepository[Slide], ISlideRepository):
    """幻灯片仓储实现"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Slide)

    async def get_by_presentation(self, presentation_id: UUID) -> list[Slide]:
        """获取指定演示文稿的所有幻灯片"""
        stmt = (
            select(Slide)
            .where(Slide.presentation_id == presentation_id)
            .order_by(Slide.order_index)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_max_order(self, presentation_id: UUID) -> int:
        """获取最大排序索引"""
        stmt = select(func.max(Slide.order_index)).where(
            Slide.presentation_id == presentation_id
        )
        result = await self._session.execute(stmt)
        max_order = result.scalar_one_or_none()
        return max_order or 0

    async def reorder_slides(
        self,
        presentation_id: UUID,
        slide_orders: dict[UUID, int],
    ) -> None:
        """批量重新排序幻灯片"""
        for slide_id, new_order in slide_orders.items():
            stmt = (
                update(Slide)
                .where(
                    Slide.id == slide_id,
                    Slide.presentation_id == presentation_id,
                )
                .values(order_index=new_order)
            )
            await self._session.execute(stmt)
        await self._session.flush()

    async def delete_by_presentation(self, presentation_id: UUID) -> int:
        """
        删除指定演示文稿的所有幻灯片

        Args:
            presentation_id: 演示文稿 ID

        Returns:
            删除的幻灯片数量
        """
        from sqlalchemy import delete

        stmt = delete(Slide).where(Slide.presentation_id == presentation_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount
