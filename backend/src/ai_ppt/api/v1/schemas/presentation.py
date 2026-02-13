"""
PPT 演示文稿 Schema 定义
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ==================== Slide 模型 ====================

class SlideContent(BaseModel):
    """幻灯片内容 - 支持任意额外字段以适应不同布局"""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    text: Optional[str] = None
    second_column: Optional[str] = Field(None, alias="secondColumn")
    bullets: Optional[List[str]] = None
    image_url: Optional[str] = Field(None, alias="imageUrl")
    chart_data: Optional[Dict[str, Any]] = Field(None, alias="chartData")
    
    # Additional fields for various layouts
    stats: Optional[List[Dict[str, Any]]] = None  # data layout
    events: Optional[List[Dict[str, Any]]] = None  # timeline layout
    steps: Optional[List[str]] = None  # process layout
    items: Optional[List[Dict[str, Any]]] = None  # grid/comparison layout
    left: Optional[Dict[str, Any]] = None  # two-column layout
    right: Optional[Dict[str, Any]] = None  # two-column layout
    quote: Optional[str] = None  # quote layout
    author: Optional[str] = None  # quote layout
    
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class SlideLayout(BaseModel):
    """幻灯片布局"""
    type: str = Field(..., description="布局类型: title, content, split, image, chart, timeline, data, quote")
    background: Optional[str] = None
    theme: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class SlideStyle(BaseModel):
    """幻灯片样式"""
    font_family: Optional[str] = Field(None, alias="fontFamily")
    font_size: Optional[int] = Field(None, alias="fontSize")
    color: Optional[str] = None
    alignment: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class Slide(BaseModel):
    """幻灯片"""
    id: Optional[Union[str, UUID]] = None
    type: str = Field(default="content", description="幻灯片类型")
    content: Union[SlideContent, Dict[str, Any]] = Field(..., description="幻灯片内容")
    layout: Optional[SlideLayout] = None
    style: Optional[Union[SlideStyle, Dict[str, Any]]] = None
    notes: Optional[str] = None
    order_index: int = Field(default=0, alias="orderIndex")
    
    model_config = ConfigDict(extra="allow", populate_by_name=True, arbitrary_types_allowed=True)
    
    @model_validator(mode='before')
    @classmethod
    def map_slide_fields(cls, data: Any) -> Any:
        """映射 SQLAlchemy Slide 模型字段"""
        if hasattr(data, '__dict__'):
            data_dict = dict(data.__dict__)
            # 将 layout_type 映射为 type
            if hasattr(data, 'layout_type'):
                data_dict['type'] = data.layout_type
            # 将 content 保持为 dict
            if hasattr(data, 'content') and data.content is None:
                data_dict['content'] = {}
            return data_dict
        return data


# ==================== PPT 请求/响应 ====================

class PresentationBase(BaseModel):
    """PPT 基础模型"""
    title: str = Field(..., min_length=1, max_length=255)


class PresentationCreate(PresentationBase):
    """创建 PPT 请求"""
    description: Optional[str] = Field(None, max_length=1000, description="PPT 描述")
    template_id: Optional[str] = Field(None, alias="templateId", description="模板 ID")
    outline_id: Optional[UUID] = Field(None, alias="outlineId", description="关联的大纲ID")
    slides: Optional[List[Slide]] = Field(default_factory=list)
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "AI 产品介绍",
                "description": "这是一个关于 AI 产品的介绍 PPT",
                "templateId": "business-modern",
                "slides": []
            }
        }
    )


class PresentationUpdate(BaseModel):
    """更新 PPT 请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    slides: Optional[List[Slide]] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")
    template_id: Optional[str] = Field(None, alias="templateId")
    
    model_config = ConfigDict(populate_by_name=True)


class PresentationResponse(PresentationBase):
    """PPT 响应"""
    id: UUID
    owner_id: UUID = Field(..., alias="ownerId")
    outline_id: Optional[UUID] = Field(None, alias="outlineId")
    template_id: Optional[str] = Field(None, alias="templateId")
    slide_count: int = Field(default=0, alias="slideCount", description="幻灯片数量")
    status: str = Field(default="draft", description="状态: draft, published, archived")
    version: int = Field(default=1)
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True)
    
    @model_validator(mode='before')
    @classmethod
    def map_fields(cls, data: Any) -> Any:
        """映射字段：theme -> template_id"""
        if hasattr(data, '__dict__'):
            data_dict = dict(data.__dict__)
            # 将 theme 映射为 template_id
            if hasattr(data, 'theme'):
                data_dict['template_id'] = data.theme
            return data_dict
        return data


