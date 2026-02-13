"""
用户认证 API
处理用户注册、登录、令牌刷新和用户信息获取
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.api.deps import get_current_user
from ai_ppt.api.v1.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from ai_ppt.api.v1.schemas.common import ErrorResponse
from ai_ppt.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from ai_ppt.database import get_db
from ai_ppt.models.user import User

router = APIRouter(prefix="/auth", tags=["用户认证"])


async def _get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """通过邮箱获取用户"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def _get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """通过用户名获取用户"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


def _user_to_response(user: User) -> UserResponse:
    """将 User 模型转换为 UserResponse"""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.username,  # username 映射为 name
        createdAt=user.created_at,
    )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误或用户已存在"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)) -> RegisterResponse:
    """
    注册新用户

    - **email**: 邮箱地址（唯一）
    - **password**: 密码（至少6位）
    - **name**: 用户名称

    返回包含 accessToken 和 user 信息的响应
    """
    # 检查邮箱是否已存在
    existing_user = await _get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMAIL_EXISTS", "message": "该邮箱已被注册"},
        )

    # 检查用户名是否已存在（使用 name 作为 username）
    existing_username = await _get_user_by_username(db, data.name)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "USERNAME_EXISTS", "message": "该用户名已被使用"},
        )

    # 创建新用户
    hashed_password = get_password_hash(data.password)
    new_user = User(
        email=data.email,
        username=data.name,  # name 映射为 username
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 生成令牌
    access_token = create_access_token(new_user.id)

    return RegisterResponse(
        accessToken=access_token, tokenType="bearer", user=_user_to_response(new_user)
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="用户登录",
    responses={
        401: {"model": ErrorResponse, "description": "邮箱或密码错误"},
        403: {"model": ErrorResponse, "description": "用户账户已被禁用"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    """
    用户登录

    - **email**: 邮箱地址
    - **password**: 密码

    验证成功后返回 accessToken 和用户信息
    """
    # 查找用户
    user = await _get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "邮箱或密码错误"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证密码
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "邮箱或密码错误"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "USER_INACTIVE", "message": "用户账户已被禁用"},
        )

    # 更新最后登录时间
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    # 生成令牌
    access_token = create_access_token(user.id)

    return LoginResponse(accessToken=access_token, tokenType="bearer", user=_user_to_response(user))


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="刷新访问令牌",
    responses={
        401: {"model": ErrorResponse, "description": "无效的刷新令牌"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)) -> RefreshResponse:
    """
    使用刷新令牌获取新的访问令牌

    - **refreshToken**: 刷新令牌

    返回新的 accessToken
    """
    # 解码刷新令牌
    user_id, error = decode_token(data.refresh_token, expected_type="refresh")

    if error:
        code = "TOKEN_EXPIRED" if error == "Token expired" else "INVALID_TOKEN"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": code,
                "message": (
                    "无效的刷新令牌" if code == "INVALID_TOKEN" else "刷新令牌已过期，请重新登录"
                ),
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证用户是否存在且激活
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "用户不存在"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "USER_INACTIVE", "message": "用户账户已被禁用"},
        )

    # 生成新的访问令牌
    new_access_token = create_access_token(user.id)

    return RefreshResponse(accessToken=new_access_token, tokenType="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        403: {"model": ErrorResponse, "description": "用户账户已被禁用"},
        500: {"model": ErrorResponse, "description": "服务器错误"},
    },
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    获取当前登录用户的信息

    需要有效的访问令牌
    """
    return _user_to_response(current_user)
