"""
FastAPI 主应用入口

功能：
- FastAPI 应用实例
- 生命周期管理（lifespan）
- 异常处理器
- CORS 配置
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai_ppt.api.v1.router import router as api_router
from ai_ppt.config import settings
from ai_ppt.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    应用生命周期管理

    启动时：
        - 初始化数据库
        - 加载配置

    关闭时：
        - 关闭数据库连接
        - 清理资源
    """
    # 启动
    try:
        await init_db()
        print(
            f"[START] {settings.APP_NAME} v{settings.APP_VERSION} started successfully"
        )
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        raise

    yield

    # 关闭
    try:
        await close_db()
        print("[STOP] Application stopped")
    except Exception as e:
        print(f"[ERROR] Error during shutdown: {e}")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    AI PPT Generator - 智能 PPT 生成服务

    ## 功能特性
    - 🤖 AI 自动生成大纲和 PPT 内容
    - 🔌 多数据源连接器支持（MySQL, PostgreSQL, MongoDB 等）
    - 📝 对话式 PPT 编辑
    - 🎨 丰富的模板和主题系统
    - 📤 多格式导出（PPTX, PDF）
    - ↩️ 撤销/重做操作历史

    ## 认证方式
    所有需要认证的接口都需要在请求头中传递：
    ```
    Authorization: Bearer {your_jwt_token}
    ```

    ## API 版本
    - 当前版本: v1
    - 基础路径: /api/v1
    """,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc 文档
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={"name": "AI PPT Team", "email": "support@aippt.example.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # 用于文件下载
)


# ==================== 异常处理器 ====================


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """
    统一 HTTP 异常返回格式

    将所有 HTTP 异常转换为统一的 JSON 格式
    """
    if isinstance(exc.detail, dict):
        content = exc.detail
    else:
        content = {"code": "HTTP_ERROR", "message": exc.detail}

    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    全局异常处理

    捕获所有未处理的异常，返回统一的错误格式
    生产环境不暴露详细错误信息
    """
    import traceback

    error_message = str(exc)

    # 开发模式显示详细错误
    if settings.DEBUG:
        content = {
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误",
            "details": {
                "error": error_message,
                "traceback": traceback.format_exc().split("\n"),
            },
        }
    else:
        content = {
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误，请稍后重试",
        }

    # 记录错误日志
    print(f"[ERROR] {error_message}")

    return JSONResponse(status_code=500, content=content)


# ==================== 路由注册 ====================


# 健康检查（根路径，无需认证）
@app.get("/health", tags=["系统"], summary="健康检查")
async def health_check() -> dict[str, Any]:
    """
    健康检查端点

    用于：
    - 监控系统状态
    - 负载均衡健康检查
    - 服务发现
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "service": settings.APP_NAME,
    }


@app.get("/", tags=["系统"], summary="API 信息")
async def root() -> dict[str, Any]:
    """
    API 根路径

    返回 API 基本信息
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# 注册 API 路由
app.include_router(api_router)


# ==================== 启动入口 ====================

if __name__ == "__main__":
    import sys

    import uvicorn

    # Windows 平台强制使用单进程模式
    is_windows = sys.platform.startswith("win")
    workers = 1 if (settings.DEBUG or is_windows) else 4

    uvicorn.run(
        "ai_ppt.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=workers,
        loop="asyncio" if is_windows else "auto",
        access_log=True,
        log_level="debug" if settings.DEBUG else "info",
    )
