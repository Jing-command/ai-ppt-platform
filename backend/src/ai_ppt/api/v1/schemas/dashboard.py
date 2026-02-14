"""
Dashboard Schema - 仪表盘数据模型
定义 Dashboard 统计数据的请求/响应结构
"""

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecentActivity(BaseModel):
    """最近活动项"""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="活动项 ID")
    title: str = Field(..., description="标题")
    type: Literal["outline", "ppt"] = Field(..., description="类型: outline 或 ppt")
    status: Literal["completed", "draft", "published", "generating", "archived"] = Field(
        ..., description="状态"
    )
    updated_at: str = Field(..., alias="updatedAt", description="更新时间（人性化格式）")


class DashboardStatsResponse(BaseModel):
    """Dashboard 统计数据响应"""

    model_config = ConfigDict(populate_by_name=True)

    total_outlines: int = Field(..., alias="totalOutlines", description="总大纲数")
    created_this_week: int = Field(
        ..., alias="createdThisWeek", description="本周创建数"
    )
    completed_ppts: int = Field(..., alias="completedPpts", description="已完成 PPT 数")
    recent_edits: int = Field(..., alias="recentEdits", description="最近编辑数")
    recent_activities: List[RecentActivity] = Field(
        ..., alias="recentActivities", description="最近活动列表"
    )
