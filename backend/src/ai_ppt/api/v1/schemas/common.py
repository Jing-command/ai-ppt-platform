"""
通用 Schema 定义
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """统一错误响应格式"""
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误信息")
    details: Optional[Dict[str, Any]] = Field(None, description="详细错误信息")


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = Field(..., alias="page")
    page_size: int = Field(..., alias="pageSize")
    total: int = Field(..., description="总记录数")
    total_pages: int = Field(..., alias="totalPages", description="总页数")
    
    model_config = ConfigDict(populate_by_name=True)


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    data: List[T]
    meta: PaginationMeta


class SuccessResponse(BaseModel):
    """成功响应格式"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class TaskStatusResponse(BaseModel):
    """异步任务状态响应"""
    task_id: UUID = Field(..., alias="taskId")
    status: str = Field(..., description="任务状态: pending, processing, completed, failed")
    progress: int = Field(default=0, ge=0, le=100, description="进度百分比")
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = Field(None, alias="errorMessage")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    
    model_config = ConfigDict(populate_by_name=True)
