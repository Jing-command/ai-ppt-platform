"""
幻灯片应用服务
处理幻灯片编辑和撤销/重做操作（Command 模式）
"""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.api.v1.schemas.presentation import SlideUpdate
from ai_ppt.application.services.presentation_service import (
    PresentationService,
)
from ai_ppt.domain.commands.command_history import CommandHistory
from ai_ppt.domain.commands.slide_commands import UpdateSlideCommand
from ai_ppt.infrastructure.repositories.slide import SlideRepository


class SlideServiceError(Exception):
    """幻灯片服务错误基类"""


class UndoRedoError(SlideServiceError):
    """撤销/重做错误"""


class SlideService:
    """
    幻灯片应用服务

    使用 Command 模式实现撤销/重做功能：
    1. 每次编辑操作创建一个 Command
    2. Command 保存执行前的状态
    3. undo() 方法恢复之前的状态
    4. redo() 方法重新执行命令

    使用示例:
        >>> service = SlideService(db_session)
        >>> await service.update_slide(
        ...     ppt_id, slide_id, updates, user_id
        ... )
        >>> result = await service.undo(ppt_id, slide_id)
        >>> result = await service.redo(ppt_id, slide_id)
    """

    # 每个 PPT 的命令历史（实际项目中应该持久化到数据库或 Redis）
    _command_histories: Dict[UUID, CommandHistory] = {}

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        初始化幻灯片服务

        Args:
            session: SQLAlchemy 异步会话
        """
        self._session = session
        self._slide_repo = SlideRepository(session)
        self._presentation_service = PresentationService(session)

    def _get_command_history(self, presentation_id: UUID) -> CommandHistory:
        """
        获取指定 PPT 的命令历史

        Args:
            presentation_id: PPT ID

        Returns:
            CommandHistory 实例
        """
        if presentation_id not in self._command_histories:
            self._command_histories[presentation_id] = CommandHistory(
                max_history=50
            )
        return self._command_histories[presentation_id]

    async def update_slide(
        self,
        presentation_id: UUID,
        slide_id: UUID,
        user_id: UUID,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        更新幻灯片（使用 Command 模式）

        Args:
            presentation_id: PPT ID
            slide_id: 幻灯片 ID
            user_id: 用户 ID
            updates: 更新内容

        Returns:
            更新后的幻灯片数据

        Raises:
            SlideNotFoundError: 幻灯片不存在
        """
        # 先更新幻灯片获取当前状态
        slide = await self._presentation_service.update_slide(
            presentation_id=presentation_id,
            slide_id=slide_id,
            user_id=user_id,
            data=SlideUpdate(**updates),
        )

        # 创建 Command 记录操作
        command = UpdateSlideCommand(
            slide_id=slide_id,
            updates=updates,
            slide_repository=self._slide_repo,
        )

        # 手动设置执行状态（因为上面已经更新了）
        command.mark_executed()

        # 添加到命令历史
        history = self._get_command_history(presentation_id)
        await history.execute(command)

        # 返回更新后的数据
        return {
            "id": str(slide.id),
            "title": slide.title,
            "content": slide.content,
            "notes": slide.notes,
            "order_index": slide.order_index,
            "version": slide.version,
        }

    async def undo(
        self,
        presentation_id: UUID,
        slide_id: UUID,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        撤销最后一次操作

        Args:
            presentation_id: PPT ID
            slide_id: 幻灯片 ID
            user_id: 用户 ID

        Returns:
            撤销结果

        Raises:
            UndoRedoError: 无可撤销的操作
        """
        # 检查权限
        await self._presentation_service.get_by_id_or_raise(
            presentation_id, user_id
        )

        history = self._get_command_history(presentation_id)

        if not history.can_undo:
            raise UndoRedoError("没有可撤销的操作")

        # 撤销最后一个命令
        command = await history.undo()

        if not command:
            raise UndoRedoError("撤销失败")

        # 获取撤销后的幻灯片状态
        slide = await self._slide_repo.get_by_id(slide_id)

        return {
            "success": True,
            "description": f"已撤销 {command.command_type}",
            "slide_id": str(slide_id),
            "state": slide.to_dict() if slide else None,
            "can_undo": history.can_undo,
            "can_redo": history.can_redo,
        }

    async def redo(
        self,
        presentation_id: UUID,
        slide_id: UUID,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        重做被撤销的操作

        Args:
            presentation_id: PPT ID
            slide_id: 幻灯片 ID
            user_id: 用户 ID

        Returns:
            重做结果

        Raises:
            UndoRedoError: 无可重做的操作
        """
        # 检查权限
        await self._presentation_service.get_by_id_or_raise(
            presentation_id, user_id
        )

        history = self._get_command_history(presentation_id)

        if not history.can_redo:
            raise UndoRedoError("没有可重做的操作")

        # 重做下一个命令
        command = await history.redo()

        if not command:
            raise UndoRedoError("重做失败")

        # 获取重做后的幻灯片状态
        slide = await self._slide_repo.get_by_id(slide_id)

        return {
            "success": True,
            "description": f"已重做 {command.command_type}",
            "slide_id": str(slide_id),
            "state": slide.to_dict() if slide else None,
            "can_undo": history.can_undo,
            "can_redo": history.can_redo,
        }

    def get_undo_redo_status(
        self,
        presentation_id: UUID,
    ) -> Dict[str, Any]:
        """
        获取撤销/重做状态

        Args:
            presentation_id: PPT ID

        Returns:
            撤销/重做状态
        """
        history = self._get_command_history(presentation_id)

        return {
            "can_undo": history.can_undo,
            "can_redo": history.can_redo,
            "undo_count": history.undo_count,
            "redo_count": history.redo_count,
        }

    async def clear_history(self, presentation_id: UUID) -> None:
        """
        清除命令历史

        Args:
            presentation_id: PPT ID
        """
        if presentation_id in self._command_histories:
            self._command_histories[presentation_id].clear()
