"""
Command 历史管理器
实现撤销/重做功能的核心逻辑
"""
from collections import deque
from typing import Any, Dict, List, Optional
from uuid import UUID

from ai_ppt.domain.commands.base import Command, CommandExecutionError, CommandUndoError


class CommandHistory:
    """
    命令历史管理器
    
    管理命令的执行历史，支持撤销（undo）和重做（redo）。
    限制历史记录数量，防止内存无限增长。
    
    使用示例:
        >>> history = CommandHistory(max_history=50)
        >>> await history.execute(CreateSlideCommand(...))
        >>> await history.execute(UpdateSlideCommand(...))
        >>> await history.undo()  # 撤销最后一个命令
        >>> await history.redo()  # 重做被撤销的命令
        >>> history.can_undo  # 是否可以撤销
        >>> history.can_redo  # 是否可以重做
    """
    
    DEFAULT_MAX_HISTORY = 50
    
    def __init__(self, max_history: int = DEFAULT_MAX_HISTORY) -> None:
        """
        初始化命令历史管理器
        
        Args:
            max_history: 最大历史记录数量，默认 50 条
        """
        self._max_history = max(1, max_history)
        self._history: deque[Command] = deque(maxlen=self._max_history)
        self._current_index: int = -1  # -1 表示没有命令
    
    @property
    def max_history(self) -> int:
        """最大历史记录数量"""
        return self._max_history
    
    @property
    def can_undo(self) -> bool:
        """
        是否可以撤销
        
        Returns:
            如果当前有已执行的命令可以撤销，返回 True
        """
        return self._current_index >= 0
    
    @property
    def can_redo(self) -> bool:
        """
        是否可以重做
        
        Returns:
            如果有被撤销的命令可以重做，返回 True
        """
        return self._current_index < len(self._history) - 1
    
    @property
    def current_position(self) -> int:
        """当前位置索引（-1 表示在起始位置）"""
        return self._current_index
    
    @property
    def history_size(self) -> int:
        """当前历史记录数量"""
        return len(self._history)
    
    @property
    def undo_count(self) -> int:
        """可以撤销的命令数量"""
        return self._current_index + 1
    
    @property
    def redo_count(self) -> int:
        """可以重做的命令数量"""
        return len(self._history) - self._current_index - 1
    
    def get_command_at(self, index: int) -> Optional[Command]:
        """
        获取指定位置的命令
        
        Args:
            index: 命令索引
            
        Returns:
            命令实例，如果索引无效返回 None
        """
        if 0 <= index < len(self._history):
            return self._history[index]
        return None
    
    def get_current_command(self) -> Optional[Command]:
        """
        获取当前位置的命令
        
        Returns:
            当前命令，如果没有返回 None
        """
        return self.get_command_at(self._current_index)
    
    async def execute(self, command: Command) -> None:
        """
        执行新命令
        
        执行命令并将其添加到历史记录中。
        如果之前有被撤销的命令，会被清除。
        
        Args:
            command: 要执行的命令
            
        Raises:
            CommandExecutionError: 命令执行失败
        """
        try:
            await command.execute()
        except Exception as e:
            raise CommandExecutionError(
                f"Command execution failed: {e}",
                command=command
            ) from e
        
        # 如果有被撤销的命令，清除它们
        if self._current_index < len(self._history) - 1:
            # 只保留到当前索引的历史
            while len(self._history) > self._current_index + 1:
                self._history.pop()
        
        # 添加新命令
        self._history.append(command)
        self._current_index = len(self._history) - 1
        
        # 如果超出最大限制，deque 会自动处理
        # 但我们需要调整 current_index
        if len(self._history) > self._max_history:
            self._current_index = min(self._current_index, self._max_history - 1)
    
    async def undo(self) -> Optional[Command]:
        """
        撤销最后一个命令
        
        Returns:
            被撤销的命令，如果没有可撤销的命令返回 None
            
        Raises:
            CommandUndoError: 命令撤销失败
        """
        if not self.can_undo:
            return None
        
        command = self._history[self._current_index]
        
        try:
            await command.undo()
        except Exception as e:
            raise CommandUndoError(
                f"Command undo failed: {e}",
                command=command
            ) from e
        
        self._current_index -= 1
        return command
    
    async def redo(self) -> Optional[Command]:
        """
        重做被撤销的命令
        
        Returns:
            被重做的命令，如果没有可重做的命令返回 None
            
        Raises:
            CommandExecutionError: 命令重做失败
        """
        if not self.can_redo:
            return None
        
        next_index = self._current_index + 1
        command = self._history[next_index]
        
        try:
            # 重做就是再次执行命令
            await command.execute()
        except Exception as e:
            raise CommandExecutionError(
                f"Command redo failed: {e}",
                command=command
            ) from e
        
        self._current_index = next_index
        return command
    
    async def undo_many(self, count: int) -> List[Command]:
        """
        撤销多个命令
        
        Args:
            count: 要撤销的命令数量
            
        Returns:
            被撤销的命令列表
        """
        undone_commands: List[Command] = []
        
        for _ in range(min(count, self.undo_count)):
            command = await self.undo()
            if command:
                undone_commands.append(command)
        
        return undone_commands
    
    async def redo_many(self, count: int) -> List[Command]:
        """
        重做多个命令
        
        Args:
            count: 要重做的命令数量
            
        Returns:
            被重做的命令列表
        """
        redone_commands: List[Command] = []
        
        for _ in range(min(count, self.redo_count)):
            command = await self.redo()
            if command:
                redone_commands.append(command)
        
        return redone_commands
    
    def clear(self) -> None:
        """清除所有历史记录"""
        self._history.clear()
        self._current_index = -1
    
    def get_history_summary(self) -> List[Dict[str, Any]]:
        """
        获取历史记录摘要
        
        Returns:
            命令摘要列表，用于 UI 显示
        """
        summary = []
        for i, command in enumerate(self._history):
            summary.append({
                "index": i,
                "type": command.command_type,
                "id": str(command.id),
                "is_current": i == self._current_index,
                "can_undo": i <= self._current_index,
                "executed_at": command.executed_at.isoformat() if command.executed_at else None,
                "undone_at": command.undone_at.isoformat() if command.undone_at else None,
            })
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """
        序列化历史记录
        
        Returns:
            包含历史数据的字典
        """
        return {
            "max_history": self._max_history,
            "current_index": self._current_index,
            "commands": [
                cmd.to_dict() for cmd in self._history
            ],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], command_factory: Any = None) -> "CommandHistory":
        """
        从字典反序列化历史记录
        
        Args:
            data: 包含历史数据的字典
            command_factory: 命令工厂，用于从字典创建命令实例
            
        Returns:
            恢复的 CommandHistory 实例
        """
        history = cls(max_history=data.get("max_history", cls.DEFAULT_MAX_HISTORY))
        history._current_index = data.get("current_index", -1)
        
        if command_factory:
            for cmd_data in data.get("commands", []):
                try:
                    command = command_factory.create(cmd_data)
                    history._history.append(command)
                except ValueError:
                    # 跳过无法识别的命令
                    continue
        
        return history


