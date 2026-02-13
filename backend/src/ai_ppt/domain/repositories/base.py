"""
Repository 接口基类（泛型）
定义仓储模式的标准接口
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

# 领域模型类型变量
T = TypeVar("T")


class RepositoryError(Exception):
    """仓储层错误基类"""
    pass


class EntityNotFoundError(RepositoryError):
    """实体不存在错误"""
    def __init__(self, entity_type: str, entity_id: UUID | str) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id {entity_id} not found")


class DuplicateEntityError(RepositoryError):
    """重复实体错误"""
    pass


class IRepository(Generic[T], ABC):
    """
    泛型仓储接口基类
    
    所有具体仓储接口继承此类，定义通用的 CRUD 操作
    """
    
    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None:
        """根据 ID 获取实体"""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_id_or_raise(self, entity_id: UUID) -> T:
        """根据 ID 获取实体，不存在则抛出异常"""
        raise NotImplementedError
    
    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[T]:
        """分页获取所有实体"""
        raise NotImplementedError
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """创建实体"""
        raise NotImplementedError
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """更新实体"""
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """删除实体，返回是否成功"""
        raise NotImplementedError
    
    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        """检查实体是否存在"""
        raise NotImplementedError
