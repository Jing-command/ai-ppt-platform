"""
数据库连接管理
SQLAlchemy 异步会话配置
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ai_ppt.config import settings
from ai_ppt.domain.models.base import Base

# 创建异步引擎
# 使用 NullPool 在测试环境中避免连接池问题
echo = settings.DEBUG

# SQLite 不支持连接池参数，需要特殊处理
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=echo,
        pool_pre_ping=True,  # 自动检测断开的连接
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=echo,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
    )

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    依赖注入用的数据库会话生成器

    使用示例：
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
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


async def init_db() -> None:
    """
    初始化数据库，创建所有表
    用于应用启动时调用
    """
    # 导入所有模型以确保它们被注册到 Base.metadata
    from ai_ppt.domain.models.connector import Connector  # noqa: F401
    from ai_ppt.domain.models.outline import Outline  # noqa: F401
    from ai_ppt.domain.models.presentation import Presentation  # noqa: F401
    from ai_ppt.domain.models.slide import Slide  # noqa: F401
    from ai_ppt.models.user import User  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    关闭数据库连接
    用于应用关闭时调用
    """
    await engine.dispose()
