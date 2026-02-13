"""
Outline（大纲）领域模型 - 更新版
存储 AI 生成的大纲结构和元数据，匹配 API Contract v1.0
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_ppt.domain.models.base import Base

if TYPE_CHECKING:
    from ai_ppt.domain.models.presentation import Presentation


class OutlineStatus(str, PyEnum):
    """大纲状态枚举 - 匹配 API Contract"""

    DRAFT = "draft"  # 草稿
    GENERATING = "generating"  # 生成中
    COMPLETED = "completed"  # 已完成
    ARCHIVED = "archived"  # 已归档


class OutlineBackgroundType(str, PyEnum):
    """背景类型枚举"""

    AI = "ai"  # AI生成
    UPLOAD = "upload"  # 上传图片
    SOLID = "solid"  # 纯色


class OutlinePageType(str, PyEnum):
    """页面类型枚举"""

    TITLE = "title"  # 标题页
    CONTENT = "content"  # 内容页
    SECTION = "section"  # 章节页
    CHART = "chart"  # 图表页
    CONCLUSION = "conclusion"  # 结论页


class OutlinePage:
    """
    大纲页面（数据类，存储在 JSON 中）

    对应 API Contract 中的 OutlineSection，但使用 "pages" 字段名
    """

    def __init__(
        self,
        id: str,
        page_number: int,
        title: str,
        content: Optional[str] = None,
        page_type: str = "content",
        layout: Optional[str] = None,
        notes: Optional[str] = None,
        image_prompt: Optional[str] = None,
    ) -> None:
        self.id = id
        self.page_number = page_number
        self.title = title
        self.content = content
        self.page_type = page_type
        self.layout = layout
        self.notes = notes
        self.image_prompt = image_prompt

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "pageNumber": self.page_number,
            "title": self.title,
            "content": self.content,
            "pageType": self.page_type,
            "layout": self.layout,
            "notes": self.notes,
            "imagePrompt": self.image_prompt,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OutlinePage":
        """从字典创建"""
        return cls(
            id=data.get("id", str(uuid4())),
            page_number=data.get("pageNumber", data.get("page_number", 1)),
            title=data.get("title", ""),
            content=data.get("content"),
            page_type=data.get("pageType", data.get("page_type", "content")),
            layout=data.get("layout"),
            notes=data.get("notes"),
            image_prompt=data.get("imagePrompt", data.get("image_prompt")),
        )


class OutlineBackground:
    """
    大纲背景设置（数据类，存储在 JSON 中）
    """

    def __init__(
        self,
        type: str = "ai",
        prompt: Optional[str] = None,
        url: Optional[str] = None,
        color: Optional[str] = None,
        opacity: float = 1.0,
        blur: float = 0.0,
    ) -> None:
        self.type = type
        self.prompt = prompt
        self.url = url
        self.color = color
        self.opacity = opacity
        self.blur = blur

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.type,
            "prompt": self.prompt,
            "url": self.url,
            "color": self.color,
            "opacity": self.opacity,
            "blur": self.blur,
        }

    @classmethod
    def from_dict(cls, data: Optional[dict[str, Any]]) -> Optional["OutlineBackground"]:
        """从字典创建"""
        if not data:
            return None
        return cls(
            type=data.get("type", "ai"),
            prompt=data.get("prompt"),
            url=data.get("url"),
            color=data.get("color"),
            opacity=data.get("opacity", 1.0),
            blur=data.get("blur", 0.0),
        )


class Outline(Base):
    """
    大纲实体 - 更新版，匹配 API Contract v1.0

    存储 AI 生成的演示文稿大纲，可以被多个 Presentation 使用
    """

    __tablename__ = "outlines"
    __allow_unmapped__ = True  # 允许非 Mapped 注解

    # 主键
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # 外键
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 基础字段
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 页面数据（JSON格式存储页面列表）
    pages: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        comment="页面列表（JSON格式）",
    )

    # 背景设置（JSON格式）
    background: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="背景设置（JSON格式）",
    )

    # 统计信息
    total_slides: Mapped[int] = mapped_column(default=0, comment="总页数")

    # 状态
    status: Mapped[str] = mapped_column(
        String(50),
        default=OutlineStatus.DRAFT.value,
        comment="状态: draft, generating, completed, archived",
    )

    # AI 生成信息
    ai_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="生成大纲使用的 AI Prompt",
    )
    ai_parameters: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="AI 生成参数",
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # 关系
    presentations: Mapped[list["Presentation"]] = relationship(
        "Presentation",
        back_populates="outline",
        lazy="selectin",
    )

    # 非持久化属性，用于缓存页面列表（实例变量，在__init__中初始化）
    _pages_cache: Optional[list[OutlinePage]]
    _background_cache: Optional[OutlineBackground]

    def __init__(
        self,
        title: str,
        user_id: UUID,
        description: Optional[str] = None,
        pages: Optional[list[dict[str, Any]]] = None,
        background: Optional[dict[str, Any]] = None,
        total_slides: int = 0,
        status: Optional[str] = None,
        ai_prompt: Optional[str] = None,
        ai_parameters: Optional[dict[str, Any]] = None,
    ) -> None:
        self.title = title
        self.user_id = user_id
        self.description = description
        self.pages = pages or []
        self.background = background
        self.total_slides = total_slides
        self.status = status or OutlineStatus.DRAFT.value
        self.ai_prompt = ai_prompt
        self.ai_parameters = ai_parameters
        self._pages_cache = None
        self._background_cache = None

    def get_pages(self) -> list[OutlinePage]:
        """获取页面列表（从 pages JSON 解析）"""
        if self._pages_cache is None:
            self._pages_cache = [OutlinePage.from_dict(p) for p in (self.pages or [])]
        return self._pages_cache

    def set_pages(self, pages: list[OutlinePage]) -> None:
        """设置页面列表"""
        self._pages_cache = pages
        self.pages = [p.to_dict() for p in pages]
        self.total_slides = len(pages)

    def get_background(self) -> Optional[OutlineBackground]:
        """获取背景设置"""
        if self._background_cache is None and self.background:
            self._background_cache = OutlineBackground.from_dict(self.background)
        return self._background_cache

    def set_background(self, background: Optional[OutlineBackground]) -> None:
        """设置背景"""
        self._background_cache = background
        self.background = background.to_dict() if background else None

    def add_page(self, page: OutlinePage) -> None:
        """添加页面"""
        pages = self.get_pages()
        pages.append(page)
        self.set_pages(pages)

    def mark_as_generating(self) -> None:
        """标记为生成中"""
        self.status = OutlineStatus.GENERATING.value

    def mark_as_completed(self) -> None:
        """标记为已完成"""
        self.status = OutlineStatus.COMPLETED.value
        self.generated_at = datetime.utcnow()

    def mark_as_archived(self) -> None:
        """标记为已归档"""
        self.status = OutlineStatus.ARCHIVED.value

    def update_pages_from_dict(self, pages_data: list[dict[str, Any]]) -> None:
        """从字典列表更新页面"""
        pages = [OutlinePage.from_dict(p) for p in pages_data]
        self.set_pages(pages)
