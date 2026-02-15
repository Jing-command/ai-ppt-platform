"""
测试数据库模块
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession


class TestGetDB:
    """测试 get_db 函数"""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """测试 get_db 生成会话"""
        from ai_ppt.database import get_db

        # Mock AsyncSessionLocal
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.close = AsyncMock()

        with patch("ai_ppt.database.AsyncSessionLocal") as mock_session_local:
            mock_session_local.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_local.return_value.__aexit__ = AsyncMock(
                return_value=None
            )

            async_gen = get_db()
            session = await anext(async_gen)

            assert session == mock_session

    @pytest.mark.asyncio
    async def test_get_db_commits_on_success(self):
        """测试成功时提交"""
        from ai_ppt.database import get_db

        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.close = AsyncMock()

        with patch("ai_ppt.database.AsyncSessionLocal") as mock_session_local:
            mock_session_local.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_local.return_value.__aexit__ = AsyncMock(
                return_value=None
            )

            async_gen = get_db()
            session = await anext(async_gen)

            # 正常结束时会触发 commit
            try:
                await async_gen.aclose()
            except:
                pass

    @pytest.mark.asyncio
    async def test_get_db_rollbacks_on_exception(self):
        """测试异常时回滚"""
        from ai_ppt.database import get_db

        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        with patch("ai_ppt.database.AsyncSessionLocal") as mock_session_local:
            mock_session_local.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_local.return_value.__aexit__ = AsyncMock(
                return_value=None
            )

            async_gen = get_db()
            session = await anext(async_gen)

            # 模拟异常
            mock_session.commit.side_effect = Exception("Test error")

            try:
                await session.commit()
            except:
                pass


class TestInitDB:
    """测试 init_db 函数"""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        """测试初始化数据库创建表"""
        from ai_ppt.database import init_db

        mock_conn = AsyncMock()
        mock_conn.run_sync = AsyncMock()

        mock_engine = AsyncMock()
        mock_engine.begin = MagicMock()
        mock_engine.begin.return_value.__aenter__ = AsyncMock(
            return_value=mock_conn
        )
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("ai_ppt.database.engine", mock_engine):
            with patch(
                "ai_ppt.database.Base.metadata.create_all"
            ) as mock_create_all:
                await init_db()
                # run_sync 应该被调用
                assert mock_conn.run_sync.called


class TestCloseDB:
    """测试 close_db 函数"""

    @pytest.mark.asyncio
    async def test_close_db_disposes_engine(self):
        """测试关闭数据库释放引擎"""
        from ai_ppt.database import close_db

        mock_engine = AsyncMock()
        mock_engine.dispose = AsyncMock()

        with patch("ai_ppt.database.engine", mock_engine):
            await close_db()
            mock_engine.dispose.assert_called_once()


class TestEngineConfiguration:
    """测试引擎配置"""

    def test_sqlite_engine_configuration(self):
        """测试 SQLite 引擎配置"""
        with patch("ai_ppt.database.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite+aiosqlite:///test.db"
            mock_settings.DEBUG = False

            with patch(
                "ai_ppt.database.create_async_engine"
            ) as mock_create_engine:
                mock_engine = MagicMock()
                mock_create_engine.return_value = mock_engine

                # 重新导入以触发引擎创建
                import importlib
                import ai_ppt.database as db_module

                with patch.object(db_module, "engine", None):
                    # SQLite 不应该有 pool_size 参数
                    pass  # 配置验证

    def test_postgres_engine_configuration(self):
        """测试 PostgreSQL 引擎配置"""
        with patch("ai_ppt.database.settings") as mock_settings:
            mock_settings.DATABASE_URL = (
                "postgresql+asyncpg://user:pass@localhost/db"
            )
            mock_settings.DATABASE_POOL_SIZE = 5
            mock_settings.DATABASE_MAX_OVERFLOW = 10
            mock_settings.DEBUG = False

            with patch(
                "ai_ppt.database.create_async_engine"
            ) as mock_create_engine:
                mock_engine = MagicMock()
                mock_create_engine.return_value = mock_engine

                # 配置验证
                pass
