"""
认证 API 集成测试
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthAPI:
    """测试认证 API 端点"""

    async def test_register_success(self, client: AsyncClient, db_session):
        """测试成功注册"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "name": "newuser",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "accessToken" in data
        assert "tokenType" in data
        assert data["tokenType"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"

    async def test_register_email_exists(
        self, client: AsyncClient, db_session
    ):
        """测试注册已存在的邮箱"""
        # 首先创建一个用户
        with patch.object(db_session, "execute") as mock_execute:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = MagicMock(
                id=uuid.uuid4(),
                email="exists@example.com",
                username="exists",
            )
            mock_execute.return_value = mock_result

            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "exists@example.com",
                    "password": "password123",
                    "name": "exists",
                },
            )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "EMAIL_EXISTS"

    async def test_register_invalid_email(self, client: AsyncClient):
        """测试无效的邮箱格式"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123",
                "name": "testuser",
            },
        )

        assert response.status_code == 422

    async def test_register_password_too_short(self, client: AsyncClient):
        """测试密码太短"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",
                "name": "testuser",
            },
        )

        assert response.status_code == 422

    async def test_login_success(self, client: AsyncClient, db_session):
        """测试成功登录"""
        from datetime import datetime, timezone
        from ai_ppt.core.security import get_password_hash

        # 创建测试用户
        user_id = uuid.uuid4()
        hashed_password = get_password_hash("password123")

        with patch.object(db_session, "execute") as mock_execute:
            mock_result = MagicMock()
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.email = "login@example.com"
            mock_user.username = "loginuser"
            mock_user.hashed_password = hashed_password
            mock_user.is_active = True
            mock_user.avatar_url = None
            mock_user.created_at = datetime.now(timezone.utc)
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_execute.return_value = mock_result

            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "login@example.com",
                    "password": "password123",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert "user" in data

    async def test_login_wrong_password(self, client: AsyncClient, db_session):
        """测试错误的密码"""
        from ai_ppt.core.security import get_password_hash

        user_id = uuid.uuid4()
        hashed_password = get_password_hash("correctpassword")

        with patch.object(db_session, "execute") as mock_execute:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = MagicMock(
                id=user_id,
                email="test@example.com",
                username="testuser",
                hashed_password=hashed_password,
                is_active=True,
            )
            mock_execute.return_value = mock_result

            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword",
                },
            )

        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "INVALID_CREDENTIALS"

    async def test_login_user_not_found(self, client: AsyncClient, db_session):
        """测试用户不存在"""
        with patch.object(db_session, "execute") as mock_execute:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_execute.return_value = mock_result

            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "nonexistent@example.com",
                    "password": "password123",
                },
            )

        assert response.status_code == 401

    async def test_login_inactive_user(self, client: AsyncClient, db_session):
        """测试禁用的用户"""
        from ai_ppt.core.security import get_password_hash

        hashed_password = get_password_hash("password123")

        with patch.object(db_session, "execute") as mock_execute:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = MagicMock(
                id=uuid.uuid4(),
                email="inactive@example.com",
                username="inactive",
                hashed_password=hashed_password,
                is_active=False,
            )
            mock_execute.return_value = mock_result

            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "inactive@example.com",
                    "password": "password123",
                },
            )

        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "USER_INACTIVE"

    async def test_refresh_success(self, client: AsyncClient, db_session):
        """测试成功刷新令牌"""
        from ai_ppt.core.security import create_refresh_token

        user_id = uuid.uuid4()
        refresh_token = create_refresh_token(user_id)

        with patch.object(db_session, "execute") as mock_execute:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = MagicMock(
                id=user_id,
                email="refresh@example.com",
                is_active=True,
            )
            mock_execute.return_value = mock_result

            response = await client.post(
                "/api/v1/auth/refresh",
                json={"refreshToken": refresh_token},
            )

        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert "tokenType" in data

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """测试无效的刷新令牌"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": "invalid.token.here"},
        )

        assert response.status_code == 401

    async def test_refresh_user_not_found(
        self, client: AsyncClient, db_session
    ):
        """测试刷新时用户不存在"""
        from ai_ppt.core.security import create_refresh_token

        user_id = uuid.uuid4()
        refresh_token = create_refresh_token(user_id)

        with patch.object(db_session, "execute") as mock_execute:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_execute.return_value = mock_result

            response = await client.post(
                "/api/v1/auth/refresh",
                json={"refreshToken": refresh_token},
            )

        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "USER_NOT_FOUND"

    async def test_get_me_success(
        self, client: AsyncClient, authenticated_user
    ):
        """测试获取当前用户信息"""
        from ai_ppt.core.security import create_access_token

        token = create_access_token(authenticated_user.id)

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == authenticated_user.email
        assert data["name"] == authenticated_user.username

    async def test_get_me_no_auth(self, client: AsyncClient):
        """测试未认证访问"""
        response = await client.get("/api/v1/auth/me")

        # 401 (Unauthorized) 或 403 (Forbidden) 都是有效的未认证响应
        assert response.status_code in [401, 403]

    async def test_get_me_invalid_token(self, client: AsyncClient):
        """测试无效的令牌"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token"},
        )

        assert response.status_code == 401
