"""
Command 模式模块
实现撤销/重做功能
"""

from ai_ppt.domain.commands.base import (Command, CommandException,
                                         CommandExecutionError,
                                         CommandUndoError)
from ai_ppt.domain.commands.command_history import (CommandHistory,
                                                    PresentationCommandHistory)
from ai_ppt.domain.commands.slide_commands import (CreateSlideCommand,
                                                   DeleteSlideCommand,
                                                   MoveSlideCommand,
                                                   UpdateSlideCommand)

__all__ = [
    # Base
    "Command",
    "CommandException",
    "CommandExecutionError",
    "CommandUndoError",
    # History
    "CommandHistory",
    "PresentationCommandHistory",
    # Slide Commands
    "CreateSlideCommand",
    "UpdateSlideCommand",
    "DeleteSlideCommand",
    "MoveSlideCommand",
]
