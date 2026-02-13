"""
Slide（幻灯片）领域模型
支持单页编辑和版本控制
"""
from __future__ import annotations

from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_ppt.domain.models.base import (
    Base,
    UUIDPk,
    Str255,
    TextOptional,
    DateTimeAuto,
    DateTimeUpdated,
)

if TYPE_CHECKING:
    from ai_ppt.domain.models.presentation import Presentation


class SlideLayoutType(str, PyEnum):
    """幻灯片布局类型枚举"""
    TITLE_ONLY = "title_only"
    TITLE_CONTENT = "title_content"
    TWO_COLUMN = "two_column"
    THREE_COLUMN = "three_column"
    COMPARISON = "comparison"
    IMAGE_LEFT = "image_left"
    IMAGE_RIGHT = "image_right"
    FULL_IMAGE = "full_image"
    BLANK = "blank"


class Slide(Base):
    """
    幻灯片实体
    
    每个 Slide 属于一个 Presentation，支持独立的版本控制
    """
    __tablename__ = "slides"
    
    # 索引
    __table_args__ = (
        Index("ix_slides_presentation_order", "presentation_id", "order_index"),
    )
    
    # 主键
    id: Mapped[UUIDPk]
    
    # 基础字段
    title: Mapped[Str255]
    subtitle: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 布局和内容
    layout_type: Mapped[SlideLayoutType] = mapped_column(
        String(50),
        default=SlideLayoutType.TITLE_CONTENT,
    )
    content: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        comment="幻灯片内容（JSON格式）",
    )
    notes: Mapped[TextOptional] = mapped_column(
        comment="演讲者备注"
    )
    
    # 排序和版本控制
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment="幻灯片版本号",
    )
    
    # 外键
    presentation_id: Mapped[UUID] = mapped_column(
        ForeignKey("presentations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # 时间戳
    created_at: Mapped[DateTimeAuto]
    updated_at: Mapped[DateTimeUpdated]
    
    # 关系
    presentation: Mapped["Presentation"] = relationship(
        "Presentation",
        back_populates="slides",
    )
    
    def __init__(
        self,
        title: str,
        presentation_id: UUID,
        layout_type: SlideLayoutType = SlideLayoutType.TITLE_CONTENT,
        order_index: int = 0,
        content: Optional[dict[str, Any]] = None,
        subtitle: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        self.title = title
        self.presentation_id = presentation_id
        self.layout_type = layout_type
        self.order_index = order_index
        self.content = content or {}
        self.subtitle = subtitle
        self.notes = notes
    
    def update_content(self, new_content: dict[str, Any]) -> None:
        """
        更新内容并增加版本号
        
        Args:
            new_content: 新的内容字典
        """
        self.content = new_content
        self.version += 1
    
    def move_to(self, new_order: int) -> None:
        """
        移动到新位置
        
        Args:
            new_order: 新的排序索引
        """
        self.order_index = new_order
    
    def clone(self) -> Slide:
        """
        创建副本（用于复制幻灯片）
        
        Returns:
            新的 Slide 实例，内容相同但 ID 不同
        """
        return Slide(
            title=f"{self.title} (Copy)",
            presentation_id=self.presentation_id,
            layout_type=self.layout_type,
            content=self.content.copy(),
            notes=self.notes,
        )
