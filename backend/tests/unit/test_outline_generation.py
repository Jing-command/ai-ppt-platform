"""
大纲生成服务单元测试
"""

import json
import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_ppt.domain.models.outline import Outline, OutlineStatus
from ai_ppt.infrastructure.ai.models import LLMResponse
from ai_ppt.services.outline_generation import (
    OutlineGenerationError,
    OutlineGenerationService,
)


@pytest.fixture
def mock_llm_client():
    """模拟 LLM 客户端"""
    client = AsyncMock()
    return client


@pytest.fixture
def generation_service(mock_llm_client):
    """创建生成服务实例"""
    return OutlineGenerationService(mock_llm_client)


class TestOutlineGenerationBuildPrompt:
    """测试生成提示词构建"""

    def test_build_prompt_basic(self, generation_service):
        """测试基本提示词构建"""
        prompt = generation_service._build_generation_prompt(
            topic="人工智能",
            num_slides=10,
            language="zh",
            style="business",
        )

        assert "人工智能" in prompt
        assert "10" in prompt
        assert "中文" in prompt
        assert "商务专业风格" in prompt
        assert "JSON" in prompt

    def test_build_prompt_english(self, generation_service):
        """测试英文提示词"""
        prompt = generation_service._build_generation_prompt(
            topic="Artificial Intelligence",
            num_slides=5,
            language="en",
            style="technical",
        )

        assert "English" in prompt
        assert "技术专业风格" in prompt

    def test_build_prompt_with_context(self, generation_service):
        """测试带上下文的提示词"""
        context_data = {"sales": 1000000, "growth": "20%"}

        prompt = generation_service._build_generation_prompt(
            topic="销售报告",
            num_slides=8,
            context_data=context_data,
        )

        assert "参考数据" in prompt
        assert "sales" in prompt
        assert "1000000" in prompt

    def test_build_prompt_different_styles(self, generation_service):
        """测试不同风格的提示词"""
        styles = {
            "business": "商务专业风格",
            "education": "教育学术风格",
            "creative": "创意设计风格",
            "technical": "技术专业风格",
            "unknown": "商务专业风格",  # 默认
        }

        for style, expected_desc in styles.items():
            prompt = generation_service._build_generation_prompt(
                topic="Test",
                num_slides=5,
                style=style,
            )
            assert expected_desc in prompt


class TestOutlineGenerationGenerateOutline:
    """测试大纲生成"""

    async def test_generate_outline_success(self, generation_service, mock_llm_client):
        """测试成功生成大纲"""
        # 模拟 LLM 响应
        mock_response_data = {
            "title": "AI Presentation",
            "description": "About AI technology",
            "pages": [
                {
                    "id": "page-1",
                    "pageNumber": 1,
                    "title": "Introduction",
                    "content": "Overview of AI",
                    "pageType": "title",
                    "imagePrompt": "Futuristic AI background",
                },
                {
                    "id": "page-2",
                    "pageNumber": 2,
                    "title": "History",
                    "content": "AI development history",
                    "pageType": "content",
                },
            ],
            "background": {
                "type": "ai",
                "prompt": "Blue tech background",
            },
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(mock_response_data),
            model="deepseek-chat",
            usage={"prompt_tokens": 100, "completion_tokens": 200},
        )

        result = await generation_service.generate_outline(
            topic="Artificial Intelligence",
            num_slides=10,
        )

        assert result["title"] == "AI Presentation"
        assert len(result["pages"]) == 2
        assert "background" in result

        mock_llm_client.complete.assert_called_once()

    async def test_generate_outline_missing_pages(self, generation_service, mock_llm_client):
        """测试缺少 pages 字段的响应"""
        mock_response_data = {
            "title": "Invalid Response",
            "description": "Missing pages",
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(mock_response_data),
            model="deepseek-chat",
            usage={},
        )

        with pytest.raises(OutlineGenerationError) as exc_info:
            await generation_service.generate_outline(topic="Test")

        assert "pages" in str(exc_info.value)

    async def test_generate_outline_adds_missing_ids(self, generation_service, mock_llm_client):
        """测试为页面添加缺失的 ID"""
        mock_response_data = {
            "title": "Test",
            "pages": [
                {"pageNumber": 1, "title": "Page 1"},  # 缺少 id
                {"pageNumber": 2, "title": "Page 2"},  # 缺少 id
            ],
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(mock_response_data),
            model="deepseek-chat",
            usage={},
        )

        result = await generation_service.generate_outline(topic="Test")

        # 应该自动添加 id
        assert "id" in result["pages"][0]
        assert "id" in result["pages"][1]

    async def test_generate_outline_adds_missing_page_numbers(
        self, generation_service, mock_llm_client
    ):
        """测试为页面添加缺失的页码"""
        mock_response_data = {
            "title": "Test",
            "pages": [
                {"id": "page-1", "title": "Page 1"},  # 缺少 pageNumber
                {"id": "page-2", "title": "Page 2"},  # 缺少 pageNumber
            ],
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(mock_response_data),
            model="deepseek-chat",
            usage={},
        )

        result = await generation_service.generate_outline(topic="Test")

        # 应该自动添加 pageNumber
        assert result["pages"][0]["pageNumber"] == 1
        assert result["pages"][1]["pageNumber"] == 2

    async def test_generate_outline_json_decode_error(self, generation_service, mock_llm_client):
        """测试 JSON 解析错误"""
        mock_llm_client.complete.return_value = LLMResponse(
            content="Invalid JSON",
            model="deepseek-chat",
            usage={},
        )

        with pytest.raises(OutlineGenerationError) as exc_info:
            await generation_service.generate_outline(topic="Test")

        assert "解析" in str(exc_info.value) or "JSON" in str(exc_info.value)

    async def test_generate_outline_llm_error(self, generation_service, mock_llm_client):
        """测试 LLM 调用错误"""
        mock_llm_client.complete.side_effect = Exception("LLM API Error")

        with pytest.raises(OutlineGenerationError) as exc_info:
            await generation_service.generate_outline(topic="Test")

        assert "LLM API Error" in str(exc_info.value)


