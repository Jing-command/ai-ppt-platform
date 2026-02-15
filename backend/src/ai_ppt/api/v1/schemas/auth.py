"""
认证相关 Schema 定义
使用 camelCase alias 以匹配前端格式
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """用户基础信息"""

    email: EmailStr = Field(..., description="邮箱地址")
    name: str = Field(..., description="用户名称")


class UserCreate(UserBase):
    """用户注册请求"""

    password: str = Field(..., min_length=6, description="密码")


class UserResponse(BaseModel):
    """用户信息响应"""

    id: UUID = Field(..., description="用户ID")
    email: EmailStr = Field(..., description="邮箱地址")
    name: str = Field(..., description="用户名称")
    avatar: str | None = Field(None, description="头像URL")
    created_at: datetime = Field(..., alias="createdAt", description="创建时间")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class LoginRequest(BaseModel):
    """登录请求"""

    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应"""

    access_token: str = Field(..., alias="accessToken", description="访问令牌")
    token_type: str = Field(default="bearer", alias="tokenType", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")

    model_config = ConfigDict(populate_by_name=True)


class RefreshRequest(BaseModel):
    """刷新令牌请求"""

    refresh_token: str = Field(..., alias="refreshToken", description="刷新令牌")

    model_config = ConfigDict(populate_by_name=True)


class RefreshResponse(BaseModel):
    """刷新令牌响应"""

    access_token: str = Field(..., alias="accessToken", description="新的访问令牌")
    token_type: str = Field(default="bearer", alias="tokenType", description="令牌类型")

    model_config = ConfigDict(populate_by_name=True)


class RegisterRequest(BaseModel):
    """注册请求"""

    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, description="密码")
    name: str = Field(..., min_length=1, max_length=100, description="用户名称")


class UpdateUserRequest(BaseModel):
    """更新用户信息请求"""

    name: str | None = Field(None, min_length=1, max_length=100, description="用户名称")
    avatar_url: str | None = Field(None, description="头像URL")


class AvatarUploadResponse(BaseModel):
    """头像上传响应"""

    avatar_url: str = Field(..., alias="avatarUrl", description="头像URL")

    model_config = ConfigDict(populate_by_name=True)


class RegisterResponse(LoginResponse):
    """注册响应（与登录响应相同）"""
