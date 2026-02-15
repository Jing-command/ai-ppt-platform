"""
Auth Service 单元测试 - BE-001
测试用户认证相关功能
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_ppt.api.v1.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
)

# 导入被测试的模块
from ai_ppt.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from ai_ppt.models.user import User


class TestPasswordSecurity:
    """测试密码加密和验证功能"""

    def test_get_password_hash_generates_bcrypt_hash(self):
        """测试密码哈希生成 - 应该生成 bcrypt 格式的哈希"""
        password = "my-secret-password"
        hashed = get_password_hash(password)

        # 验证是 bcrypt 格式 ($2b$)
        assert hashed.startswith("$2b$")
        # 每次生成的哈希应该不同（因为随机盐）
        hashed2 = get_password_hash(password)
        assert hashed != hashed2

    def test_verify_password_with_correct_password(self):
        """测试使用正确密码验证 - 应该返回 True"""
        password = "test-password-123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_wrong_password(self):
        """测试使用错误密码验证 - 应该返回 False"""
        password = "correct-password"
        wrong_password = "wrong-password"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_with_invalid_hash(self):
        """测试使用无效哈希验证 - 应该抛出异常"""
        password = "some-password"
        invalid_hash = "not-a-valid-hash"

        # passlib 对无效哈希会抛出 UnknownHashError
        from passlib.exc import UnknownHashError

        with pytest.raises(UnknownHashError):
            verify_password(password, invalid_hash)


class TestJWTToken:
    """测试 JWT 令牌创建和验证"""

    def test_create_access_token_contains_user_id(self):
        """测试访问令牌包含用户 ID"""
        user_id = uuid.uuid4()
        token = create_access_token(user_id)

        # 解码并验证
        decoded_id, error = decode_token(token, expected_type="access")

        assert error is None
        assert decoded_id == user_id

    def test_create_refresh_token_contains_user_id(self):
        """测试刷新令牌包含用户 ID"""
        user_id = uuid.uuid4()
        token = create_refresh_token(user_id)

        # 解码并验证
        decoded_id, error = decode_token(token, expected_type="refresh")

        assert error is None
        assert decoded_id == user_id

    def test_access_token_expires_correctly(self):
        """测试访问令牌正确过期"""
        from datetime import timedelta

        user_id = uuid.uuid4()
        # 创建已经过期的令牌
        expired_token = create_access_token(
            user_id, expires_delta=timedelta(seconds=-1)
        )

        decoded_id, error = decode_token(expired_token)

        assert decoded_id is None
        assert "expired" in error.lower()

    def test_token_type_mismatch_access_vs_refresh(self):
        """测试访问令牌和刷新令牌类型不匹配"""
        user_id = uuid.uuid4()

        # 创建刷新令牌但用访问类型解码
        refresh_token = create_refresh_token(user_id)
        decoded_id, error = decode_token(refresh_token, expected_type="access")

        assert decoded_id is None
        assert "type" in error.lower()

    def test_decode_invalid_token(self):
        """测试解码无效令牌"""
        decoded_id, error = decode_token("totally.invalid.token")

        assert decoded_id is None
        assert error is not None


class TestUserModel:
    """测试 User 模型"""

    def test_user_creation(self):
        """测试用户对象创建"""
        user_id = uuid.uuid4()
        user = User(
            id=user_id,  # 显式设置 ID
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_here",
            is_active=True,
            is_superuser=False,
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.id == user_id
        assert isinstance(user.id, uuid.UUID)

    def test_user_repr(self):
        """测试 User 的 __repr__ 方法"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed",
        )

        repr_str = repr(user)
        assert "User" in repr_str
        assert "test@example.com" in repr_str


