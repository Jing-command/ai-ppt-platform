"""
Pydantic Settings 配置管理
支持环境变量、.env 文件和默认值
"""

import os
from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取 backend 目录路径
# __file__ 是 config.py 的路径: ai_ppt/infrastructure/config.py
# 需要向上回溯 4 层: infrastructure -> ai_ppt -> src -> backend
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)


class Settings(BaseSettings):
    """全局应用配置"""

    model_config = SettingsConfigDict(
        env_file=os.path.join(_PROJECT_ROOT, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用基础配置
    app_name: str = Field(default="AI PPT Platform")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # API 配置
    api_v1_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # 数据库配置
    db_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_ppt",
        alias="DB_URL",
    )
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # Redis 配置
    redis_url: str = Field(
        default="redis://localhost:6379/0", alias="REDIS_URL"
    )
    redis_connection_timeout: int = Field(
        default=5, alias="REDIS_CONNECTION_TIMEOUT"
    )

    # AI/LLM 配置
    ai_provider: Literal[
        "openai", "azure", "anthropic", "deepseek", "kimi"
    ] = Field(default="deepseek", alias="AI_PROVIDER")
    ai_api_key: SecretStr = Field(
        default_factory=lambda: SecretStr(""), alias="AI_API_KEY"
    )
    ai_base_url: Optional[str] = Field(default=None, alias="AI_BASE_URL")
    ai_model: str = Field(default="deepseek-chat", alias="AI_MODEL")
    ai_temperature: float = Field(default=0.7, alias="AI_TEMPERATURE")
    ai_max_tokens: int = Field(default=4096, alias="AI_MAX_TOKENS")
    ai_timeout: int = Field(default=60, alias="AI_TIMEOUT")

    # 安全配置
    security_secret_key: str = Field(
        default="change-me-in-production", alias="SECURITY_SECRET_KEY"
    )
    security_algorithm: str = Field(
        default="HS256", alias="SECURITY_ALGORITHM"
    )
    security_access_token_expire_minutes: int = Field(
        default=30, alias="SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    security_refresh_token_expire_days: int = Field(
        default=7, alias="SECURITY_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # 导出引擎配置
    export_max_file_size_mb: int = Field(
        default=50, alias="EXPORT_MAX_FILE_SIZE_MB"
    )
    export_temp_dir: str = Field(
        default="/tmp/ai-ppt-exports",  # nosec: B108 - 可配置的临时目录
        alias="EXPORT_TEMP_DIR",
    )
    export_cleanup_interval_hours: int = Field(
        default=24, alias="EXPORT_CLEANUP_INTERVAL_HOURS"
    )


@lru_cache
def get_settings() -> Settings:
    """获取全局配置实例（单例模式）"""
    return Settings()


# 导出便捷访问
settings = get_settings()
