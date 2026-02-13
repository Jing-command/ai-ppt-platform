"""
FastAPI Dependencies
依赖注入函数
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.core.security import decode_token
from ai_ppt.database import get_db
from ai_ppt.models.user import User

# HTTP Bearer 认证
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    获取当前登录用户

    用法：
        @app.get("/items/")
        async def read_items(current_user: User = Depends(get_current_user)):
            ...
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "缺少认证令牌"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user_id, error = decode_token(token, expected_type="access")

    if error:
        code = "TOKEN_EXPIRED" if error == "Token expired" else "INVALID_TOKEN"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": code,
                "message": (
                    "无效的认证令牌"
                    if code == "INVALID_TOKEN"
                    else "登录已过期，请重新登录"
                ),
                "details": {"error": error},
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查询用户
    from sqlalchemy import select

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

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    可选地获取当前用户

    用于某些接口既支持认证用户，也支持匿名访问

    Returns:
        User 或 None
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