class TestOutlineGenerationCreateFromGeneration:
    """测试从生成结果创建大纲实体"""

    async def test_create_outline_from_generation(self, generation_service, mock_llm_client):
        """测试从生成结果创建大纲"""
        user_id = uuid.uuid4()

        mock_response_data = {
            "title": "Generated Title",
            "description": "Generated description",
            "pages": [
                {
                    "id": "page-1",
                    "pageNumber": 1,
                    "title": "Page 1",
                    "pageType": "title",
                },
                {
                    "id": "page-2",
                    "pageNumber": 2,
                    "title": "Page 2",
                    "pageType": "content",
                },
            ],
            "background": {"type": "ai", "prompt": "Blue background"},
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(mock_response_data),
            model="deepseek-chat",
            usage={},
        )

        result = await generation_service.create_outline_from_generation(
            user_id=user_id,
            topic="Test Topic",
            num_slides=5,
            language="zh",
            style="business",
            context_data={"key": "value"},
            connector_id=uuid.uuid4(),
        )

        assert isinstance(result, Outline)
        assert result.title == "Generated Title"
        assert result.user_id == user_id
        assert result.status == OutlineStatus.COMPLETED.value
        assert len(result.pages) == 2
        assert result.total_slides == 2
        assert result.ai_prompt == "Test Topic"
        assert result.ai_parameters is not None

    async def test_create_outline_without_background(self, generation_service, mock_llm_client):
        """测试创建没有背景的大纲"""
        user_id = uuid.uuid4()

        mock_response_data = {
            "title": "No Background",
            "pages": [{"id": "page-1", "pageNumber": 1, "title": "Page 1"}],
        }

        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps(mock_response_data),
            model="deepseek-chat",
            usage={},
        )

        result = await generation_service.create_outline_from_generation(
            user_id=user_id,
            topic="Test",
        )

        assert result.background is None


class TestOutlineGenerationLifecycle:
    """测试生成服务生命周期"""

    async def test_close(self, generation_service, mock_llm_client):
        """测试关闭服务"""
        mock_llm_client.close = AsyncMock()

        await generation_service.close()

        mock_llm_client.close.assert_called_once()

    async def test_async_context_manager(self, mock_llm_client):
        """测试异步上下文管理器"""
        mock_llm_client.close = AsyncMock()

        async with OutlineGenerationService(mock_llm_client) as service:
            assert isinstance(service, OutlineGenerationService)

        mock_llm_client.close.assert_called_once()

    async def test_auto_create_llm_client(self):
        """测试自动创建 LLM 客户端"""
        with patch("ai_ppt.services.outline_generation.LLMClient") as mock_client_class:
            mock_instance = AsyncMock()
            mock_client_class.return_value = mock_instance

            service = OutlineGenerationService()

            mock_client_class.assert_called_once()
            assert service._llm_client is mock_instance

    async def test_generate_uses_default_params(self, generation_service, mock_llm_client):
        """测试使用默认参数生成"""
        mock_llm_client.complete.return_value = LLMResponse(
            content=json.dumps({"title": "Test", "pages": []}),
            model="deepseek-chat",
            usage={},
        )

        await generation_service.generate_outline(topic="Test")

        call_args = mock_llm_client.complete.call_args[0][0]

        # 验证使用了默认参数
        assert call_args.temperature == 0.7
        assert call_args.max_tokens == 4096
        assert call_args.response_format == {"type": "json_object"}


class TestOutlineGenerationPromptContent:
    """测试提示词内容"""

    def test_prompt_includes_page_types(self, generation_service):
        """测试提示词包含页面类型说明"""
        prompt = generation_service._build_generation_prompt(topic="Test", num_slides=5)

        assert "title" in prompt
        assert "content" in prompt
        assert "section" in prompt
        assert "chart" in prompt
        assert "conclusion" in prompt

    def test_prompt_includes_json_structure(self, generation_service):
        """测试提示词包含 JSON 结构说明"""
        prompt = generation_service._build_generation_prompt(topic="Test", num_slides=5)

        assert '"title"' in prompt
        assert '"pages"' in prompt
        assert '"background"' in prompt

    def test_prompt_length_constraints(self, generation_service):
        """测试提示词长度限制说明"""
        prompt = generation_service._build_generation_prompt(topic="Test", num_slides=5)

        assert "100字" in prompt or "200字" in prompt
        assert "50字" in prompt