class PresentationDetailResponse(PresentationBase):
    """PPT 详情响应"""
    id: UUID
    owner_id: UUID = Field(..., alias="ownerId")
    outline_id: Optional[UUID] = Field(None, alias="outlineId")
    template_id: Optional[str] = Field(None, alias="templateId")
    description: Optional[str] = None
    slides: List[Slide] = Field(default_factory=list)
    slide_count: int = Field(default=0, alias="slideCount")
    status: str = Field(default="draft")
    version: int = Field(default=1)
    ai_prompt: Optional[str] = Field(None, alias="aiPrompt")
    ai_parameters: Optional[Dict[str, Any]] = Field(None, alias="aiParameters")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True)
    
    @model_validator(mode='before')
    @classmethod
    def map_fields(cls, data: Any) -> Any:
        """映射字段：theme -> template_id"""
        if hasattr(data, '__dict__'):
            data_dict = dict(data.__dict__)
            # 将 theme 映射为 template_id
            if hasattr(data, 'theme'):
                data_dict['template_id'] = data.theme
            return data_dict
        return data
    
    @model_validator(mode='before')
    @classmethod
    def calculate_slide_count(cls, data: Any) -> Any:
        """自动计算 slide_count"""
        if hasattr(data, 'slides'):
            slides = data.slides
            if isinstance(slides, list):
                if hasattr(data, '__dict__'):
                    data_dict = dict(data.__dict__)
                    data_dict['slide_count'] = len(slides)
                    return data_dict
        return data


# ==================== 幻灯片操作 ====================

class SlideCreate(BaseModel):
    """添加幻灯片请求"""
    type: str = Field(default="content", description="幻灯片类型")
    content: SlideContent
    layout: Optional[SlideLayout] = None
    style: Optional[SlideStyle] = None
    notes: Optional[str] = None
    position: Optional[int] = Field(None, ge=0, description="插入位置，None 表示末尾")
    
    model_config = ConfigDict(populate_by_name=True)


class SlideUpdate(BaseModel):
    """更新幻灯片请求"""
    type: Optional[str] = None
    content: Optional[SlideContent] = None
    layout: Optional[SlideLayout] = None
    style: Optional[SlideStyle] = None
    notes: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0, alias="orderIndex")
    
    model_config = ConfigDict(populate_by_name=True)


class SlideResponse(Slide):
    """幻灯片响应"""
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True, arbitrary_types_allowed=True)


class SlideReorderRequest(BaseModel):
    """重新排序幻灯片请求"""
    slide_ids: List[str] = Field(..., alias="slideIds", min_length=1, description="幻灯片ID顺序列表")
    
    model_config = ConfigDict(populate_by_name=True)


class SlideDuplicateRequest(BaseModel):
    """复制幻灯片请求"""
    target_position: Optional[int] = Field(None, ge=0, alias="targetPosition")
    
    model_config = ConfigDict(populate_by_name=True)


class GenerateFromOutlineRequest(BaseModel):
    """从大纲生成 PPT 请求"""
    outline_id: UUID = Field(..., alias="outlineId")
    template_id: Optional[str] = Field(None, alias="templateId")
    theme: Optional[str] = None
    generate_content: bool = Field(default=True, alias="generateContent")
    provider: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class GenerateRequest(BaseModel):
    """直接生成 PPT 请求（无需大纲）"""
    prompt: str = Field(..., min_length=10, max_length=2000, description="生成提示词")
    template_id: Optional[str] = Field(None, alias="templateId", description="模板 ID")
    num_slides: int = Field(default=10, ge=1, le=50, alias="numSlides")
    language: str = Field(default="zh", pattern="^(zh|en)$")
    style: str = Field(default="business", description="风格: business, education, creative, minimal")
    provider: Optional[str] = Field(None, description="指定 AI 提供商")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "prompt": "制作一个关于人工智能发展历程的 PPT",
                "numSlides": 8,
                "language": "zh",
                "style": "business"
            }
        }
    )


class GenerateResponse(BaseModel):
    """生成任务响应"""
    task_id: UUID = Field(..., alias="taskId")
    status: str
    estimated_time: int = Field(..., alias="estimatedTime", description="预估秒数")
    message: str
    
    model_config = ConfigDict(populate_by_name=True)


class GenerateStatusResponse(BaseModel):
    """生成状态响应"""
    task_id: UUID = Field(..., alias="taskId")
    status: str  # pending, processing, completed, failed, cancelled
    progress: int  # 0-100
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = Field(None, alias="errorMessage")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
