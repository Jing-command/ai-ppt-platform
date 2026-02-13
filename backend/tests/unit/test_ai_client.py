"""
测试 AI Client
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from jinja2 import Environment

from ai_ppt.infrastructure.ai.client import (
    LLMAPIError,
    LLMClient,
    LLMClientError,
    LLMFormatError,
    LLMProvider,
    LLMTimeoutError,
)
from ai_ppt.infrastructure.ai.models import DataSchema, LLMRequest


class TestLLMProvider:
    """测试 LLMProvider 枚举"""

    def test_provider_values(self):
        """测试提供商值"""
        assert LLMProvider.OPENAI == "openai"
        assert LLMProvider.DEEPSEEK == "deepseek"
        assert LLMProvider.KIMI == "kimi"


class TestLLMClient:
    """测试 LLMClient"""

    class TestInitialization:
        """测试初始化"""

        def test_default_initialization(self):
            """测试默认初始化"""
            with patch.dict('os.environ', {'AI_API_KEY': 'test_key'}):
                with patch('ai_ppt.infrastructure.ai.client.settings') as mock_settings:
                    mock_settings.ai.provider = 'deepseek'
                    mock_settings.ai.api_key.get_secret_value.return_value = 'test_key'
                    mock_settings.ai.model = None

                    client = LLMClient()

                    assert client.provider == LLMProvider.DEEPSEEK
                    assert client.api_key == "test_key"
                    assert client.model == "deepseek-chat"
                    assert client.timeout == 60.0

        def test_custom_initialization(self):
            """测试自定义初始化"""
            client = LLMClient(
                provider=LLMProvider.OPENAI,
                api_key="custom_key",
                base_url="https://custom.api.com",
                model="gpt-4-turbo",
                timeout=120.0,
            )

            assert client.provider == LLMProvider.OPENAI
            assert client.api_key == "custom_key"
            assert client.base_url == "https://custom.api.com"
            assert client.model == "gpt-4-turbo"
            assert client.timeout == 120.0

        def test_initialization_without_api_key(self):
            """测试缺少 API key 时抛出异常"""
            with patch.dict('os.environ', {}, clear=True):
                with patch('ai_ppt.infrastructure.ai.client.settings') as mock_settings:
                    mock_settings.ai.provider = 'deepseek'
                    mock_settings.ai.api_key.get_secret_value.return_value = ''
                    mock_settings.ai.model = None

                    with pytest.raises(LLMClientError, match="API key not configured"):
                        LLMClient()

        def test_initialization_from_env(self):
            """测试从环境变量读取 API key"""
            with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'env_key'}):
                with patch('ai_ppt.infrastructure.ai.client.settings') as mock_settings:
                    mock_settings.ai.provider = 'deepseek'
                    mock_settings.ai.api_key.get_secret_value.return_value = ''
                    mock_settings.ai.model = None

                    client = LLMClient()

                    assert client.api_key == "env_key"

    class TestHeaders:
        """测试请求头"""

        def test_get_headers(self):
            """测试获取请求头"""
            client = LLMClient(
                provider=LLMProvider.OPENAI,
                api_key="test_key",
            )

            headers = client._get_headers()

            assert headers["Authorization"] == "Bearer test_key"
            assert headers["Content-Type"] == "application/json"

    class TestBuildRequestBody:
        """测试构建请求体"""

        def test_build_request_body(self):
            """测试构建请求体"""
            client = LLMClient(
                provider=LLMProvider.DEEPSEEK,
                api_key="key",
                model="deepseek-chat",
            )

            request = LLMRequest(
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.5,
                max_tokens=1000,
            )

            body = client._build_request_body(request)

            assert body["model"] == "deepseek-chat"
            assert body["messages"] == [{"role": "user", "content": "Hello"}]
            assert body["temperature"] == 0.5
            assert body["max_tokens"] == 1000
            assert body["stream"] is False

        def test_build_request_body_with_response_format(self):
            """测试带响应格式的请求体"""
            client = LLMClient(
                provider=LLMProvider.DEEPSEEK,
                api_key="key",
                model="deepseek-chat",
            )

            request = LLMRequest(
                messages=[{"role": "user", "content": "Hello"}],
                response_format={"type": "json_object"},
            )

            body = client._build_request_body(request)

            assert body["response_format"]["type"] == "json_object"

    class TestComplete:
        """测试 complete 方法"""

        async def test_complete_success(self):
            """测试成功完成请求"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(return_value={
                "choices": [{"message": {"content": "Hello!"}, "finish_reason": "stop"}],
                "model": "deepseek-chat",
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            })

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()

            with patch('httpx.AsyncClient', return_value=mock_client):
                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                )

                request = LLMRequest(messages=[{"role": "user", "content": "Hi"}])
                response = await client.complete(request)

                assert response.content == "Hello!"
                assert response.model == "deepseek-chat"
                assert response.usage.prompt_tokens == 10

        async def test_complete_timeout(self):
            """测试请求超时"""
            mock_client = MagicMock()
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))
            mock_client.aclose = AsyncMock()

            with patch('httpx.AsyncClient', return_value=mock_client):
                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                    timeout=1.0,
                )

                request = LLMRequest(messages=[{"role": "user", "content": "Hi"}])

                with pytest.raises(LLMTimeoutError, match="timed out"):
                    await client.complete(request)

        async def test_complete_http_error(self):
            """测试 HTTP 错误"""
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"

            mock_client = MagicMock()
            mock_client.post = AsyncMock(side_effect=httpx.HTTPStatusError(
                "401 Unauthorized",
                request=MagicMock(),
                response=mock_response,
            ))
            mock_client.aclose = AsyncMock()

            with patch('httpx.AsyncClient', return_value=mock_client):
                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                )

                request = LLMRequest(messages=[{"role": "user", "content": "Hi"}])

                with pytest.raises(LLMAPIError, match="API error") as exc_info:
                    await client.complete(request)

                assert exc_info.value.status_code == 401

        async def test_complete_invalid_response_format(self):
            """测试无效响应格式"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(return_value={
                "invalid": "response",  # 缺少必要字段
            })

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()

            with patch('httpx.AsyncClient', return_value=mock_client):
                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                )

                request = LLMRequest(messages=[{"role": "user", "content": "Hi"}])

                with pytest.raises(LLMFormatError, match="Invalid LLM response format"):
                    await client.complete(request)

    class TestCompleteStream:
        """测试 complete_stream 方法"""

        async def test_complete_stream_success(self):
            """测试成功流式请求"""
            sse_lines = [
                "data: " + json.dumps({
                    "choices": [{"delta": {"content": "Hello"}, "finish_reason": None}]
                }),
                "data: " + json.dumps({
                    "choices": [{"delta": {"content": " World"}, "finish_reason": "stop"}]
                }),
                "data: [DONE]",
            ]

            async def mock_aiter_lines():
                for line in sse_lines:
                    yield line

            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.aiter_lines = mock_aiter_lines

            mock_client = MagicMock()
            mock_client.stream = MagicMock(return_value=async_context_manager(mock_response))
            mock_client.aclose = AsyncMock()

            with patch('httpx.AsyncClient', return_value=mock_client):
                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                )

                request = LLMRequest(messages=[{"role": "user", "content": "Hi"}])
                chunks = []
                async for chunk in client.complete_stream(request):
                    chunks.append(chunk)

                assert len(chunks) >= 2

        async def test_complete_stream_timeout(self):
            """测试流式请求超时"""
            mock_client = MagicMock()
            mock_client.stream = MagicMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_client.aclose = AsyncMock()

            with patch('httpx.AsyncClient', return_value=mock_client):
                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                )

                request = LLMRequest(messages=[{"role": "user", "content": "Hi"}])

                with pytest.raises(LLMTimeoutError, match="streaming request timed out"):
                    async for _ in client.complete_stream(request):
                        pass

    class TestRenderPrompt:
        """测试 render_prompt 方法"""

        def test_render_prompt(self):
            """测试渲染提示词"""
            with patch.object(Environment, 'get_template') as mock_get_template:
                mock_template = MagicMock()
                mock_template.render = MagicMock(return_value="Rendered prompt")
                mock_get_template.return_value = mock_template

                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                )

                result = client.render_prompt("test.j2", name="Test")

                assert result == "Rendered prompt"
                mock_get_template.assert_called_once_with("test.j2")
                mock_template.render.assert_called_once_with(name="Test")

    class TestGenerateOutline:
        """测试 generate_outline 方法"""

        async def test_generate_outline_success(self):
            """测试成功生成大纲"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(return_value={
                "choices": [{"message": {"content": json.dumps({
                    "title": "Test Outline",
                    "pages": [{"title": "Page 1", "content": "Content 1"}],
                })}, "finish_reason": "stop"}],
                "model": "deepseek-chat",
                "usage": {"prompt_tokens": 100, "completion_tokens": 50},
            })

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()

            with patch('httpx.AsyncClient', return_value=mock_client):
                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                )

                data_schema = [DataSchema(name="sales", columns=["date", "amount"])]
                result = await client.generate_outline(
                    user_prompt="Generate sales report",
                    data_schema=data_schema,
                )

                assert result.title == "Test Outline"
                assert len(result.pages) == 1

        async def test_generate_outline_invalid_json(self):
            """测试无效 JSON 响应"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(return_value={
                "choices": [{"message": {"content": "not valid json"}, "finish_reason": "stop"}],
                "model": "deepseek-chat",
                "usage": {},
            })

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()

            with patch('httpx.AsyncClient', return_value=mock_client):
                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                )

                with pytest.raises(LLMFormatError, match="Failed to parse outline JSON"):
                    await client.generate_outline(
                        user_prompt="Generate report",
                        data_schema=[],
                    )

    class TestEnhanceSlideContent:
        """测试 enhance_slide_content 方法"""

        async def test_enhance_slide_content_success(self):
            """测试成功增强幻灯片内容"""
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(return_value={
                "choices": [{"message": {"content": json.dumps({
                    "content": {"text": "Enhanced content"},
                    "improvements": ["Better formatting"],
                })}, "finish_reason": "stop"}],
                "model": "deepseek-chat",
                "usage": {},
            })

            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()

            with patch('httpx.AsyncClient', return_value=mock_client):
                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                )

                result = await client.enhance_slide_content(
                    content={"text": "Original content"},
                    enhancement_type="professional",
                )

                assert result.content["text"] == "Enhanced content"

    class TestContextManager:
        """测试异步上下文管理器"""

        async def test_async_context_manager(self):
            """测试异步上下文管理器"""
            mock_client = MagicMock()
            mock_client.aclose = AsyncMock()

            with patch('httpx.AsyncClient', return_value=mock_client):
                client = LLMClient(
                    provider=LLMProvider.DEEPSEEK,
                    api_key="key",
                )

                async with client as c:
                    assert c is client

                mock_client.aclose.assert_called_once()


# Helper functions
async def async_iterator(items):
    """创建异步迭代器"""
    for item in items:
        yield item


class async_context_manager:
    """异步上下文管理器模拟"""

    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestLLMClientEdgeCases:
    """测试边界情况"""

    def test_init_with_string_provider(self):
        """测试使用字符串作为 provider"""
        client = LLMClient(
            provider="openai",
            api_key="key",
        )

        assert client.provider == LLMProvider.OPENAI

    def test_default_models(self):
        """测试默认模型"""
        with patch('ai_ppt.infrastructure.ai.client.settings') as mock_settings:
            mock_settings.ai.model = None

            client = LLMClient(
                provider=LLMProvider.OPENAI,
                api_key="key",
            )

            assert client.model == "gpt-4"

            client2 = LLMClient(
                provider=LLMProvider.KIMI,
                api_key="key",
            )

            assert client2.model == "moonshot-v1-8k"

    def test_default_base_urls(self):
        """测试默认基础 URL"""
        client = LLMClient(
            provider=LLMProvider.OPENAI,
            api_key="key",
        )

        assert client.base_url == "https://api.openai.com/v1"

        client2 = LLMClient(
            provider=LLMProvider.KIMI,
            api_key="key",
        )

        assert client2.base_url == "https://api.moonshot.cn/v1"