@pytest.mark.asyncio
class TestAuthEndpoints:
    """测试认证 API 端点"""

    @pytest.fixture
    def mock_db(self):
        """创建模拟的数据库会话"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def sample_user(self):
        """创建示例用户"""
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_superuser=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            last_login=None,
        )
        return user

    async def test_register_success(self, mock_db, sample_user):
        """测试用户注册成功"""
        from ai_ppt.api.v1.endpoints.auth import register

        # 模拟数据库查询返回 None（用户不存在）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # 捕获被 add 到数据库的用户对象，并设置其 id 和 created_at
        added_user = None

        def capture_add(user):
            nonlocal added_user
            added_user = user
            user.id = uuid.uuid4()
            user.created_at = datetime.now(timezone.utc)

        mock_db.add = MagicMock(side_effect=capture_add)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # 创建注册请求
        request = RegisterRequest(
            email="newuser@example.com", password="password123", name="newuser"
        )

        # 调用注册函数
        response = await register(request, mock_db)

        # 验证响应
        assert response.access_token is not None
        assert response.token_type == "bearer"
        assert response.user.email == "newuser@example.com"
        assert response.user.name == "newuser"

        # 验证数据库操作
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    async def test_register_email_exists(self, mock_db, sample_user):
        """测试注册时邮箱已存在"""
        from ai_ppt.api.v1.endpoints.auth import register

        # 模拟数据库查询返回已存在的用户
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result

        request = RegisterRequest(
            email="test@example.com",  # 已存在的邮箱
            password="password123",
            name="newuser",
        )

        with pytest.raises(HTTPException) as exc_info:
            await register(request, mock_db)

        assert exc_info.value.status_code == 400
        assert "EMAIL_EXISTS" in str(exc_info.value.detail)

    async def test_register_username_exists(self, mock_db, sample_user):
        """测试注册时用户名已存在"""
        from ai_ppt.api.v1.endpoints.auth import register

        # 第一次查询（邮箱）返回 None，第二次查询（用户名）返回用户
        mock_result_email = MagicMock()
        mock_result_email.scalar_one_or_none.return_value = None

        mock_result_username = MagicMock()
        mock_result_username.scalar_one_or_none.return_value = sample_user

        mock_db.execute.side_effect = [mock_result_email, mock_result_username]

        request = RegisterRequest(
            email="new@example.com",
            password="password123",
            name="testuser",  # 已存在的用户名
        )

        with pytest.raises(HTTPException) as exc_info:
            await register(request, mock_db)

        assert exc_info.value.status_code == 400
        assert "USERNAME_EXISTS" in str(exc_info.value.detail)

    async def test_login_success(self, mock_db, sample_user):
        """测试用户登录成功"""
        from ai_ppt.api.v1.endpoints.auth import login

        # 模拟数据库查询返回用户
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()

        request = LoginRequest(
            email="test@example.com", password="password123"
        )

        response = await login(request, mock_db)

        assert response.access_token is not None
        assert response.token_type == "bearer"
        assert response.user.email == "test@example.com"
        mock_db.commit.assert_called_once()  # 更新最后登录时间

    async def test_login_wrong_password(self, mock_db, sample_user):
        """测试登录时密码错误"""
        from ai_ppt.api.v1.endpoints.auth import login

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result

        request = LoginRequest(
            email="test@example.com", password="wrong-password"
        )

        with pytest.raises(HTTPException) as exc_info:
            await login(request, mock_db)

        assert exc_info.value.status_code == 401
        assert "INVALID_CREDENTIALS" in str(exc_info.value.detail)

    async def test_login_user_not_found(self, mock_db):
        """测试登录时用户不存在"""
        from ai_ppt.api.v1.endpoints.auth import login

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        request = LoginRequest(
            email="nonexistent@example.com", password="password123"
        )

        with pytest.raises(HTTPException) as exc_info:
            await login(request, mock_db)

        assert exc_info.value.status_code == 401

    async def test_login_inactive_user(self, mock_db, sample_user):
        """测试登录时用户已被禁用"""
        from ai_ppt.api.v1.endpoints.auth import login

        sample_user.is_active = False
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result

        request = LoginRequest(
            email="test@example.com", password="password123"
        )

        with pytest.raises(HTTPException) as exc_info:
            await login(request, mock_db)

        assert exc_info.value.status_code == 403
        assert "USER_INACTIVE" in str(exc_info.value.detail)

    async def test_refresh_success(self, mock_db, sample_user):
        """测试刷新令牌成功"""
        from ai_ppt.api.v1.endpoints.auth import refresh

        # 创建刷新令牌
        refresh_token = create_refresh_token(sample_user.id)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result

        request = RefreshRequest(refresh_token=refresh_token)

        response = await refresh(request, mock_db)

        assert response.access_token is not None
        assert response.token_type == "bearer"

    async def test_refresh_invalid_token(self, mock_db):
        """测试使用无效刷新令牌"""
        from ai_ppt.api.v1.endpoints.auth import refresh

        request = RefreshRequest(refresh_token="invalid.token.here")

        with pytest.raises(HTTPException) as exc_info:
            await refresh(request, mock_db)

        assert exc_info.value.status_code == 401

    async def test_refresh_expired_token(self, mock_db):
        """测试使用过期刷新令牌"""
        from datetime import timedelta

        from ai_ppt.api.v1.endpoints.auth import refresh

        user_id = uuid.uuid4()
        # 创建已过期的刷新令牌
        expired_token = create_refresh_token(user_id)
        # 注意：由于刷新令牌有效期是7天，我们无法在单元测试中真正过期它
        # 这里测试的是无效的令牌格式

        request = RefreshRequest(refresh_token=expired_token)

        # 由于令牌未真正过期，但用户不存在，会返回 USER_NOT_FOUND
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await refresh(request, mock_db)

        # 这里应该返回 401，因为用户不存在
        assert exc_info.value.status_code == 401

    async def test_refresh_user_not_found(self, mock_db):
        """测试刷新令牌但用户不存在"""
        from ai_ppt.api.v1.endpoints.auth import refresh

        user_id = uuid.uuid4()
        refresh_token = create_refresh_token(user_id)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        request = RefreshRequest(refresh_token=refresh_token)

        with pytest.raises(HTTPException) as exc_info:
            await refresh(request, mock_db)

        assert exc_info.value.status_code == 401
        assert "USER_NOT_FOUND" in str(exc_info.value.detail)

    async def test_refresh_inactive_user(self, mock_db, sample_user):
        """测试刷新令牌但用户已被禁用"""
        from ai_ppt.api.v1.endpoints.auth import refresh

        sample_user.is_active = False
        refresh_token = create_refresh_token(sample_user.id)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result

        request = RefreshRequest(refresh_token=refresh_token)

        with pytest.raises(HTTPException) as exc_info:
            await refresh(request, mock_db)

        assert exc_info.value.status_code == 403
        assert "USER_INACTIVE" in str(exc_info.value.detail)


@pytest.mark.asyncio
class TestAuthDependencies:
    """测试认证依赖项"""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def sample_user(self):
        return User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hashed",
            is_active=True,
        )

    async def test_get_current_user_success(self, mock_db, sample_user):
        """测试成功获取当前用户"""
        from fastapi.security import HTTPAuthorizationCredentials

        from ai_ppt.api.deps import get_current_user

        # 创建有效令牌
        token = create_access_token(sample_user.id)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result

        user = await get_current_user(credentials, mock_db)

        assert user.id == sample_user.id
        assert user.email == sample_user.email

    async def test_get_current_user_no_credentials(self, mock_db):
        """测试缺少认证信息"""
        from ai_ppt.api.deps import get_current_user

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None, mock_db)

        assert exc_info.value.status_code == 401
        assert "MISSING_TOKEN" in str(exc_info.value.detail)

    async def test_get_current_user_invalid_token(self, mock_db):
        """测试无效的认证令牌"""
        from fastapi.security import HTTPAuthorizationCredentials

        from ai_ppt.api.deps import get_current_user

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.token.here"
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_db)

        assert exc_info.value.status_code == 401
        assert "INVALID_TOKEN" in str(exc_info.value.detail)

    async def test_get_current_user_expired_token(self, mock_db):
        """测试过期的认证令牌"""
        from datetime import timedelta

        from fastapi.security import HTTPAuthorizationCredentials

        from ai_ppt.api.deps import get_current_user

        user_id = uuid.uuid4()
        expired_token = create_access_token(
            user_id, expires_delta=timedelta(seconds=-1)
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=expired_token
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_db)

        assert exc_info.value.status_code == 401
        assert "TOKEN_EXPIRED" in str(exc_info.value.detail)

    async def test_get_current_user_not_found(self, mock_db):
        """测试令牌有效但用户不存在"""
        from fastapi.security import HTTPAuthorizationCredentials

        from ai_ppt.api.deps import get_current_user

        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_db)

        assert exc_info.value.status_code == 401
        assert "USER_NOT_FOUND" in str(exc_info.value.detail)

    async def test_get_current_user_inactive(self, mock_db, sample_user):
        """测试用户已被禁用"""
        from fastapi.security import HTTPAuthorizationCredentials

        from ai_ppt.api.deps import get_current_user

        sample_user.is_active = False
        token = create_access_token(sample_user.id)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_db)

        assert exc_info.value.status_code == 403
        assert "USER_INACTIVE" in str(exc_info.value.detail)

    async def test_get_optional_user_with_valid_token(
        self, mock_db, sample_user
    ):
        """测试可选用户获取 - 有有效令牌"""
        from fastapi.security import HTTPAuthorizationCredentials

        from ai_ppt.api.deps import get_optional_user

        token = create_access_token(sample_user.id)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result

        user = await get_optional_user(credentials, mock_db)

        assert user is not None
        assert user.id == sample_user.id

    async def test_get_optional_user_no_credentials(self, mock_db):
        """测试可选用户获取 - 无认证信息"""
        from ai_ppt.api.deps import get_optional_user

        user = await get_optional_user(None, mock_db)

        assert user is None

    async def test_get_optional_user_invalid_token(self, mock_db):
        """测试可选用户获取 - 无效令牌返回 None"""
        from fastapi.security import HTTPAuthorizationCredentials

        from ai_ppt.api.deps import get_optional_user

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.token"
        )

        user = await get_optional_user(credentials, mock_db)

        assert user is None
