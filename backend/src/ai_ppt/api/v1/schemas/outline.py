"""
大纲 Schema 定义 - 更新版，匹配 API Contract v1.0
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OutlinePage(BaseModel):
    """大纲页面（对应 API Contract 的 OutlineSection）"""

    id: str = Field(
        default_factory=lambda: str(UUID(int=0)), description="页面ID"
    )
    page_number: int = Field(..., ge=1, alias="pageNumber", description="页码")
    title: str = Field(
        ..., min_length=1, max_length=200, description="页面标题"
    )
    content: Optional[str] = Field(
        None, max_length=1000, description="页面内容描述"
    )
    page_type: str = Field(
        default="content",
        alias="pageType",
        description="页面类型: title, content, section, chart, conclusion",
    )
    layout: Optional[str] = Field(None, description="布局模板")
    notes: Optional[str] = Field(None, description="演讲备注")
    image_prompt: Optional[str] = Field(
        None, alias="imagePrompt", description="插图提示词"
    )

    model_config = ConfigDict(populate_by_name=True)


class OutlineBackground(BaseModel):
    """PPT背景设置"""

    type: str = Field(default="ai", description="背景类型: ai, upload, solid")
    prompt: Optional[str] = Field(None, description="AI生成背景时的提示词")
    url: Optional[str] = Field(None, description="上传图片的URL")
    color: Optional[str] = Field(None, description="纯色背景的颜色值 (hex)")
    opacity: float = Field(
        default=1.0, ge=0.0, le=1.0, description="背景透明度"
    )
    blur: float = Field(
        default=0.0, ge=0.0, le=20.0, description="背景模糊度(px)"
    )

    model_config = ConfigDict(populate_by_name=True)


class OutlineBase(BaseModel):
    """大纲基础模型"""

    title: str = Field(
        ..., min_length=1, max_length=200, description="大纲标题"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="描述"
    )


class OutlineCreate(OutlineBase):
    """手动创建大纲请求"""

    pages: List[OutlinePage] = Field(
        default_factory=list, description="页面列表"
    )
    background: Optional[OutlineBackground] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "人工智能发展概述",
                "description": "介绍AI发展历程、现状和未来趋势",
                "pages": [
                    {
                        "id": "page-1",
                        "pageNumber": 1,
                        "title": "封面",
                        "content": "人工智能发展概述",
                        "pageType": "title",
                        "imagePrompt": "科技感背景，蓝色渐变",
                    },
                    {
                        "id": "page-2",
                        "pageNumber": 2,
                        "title": "AI的起源",
                        "content": "早期人工智能发展历程",
                        "pageType": "content",
                    },
                ],
                "background": {"type": "ai", "prompt": "科技感蓝色渐变背景"},
            }
        },
    )


class OutlineGenerateRequest(BaseModel):
    """AI 生成大纲请求"""

    prompt: str = Field(
        ..., min_length=10, max_length=2000, description="主题描述"
    )
    num_slides: int = Field(
        default=10, ge=3, le=50, alias="numSlides", description="PPT总页数"
    )
    language: str = Field(default="zh", pattern="^(zh|en)$")
    style: str = Field(
        default="business",
        description="风格: business, education, creative, technical",
    )
    context_data: Optional[Dict[str, Any]] = Field(
        None, alias="contextData", description="上下文数据"
    )
    connector_id: Optional[UUID] = Field(
        None, alias="connectorId", description="关联的数据源ID"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "prompt": "制作一个关于人工智能在医疗领域应用的PPT",
                "numSlides": 10,
                "language": "zh",
                "style": "business",
            }
        },
    )


class OutlineGenerateResponse(BaseModel):
    """AI 生成大纲响应"""

    task_id: UUID = Field(..., alias="taskId")
    status: str = Field(
        ..., description="状态: pending, processing, completed, failed"
    )
    estimated_time: int = Field(
        ..., ge=0, alias="estimatedTime", description="预估时间(秒)"
    )
    message: str

    model_config = ConfigDict(populate_by_name=True)


class OutlineUpdate(BaseModel):
    """更新大纲请求"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    pages: Optional[List[OutlinePage]] = None
    background: Optional[OutlineBackground] = None
    status: Optional[str] = Field(
        None, description="状态: draft, generating, completed, archived"
    )

    model_config = ConfigDict(populate_by_name=True)


class OutlineResponse(OutlineBase):
    """大纲响应"""

    id: UUID
    user_id: UUID = Field(..., alias="userId")
    pages: List[OutlinePage] = Field(default_factory=list)
    background: Optional[OutlineBackground] = None
    total_slides: int = Field(
        default=0, alias="totalSlides", description="总页数"
    )
    status: str = Field(
        default="draft",
        description="状态: draft, generating, completed, archived",
    )
    ai_prompt: Optional[str] = Field(None, alias="aiPrompt")
    ai_parameters: Optional[Dict[str, Any]] = Field(None, alias="aiParameters")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    generated_at: Optional[datetime] = Field(None, alias="generatedAt")

    model_config = ConfigDict(populate_by_name=True)


class OutlineDetailResponse(OutlineResponse):
    """大纲详情响应"""


class OutlineToPresentationRequest(BaseModel):
    """基于大纲创建 PPT 请求"""

    title: Optional[str] = Field(
        None, description="自定义标题，默认使用大纲标题"
    )
    template_id: Optional[str] = Field(
        None, alias="templateId", description="模板ID"
    )
    theme: Optional[str] = Field(None, description="主题风格")
    slide_layout: str = Field(
        default="auto",
        alias="slideLayout",
        description="幻灯片布局: auto, detailed, minimal",
    )
    generate_content: bool = Field(
        default=True,
        alias="generateContent",
        description="是否使用AI生成详细内容",
    )
    provider: Optional[str] = Field(None, description="指定 AI 提供商")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "templateId": "business-modern",
                "theme": "blue",
                "slideLayout": "auto",
                "generateContent": True,
            }
        },
    )


class OutlineToPresentationResponse(BaseModel):
    """基于大纲创建 PPT 响应"""

    presentation_id: UUID = Field(..., alias="presentationId")
    task_id: UUID = Field(..., alias="taskId")
    status: str
    message: str
    estimated_time: int = Field(..., alias="estimatedTime")

    model_config = ConfigDict(populate_by_name=True)
