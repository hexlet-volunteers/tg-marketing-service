from itertools import count

import pytest

from apps.group_channels.models import AutoGroupRule, Group
from apps.parser.models import TelegramChannel
from apps.users.models import User


@pytest.fixture
def user_factory(db):
    """Фабрика пользователей."""

    def factory(**kwargs):
        defaults = {
            "username": "test-user",
            "email": "test@example.com",
            "password": "test-password",
            "role": "user",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return factory


@pytest.fixture
def owner(user_factory):
    return user_factory(username="owner", email="owner@example.com")


@pytest.fixture
def curator(user_factory):
    return user_factory(username="editor", email="editor@example.com")


@pytest.fixture
def group_factory(db, owner):
    """Фабрика ручных и редакторских подборок."""

    def factory(**kwargs):
        defaults = {
            "name": "Тестовая подборка",
            "slug": "test-collection",
            "description": "Описание тестовой подборки",
            "owner": owner,
        }
        defaults.update(kwargs)
        return Group.objects.create(**defaults)

    return factory


@pytest.fixture
def channel_factory(db):
    """Фабрика каналов с уникальными channel_id."""

    ids = count(100001)

    def factory(**kwargs):
        channel_id = next(ids)

        defaults = {
            "channel_id": channel_id,
            "username": f"channel_{channel_id}",
            "title": "Тестовый канал",
            "participants_count": 1000,
            "average_views": 500,
            "category": "Технологии",
            "country": "RU",
        }
        defaults.update(kwargs)
        return TelegramChannel.objects.create(**defaults)

    return factory


@pytest.fixture
def auto_rule_factory(db):
    """Фабрика правил автоматических подборок."""

    def factory(group, **kwargs):
        return AutoGroupRule.objects.create(
            group=group,
            **kwargs,
        )

    return factory


@pytest.fixture
def manual_group(group_factory, channel_factory):
    """Ручная подборка с одним каналом."""

    group = group_factory(
        name="Топ IT-каналов",
        slug="top-it",
        description="Подборка технологических каналов",
        is_editorial=True,
    )

    channel = channel_factory(
        username="product_radar",
        title="Product Radar",
        participants_count=142000,
        average_views=38200,
        category="Технологии",
        country="RU",
    )

    group.channels.add(channel)

    return group


@pytest.fixture
def auto_group(group_factory, auto_rule_factory):
    """Автоматическая подборка по категории."""

    group = group_factory(
        name="Научные каналы",
        slug="science",
    )

    auto_rule_factory(group, category="Наука")

    return group
