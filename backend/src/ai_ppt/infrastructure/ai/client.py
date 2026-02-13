"""
LLM HTTP 客户端
使用 httpx.AsyncClient 调用 LLM API
支持: OpenAI, DeepSeek, Kimi
"""

import json
import os
import time
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Literal, Optional, Union

import httpx
from jinja2 import Environment, PackageLoader, select_autoescape

from ai_ppt.infrastructure.ai.models import (
    DataSchema,
    LLMRequest,
    LLMResponse,
    OutlineResult,
    SlideEnhancementResult,
    StreamingChunk,
    Usage,
)
from ai_ppt.infrastructure.config import settings


class LLMProvider(str, Enum):
    """支持的 LLM 提供商"""

    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    KIMI = "kimi"


class LLMClientError(Exception):
    """LLM 客户端错误基类"""


class LLMAPIError(LLMClientError):
    """API 调用错误"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class LLMTimeoutError(LLMClientError):
    """API 超时错误"""


class LLMFormatError(LLMClientError):
    """响应格式错误"""


class LLMClient:
    """
    异步 LLM HTTP 客户端

    支持多个提供商:
    - OpenAI (GPT-4, GPT-3.5-turbo)
    - DeepSeek (deepseek-chat, deepseek-coder)
    - Kimi (moonshot-v1)

    使用示例:
        >>> client = LLMClient(provider=LLMProvider.DEEPSEEK)
        >>> response = await client.generate_outline(
        ...     user_prompt="生成销售报告PPT",
        ...     data_schema=[DataSchema(name="sales", columns=["date", "amount"])]
        ... )
    """

    # 提供商默认配置
    DEFAULT_BASE_URLS = {
        LLMProvider.OPENAI: "https://api.openai.com/v1",
        LLMProvider.DEEPSEEK: "https://api.deepseek.com/v1",
        LLMProvider.KIMI: "https://api.moonshot.cn/v1",
    }

    DEFAULT_MODELS = {
        LLMProvider.OPENAI: "gpt-4",
        LLMProvider.DEEPSEEK: "deepseek-chat",
        LLMProvider.KIMI: "moonshot-v1-8k",
    }

    def __init__(
        self,
        provider: Optional[Union[LLMProvider, str]] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        """
        初始化 LLM 客户端

        Args:
            provider: LLM 提供商，默认从配置读取
            api_key: API 密钥，默认从配置读取
            base_url: API 基础 URL，默认使用提供商官方地址
            model: 模型名称，默认使用提供商推荐模型
            timeout: 请求超时时间（秒）
        """
        self.provider = LLMProvider(provider or settings.ai.provider)

        # 优先使用传入的 api_key（仅当不为 None），其次从 settings 读取，最后从环境变量读取
        if api_key is not None:
            _api_key = api_key
        else:
            _api_key = settings.ai.api_key.get_secret_value()
        if not _api_key:
            # 尝试从环境变量直接读取（兼容不同的环境变量命名）
            _api_key = (
                os.environ.get("AI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY") or ""
            )

        self.api_key = _api_key
        self.base_url = base_url or self.DEFAULT_BASE_URLS[self.provider]
        self.model = model or settings.ai.model or self.DEFAULT_MODELS[self.provider]
        self.timeout = timeout

        # 验证 API key 是否配置
        if not self.api_key or not self.api_key.strip():
            raise LLMClientError(
                f"API key not configured for provider '{self.provider}'. "
                "Please set AI_API_KEY environment variable or pass api_key parameter."
            )

        # 初始化 HTTP 客户端
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout, connect=10.0),
            headers=self._get_headers(),
        )

        # 初始化 Jinja2 模板引擎
        self._jinja_env = Environment(
            loader=PackageLoader("ai_ppt", "infrastructure/ai/prompts"),
            autoescape=select_autoescape(["j2"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _get_headers(self) -> Dict[str, str]:
        """获取 API 请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_request_body(self, request: LLMRequest) -> Dict[str, Any]:
        """构建 API 请求体"""
        body: Dict[str, Any] = {
            "model": self.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": request.stream,
        }

        # Kimi 和 DeepSeek 支持 response_format
        if request.response_format and self.provider != LLMProvider.OPENAI:
            body["response_format"] = request.response_format

        # OpenAI 的 JSON 模式需要特定参数
        if request.response_format and self.provider == LLMProvider.OPENAI:
            body["response_format"] = request.response_format

        return body

    def _parse_response(self, data: Dict[str, Any], latency_ms: float) -> LLMResponse:
        """解析 API 响应"""
        choice = data["choices"][0]

        # 提取使用统计
        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", self.model),
            provider=self.provider.value,
            usage=usage,
            finish_reason=choice.get("finish_reason"),
            latency_ms=latency_ms,
        )

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """
        发送非流式完成请求

        Args:
            request: LLM 请求参数

        Returns:
            LLM 响应

        Raises:
            LLMTimeoutError: 请求超时
            LLMAPIError: API 调用错误
            LLMFormatError: 响应格式错误
        """
        body = self._build_request_body(request)
        start_time = time.time()

        try:
            response = await self._client.post("/chat/completions", json=body)
            response.raise_for_status()
            latency_ms = (time.time() - start_time) * 1000

            data = response.json()
            return self._parse_response(data, latency_ms)

        except httpx.TimeoutException as e:
            raise LLMTimeoutError(f"LLM request timed out after {self.timeout}s") from e
        except httpx.HTTPStatusError as e:
            response_body = e.response.text if hasattr(e, "response") else None
            raise LLMAPIError(
                f"LLM API error: {e}",
                status_code=e.response.status_code if hasattr(e, "response") else None,
                response_body=response_body,
            ) from e
        except httpx.HTTPError as e:
            raise LLMAPIError(f"LLM request failed: {e}") from e
        except (KeyError, IndexError) as e:
            raise LLMFormatError(f"Invalid LLM response format: {e}") from e

    async def complete_stream(
        self, request: LLMRequest
    ) -> AsyncIterator[StreamingChunk]:
        """
        发送流式完成请求

        Args:
            request: LLM 请求参数

        Yields:
            流式响应块
        """
        stream_request = LLMRequest(**request.model_dump(), stream=True)
        body = self._build_request_body(stream_request)
        index = 0

        try:
            async with self._client.stream(
                "POST", "/chat/completions", json=body
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    line = line.strip()

                    # 跳过空行和注释
                    if not line or line.startswith(":"):
                        continue

                    # 处理 SSE 数据行
                    if line.startswith("data: "):
                        data_str = line[6:]

                        # 流结束标记
                        if data_str == "[DONE]":
                            yield StreamingChunk(
                                content="", is_finished=True, index=index
                            )
                            break

                        try:
                            data = json.loads(data_str)
                            choice = data["choices"][0]
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")

                            if content:
                                is_finished = choice.get("finish_reason") is not None
                                yield StreamingChunk(
                                    content=content,
                                    is_finished=is_finished,
                                    index=index,
                                )
                                index += 1

                                if is_finished:
                                    break

                        except json.JSONDecodeError:
                            continue
                        except (KeyError, IndexError):
                            continue

        except httpx.TimeoutException as e:
            raise LLMTimeoutError("LLM streaming request timed out") from e
        except httpx.HTTPError as e:
            raise LLMAPIError(f"LLM streaming request failed: {e}") from e

    def render_prompt(self, template_name: str, **kwargs: Any) -> str:
        """
        渲染 Jinja2 提示词模板

        Args:
            template_name: 模板文件名（如 "outline_generation.j2"）
            **kwargs: 模板变量

        Returns:
            渲染后的提示词字符串
        """
        template = self._jinja_env.get_template(template_name)
        return template.render(**kwargs)

    async def generate_outline(
        self,
        user_prompt: str,
        data_schema: List[DataSchema],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> OutlineResult:
        """
        生成 PPT 大纲

        Args:
            user_prompt: 用户需求描述
            data_schema: 数据源结构信息
            temperature: 采样温度
            max_tokens: 最大 token 数

        Returns:
            结构化的大纲结果

        Raises:
            LLMClientError: 生成失败
        """
        # 渲染提示词
        prompt = self.render_prompt(
            "outline_generation.j2",
            user_prompt=user_prompt,
            data_schema=[schema.to_dict() for schema in data_schema],
        )

        # 构建请求
        request = LLMRequest(
            messages=[
                {"role": "system", "content": "你是一个专业的 PPT 大纲设计专家。"},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        # 发送请求
        response = await self.complete(request)

        # 解析 JSON 结果
        try:
            content = json.loads(response.content)
            return OutlineResult.model_validate(content)
        except json.JSONDecodeError as e:
            raise LLMFormatError(f"Failed to parse outline JSON: {e}") from e
        except Exception as e:
            raise LLMFormatError(f"Invalid outline format: {e}") from e

    async def enhance_slide_content(
        self,
        content: Dict[str, Any],
        enhancement_type: Literal[
            "professional", "concise", "storytelling", "creative"
        ] = "professional",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> SlideEnhancementResult:
        """
        增强幻灯片内容

        Args:
            content: 原始幻灯片内容
            enhancement_type: 增强类型
            temperature: 采样温度
            max_tokens: 最大 token 数

        Returns:
            增强后的内容
        """
        # 渲染提示词
        prompt = self.render_prompt(
            "slide_enhancement.j2",
            content=content,
            enhancement_type=enhancement_type,
        )

        # 构建请求
        request = LLMRequest(
            messages=[
                {"role": "system", "content": "你是一个专业的 PPT 内容优化专家。"},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        # 发送请求
        response = await self.complete(request)

        # 解析 JSON 结果
        try:
            result_content = json.loads(response.content)
            return SlideEnhancementResult.model_validate(result_content)
        except json.JSONDecodeError as e:
            raise LLMFormatError(f"Failed to parse enhancement JSON: {e}") from e
        except Exception as e:
            raise LLMFormatError(f"Invalid enhancement format: {e}") from e

    async def close(self) -> None:
        """关闭 HTTP 客户端"""
        await self._client.aclose()

    async def __aenter__(self) -> "LLMClient":
        """异步上下文管理器入口"""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """异步上下文管理器出口"""
        await self.close()
