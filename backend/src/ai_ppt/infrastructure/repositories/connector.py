"""
Connector 仓储实现
"""
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.domain.models.connector import Connector
from ai_ppt.domain.repositories.connector import IConnectorRepository
from ai_ppt.infrastructure.repositories.base import BaseRepository


class ConnectorRepository(BaseRepository[Connector], IConnectorRepository):
    """连接器仓储实现"""
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Connector)
    
    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        connector_type: str | None = None,
    ) -> list[Connector]:
        """获取指定用户的连接器列表"""
        stmt = (
            select(Connector)
            .where(Connector.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Connector.updated_at.desc())
        )
        
        if connector_type:
            stmt = stmt.where(Connector.type == connector_type)
        
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_user_and_name(
        self,
        user_id: UUID,
        name: str,
    ) -> Connector | None:
        """根据用户 ID 和名称获取连接器"""
        stmt = (
            select(Connector)
            .where(
                Connector.user_id == user_id,
                Connector.name == name,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def count_by_user(
        self,
        user_id: UUID,
        connector_type: str | None = None,
    ) -> int:
        """统计用户的连接器数量"""
        stmt = (
            select(func.count())
            .select_from(Connector)
            .where(Connector.user_id == user_id)
        )
        
        if connector_type:
            stmt = stmt.where(Connector.type == connector_type)
        
        result = await self._session.execute(stmt)
        return result.scalar_one()
    
    async def name_exists(
        self,
        user_id: UUID,
        name: str,
        exclude_id: UUID | None = None,
    ) -> bool:
        """检查名称是否已存在"""
        stmt = (
            select(func.count())
            .select_from(Connector)
            .where(
                Connector.user_id == user_id,
                Connector.name == name,
            )
        )
        
        if exclude_id:
            stmt = stmt.where(Connector.id != exclude_id)
        
        result = await self._session.execute(stmt)
        count = result.scalar_one()
        return count > 0
