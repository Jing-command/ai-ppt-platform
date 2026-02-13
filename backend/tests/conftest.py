"""
测试配置文件
提供共享的 fixtures 和配置
"""

import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 设置测试环境变量
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only-32chars-long"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DEBUG"] = "True"

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from ai_ppt.api.v1.router import router as api_router
from ai_ppt.config import Settings, get_settings
from ai_ppt.database import get_db
from ai_ppt.domain.models.base import Base
from ai_ppt.models.user import User

# ==================== 数据库 Fixtures ====================


@pytest_asyncio.fixture(scope="session")
async def engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


# ==================== FastAPI App Fixtures ====================


@pytest.fixture
def app(db_session: AsyncSession) -> FastAPI:
    """创建测试 FastAPI 应用"""
    from ai_ppt.main import app

    # 覆盖依赖
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # 覆盖设置
    def override_get_settings() -> Settings:
        return Settings(
            JWT_SECRET_KEY="test-secret-key-for-testing-only-32chars-long",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            DEBUG=True,
        )

    app.dependency_overrides[get_settings] = override_get_settings

    return app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """创建测试 HTTP 客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ==================== 认证 Fixtures ====================


@pytest.fixture
def test_user_id() -> uuid.UUID:
    """测试用户 ID"""
    return uuid.uuid4()


@pytest.fixture
def test_user_data(test_user_id: uuid.UUID) -> dict[str, Any]:
    """测试用户数据"""
    return {
        "id": test_user_id,
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "$2b$12$test_hash",
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def auth_headers(test_user_id: uuid.UUID) -> dict[str, str]:
    """生成认证请求头"""
    from ai_ppt.core.security import create_access_token

    token = create_access_token(test_user_id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def authenticated_user(db_session: AsyncSession) -> Any:
    """创建并返回已认证的测试用户"""
    from ai_ppt.core.security import get_password_hash
    from ai_ppt.models.user import User

    # 使用唯一 ID 和邮箱避免冲突
    unique_id = uuid.uuid4()
    user = User(
        id=unique_id,
        email=f"test_{unique_id.hex[:8]}@example.com",
        username=f"testuser_{unique_id.hex[:8]}",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ==================== Mock Fixtures ====================


@pytest.fixture
def mock_llm_client():
    """模拟 LLM 客户端"""
    with patch("ai_ppt.infrastructure.ai.client.LLMClient") as mock:
        instance = MagicMock()
        instance.complete = AsyncMock()
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_export_service():
    """模拟导出服务"""
    with patch("ai_ppt.services.export_service.ExportService") as mock:
        instance = MagicMock()
        instance.create_task = AsyncMock()
        instance.get_task = AsyncMock()
        mock.return_value = instance
        yield instance


# ==================== 工具 Fixtures ====================


@pytest.fixture
def sample_outline_pages() -> list[dict[str, Any]]:
    """示例大纲页面数据"""
    return [
        {
            "id": "page-1",
            "pageNumber": 1,
            "title": "封面",
            "content": "演示文稿封面",
            "pageType": "title",
            "imagePrompt": "科技感背景",
        },
        {
            "id": "page-2",
            "pageNumber": 2,
            "title": "内容页",
            "content": "主要内容",
            "pageType": "content",
        },
    ]


@pytest.fixture
def sample_presentation_data() -> dict[str, Any]:
    """示例 PPT 数据"""
    return {
        "title": "测试演示文稿",
        "description": "这是一个测试PPT",
        "templateId": "default",
    }


@pytest.fixture
def sample_slide_data() -> dict[str, Any]:
    """示例幻灯片数据"""
    return {
        "type": "content",
        "content": {
            "title": "测试幻灯片",
            "text": "这是测试内容",
        },
        "layout": {
            "type": "title_content",
        },
    }


@pytest.fixture
def sample_connector_config() -> dict[str, Any]:
    """示例连接器配置"""
    return {
        "host": "localhost",
        "port": 3306,
        "database": "test_db",
        "username": "test_user",
        "password": "test_pass",
    }
