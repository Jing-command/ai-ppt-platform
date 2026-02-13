"""
Presentation（演示文稿）领域模型
"""

from __future__ import annotations

from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_ppt.domain.models.base import (
    Base,
    BoolTrue,
    DateTimeAuto,
    DateTimeUpdated,
    Str255,
    TextOptional,
    UUIDPk,
)

if TYPE_CHECKING:
    from ai_ppt.domain.models.outline import Outline
    from ai_ppt.domain.models.slide import Slide


class PresentationStatus(str, PyEnum):
    """演示文稿状态枚举"""

    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Presentation(Base):
    """
    演示文稿实体

    一个 Presentation 包含多个 Slide，可以关联一个 Outline
    """

    __tablename__ = "presentations"

    # 主键
    id: Mapped[UUIDPk]

    # 基础字段
    title: Mapped[Str255]
    description: Mapped[TextOptional]
    status: Mapped[PresentationStatus] = mapped_column(
        Enum(PresentationStatus, name="presentation_status"),
        default=PresentationStatus.DRAFT,
    )

    # 模板和样式
    theme: Mapped[str] = mapped_column(String(50), default="default")
    color_scheme: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # 元数据
    is_public: Mapped[BoolTrue]
    view_count: Mapped[int] = mapped_column(default=0)

    # 外键
    outline_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("outlines.id", ondelete="SET NULL"),
        nullable=True,
    )
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 时间戳
    created_at: Mapped[DateTimeAuto]
    updated_at: Mapped[DateTimeUpdated]

    # 关系
    outline: Mapped[Optional["Outline"]] = relationship(
        "Outline",
        back_populates="presentations",
        lazy="selectin",
    )
    slides: Mapped[List["Slide"]] = relationship(
        "Slide",
        back_populates="presentation",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="Slide.order_index",
    )

    def __init__(
        self,
        title: str,
        owner_id: UUID,
        description: Optional[str] = None,
        theme: str = "default",
    ) -> None:
        self.title = title
        self.owner_id = owner_id
        self.description = description
        self.theme = theme

    def update_title(self, new_title: str) -> None:
        """更新标题（领域方法）"""
        if not new_title or len(new_title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        self.title = new_title.strip()

    def publish(self) -> None:
        """发布演示文稿"""
        if self.status == PresentationStatus.ARCHIVED:
            raise ValueError("Cannot publish archived presentation")
        self.status = PresentationStatus.PUBLISHED

    def archive(self) -> None:
        """归档演示文稿"""
        self.status = PresentationStatus.ARCHIVED

    def increment_view(self) -> None:
        """增加浏览次数"""
        self.view_count += 1
