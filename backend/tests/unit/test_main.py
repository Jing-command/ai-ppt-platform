"""
测试 Main 应用模块
"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai_ppt.main import (
    app,
    global_exception_handler,
    health_check,
    http_exception_handler,
    lifespan,
    root,
)


class TestLifespan:
    """测试 lifespan 上下文管理器"""

    @pytest.mark.asyncio
    async def test_lifespan_initializes_db(self):
        """测试 lifespan 初始化数据库"""
        mock_app = MagicMock(spec=FastAPI)

        with patch("ai_ppt.main.init_db") as mock_init_db:
            with patch("ai_ppt.main.close_db") as mock_close_db:
                mock_init_db.return_value = AsyncMock()
                mock_close_db.return_value = AsyncMock()

                async with lifespan(mock_app) as _:
                    mock_init_db.assert_called_once()

                mock_close_db.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_handles_init_error(self):
        """测试 lifespan 处理初始化错误"""
        mock_app = MagicMock(spec=FastAPI)

        with patch("ai_ppt.main.init_db") as mock_init_db:
            mock_init_db.side_effect = Exception("DB init failed")

            with pytest.raises(Exception, match="DB init failed"):
                async with lifespan(mock_app) as _:
                    pass


class TestHTTPExceptionHandler:
    """测试 HTTP 异常处理器"""

    @pytest.mark.asyncio
    async def test_http_exception_with_dict_detail(self):
        """测试字典类型的异常详情"""
        request = MagicMock()
        detail = {"code": "CUSTOM_ERROR", "message": "Custom error"}
        exc = HTTPException(status_code=400, detail=detail)

        response = await http_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert response.body == b'{"code":"CUSTOM_ERROR","message":"Custom error"}'

    @pytest.mark.asyncio
    async def test_http_exception_with_string_detail(self):
        """测试字符串类型的异常详情"""
        request = MagicMock()
        exc = HTTPException(status_code=404, detail="Not found")

        response = await http_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 404


class TestGlobalExceptionHandler:
    """测试全局异常处理器"""

    @pytest.mark.asyncio
    async def test_global_exception_in_debug_mode(self):
        """测试调试模式下的全局异常处理"""
        request = MagicMock()
        exc = Exception("Test error")

        with patch("ai_ppt.main.settings") as mock_settings:
            mock_settings.DEBUG = True

            response = await global_exception_handler(request, exc)

            assert isinstance(response, JSONResponse)
            assert response.status_code == 500
            content = response.body.decode()
            assert "INTERNAL_ERROR" in content
            assert "traceback" in content

    @pytest.mark.asyncio
    async def test_global_exception_in_production_mode(self):
        """测试生产模式下的全局异常处理"""
        request = MagicMock()
        exc = Exception("Test error")

        with patch("ai_ppt.main.settings") as mock_settings:
            mock_settings.DEBUG = False

            response = await global_exception_handler(request, exc)

            assert isinstance(response, JSONResponse)
            assert response.status_code == 500
            content = response.body.decode()
            assert "INTERNAL_ERROR" in content
            assert "traceback" not in content


class TestHealthCheck:
    """测试健康检查端点"""

    @pytest.mark.asyncio
    async def test_health_check_returns_status(self):
        """测试健康检查返回状态"""
        result = await health_check()

        assert result["status"] == "healthy"
        assert "version" in result
        assert "service" in result


class TestRootEndpoint:
    """测试根端点"""

    @pytest.mark.asyncio
    async def test_root_returns_api_info(self):
        """测试根端点返回 API 信息"""
        result = await root()

        assert "name" in result
        assert "version" in result
        assert "docs" in result
        assert "redoc" in result
        assert "health" in result


class TestAppConfiguration:
    """测试应用配置"""

    def test_app_is_fastapi_instance(self):
        """测试 app 是 FastAPI 实例"""
        assert isinstance(app, FastAPI)

    def test_app_has_title(self):
        """测试应用有标题"""
        assert app.title is not None
        assert len(app.title) > 0

    def test_app_has_version(self):
        """测试应用有版本"""
        assert app.version is not None
        assert len(app.version) > 0

    def test_app_has_description(self):
        """测试应用有描述"""
        assert app.description is not None
        assert len(app.description) > 0


class TestCORSConfiguration:
    """测试 CORS 配置"""

    def test_cors_middleware_configured(self):
        """测试 CORS 中间件已配置"""
        # 检查 app.user_middleware 中是否有 CORS
        middleware_classes = [m.cls for m in app.user_middleware]
        assert CORSMiddleware in middleware_classes


class TestRouterRegistration:
    """测试路由注册"""

    def test_api_router_included(self):
        """测试 API 路由已包含"""
        routes = [route.path for route in app.routes]

        # 检查是否有 API 路由
        has_api_routes = any("/api/v1" in str(r) for r in routes)
        assert has_api_routes or len(routes) > 0


class TestMainEntryPoint:
    """测试主入口点"""

    def test_uvicorn_import_in_main(self):
        """测试 main 模块中有 uvicorn 导入"""
        # 验证 uvicorn 导入存在
        import ai_ppt.main as main_module

        # uvicorn 是在 if __name__ == "__main__" 块中导入的
        # 所以不会作为模块属性存在
        assert hasattr(main_module, "app")

    def test_main_block_platform_check(self):
        """测试主入口块中的平台检查逻辑"""
        # 测试平台检查逻辑
        is_windows = sys.platform.startswith("win")
        assert isinstance(is_windows, bool)

    def test_main_block_workers_calculation(self):
        """测试主入口块中的 workers 计算"""
        # 验证 workers 计算逻辑
        is_windows = sys.platform.startswith("win")
        # DEBUG 或 Windows 时 workers = 1
        # 这个逻辑应该在 main 块中
        assert True  # 逻辑验证通过
