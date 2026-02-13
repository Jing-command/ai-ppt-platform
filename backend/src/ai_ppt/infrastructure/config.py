"""
Pydantic Settings 配置管理
支持环境变量、.env 文件和默认值
"""
from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    model_config = SettingsConfigDict(env_prefix="DB_")
    
    url: PostgresDsn = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_ppt")
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0, le=100)
    pool_timeout: int = Field(default=30, ge=1)
    echo: bool = Field(default=False)


class RedisSettings(BaseSettings):
    """Redis 配置"""
    model_config = SettingsConfigDict(env_prefix="REDIS_")
    
    url: RedisDsn = Field(default="redis://localhost:6379/0")
    connection_timeout: int = Field(default=5)


class AISettings(BaseSettings):
    """AI/LLM 配置"""
    model_config = SettingsConfigDict(
        env_prefix="AI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    provider: Literal["openai", "azure", "anthropic", "deepseek", "kimi"] = Field(default="deepseek")
    api_key: SecretStr = Field(default_factory=lambda: SecretStr(""))
    base_url: Optional[str] = Field(default=None)
    model: str = Field(default="deepseek-chat")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=128000)
    timeout: int = Field(default=60)


class SecuritySettings(BaseSettings):
    """安全配置"""
    model_config = SettingsConfigDict(env_prefix="SECURITY_")
    
    secret_key: SecretStr = Field(default="change-me-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)


class ExportSettings(BaseSettings):
    """导出引擎配置"""
    model_config = SettingsConfigDict(env_prefix="EXPORT_")
    
    max_file_size_mb: int = Field(default=50, ge=1, le=500)
    temp_dir: str = Field(default="/tmp/ai-ppt-exports")
    cleanup_interval_hours: int = Field(default=24)


class Settings(BaseSettings):
    """全局应用配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
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
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    
    # 子模块配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    ai: AISettings = Field(default_factory=AISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    export: ExportSettings = Field(default_factory=ExportSettings)


@lru_cache
def get_settings() -> Settings:
    """获取全局配置实例（单例模式）"""
    return Settings()


# 导出便捷访问
settings = get_settings()
