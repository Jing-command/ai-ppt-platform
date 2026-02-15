"""
测试 AI Models
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List

import pytest

from ai_ppt.infrastructure.ai.models import (
    DataSchema,
    LLMRequest,
    LLMResponse,
    OutlineResult,
    OutlineSection,
    SlideEnhancementRequest,
    SlideEnhancementResult,
    StreamingChunk,
    Usage,
)


class TestUsage:
    """测试 Usage 模型"""

    def test_default_values(self):
        """测试默认值"""
        usage = Usage()

        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0

    def test_custom_values(self):
        """测试自定义值"""
        usage = Usage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        )

        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150


class TestStreamingChunk:
    """测试 StreamingChunk 模型"""

    def test_default_values(self):
        """测试默认值"""
        chunk = StreamingChunk(content="Hello")

        assert chunk.content == "Hello"
        assert chunk.is_finished is False
        assert chunk.index == 0

    def test_custom_values(self):
        """测试自定义值"""
        chunk = StreamingChunk(
            content="World",
            is_finished=True,
            index=5,
        )

        assert chunk.content == "World"
        assert chunk.is_finished is True
        assert chunk.index == 5


class TestLLMResponse:
    """测试 LLMResponse 模型"""

    def test_required_fields(self):
        """测试必填字段"""
        response = LLMResponse(
            content="Test response",
            model="gpt-4",
            provider="openai",
        )

        assert response.content == "Test response"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.usage is not None
        assert response.finish_reason is None
        assert response.latency_ms is None

    def test_full_fields(self):
        """测试完整字段"""
        usage = Usage(prompt_tokens=10, completion_tokens=5)
        response = LLMResponse(
            content="Test",
            model="gpt-4",
            provider="openai",
            usage=usage,
            finish_reason="stop",
            latency_ms=100.0,
        )

        assert response.finish_reason == "stop"
        assert response.latency_ms == 100.0


class TestDataSchema:
    """测试 DataSchema 模型"""

    def test_default_values(self):
        """测试默认值"""
        schema = DataSchema(name="sales")

        assert schema.name == "sales"
        assert schema.columns == []
        assert schema.description is None

    def test_full_values(self):
        """测试完整值"""
        schema = DataSchema(
            name="users",
            columns=["id", "name", "email"],
            description="User table schema",
        )

        assert schema.name == "users"
        assert schema.columns == ["id", "name", "email"]
        assert schema.description == "User table schema"

    def test_to_dict(self):
        """测试 to_dict 方法"""
        schema = DataSchema(
            name="orders",
            columns=["id", "total", "date"],
            description="Orders table",
        )

        data = schema.to_dict()

        assert data["name"] == "orders"
        assert data["columns"] == ["id", "total", "date"]
        assert data["description"] == "Orders table"


class TestOutlineSection:
    """测试 OutlineSection 模型"""

    def test_required_fields(self):
        """测试必填字段"""
        section = OutlineSection(title="Introduction")

        assert section.title == "Introduction"
        assert section.description is None
        assert section.key_points == []
        assert section.estimated_slides == 2
        assert section.visualization_type is None

    def test_full_fields(self):
        """测试完整字段"""
        section = OutlineSection(
            title="Overview",
            description="Brief overview of the topic",
            key_points=["Point 1", "Point 2"],
            estimated_slides=3,
            visualization_type="chart",
        )

        assert section.title == "Overview"
        assert section.description == "Brief overview of the topic"
        assert section.key_points == ["Point 1", "Point 2"]
        assert section.estimated_slides == 3
        assert section.visualization_type == "chart"


class TestOutlineResult:
    """测试 OutlineResult 模型"""

    def test_required_fields(self):
        """测试必填字段"""
        result = OutlineResult(title="Test Outline")

        assert result.title == "Test Outline"
        assert result.sections == []
        assert result.description is None

    def test_full_fields(self):
        """测试完整字段"""
        result = OutlineResult(
            title="Full Outline",
            description="A comprehensive outline",
            sections=[
                OutlineSection(title="Page 1"),
                OutlineSection(title="Page 2"),
            ],
        )

        assert result.title == "Full Outline"
        assert len(result.sections) == 2
        assert result.description == "A comprehensive outline"

    def test_total_slides_property(self):
        """测试总幻灯片数计算属性"""
        result = OutlineResult(
            title="Test",
            sections=[
                OutlineSection(title="S1", estimated_slides=3),
                OutlineSection(title="S2", estimated_slides=5),
            ],
        )

        assert result.total_slides == 8


class TestSlideEnhancementResult:
    """测试 SlideEnhancementResult 模型"""

    def test_required_fields(self):
        """测试必填字段"""
        result = SlideEnhancementResult(content={"text": "Enhanced"})

        assert result.content == {"text": "Enhanced"}
        assert result.changes_summary is None
        assert result.suggestions == []

    def test_full_fields(self):
        """测试完整字段"""
        result = SlideEnhancementResult(
            content={"title": "Enhanced Title", "body": "Enhanced body"},
            changes_summary="Improved formatting",
            suggestions=["Better formatting", "Clearer language"],
        )

        assert result.content == {
            "title": "Enhanced Title",
            "body": "Enhanced body",
        }
        assert result.changes_summary == "Improved formatting"
        assert result.suggestions == ["Better formatting", "Clearer language"]


class TestSlideEnhancementRequest:
    """测试 SlideEnhancementRequest 模型"""

    def test_required_fields(self):
        """测试必填字段"""
        request = SlideEnhancementRequest(content={"text": "Original"})

        assert request.content == {"text": "Original"}
        assert request.enhancement_type == "professional"
        assert request.target_audience is None
        assert request.tone is None

    def test_full_fields(self):
        """测试完整字段"""
        request = SlideEnhancementRequest(
            content={"text": "Original"},
            enhancement_type="creative",
            target_audience="executives",
            tone="formal",
        )

        assert request.content == {"text": "Original"}
        assert request.enhancement_type == "creative"
        assert request.target_audience == "executives"
        assert request.tone == "formal"


class TestLLMRequest:
    """测试 LLMRequest 模型"""

    def test_required_fields(self):
        """测试必填字段"""
        request = LLMRequest(messages=[{"role": "user", "content": "Hello"}])

        assert len(request.messages) == 1
        assert request.temperature == 0.7  # 默认值
        assert request.max_tokens == 4096  # 默认值
        assert request.stream is False  # 默认值
        assert request.response_format is None

    def test_full_fields(self):
        """测试完整字段"""
        request = LLMRequest(
            messages=[
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"},
            ],
            temperature=0.5,
            max_tokens=2048,
            stream=True,
            response_format={"type": "json_object"},
        )

        assert len(request.messages) == 2
        assert request.temperature == 0.5
        assert request.max_tokens == 2048
        assert request.stream is True
        assert request.response_format == {"type": "json_object"}

    def test_model_dump(self):
        """测试 model_dump 方法"""
        request = LLMRequest(
            messages=[{"role": "user", "content": "Test"}],
            temperature=0.8,
        )

        data = request.model_dump()

        assert data["messages"] == [{"role": "user", "content": "Test"}]
        assert data["temperature"] == 0.8
        assert data["stream"] is False


class TestSlideEnhancementRequest:
    """测试 SlideEnhancementRequest 模型"""

    def test_required_fields(self):
        """测试必填字段"""
        request = SlideEnhancementRequest(content={"text": "Original"})

        assert request.content == {"text": "Original"}
        assert request.enhancement_type == "professional"
        assert request.target_audience is None
        assert request.tone is None

    def test_full_fields(self):
        """测试完整字段"""
        request = SlideEnhancementRequest(
            content={"text": "Original"},
            enhancement_type="creative",
            target_audience="executives",
            tone="formal",
        )

        assert request.content == {"text": "Original"}
        assert request.enhancement_type == "creative"
        assert request.target_audience == "executives"
        assert request.tone == "formal"


class TestModelValidation:
    """测试模型验证"""

    def test_outline_result_validation_error(self):
        """测试 OutlineResult 验证错误"""
        # 缺少必填字段
        with pytest.raises(Exception):
            OutlineResult(pages=[])

    def test_llm_response_validation(self):
        """测试 LLMResponse 验证"""
        # 正常情况
        response = LLMResponse(
            content="Test",
            model="gpt-4",
            provider="openai",
        )

        assert response.content == "Test"

    def test_usage_with_negative_tokens(self):
        """测试负数的 token 计数会被验证阻止"""
        # Pydantic 会阻止负数，抛出验证错误
        with pytest.raises(Exception):
            Usage(prompt_tokens=-10)
