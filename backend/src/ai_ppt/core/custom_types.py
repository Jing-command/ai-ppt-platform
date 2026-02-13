"""
自定义 SQLAlchemy 类型
"""

import uuid
from typing import Any, Optional

from sqlalchemy import Dialect, String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import JSON


class GUID(TypeDecorator):
    """
    跨平台的 UUID 类型

    在 PostgreSQL 中使用原生 UUID 类型
    在其他数据库中使用 String(36)
    """

    impl = String
    cache_ok = True

    def __init__(self, length: int = 36) -> None:
        super().__init__(length=length)

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value: Optional[uuid.UUID], dialect: Dialect) -> Optional[str]:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value: Optional[str], dialect: Dialect) -> Optional[uuid.UUID]:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class JSONType(TypeDecorator):
    """
    跨平台的 JSON 类型

    使用 SQLAlchemy 的原生 JSON 类型
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        return dialect.type_descriptor(JSON())
