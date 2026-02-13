"""
SQLAlchemy 2.0 基础模型配置
使用现代 Mapped[] 语法和类型注解
"""

from datetime import datetime
from typing import Annotated, Any, ClassVar, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, MetaData, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, mapped_column, registry

# 命名约定用于 Alembic 自动迁移
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# 类型别名 - 常用字段类型
IntPk = Annotated[int, mapped_column(primary_key=True)]
UUIDPk = Annotated[UUID, mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)]
Str255 = Annotated[str, mapped_column(String(255), nullable=False)]
Str50 = Annotated[str, mapped_column(String(50), nullable=False)]
StrOptional = Annotated[Optional[str], mapped_column(nullable=True)]
Text = Annotated[str, mapped_column(nullable=False)]
TextOptional = Annotated[Optional[str], mapped_column(nullable=True)]
BoolFalse = Annotated[bool, mapped_column(default=False)]
BoolTrue = Annotated[bool, mapped_column(default=True)]
DateTimeAuto = Annotated[
    datetime, mapped_column(DateTime(timezone=True), server_default=func.now())
]
DateTimeUpdated = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
]


class Base(DeclarativeBase):
    """
    SQLAlchemy 基础模型类

    所有领域模型继承此类，自动获得：
    - 统一的元数据和命名约定
    - 类型注册表
    """

    registry: ClassVar[registry] = registry()
    metadata: ClassVar[MetaData] = MetaData(naming_convention=convention)

    def __repr__(self) -> str:
        """统一的字符串表示"""
        columns = [f"{col.key}={getattr(self, col.key)}" for col in self.__table__.columns]
        return f"<{self.__class__.__name__}({', '.join(columns)})>"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}
