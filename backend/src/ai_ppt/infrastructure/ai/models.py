"""
LLM Pydantic 模型
定义 AI 请求/响应的数据结构
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class Usage(BaseModel):
    """LLM Token 使用统计"""

    model_config = ConfigDict(frozen=True)

    prompt_tokens: int = Field(default=0, ge=0, description="输入 token 数量")
    completion_tokens: int = Field(default=0, ge=0, description="输出 token 数量")
    total_tokens: int = Field(default=0, ge=0, description="总 token 数量")

    @property
    def cost_estimate(self) -> float:
        """估算成本（基于 OpenAI GPT-4 定价，仅供参考）"""
        # GPT-4 Turbo: $0.01 / 1K input, $0.03 / 1K output
        input_cost = (self.prompt_tokens / 1000) * 0.01
        output_cost = (self.completion_tokens / 1000) * 0.03
        return round(input_cost + output_cost, 6)


class LLMRequest(BaseModel):
    """LLM 请求模型"""

    model_config = ConfigDict(extra="allow")

    messages: List[Dict[str, str]] = Field(
        ..., description="消息列表，格式: [{role: system|user|assistant, content: str}]"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="采样温度，越高越随机")
    max_tokens: int = Field(default=4096, ge=1, le=128000, description="最大生成 token 数")
    response_format: Optional[Dict[str, str]] = Field(
        default=None, description="响应格式，如 {'type': 'json_object'}"
    )
    stream: bool = Field(default=False, description="是否使用流式响应")


class LLMResponse(BaseModel):
    """LLM 响应模型"""

    model_config = ConfigDict(frozen=True)

    content: str = Field(..., description="生成的内容")
    model: str = Field(..., description="使用的模型名称")
    provider: Literal["openai", "deepseek", "kimi"] = Field(..., description="LLM 提供商")
    usage: Usage = Field(default_factory=Usage, description="Token 使用统计")
    finish_reason: Optional[str] = Field(
        default=None, description="完成原因: stop, length, content_filter 等"
    )
    latency_ms: Optional[float] = Field(default=None, description="请求延迟（毫秒）")


class StreamingChunk(BaseModel):
    """流式响应块"""

    model_config = ConfigDict(frozen=True)

    content: str = Field(..., description="内容块")
    is_finished: bool = Field(default=False, description="是否为最后一块")
    index: Optional[int] = Field(default=None, description="块序号")


class DataSchema(BaseModel):
    """数据源表结构描述"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="表名/对象名")
    columns: List[str] = Field(default_factory=list, description="字段列表")
    description: Optional[str] = Field(default=None, description="表描述")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "columns": self.columns,
            "description": self.description,
        }


class OutlineSection(BaseModel):
    """大纲章节"""

    model_config = ConfigDict(extra="allow")

    title: str = Field(..., description="章节标题")
    description: Optional[str] = Field(default=None, description="章节描述")
    key_points: List[str] = Field(default_factory=list, description="关键要点")
    estimated_slides: int = Field(default=2, ge=1, description="预计幻灯片数量")
    visualization_type: Optional[str] = Field(
        default=None, description="建议的可视化类型: chart, table, text, image"
    )


class OutlineResult(BaseModel):
    """大纲生成结果"""

    model_config = ConfigDict(extra="allow")

    title: str = Field(..., description="PPT 标题")
    description: Optional[str] = Field(default=None, description="PPT 描述")
    sections: List[OutlineSection] = Field(default_factory=list, description="章节列表")

    @property
    def total_slides(self) -> int:
        """计算总幻灯片数量"""
        return sum(section.estimated_slides for section in self.sections)


class SlideEnhancementRequest(BaseModel):
    """幻灯片内容增强请求"""

    model_config = ConfigDict(extra="allow")

    content: Dict[str, Any] = Field(..., description="原始内容")
    enhancement_type: Literal["professional", "concise", "storytelling", "creative"] = Field(
        default="professional", description="增强类型"
    )
    target_audience: Optional[str] = Field(default=None, description="目标受众")
    tone: Optional[str] = Field(default=None, description="语气风格")


class SlideEnhancementResult(BaseModel):
    """幻灯片内容增强结果"""

    model_config = ConfigDict(extra="allow")

    content: Dict[str, Any] = Field(..., description="增强后的内容")
    changes_summary: Optional[str] = Field(default=None, description="变更摘要")
    suggestions: List[str] = Field(default_factory=list, description="额外建议")
