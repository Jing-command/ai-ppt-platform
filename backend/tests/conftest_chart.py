"""
图表 API 测试专用配置
绕过数据库依赖，直接测试 API 端点
"""

import os
import sys
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

# 设置测试环境变量
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only-32chars-long"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DEBUG"] = "True"

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

# 导入必要的模块
from ai_ppt.api.v1.router import router as api_router
from ai_ppt.api.v1.endpoints.chart import router as chart_router

# ==================== FastAPI App Fixtures ====================


@pytest.fixture
def app() -> FastAPI:
    """创建测试 FastAPI 应用 - 仅包含图表路由"""
    test_app = FastAPI()
    # 只注册图表路由，避免数据库模型问题
    test_app.include_router(chart_router, prefix="/api/v1/charts")
    return test_app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """创建测试 HTTP 客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
