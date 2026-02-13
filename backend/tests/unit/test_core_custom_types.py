"""
测试自定义 SQLAlchemy 类型
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import JSON, String

from ai_ppt.core.custom_types import GUID, JSONType


class TestGUID:
    """测试 GUID 类型"""

    def test_init_default_length(self):
        """测试默认长度初始化"""
        guid = GUID()
        assert guid.length == 36

    def test_init_custom_length(self):
        """测试自定义长度初始化"""
        guid = GUID(length=50)
        assert guid.length == 50

    def test_load_dialect_impl_postgresql(self):
        """测试 PostgreSQL 方言实现"""
        guid = GUID()
        dialect = MagicMock()
        dialect.name = "postgresql"
        dialect.type_descriptor.return_value = PG_UUID()

        result = guid.load_dialect_impl(dialect)
        assert isinstance(result, PG_UUID)

    def test_load_dialect_impl_sqlite(self):
        """测试 SQLite 方言实现"""
        guid = GUID()
        dialect = MagicMock()
        dialect.name = "sqlite"

        result = guid.load_dialect_impl(dialect)
        # 应该返回 String(36) 类型
        assert result is not None

    def test_process_bind_param_none(self):
        """测试绑定参数为 None"""
        guid = GUID()
        dialect = MagicMock()
        dialect.name = "postgresql"

        result = guid.process_bind_param(None, dialect)
        assert result is None

    def test_process_bind_param_postgresql(self):
        """测试 PostgreSQL 绑定参数处理"""
        guid = GUID()
        dialect = MagicMock()
        dialect.name = "postgresql"
        test_uuid = uuid.uuid4()

        result = guid.process_bind_param(test_uuid, dialect)
        assert result == str(test_uuid)

    def test_process_bind_param_other_db(self):
        """测试其他数据库绑定参数处理"""
        guid = GUID()
        dialect = MagicMock()
        dialect.name = "sqlite"
        test_uuid = uuid.uuid4()

        result = guid.process_bind_param(test_uuid, dialect)
        assert result == str(test_uuid)

    def test_process_bind_param_string_value(self):
        """测试字符串 UUID 值"""
        guid = GUID()
        dialect = MagicMock()
        dialect.name = "sqlite"
        test_uuid_str = str(uuid.uuid4())

        result = guid.process_bind_param(test_uuid_str, dialect)
        assert result == test_uuid_str

    def test_process_result_value_none(self):
        """测试结果值为 None"""
        guid = GUID()
        dialect = MagicMock()

        result = guid.process_result_value(None, dialect)
        assert result is None

    def test_process_result_value_uuid(self):
        """测试结果值已经是 UUID 对象"""
        guid = GUID()
        dialect = MagicMock()
        test_uuid = uuid.uuid4()

        result = guid.process_result_value(test_uuid, dialect)
        assert result == test_uuid

    def test_process_result_value_string(self):
        """测试结果值是字符串"""
        guid = GUID()
        dialect = MagicMock()
        test_uuid = uuid.uuid4()

        result = guid.process_result_value(str(test_uuid), dialect)
        assert result == test_uuid
        assert isinstance(result, uuid.UUID)


class TestJSONType:
    """测试 JSONType 类型"""

    def test_init(self):
        """测试初始化"""
        json_type = JSONType()
        assert json_type.cache_ok is True

    def test_load_dialect_impl(self):
        """测试方言实现加载"""
        json_type = JSONType()
        dialect = MagicMock()

        result = json_type.load_dialect_impl(dialect)
        assert result is not None
