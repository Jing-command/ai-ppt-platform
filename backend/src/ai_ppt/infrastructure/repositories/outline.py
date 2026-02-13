"""
Outline 仓储实现
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.domain.models.outline import Outline, OutlineStatus
from ai_ppt.domain.repositories.outline import IOutlineRepository
from ai_ppt.infrastructure.repositories.base import BaseRepository


class OutlineRepository(BaseRepository[Outline], IOutlineRepository):
    """大纲仓储实现"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Outline)

    async def get_by_owner(
        self,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Outline]:
        """获取指定用户的所有大纲"""
        stmt = (
            select(Outline)
            .where(Outline.user_id == owner_id)
            .offset(skip)
            .limit(limit)
            .order_by(Outline.updated_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_ready_outlines(
        self,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Outline]:
        """获取指定用户的就绪状态大纲"""
        stmt = (
            select(Outline)
            .where(
                Outline.user_id == owner_id,
                Outline.status == OutlineStatus.COMPLETED.value,
            )
            .offset(skip)
            .limit(limit)
            .order_by(Outline.updated_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_title(
        self,
        owner_id: UUID,
        keyword: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Outline]:
        """按标题搜索大纲"""
        stmt = (
            select(Outline)
            .where(
                Outline.user_id == owner_id,
                Outline.title.ilike(f"%{keyword}%"),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
