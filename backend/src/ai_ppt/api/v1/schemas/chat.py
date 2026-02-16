"""
聊天相关 Schema 定义
用于 AI 提示词助手的聊天 API
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(str, Enum):
    """聊天消息角色"""

    USER = "user"  # 用户消息
    ASSISTANT = "assistant"  # AI 助手消息
    SYSTEM = "system"  # 系统消息


class ChatMessage(BaseModel):
    """聊天消息"""

    role: MessageRole = Field(
        ..., description="消息角色: user/assistant/system"
    )
    content: str = Field(..., description="消息内容")

    model_config = ConfigDict(
        # 允许从枚举值创建
        use_enum_values=True,
    )


class ChatContext(BaseModel):
    """聊天上下文信息"""

    presentation_id: Optional[str] = Field(
        None, alias="presentationId", description="当前演示文稿 ID"
    )
    slide_id: Optional[str] = Field(
        None, alias="slideId", description="当前幻灯片 ID"
    )
    current_prompt: Optional[str] = Field(
        None, alias="currentPrompt", description="用户当前正在编辑的提示词"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="额外的元数据信息"
    )

    model_config = ConfigDict(populate_by_name=True)


class ChatRequest(BaseModel):
    """聊天请求"""

    messages: List[ChatMessage] = Field(
        ..., min_length=1, description="聊天消息列表"
    )
    context: Optional[ChatContext] = Field(
        None, description="可选的上下文信息"
    )
    stream: bool = Field(default=True, description="是否使用流式响应")


class ChatResponseChunk(BaseModel):
    """聊天响应块（用于流式响应）"""

    content: str = Field(..., description="响应内容片段")
    is_finished: bool = Field(default=False, description="是否响应结束")
    has_optimized_prompt: bool = Field(
        default=False, description="是否包含优化后的提示词"
    )
    optimized_prompt: Optional[str] = Field(None, description="优化后的提示词")
    thinking_content: Optional[str] = Field(None, description="思考过程内容")

    model_config = ConfigDict(populate_by_name=True)


class ChatResponse(BaseModel):
    """聊天响应（非流式）"""

    message: ChatMessage = Field(..., description="AI 响应消息")
    has_optimized_prompt: bool = Field(
        default=False, description="是否包含优化后的提示词"
    )
    optimized_prompt: Optional[str] = Field(None, description="优化后的提示词")

    model_config = ConfigDict(populate_by_name=True)


class IntentType(str, Enum):
    """用户意图类型"""

    CLARIFICATION = "clarification"  # 需要澄清
    PROMPT_OPTIMIZATION = "prompt_optimization"  # 提示词优化
    SUGGESTION = "suggestion"  # 提供建议
    GENERAL = "general"  # 一般对话


class IntentAnalysis(BaseModel):
    """意图分析结果"""

    intent_type: IntentType = Field(..., description="意图类型")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    missing_info: Optional[List[str]] = Field(
        None, description="缺失的信息列表"
    )
    suggested_questions: Optional[List[str]] = Field(
        None, description="建议的问题列表"
    )
