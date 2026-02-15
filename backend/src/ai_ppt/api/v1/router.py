"""
API v1 路由聚合
注册所有 v1 版本的 API 端点
"""

from fastapi import APIRouter

from ai_ppt.api.v1.endpoints import (
    auth,
    chart,
    chat,
    connectors,
    dashboard,
    exports,
    outlines,
    presentations,
    slides,
)

# 创建 v1 主路由
router = APIRouter(prefix="/api/v1")

# 注册子路由
router.include_router(auth.router)
router.include_router(chart.router)
router.include_router(chat.router)
router.include_router(connectors.router)
router.include_router(dashboard.router)
router.include_router(outlines.router)
router.include_router(presentations.router)
# slides router 已包含在 presentations 路径下，不需要单独注册
router.include_router(slides.router)
router.include_router(exports.router)

__all__ = ["router"]
