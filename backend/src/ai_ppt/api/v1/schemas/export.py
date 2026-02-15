"""
导出任务 Schema 定义
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExportRequest(BaseModel):
    """导出请求"""

    format: str = Field(
        ..., pattern="^(pptx|pdf|png|jpg)$", description="导出格式"
    )
    quality: str = Field(
        default="standard", pattern="^(standard|high)$", description="导出质量"
    )
    slide_range: Optional[str] = Field(
        None, alias="slideRange", description="页面范围，如 '1-5' 或 'all'"
    )
    include_notes: bool = Field(
        default=False, alias="includeNotes", description="是否包含备注"
    )

    model_config = ConfigDict(populate_by_name=True)


class ExportResponse(BaseModel):
    """导出任务响应"""

    task_id: UUID = Field(..., alias="taskId")
    status: str = Field(
        ..., description="状态: pending, processing, completed, failed"
    )
    download_url: Optional[str] = Field(None, alias="downloadUrl")
    file_size: Optional[int] = Field(
        None, alias="fileSize", description="文件大小（字节）"
    )
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)


class ExportStatusResponse(BaseModel):
    """导出状态响应"""

    task_id: UUID = Field(..., alias="taskId")
    presentation_id: UUID = Field(..., alias="presentationId")
    format: str
    status: str  # pending, processing, completed, failed
    progress: int = Field(default=0, ge=0, le=100, description="进度百分比")
    file_path: Optional[str] = Field(None, alias="filePath")
    file_size: Optional[int] = Field(None, alias="fileSize")
    error_message: Optional[str] = Field(None, alias="errorMessage")
    download_url: Optional[str] = Field(None, alias="downloadUrl")
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")
    created_at: datetime = Field(..., alias="createdAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")

    model_config = ConfigDict(populate_by_name=True)


class PptxExportOptions(BaseModel):
    """PPTX 导出选项"""

    template: Optional[str] = None
    include_notes: bool = Field(default=False, alias="includeNotes")
    compress_images: bool = Field(default=True, alias="compressImages")

    model_config = ConfigDict(populate_by_name=True)


class PdfExportOptions(BaseModel):
    """PDF 导出选项"""

    page_size: str = Field(
        default="16:9", alias="pageSize", description="页面尺寸: 16:9, 4:3, A4"
    )
    quality: str = Field(default="standard", pattern="^(standard|high|print)$")
    include_notes: bool = Field(default=False, alias="includeNotes")

    model_config = ConfigDict(populate_by_name=True)
