"""
Connector（连接器）领域模型
存储数据源连接器配置和元数据
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any, Optional
from uuid import UUID

# 根据数据库类型选择 JSON 类型
from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ai_ppt.domain.models.base import (Base, DateTimeAuto, DateTimeUpdated,
                                       Str255, TextOptional, UUIDPk)


class ConnectorStatus(str, PyEnum):
    """连接器状态枚举"""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    TESTING = "testing"


class Connector(Base):
    """
    连接器实体

    存储数据源连接器配置，支持多种数据源类型（MySQL、PostgreSQL、Salesforce 等）
    """

    __tablename__ = "connectors"

    # 主键
    id: Mapped[UUIDPk]

    # 基础字段
    name: Mapped[Str255]
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="连接器类型: mysql, postgresql, mongodb, csv, api, salesforce",
    )
    description: Mapped[TextOptional]

    # 连接配置（JSON格式存储）
    config: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        comment="连接配置参数（主机、端口、认证信息等）",
    )

    # 状态
    status: Mapped[ConnectorStatus] = mapped_column(
        String(20),
        default=ConnectorStatus.DISCONNECTED,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment="是否激活",
    )

    # 外键 - 所属用户
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 时间戳
    created_at: Mapped[DateTimeAuto]
    updated_at: Mapped[DateTimeUpdated]
    last_tested_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="上次测试连接时间",
    )

    def __init__(
        self,
        name: str,
        type: str,
        user_id: UUID,
        config: dict[str, Any] | None = None,
        description: Optional[str] = None,
    ) -> None:
        self.name = name
        self.type = type
        self.user_id = user_id
        self.config = config or {}
        self.description = description
        self.status = ConnectorStatus.DISCONNECTED
        self.is_active = True

    def update_status(self, status: ConnectorStatus) -> None:
        """更新连接器状态"""
        self.status = status

    def mark_as_tested(self, success: bool) -> None:
        """标记为已测试"""
        self.last_tested_at = datetime.utcnow()
        self.status = ConnectorStatus.CONNECTED if success else ConnectorStatus.ERROR

    def update_config(self, new_config: dict[str, Any]) -> None:
        """更新连接配置"""
        self.config = {**self.config, **new_config}

    def deactivate(self) -> None:
        """停用连接器"""
        self.is_active = False

    def activate(self) -> None:
        """激活连接器"""
        self.is_active = True
