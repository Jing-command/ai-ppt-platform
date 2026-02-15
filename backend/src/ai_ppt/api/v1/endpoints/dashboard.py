"""
Dashboard API - 仪表盘统计接口
提供 Dashboard 页面所需的统计数据
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ai_ppt.api.deps import get_current_user
from ai_ppt.api.v1.schemas.common import ErrorResponse
from ai_ppt.api.v1.schemas.dashboard import DashboardStatsResponse
from ai_ppt.database import get_db
from ai_ppt.domain.models.outline import Outline
from ai_ppt.domain.models.presentation import Presentation, PresentationStatus
from ai_ppt.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_week_start() -> datetime:
    """获取本周开始时间（周一 00:00:00）"""
    now = datetime.now(timezone.utc)
    # weekday(): Monday is 0, Sunday is 6
    days_since_monday = now.weekday()
    monday = now - timedelta(days=days_since_monday)
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def get_seven_days_ago() -> datetime:
    """获取7天前的时间"""
    return datetime.now(timezone.utc) - timedelta(days=7)


def format_relative_time(updated_at: datetime) -> str:
    """
    将时间格式化为相对时间（人性化格式）
    如：2小时前、昨天、3天前
    """
    now = datetime.now(timezone.utc)
    # 如果 updated_at 没有时区信息，假设它是 UTC
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    diff = now - updated_at

    # 小于1分钟
    if diff.total_seconds() < 60:
        return "刚刚"

    # 小于1小时
    if diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() // 60)
        return f"{minutes}分钟前"

    # 小于24小时
    if diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() // 3600)
        return f"{hours}小时前"

    # 小于48小时（昨天）
    if diff.total_seconds() < 172800:
        return "昨天"

    # 小于30天
    if diff.days < 30:
        return f"{diff.days}天前"

    # 小于365天
    if diff.days < 365:
        months = diff.days // 30
        return f"{months}个月前"

    # 超过1年
    years = diff.days // 365
    return f"{years}年前"


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
    summary="获取 Dashboard 统计数据",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    获取 Dashboard 统计数据

    返回当前用户的统计数据：
    - totalOutlines: 总大纲数
    - createdThisWeek: 本周创建数（大纲+PPT）
    - completedPpts: 已完成 PPT 数（published 状态）
    - recentEdits: 最近7天编辑数
    - recentActivities: 最近5条编辑记录
    """
    try:
        user_id = current_user.id
        week_start = get_week_start()
        seven_days_ago = get_seven_days_ago()

        # 1. 总大纲数
        total_outlines_result = await db.execute(
            select(func.count())
            .select_from(Outline)
            .where(Outline.user_id == user_id)
        )
        total_outlines = total_outlines_result.scalar() or 0

        # 2. 本周创建的大纲数
        outlines_this_week_result = await db.execute(
            select(func.count())
            .select_from(Outline)
            .where(
                Outline.user_id == user_id, Outline.created_at >= week_start
            )
        )
        outlines_this_week = outlines_this_week_result.scalar() or 0

        # 3. 本周创建的 PPT 数
        ppts_this_week_result = await db.execute(
            select(func.count())
            .select_from(Presentation)
            .where(
                Presentation.owner_id == user_id,
                Presentation.created_at >= week_start,
            )
        )
        ppts_this_week = ppts_this_week_result.scalar() or 0

        created_this_week = outlines_this_week + ppts_this_week

        # 4. 已完成的 PPT 数（published 状态）
        completed_ppts_result = await db.execute(
            select(func.count())
            .select_from(Presentation)
            .where(
                Presentation.owner_id == user_id,
                Presentation.status == PresentationStatus.PUBLISHED,
            )
        )
        completed_ppts = completed_ppts_result.scalar() or 0

        # 5. 最近7天编辑数（大纲和 PPT 的 updated_at 在7天内）
        recent_outlines_result = await db.execute(
            select(func.count())
            .select_from(Outline)
            .where(
                Outline.user_id == user_id,
                Outline.updated_at >= seven_days_ago,
            )
        )
        recent_outlines = recent_outlines_result.scalar() or 0

        recent_ppts_result = await db.execute(
            select(func.count())
            .select_from(Presentation)
            .where(
                Presentation.owner_id == user_id,
                Presentation.updated_at >= seven_days_ago,
            )
        )
        recent_ppts = recent_ppts_result.scalar() or 0

        recent_edits = recent_outlines + recent_ppts

        # 6. 最近5条编辑记录
        # 查询大纲
        outlines_query = (
            select(
                Outline.id,
                Outline.title,
                Outline.status,
                Outline.updated_at,
            )
            .where(Outline.user_id == user_id)
            .order_by(Outline.updated_at.desc())
            .limit(5)
        )

        # 查询 PPT
        ppts_query = (
            select(
                Presentation.id,
                Presentation.title,
                Presentation.status,
                Presentation.updated_at,
            )
            .where(Presentation.owner_id == user_id)
            .order_by(Presentation.updated_at.desc())
            .limit(5)
        )

        outlines_result = await db.execute(outlines_query)
        ppts_result = await db.execute(ppts_query)

        # 合并并排序
        activities: List[Dict[str, Any]] = []

        # 处理大纲结果
        for row in outlines_result.all():
            activities.append(
                {
                    "id": str(row[0]),
                    "title": row[1],
                    "type": "outline",
                    "status": str(row[2]),
                    "updated_at": row[3],
                    "sort_key": row[3],
                }
            )

        # 处理 PPT 结果
        for row in ppts_result.all():  # type: ignore[assignment]
            activities.append(
                {
                    "id": str(row[0]),
                    "title": row[1],
                    "type": "ppt",
                    "status": (
                        str(row[2].value)
                        if hasattr(row[2], "value")
                        else str(row[2])
                    ),
                    "updated_at": row[3],
                    "sort_key": row[3],
                }
            )

        # 按时间排序并取前5条
        activities.sort(key=lambda x: x["sort_key"], reverse=True)
        activities = activities[:5]

        # 构建响应 - 使用字典避免 mypy 类型检查问题
        return DashboardStatsResponse.model_validate(
            {
                "totalOutlines": total_outlines,
                "createdThisWeek": created_this_week,
                "completedPpts": completed_ppts,
                "recentEdits": recent_edits,
                "recentActivities": [
                    {
                        "id": a["id"],
                        "title": a["title"],
                        "type": a["type"],
                        "status": a["status"],
                        "updatedAt": format_relative_time(a["updated_at"]),
                    }
                    for a in activities
                ],
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"获取统计数据失败: {str(e)}",
            },
        )
