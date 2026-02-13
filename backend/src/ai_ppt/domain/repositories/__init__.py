"""
领域层仓储接口模块

定义所有仓储接口
"""

from ai_ppt.domain.repositories.base import (DuplicateEntityError,
                                             EntityNotFoundError, IRepository,
                                             RepositoryError)
from ai_ppt.domain.repositories.connector import IConnectorRepository
from ai_ppt.domain.repositories.outline import IOutlineRepository
from ai_ppt.domain.repositories.slide import ISlideRepository

__all__ = [
    # 基类
    "IRepository",
    "RepositoryError",
    "EntityNotFoundError",
    "DuplicateEntityError",
    # 具体接口
    "ISlideRepository",
    "IOutlineRepository",
    "IConnectorRepository",
]
