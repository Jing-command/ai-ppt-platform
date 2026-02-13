"""
Command 模式基类
实现撤销/重做功能的基础架构
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Command(ABC):
    """
    Command 抽象基类

    所有命令必须实现 execute() 和 undo() 方法。
    命令必须是可序列化的，以便持久化到数据库。

    使用示例:
        >>> class MyCommand(Command):
        ...     def __init__(self, target_id: UUID, data: dict):
        ...         self.target_id = target_id
        ...         self.data = data
        ...         self.previous_data = None
        ...
        ...     async def execute(self) -> None:
        ...         self.previous_data = await fetch_data(self.target_id)
        ...         await update_data(self.target_id, self.data)
        ...
        ...     async def undo(self) -> None:
        ...         if self.previous_data:
        ...             await update_data(self.target_id, self.previous_data)
        ...
        ...     def to_dict(self) -> dict:
        ...         return {
        ...             "type": "MyCommand",
        ...             "target_id": str(self.target_id),
        ...             "data": self.data,
        ...         }
    """

    def __init__(self) -> None:
        self._id: UUID = uuid4()
        self._executed_at: Optional[datetime] = None
        self._undone_at: Optional[datetime] = None

    @property
    def id(self) -> UUID:
        """命令唯一标识"""
        return self._id

    @property
    def executed_at(self) -> Optional[datetime]:
        """命令执行时间"""
        return self._executed_at

    @property
    def undone_at(self) -> Optional[datetime]:
        """命令撤销时间"""
        return self._undone_at

    @property
    @abstractmethod
    def command_type(self) -> str:
        """命令类型标识，用于序列化"""
        raise NotImplementedError

    @abstractmethod
    async def execute(self) -> None:
        """
        执行命令

        实现应该：
        1. 先保存执行前的状态（用于 undo）
        2. 执行实际的操作
        3. 记录执行时间
        """
        raise NotImplementedError

    @abstractmethod
    async def undo(self) -> None:
        """
        撤销命令

        实现应该：
        1. 使用 execute() 中保存的状态恢复
        2. 记录撤销时间
        """
        raise NotImplementedError

    def mark_executed(self) -> None:
        """标记命令已执行"""
        self._executed_at = datetime.utcnow()

    def mark_undone(self) -> None:
        """标记命令已撤销"""
        self._undone_at = datetime.utcnow()

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        将命令序列化为字典

        用于：
        - 持久化到数据库
        - 网络传输
        - 日志记录

        Returns:
            包含命令数据的字典，必须包含 "type" 字段
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Command":
        """
        从字典反序列化命令

        Args:
            data: 包含命令数据的字典

        Returns:
            恢复的命令实例
        """
        raise NotImplementedError


class CommandMetadata(BaseModel):
    """命令元数据（用于持久化）"""

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    command_type: str = Field(..., description="命令类型")
    target_id: UUID = Field(..., description="操作目标 ID")
    target_type: str = Field(..., description="操作目标类型")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = Field(default=None)
    undone_at: Optional[datetime] = Field(default=None)
    payload: Dict[str, Any] = Field(default_factory=dict, description="命令数据")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": str(self.id),
            "command_type": self.command_type,
            "target_id": str(self.target_id),
            "target_type": self.target_type,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "undone_at": self.undone_at.isoformat() if self.undone_at else None,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommandMetadata":
        """从字典创建"""
        return cls(
            id=UUID(data["id"]),
            command_type=data["command_type"],
            target_id=UUID(data["target_id"]),
            target_type=data["target_type"],
            created_at=datetime.fromisoformat(data["created_at"]),
            executed_at=(
                datetime.fromisoformat(data["executed_at"])
                if data.get("executed_at")
                else None
            ),
            undone_at=(
                datetime.fromisoformat(data["undone_at"])
                if data.get("undone_at")
                else None
            ),
            payload=data.get("payload", {}),
        )


class CommandFactory(ABC):
    """
    Command 工厂基类

    用于从字典反序列化命令。
    每个领域应该有自己的工厂实现。
    """

    _registry: Dict[str, type] = {}

    @classmethod
    def register(cls, command_type: str, command_class: type) -> None:
        """
        注册命令类型

        Args:
            command_type: 命令类型标识
            command_class: 命令类
        """
        cls._registry[command_type] = command_class

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Command:
        """
        创建命令实例

        Args:
            data: 包含命令数据的字典，必须包含 "type" 字段

        Returns:
            命令实例

        Raises:
            ValueError: 未知命令类型
        """
        command_type = data.get("type")
        if not command_type:
            raise ValueError("Command data must contain 'type' field")

        command_class = cls._registry.get(command_type)
        if not command_class:
            raise ValueError(f"Unknown command type: {command_type}")

        return command_class.from_dict(data)


class CommandException(Exception):
    """Command 相关异常基类"""


class CommandExecutionError(CommandException):
    """命令执行错误"""

    def __init__(self, message: str, command: Optional[Command] = None) -> None:
        super().__init__(message)
        self.command = command


class CommandUndoError(CommandException):
    """命令撤销错误"""

    def __init__(self, message: str, command: Optional[Command] = None) -> None:
        super().__init__(message)
        self.command = command
