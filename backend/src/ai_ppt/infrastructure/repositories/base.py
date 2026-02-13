"""
Repository 实现基类（泛型）
使用 SQLAlchemy 2.0 实现仓储接口
"""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.domain.models.base import Base
from ai_ppt.domain.repositories.base import EntityNotFoundError, IRepository

# 模型类型变量，约束为 Base 的子类
ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(IRepository[ModelT], Generic[ModelT]):
    """
    泛型仓储基类实现

    提供通用的 CRUD 操作，具体仓储类继承此类
    """

    def __init__(self, session: AsyncSession, model_class: type[ModelT]) -> None:
        """
        初始化仓储

        Args:
            session: SQLAlchemy 异步会话
            model_class: 模型类
        """
        self._session = session
        self._model_class = model_class

    async def get_by_id(self, entity_id: UUID) -> ModelT | None:
        """根据 ID 获取实体"""
        stmt = select(self._model_class).where(self._model_class.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, entity_id: UUID) -> ModelT:
        """根据 ID 获取实体，不存在则抛出异常"""
        entity = await self.get_by_id(entity_id)
        if entity is None:
            raise EntityNotFoundError(
                entity_type=self._model_class.__name__,
                entity_id=entity_id,
            )
        return entity

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelT]:
        """分页获取所有实体"""
        stmt = select(self._model_class).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: ModelT) -> ModelT:
        """创建实体"""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: ModelT) -> ModelT:
        """更新实体"""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """删除实体"""
        entity = await self.get_by_id(entity_id)
        if entity is None:
            return False
        await self._session.delete(entity)
        await self._session.flush()
        return True

    async def exists(self, entity_id: UUID) -> bool:
        """检查实体是否存在"""
        entity = await self.get_by_id(entity_id)
        return entity is not None
