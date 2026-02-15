"""
AI 提示词助手聊天 API
处理用户与 AI 助手的对话交互
"""

import json
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from ai_ppt.api.v1.schemas.chat import (
    ChatContext,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    MessageRole,
)
from ai_ppt.api.v1.schemas.common import ErrorResponse
from ai_ppt.services.chat_service import chat_service

# 创建路由器
router = APIRouter(prefix="/chat", tags=["AI 提示词助手"])


async def _generate_sse_stream(
    messages: List[ChatMessage],
    context: Optional[ChatContext] = None,
) -> AsyncIterator[str]:
    """
    生成 SSE 流式响应

    Args:
        messages: 聊天消息列表
        context: 可选的上下文信息

    Yields:
        SSE 格式的字符串
    """
    # 使用聊天服务生成流式响应
    async for chunk in chat_service.generate_response_stream(
        messages, context
    ):
        # 将响应块转换为 JSON
        chunk_dict = {
            "content": chunk.content,
            "isFinished": chunk.is_finished,
            "hasOptimizedPrompt": chunk.has_optimized_prompt,
            "optimizedPrompt": chunk.optimized_prompt,
        }

        # 生成 SSE 格式的数据
        yield f"data: {json.dumps(chunk_dict, ensure_ascii=False)}\n\n"


@router.post(
    "",
    summary="发送聊天消息",
    description="与 AI 提示词助手进行对话，支持流式响应",
    status_code=status.HTTP_200_OK,
    response_model=None,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def chat(request: ChatRequest) -> Union[StreamingResponse, ChatResponse]:
    """
    处理聊天请求

    接收用户的聊天消息，返回 AI 助手的流式响应。

    Args:
        request: 聊天请求，包含消息列表和可选的上下文

    Returns:
        StreamingResponse: SSE 流式响应

    请求示例:
        ```json
        {
            "messages": [
                {"role": "user", "content": "帮我生成一个销售报告 PPT"}
            ],
            "context": {
                "presentationId": "xxx",
                "currentPrompt": "销售报告"
            },
            "stream": true
        }
        ```

    响应示例 (SSE 格式):
        ```
        data: {"content": "根据", "isFinished": false,
        "hasOptimizedPrompt": false}

        data: {"content": "您的描述", "isFinished": false,
        "hasOptimizedPrompt": false}

        data: {"content": "...", "isFinished": true,
        "hasOptimizedPrompt": true,
        "optimizedPrompt": "主题：销售报告\\n目标受众：领导"}
        ```
    """
    # 检查是否使用流式响应
    if request.stream:
        # 返回 SSE 流式响应
        return StreamingResponse(
            _generate_sse_stream(request.messages, request.context),
            media_type="text/event-stream",
            headers={
                # 禁用缓冲，确保实时传输
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
            },
        )
    else:
        # 非流式响应 - 收集所有响应块
        full_content = ""
        has_optimized = False
        optimized_prompt = None

        async for chunk in chat_service.generate_response_stream(
            request.messages, request.context
        ):
            full_content += chunk.content
            if chunk.is_finished:
                has_optimized = chunk.has_optimized_prompt
                optimized_prompt = chunk.optimized_prompt

        # 构建响应
        response = ChatResponse(
            message=ChatMessage(
                role=MessageRole.ASSISTANT,
                content=full_content,
            ),
            has_optimized_prompt=has_optimized,
            optimized_prompt=optimized_prompt,
        )

        return response


@router.post(
    "/analyze",
    summary="分析用户意图",
    description="分析用户消息的意图，返回缺失信息和建议问题",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def analyze_intent(request: ChatRequest) -> Dict[str, Any]:
    """
    分析用户意图

    分析用户消息的意图类型，识别缺失的信息，提供引导性问题。

    Args:
        request: 聊天请求

    Returns:
        IntentAnalysis: 意图分析结果
    """
    # 分析意图
    intent = chat_service.analyze_intent(request.messages, request.context)

    # 转换为响应格式
    return {
        "intentType": intent.intent_type.value,
        "confidence": intent.confidence,
        "missingInfo": intent.missing_info,
        "suggestedQuestions": intent.suggested_questions,
    }