class PresentationCommandHistory:
    """
    演示文稿级别的命令历史管理器
    
    每个演示文稿有自己的命令历史，便于管理和持久化。
    """
    
    def __init__(self, presentation_id: UUID, max_history: int = 50) -> None:
        self.presentation_id = presentation_id
        self._history = CommandHistory(max_history=max_history)
    
    @property
    def history(self) -> CommandHistory:
        """获取命令历史管理器"""
        return self._history
    
    @property
    def can_undo(self) -> bool:
        return self._history.can_undo
    
    @property
    def can_redo(self) -> bool:
        return self._history.can_redo
    
    async def execute(self, command: Command) -> None:
        """执行命令"""
        await self._history.execute(command)
    
    async def undo(self) -> Optional[Command]:
        """撤销"""
        return await self._history.undo()
    
    async def redo(self) -> Optional[Command]:
        """重做"""
        return await self._history.redo()
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化"""
        return {
            "presentation_id": str(self.presentation_id),
            "history": self._history.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], command_factory: Any = None) -> "PresentationCommandHistory":
        """反序列化"""
        history_data = data.get("history", {})
        instance = cls(
            presentation_id=UUID(data["presentation_id"]),
            max_history=history_data.get("max_history", 50),
        )
        instance._history = CommandHistory.from_dict(history_data, command_factory)
        return instance
