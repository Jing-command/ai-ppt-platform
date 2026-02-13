"""
测试 DateTime 工具
"""

from datetime import datetime, timezone

import pytest

from ai_ppt.utils.datetime import ensure_aware, utcnow_aware


class TestUtcNowAware:
    """测试 utcnow_aware 函数"""

    def test_returns_datetime(self):
        """测试返回 datetime 对象"""
        result = utcnow_aware()

        assert isinstance(result, datetime)

    def test_returns_utc_time(self):
        """测试返回 UTC 时间"""
        result = utcnow_aware()

        assert result.tzinfo == timezone.utc

    def test_returns_aware_datetime(self):
        """测试返回带时区的 datetime"""
        result = utcnow_aware()

        assert result.tzinfo is not None

    def test_returns_current_time(self):
        """测试返回当前时间"""
        before = datetime.now(timezone.utc)
        result = utcnow_aware()
        after = datetime.now(timezone.utc)

        assert before <= result <= after


class TestEnsureAware:
    """测试 ensure_aware 函数"""

    def test_naive_datetime(self):
        """测试无时区的 datetime"""
        naive = datetime(2024, 1, 15, 10, 30, 0)

        result = ensure_aware(naive)

        assert result.tzinfo == timezone.utc
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30

    def test_aware_datetime(self):
        """测试带时区的 datetime"""
        aware = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

        result = ensure_aware(aware)

        assert result == aware
        assert result.tzinfo == timezone.utc

    def test_different_timezone(self):
        """测试不同时区的 datetime"""
        from datetime import timedelta

        jst = timezone(timedelta(hours=9))  # Japan Standard Time
        aware_jst = datetime(2024, 1, 15, 10, 30, 0, tzinfo=jst)

        result = ensure_aware(aware_jst)

        # 应该保持原有时区
        assert result == aware_jst
        assert result.tzinfo == jst

    def test_epoch(self):
        """测试 Unix 纪元时间"""
        epoch = datetime(1970, 1, 1, 0, 0, 0)

        result = ensure_aware(epoch)

        assert result.tzinfo == timezone.utc
        assert result.year == 1970

    def test_max_datetime(self):
        """测试最大 datetime"""
        max_dt = datetime.max.replace(tzinfo=None)

        result = ensure_aware(max_dt)

        assert result.tzinfo == timezone.utc
        assert result.year == 9999

    def test_min_datetime(self):
        """测试最小 datetime"""
        min_dt = datetime.min.replace(tzinfo=None)

        result = ensure_aware(min_dt)

        assert result.tzinfo == timezone.utc
        assert result.year == 1


class TestDatetimeEdgeCases:
    """测试边界情况"""

    def test_utcnow_aware_twice(self):
        """测试连续调用 utcnow_aware"""
        result1 = utcnow_aware()
        result2 = utcnow_aware()

        # 第二个结果应该不早于第一个
        assert result2 >= result1
        # 两者都应该带有时区
        assert result1.tzinfo == timezone.utc
        assert result2.tzinfo == timezone.utc

    def test_ensureaware_idempotent(self):
        """测试 ensure_aware 幂等性"""
        naive = datetime(2024, 1, 15, 10, 30, 0)

        result1 = ensure_aware(naive)
        result2 = ensure_aware(result1)

        assert result1 == result2
        assert result1.tzinfo == result2.tzinfo

    def test_microseconds_preserved(self):
        """测试微秒被保留"""
        naive = datetime(2024, 1, 15, 10, 30, 0, 123456)

        result = ensure_aware(naive)

        assert result.microsecond == 123456
