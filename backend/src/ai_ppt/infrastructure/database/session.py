"""
异步数据库会话管理
提供引擎创建、会话工厂和依赖注入支持
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ai_ppt.infrastructure.config import settings

# 创建异步引擎
engine = create_async_engine(
    str(settings.db_url),
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    echo=settings.db_echo,
    future=True,
)

# 会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖：获取数据库会话

    使用方式:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    上下文管理器形式的数据库会话

    使用方式:
        async with get_session_context() as session:
            await session.execute(...)
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def close_db_connections() -> None:
    """关闭所有数据库连接（用于应用关闭时）"""
    await engine.dispose()


async def init_db() -> None:
    """初始化数据库，创建所有表"""
    from ai_ppt.domain.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
