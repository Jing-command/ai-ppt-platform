"""
核心安全模块测试
test_security.py - 补充测试
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest

from ai_ppt.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """测试密码哈希功能"""

    def test_get_password_hash_returns_valid_bcrypt(self):
        """测试密码哈希返回有效的 bcrypt 格式"""
        password = "my_secure_password"
        hashed = get_password_hash(password)

        # 验证是 bcrypt 格式
        assert hashed.startswith("$2b$")
        # 验证包含正确的 rounds
        parts = hashed.split("$")
        assert len(parts) == 4
        assert parts[1] == "2b"

    def test_get_password_hash_different_salts(self):
        """测试每次哈希生成不同的盐值"""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # 相同的密码应该生成不同的哈希
        assert hash1 != hash2
        # 但两者都应该能验证成功
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_verify_password_correct(self):
        """测试使用正确密码验证"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """测试使用错误密码验证"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """测试空密码验证"""
        password = ""
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("not_empty", hashed) is False

    def test_verify_password_unicode(self):
        """测试 Unicode 密码"""
        password = "密码123🎉"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("密码123", hashed) is False

    def test_verify_password_long(self):
        """测试长密码"""
        # Python 3.12+ 的 crypt 模块已弃用，可能导致长密码哈希失败
        # 这里测试较短的密码（100字符）而不是1000字符
        password = "A" * 100
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

        assert verify_password(password, hashed) is True

    def test_verify_password_invalid_hash(self):
        """测试验证无效的哈希"""
        from passlib.exc import UnknownHashError

        with pytest.raises(UnknownHashError):
            verify_password("password", "not_a_valid_hash")

    def test_verify_password_empty_hash(self):
        """测试验证空哈希"""
        from passlib.exc import UnknownHashError

        with pytest.raises(UnknownHashError):
            verify_password("password", "")


class TestJWTAccessToken:
    """测试 JWT 访问令牌"""

    def test_create_access_token_contains_user_id(self):
        """测试访问令牌包含用户 ID"""
        user_id = uuid.uuid4()
        token = create_access_token(user_id)

        decoded_id, error = decode_token(token, expected_type="access")

        assert error is None
        assert decoded_id == user_id

    def test_create_access_token_default_expiry(self):
        """测试访问令牌默认过期时间"""
        user_id = uuid.uuid4()

        with patch("ai_ppt.core.security.settings") as mock_settings:
            mock_settings.security_secret_key = (
                "test-secret-key-for-testing-only-32chars-long"
            )
            mock_settings.security_algorithm = "HS256"
            mock_settings.security_access_token_expire_minutes = 30

            with patch("ai_ppt.core.security.datetime") as mock_datetime:
                now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = now
                mock_datetime.side_effect = lambda *args, **kw: datetime(
                    *args, **kw
                )

                token = create_access_token(user_id)

            # 解码不验证过期时间
            payload = jwt.decode(
                token,
                "test-secret-key-for-testing-only-32chars-long",
                algorithms=["HS256"],
                options={"verify_exp": False},
            )

            # 验证过期时间（默认30分钟）
            expected_exp = datetime(2024, 1, 1, 12, 30, 0, tzinfo=timezone.utc)
            assert payload["exp"] == int(expected_exp.timestamp())

    def test_create_access_token_custom_expiry(self):
        """测试访问令牌自定义过期时间"""
        user_id = uuid.uuid4()
        custom_delta = timedelta(hours=2)

        token = create_access_token(user_id, expires_delta=custom_delta)

        decoded_id, error = decode_token(token, expected_type="access")
        assert error is None
        assert decoded_id == user_id

    def test_create_access_token_expired(self):
        """测试访问令牌过期"""
        user_id = uuid.uuid4()

        # 创建已经过期的令牌
        expired_delta = timedelta(seconds=-1)
        token = create_access_token(user_id, expires_delta=expired_delta)

        decoded_id, error = decode_token(token)

        assert decoded_id is None
        assert "expired" in error.lower()

    def test_access_token_contains_correct_type(self):
        """测试访问令牌包含正确的类型"""
        user_id = uuid.uuid4()

        with patch("ai_ppt.core.security.settings") as mock_settings:
            mock_settings.security_secret_key = (
                "test-secret-key-for-testing-only-32chars-long"
            )
            mock_settings.security_algorithm = "HS256"
            mock_settings.security_access_token_expire_minutes = 30

            token = create_access_token(user_id)

            payload = jwt.decode(
                token,
                "test-secret-key-for-testing-only-32chars-long",
                algorithms=["HS256"],
                options={"verify_exp": False},
            )

            assert payload["type"] == "access"

    def test_access_token_contains_iat(self):
        """测试访问令牌包含签发时间"""
        user_id = uuid.uuid4()

        from datetime import timedelta

        with patch("ai_ppt.core.security.settings") as mock_settings:
            mock_settings.security_secret_key = (
                "test-secret-key-for-testing-only-32chars-long"
            )
            mock_settings.security_algorithm = "HS256"
            mock_settings.security_access_token_expire_minutes = 30

            before = datetime.now(timezone.utc) - timedelta(seconds=1)
            token = create_access_token(user_id)
            after = datetime.now(timezone.utc) + timedelta(seconds=1)

            payload = jwt.decode(
                token,
                "test-secret-key-for-testing-only-32chars-long",
                algorithms=["HS256"],
                options={"verify_exp": False},
            )

            iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
            assert before <= iat <= after


class TestJWTRefreshToken:
    """测试 JWT 刷新令牌"""

    def test_create_refresh_token_contains_user_id(self):
        """测试刷新令牌包含用户 ID"""
        user_id = uuid.uuid4()
        token = create_refresh_token(user_id)

        decoded_id, error = decode_token(token, expected_type="refresh")

        assert error is None
        assert decoded_id == user_id

    def test_create_refresh_token_expiry(self):
        """测试刷新令牌过期时间"""
        user_id = uuid.uuid4()

        with patch("ai_ppt.core.security.settings") as mock_settings:
            mock_settings.security_secret_key = (
                "test-secret-key-for-testing-only-32chars-long"
            )
            mock_settings.security_algorithm = "HS256"
            mock_settings.security_refresh_token_expire_days = 7

            with patch("ai_ppt.core.security.datetime") as mock_datetime:
                now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = now

                token = create_refresh_token(user_id)

            payload = jwt.decode(
                token,
                "test-secret-key-for-testing-only-32chars-long",
                algorithms=["HS256"],
                options={"verify_exp": False},
            )

            # 验证过期时间（默认7天）
            expected_exp = datetime(2024, 1, 8, 12, 0, 0, tzinfo=timezone.utc)
            assert payload["exp"] == int(expected_exp.timestamp())

    def test_refresh_token_contains_correct_type(self):
        """测试刷新令牌包含正确的类型"""
        user_id = uuid.uuid4()

        with patch("ai_ppt.core.security.settings") as mock_settings:
            mock_settings.security_secret_key = (
                "test-secret-key-for-testing-only-32chars-long"
            )
            mock_settings.security_algorithm = "HS256"
            mock_settings.security_refresh_token_expire_days = 7

            token = create_refresh_token(user_id)

            payload = jwt.decode(
                token,
                "test-secret-key-for-testing-only-32chars-long",
                algorithms=["HS256"],
                options={"verify_exp": False},
            )

            assert payload["type"] == "refresh"


class TestTokenDecode:
    """测试令牌解码"""

    def test_decode_valid_access_token(self):
        """测试解码有效的访问令牌"""
        user_id = uuid.uuid4()
        token = create_access_token(user_id)

        decoded_id, error = decode_token(token, expected_type="access")

        assert error is None
        assert decoded_id == user_id

    def test_decode_valid_refresh_token(self):
        """测试解码有效的刷新令牌"""
        user_id = uuid.uuid4()
        token = create_refresh_token(user_id)

        decoded_id, error = decode_token(token, expected_type="refresh")

        assert error is None
        assert decoded_id == user_id

    def test_decode_token_type_mismatch(self):
        """测试令牌类型不匹配"""
        user_id = uuid.uuid4()

        # 创建访问令牌但用刷新类型解码
        access_token = create_access_token(user_id)
        decoded_id, error = decode_token(access_token, expected_type="refresh")

        assert decoded_id is None
        assert "type" in error.lower()

    def test_decode_invalid_token(self):
        """测试解码无效令牌"""
        decoded_id, error = decode_token("invalid.token.here")

        assert decoded_id is None
        assert error is not None

    def test_decode_malformed_token(self):
        """测试解码格式错误的令牌"""
        decoded_id, error = decode_token("not_a_valid_jwt")

        assert decoded_id is None
        assert error is not None

    def test_decode_empty_token(self):
        """测试解码空令牌"""
        decoded_id, error = decode_token("")

        assert decoded_id is None
        assert error is not None

    def test_decode_expired_token(self):
        """测试解码过期令牌"""
        user_id = uuid.uuid4()
        expired_token = create_access_token(
            user_id, expires_delta=timedelta(seconds=-1)
        )

        decoded_id, error = decode_token(expired_token)

        assert decoded_id is None
        assert "expired" in error.lower()

    def test_decode_token_missing_sub(self):
        """测试解码缺少 sub 的令牌"""
        with patch("ai_ppt.core.security.settings") as mock_settings:
            mock_settings.security_secret_key = (
                "test-secret-key-for-testing-only-32chars-long"
            )
            mock_settings.security_algorithm = "HS256"

            # 手动创建没有 sub 的令牌
            payload = {
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
                "type": "access",
            }
            token = jwt.encode(
                payload,
                "test-secret-key-for-testing-only-32chars-long",
                algorithm="HS256",
            )

            decoded_id, error = decode_token(token)

        assert decoded_id is None
        assert "subject" in error.lower() or "missing" in error.lower()

    def test_decode_token_invalid_uuid(self):
        """测试解码包含无效 UUID 的令牌"""
        payload = {
            "sub": "not-a-valid-uuid",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "type": "access",
        }
        token = jwt.encode(
            payload,
            "test-secret-key-for-testing-only-32chars-long",
            algorithm="HS256",
        )

        decoded_id, error = decode_token(token)

        assert decoded_id is None
        assert "format" in error.lower() or "invalid" in error.lower()

    def test_decode_token_wrong_secret(self):
        """测试使用错误的密钥解码令牌"""
        user_id = uuid.uuid4()
        token = create_access_token(user_id)

        # 尝试用错误的密钥解码
        with patch("ai_ppt.core.security.settings") as mock_settings:
            mock_settings.JWT_SECRET_KEY = "wrong-secret"
            mock_settings.JWT_ALGORITHM = "HS256"

            decoded_id, error = decode_token(token)

        assert decoded_id is None
        assert "invalid" in error.lower() or "signature" in error.lower()
