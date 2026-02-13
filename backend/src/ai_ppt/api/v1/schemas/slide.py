"""
幻灯片 Schema 定义
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OperationHistoryEntry(BaseModel):
    """操作历史条目"""
    operation_id: str = Field(..., alias="operationId")
    operation_type: str = Field(..., alias="operationType", description="操作类型: add, update, delete, reorder")
    slide_id: Optional[str] = Field(None, alias="slideId")
    description: str
    timestamp: datetime
    can_undo: bool = Field(default=True, alias="canUndo")
    
    model_config = ConfigDict(populate_by_name=True)


class UndoRedoResponse(BaseModel):
    """撤销/重做响应"""
    success: bool
    description: str
    state: Optional[Dict[str, Any]] = None
    slide_id: Optional[str] = Field(None, alias="slideId")
    
    model_config = ConfigDict(populate_by_name=True)


class SlideBulkUpdateRequest(BaseModel):
    """批量更新幻灯片请求"""
    slides: List[Dict[str, Any]] = Field(..., min_length=1, description="幻灯片数据列表")
    
    model_config = ConfigDict(populate_by_name=True)


class SlideBulkUpdateResponse(BaseModel):
    """批量更新响应"""
    success: bool
    updated_count: int = Field(..., alias="updatedCount")
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    
    model_config = ConfigDict(populate_by_name=True)
