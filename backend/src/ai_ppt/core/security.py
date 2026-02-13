"""
安全工具模块
JWT 令牌生成和验证
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID

import jwt
from passlib.context import CryptContext

from ai_ppt.config import settings

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    result: bool = pwd_context.verify(plain_password, hashed_password)
    return result


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    result: str = pwd_context.hash(password)
    return result


def create_access_token(user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT 访问令牌

    Args:
        user_id: 用户 UUID
        expires_delta: 过期时间增量，默认使用配置中的设置

    Returns:
        JWT 令牌字符串
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: UUID) -> str:
    """
    创建 JWT 刷新令牌

    Args:
        user_id: 用户 UUID

    Returns:
        JWT 刷新令牌字符串
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str, expected_type: str = "access") -> Tuple[Optional[UUID], Optional[str]]:
    """
    解码并验证 JWT 令牌

    Args:
        token: JWT 令牌字符串
        expected_type: 预期的令牌类型 ("access" 或 "refresh")

    Returns:
        (user_id, error_message)
        - 成功时：user_id 为 UUID，error_message 为 None
        - 失败时：user_id 为 None，error_message 为错误描述
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # 验证令牌类型
        token_type = payload.get("type")
        if token_type != expected_type:
            return (
                None,
                f"Invalid token type: expected {expected_type}, got {token_type}",
            )

        # 获取用户 ID
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None, "Token missing subject"

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            return None, "Invalid user ID format"

        return user_id, None

    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError as e:
        return None, f"Invalid token: {str(e)}"
    except Exception as e:
        return None, f"Token decode error: {str(e)}"
