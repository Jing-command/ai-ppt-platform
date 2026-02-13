"""
测试数据工厂
使用 factory-boy 创建测试数据
"""

import uuid
from datetime import datetime, timezone

import factory
from factory import Faker


class UserFactory(factory.Factory):
    """用户工厂"""

    class Meta:
        model = dict  # 使用字典模型，避免 SQLAlchemy 依赖问题

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    hashed_password = "$2b$12$test_hash_value_for_testing_only"
    is_active = True
    is_superuser = False
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    last_login = None


class ConnectorFactory(factory.Factory):
    """连接器工厂"""

    class Meta:
        model = dict

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Connector {n}")
    type = "mysql"
    user_id = factory.LazyFunction(uuid.uuid4)
    config = factory.LazyFunction(
        lambda: {
            "host": "localhost",
            "port": 3306,
            "database": "test_db",
            "username": "test_user",
            "password": "test_pass",
        }
    )
    description = Faker("sentence")
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class OutlineFactory(factory.Factory):
    """大纲工厂"""

    class Meta:
        model = dict

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)
    title = Faker("sentence", nb_words=4)
    description = Faker("paragraph")
    pages = factory.LazyFunction(
        lambda: [
            {
                "id": f"page-{i}",
                "pageNumber": i,
                "title": f"Page {i}",
                "content": f"Content for page {i}",
                "pageType": "content",
            }
            for i in range(1, 4)
        ]
    )
    background = factory.LazyFunction(
        lambda: {
            "type": "ai",
            "prompt": "科技感蓝色渐变背景",
        }
    )
    total_slides = 3
    status = "draft"
    ai_prompt = None
    ai_parameters = None
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class PresentationFactory(factory.Factory):
    """演示文稿工厂"""

    class Meta:
        model = dict

    id = factory.LazyFunction(uuid.uuid4)
    title = Faker("sentence", nb_words=4)
    owner_id = factory.LazyFunction(uuid.uuid4)
    outline_id = None
    theme = "default"
    description = Faker("paragraph")
    status = "draft"
    version = 1
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class SlideFactory(factory.Factory):
    """幻灯片工厂"""

    class Meta:
        model = dict

    id = factory.LazyFunction(uuid.uuid4)
    presentation_id = factory.LazyFunction(uuid.uuid4)
    title = Faker("sentence", nb_words=3)
    layout_type = "title_content"
    order_index = factory.Sequence(lambda n: n)
    content = factory.LazyFunction(
        lambda: {
            "title": "Slide Title",
            "text": "Slide content text",
        }
    )
    notes = None
    version = 1
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
