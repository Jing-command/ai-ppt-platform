"""
幻灯片相关 Command 实现
支持：创建、更新、删除、移动幻灯片
"""

from typing import Any, Dict, Optional
from uuid import UUID

from ai_ppt.domain.commands.base import Command


class CreateSlideCommand(Command):
    """
    创建幻灯片命令

    支持撤销（删除创建的幻灯片）
    """

    def __init__(
        self,
        presentation_id: UUID,
        title: str,
        layout_type: str = "title_content",
        content: Optional[Dict[str, Any]] = None,
        order_index: Optional[int] = None,
        slide_repository: Optional[Any] = None,
    ) -> None:
        super().__init__()
        self.presentation_id = presentation_id
        self.title = title
        self.layout_type = layout_type
        self.content = content or {}
        self.order_index = order_index
        self._slide_repository = slide_repository
        self._created_slide_id: Optional[UUID] = None

    @property
    def command_type(self) -> str:
        return "CreateSlideCommand"

    async def execute(self) -> None:
        """执行创建幻灯片"""
        if not self._slide_repository:
            raise ValueError("Slide repository is required")

        # 创建幻灯片
        from ai_ppt.domain.models.slide import Slide, SlideLayoutType

        slide = Slide(
                title=self.title,
                presentation_id=str(self.presentation_id),
                layout_type=SlideLayoutType(self.layout_type),
                content=self.content,
                order_index=self.order_index or 0,
            )

        created_slide = await self._slide_repository.create(slide)
        self._created_slide_id = created_slide.id
        self.mark_executed()

    async def undo(self) -> None:
        """撤销：删除创建的幻灯片"""
        if not self._slide_repository:
            raise ValueError("Slide repository is required")

        if self._created_slide_id:
            await self._slide_repository.delete(self._created_slide_id)
            self.mark_undone()

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "type": self.command_type,
            "id": str(self.id),
            "presentation_id": str(self.presentation_id),
            "title": self.title,
            "layout_type": self.layout_type,
            "content": self.content,
            "order_index": self.order_index,
            "created_slide_id": (
                str(self._created_slide_id) if self._created_slide_id else None
            ),
            "executed_at": (
                self.executed_at.isoformat() if self.executed_at else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateSlideCommand":
        """从字典反序列化"""
        cmd = cls(
            presentation_id=UUID(data["presentation_id"]),
            title=data["title"],
            layout_type=data["layout_type"],
            content=data.get("content", {}),
            order_index=data.get("order_index"),
        )
        cmd._id = UUID(data["id"])
        if data.get("created_slide_id"):
            cmd._created_slide_id = UUID(data["created_slide_id"])
        return cmd


class UpdateSlideCommand(Command):
    """
    更新幻灯片命令

    支持撤销（恢复之前的内容）
    """

    def __init__(
        self,
        slide_id: UUID,
        updates: Dict[str, Any],
        slide_repository: Optional[Any] = None,
    ) -> None:
        super().__init__()
        self.slide_id = slide_id
        self.updates = updates
        self._slide_repository = slide_repository
        self._previous_data: Optional[Dict[str, Any]] = None

    @property
    def command_type(self) -> str:
        return "UpdateSlideCommand"

    async def execute(self) -> None:
        """执行更新幻灯片"""
        if not self._slide_repository:
            raise ValueError("Slide repository is required")

        # 获取当前状态
        slide = await self._slide_repository.get_by_id(self.slide_id)
        if not slide:
            raise ValueError(f"Slide {self.slide_id} not found")

        # 保存之前的状态
        self._previous_data = {
            "title": slide.title,
            "subtitle": slide.subtitle,
            "layout_type": slide.layout_type,
            "content": slide.content.copy() if slide.content else {},
            "notes": slide.notes,
            "background_color": slide.background_color,
            "text_color": slide.text_color,
            "font_family": slide.font_family,
        }

        # 应用更新
        if "title" in self.updates:
            slide.title = self.updates["title"]
        if "subtitle" in self.updates:
            slide.subtitle = self.updates["subtitle"]
        if "layout_type" in self.updates:
            slide.layout_type = self.updates["layout_type"]
        if "content" in self.updates:
            slide.update_content(self.updates["content"])
        if "notes" in self.updates:
            slide.notes = self.updates["notes"]
        if "background_color" in self.updates:
            slide.background_color = self.updates["background_color"]
        if "text_color" in self.updates:
            slide.text_color = self.updates["text_color"]
        if "font_family" in self.updates:
            slide.font_family = self.updates["font_family"]

        await self._slide_repository.update(slide)
        self.mark_executed()

    async def undo(self) -> None:
        """撤销：恢复之前的内容"""
        if not self._slide_repository:
            raise ValueError("Slide repository is required")

        if not self._previous_data:
            raise ValueError("No previous data to restore")

        slide = await self._slide_repository.get_by_id(self.slide_id)
        if not slide:
            raise ValueError(f"Slide {self.slide_id} not found")

        # 恢复之前的状态
        from ai_ppt.domain.models.slide import SlideLayoutType

        slide.title = self._previous_data["title"]
        slide.subtitle = self._previous_data["subtitle"]
        slide.layout_type = SlideLayoutType(self._previous_data["layout_type"])
        slide.content = self._previous_data["content"]
        slide.notes = self._previous_data["notes"]
        slide.background_color = self._previous_data["background_color"]
        slide.text_color = self._previous_data["text_color"]
        slide.font_family = self._previous_data["font_family"]

        await self._slide_repository.update(slide)
        self.mark_undone()

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "type": self.command_type,
            "id": str(self.id),
            "slide_id": str(self.slide_id),
            "updates": self.updates,
            "previous_data": self._previous_data,
            "executed_at": (
                self.executed_at.isoformat() if self.executed_at else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateSlideCommand":
        """从字典反序列化"""
        cmd = cls(
            slide_id=UUID(data["slide_id"]),
            updates=data["updates"],
        )
        cmd._id = UUID(data["id"])
        cmd._previous_data = data.get("previous_data")
        return cmd


class DeleteSlideCommand(Command):
    """
    删除幻灯片命令

    支持撤销（恢复删除的幻灯片）
    """

    def __init__(
        self,
        slide_id: UUID,
        slide_repository: Optional[Any] = None,
    ) -> None:
        super().__init__()
        self.slide_id = slide_id
        self._slide_repository = slide_repository
        self._deleted_data: Optional[Dict[str, Any]] = None

    @property
    def command_type(self) -> str:
        return "DeleteSlideCommand"

    async def execute(self) -> None:
        """执行删除幻灯片"""
        if not self._slide_repository:
            raise ValueError("Slide repository is required")

        # 获取当前状态
        slide = await self._slide_repository.get_by_id(self.slide_id)
        if not slide:
            raise ValueError(f"Slide {self.slide_id} not found")

        # 保存完整状态用于恢复
        self._deleted_data = {
            "id": slide.id,
            "presentation_id": slide.presentation_id,
            "title": slide.title,
            "subtitle": slide.subtitle,
            "layout_type": slide.layout_type,
            "content": slide.content.copy() if slide.content else {},
            "notes": slide.notes,
            "background_color": slide.background_color,
            "text_color": slide.text_color,
            "font_family": slide.font_family,
            "order_index": slide.order_index,
            "version": slide.version,
        }

        # 删除幻灯片
        await self._slide_repository.delete(self.slide_id)
        self.mark_executed()

    async def undo(self) -> None:
        """撤销：恢复删除的幻灯片"""
        if not self._slide_repository:
            raise ValueError("Slide repository is required")

        if not self._deleted_data:
            raise ValueError("No deleted data to restore")

        # 恢复幻灯片
        from ai_ppt.domain.models.slide import Slide, SlideLayoutType

        slide = Slide(
            title=self._deleted_data["title"],
            presentation_id=self._deleted_data["presentation_id"],
            layout_type=SlideLayoutType(self._deleted_data["layout_type"]),
            order_index=self._deleted_data["order_index"],
            content=self._deleted_data["content"],
        )
        slide.id = self._deleted_data["id"]
        slide.subtitle = self._deleted_data["subtitle"]
        slide.notes = self._deleted_data["notes"]
        slide.background_color = self._deleted_data["background_color"]
        slide.text_color = self._deleted_data["text_color"]
        slide.font_family = self._deleted_data["font_family"]
        slide.version = self._deleted_data["version"]

        await self._slide_repository.create(slide)
        self.mark_undone()

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "type": self.command_type,
            "id": str(self.id),
            "slide_id": str(self.slide_id),
            "deleted_data": self._deleted_data,
            "executed_at": (
                self.executed_at.isoformat() if self.executed_at else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteSlideCommand":
        """从字典反序列化"""
        cmd = cls(slide_id=UUID(data["slide_id"]))
        cmd._id = UUID(data["id"])
        cmd._deleted_data = data.get("deleted_data")
        return cmd


class MoveSlideCommand(Command):
    """
    移动幻灯片命令

    支持撤销（恢复原来的位置）
    """

    def __init__(
        self,
        slide_id: UUID,
        new_order: int,
        slide_repository: Optional[Any] = None,
    ) -> None:
        super().__init__()
        self.slide_id = slide_id
        self.new_order = new_order
        self._slide_repository = slide_repository
        self._previous_order: Optional[int] = None

    @property
    def command_type(self) -> str:
        return "MoveSlideCommand"

    async def execute(self) -> None:
        """执行移动幻灯片"""
        if not self._slide_repository:
            raise ValueError("Slide repository is required")

        # 获取当前状态
        slide = await self._slide_repository.get_by_id(self.slide_id)
        if not slide:
            raise ValueError(f"Slide {self.slide_id} not found")

        # 保存之前的顺序
        self._previous_order = slide.order_index

        # 更新顺序
        slide.move_to(self.new_order)
        await self._slide_repository.update(slide)

        # 重新排序其他幻灯片
        await self._slide_repository.reorder_slides(
            slide.presentation_id, {self.slide_id: self.new_order}
        )

        self.mark_executed()

    async def undo(self) -> None:
        """撤销：恢复原来的位置"""
        if not self._slide_repository:
            raise ValueError("Slide repository is required")

        if self._previous_order is None:
            raise ValueError("No previous order to restore")

        slide = await self._slide_repository.get_by_id(self.slide_id)
        if not slide:
            raise ValueError(f"Slide {self.slide_id} not found")

        # 恢复原来的顺序
        slide.move_to(self._previous_order)
        await self._slide_repository.update(slide)

        self.mark_undone()

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "type": self.command_type,
            "id": str(self.id),
            "slide_id": str(self.slide_id),
            "new_order": self.new_order,
            "previous_order": self._previous_order,
            "executed_at": (
                self.executed_at.isoformat() if self.executed_at else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MoveSlideCommand":
        """从字典反序列化"""
        cmd = cls(
            slide_id=UUID(data["slide_id"]),
            new_order=data["new_order"],
        )
        cmd._id = UUID(data["id"])
        cmd._previous_order = data.get("previous_order")
        return cmd
