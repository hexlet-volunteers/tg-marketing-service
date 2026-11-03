from datetime import timedelta
from typing import Any

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from django.utils import timezone

from apps.billing.models import Plan
from apps.parser.models import ChannelStats, Post, TelegramChannel
from apps.users.management.commands.seed_demo import (
    DEFAULT_POSTS_PER_CHANNEL,
    DEFAULT_STATS_DAYS,
    DEMO_CHANNEL_ID_MIN,
)
from apps.users.models import User
from mocks.parser import MOCK_CHANNELS

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_debug(settings: Any) -> None:
    settings.DEBUG = True


def test_seed_demo_stats_are_idempotent():
    call_command("seed_demo")
    call_command("seed_demo")

    channels = TelegramChannel.objects.filter(
        channel_id__gte=DEMO_CHANNEL_ID_MIN
    )
    stats = ChannelStats.objects.filter(channel__in=channels)
    channels_count = len(MOCK_CHANNELS)

    assert channels.count() == channels_count
    assert (
        Post.objects.filter(channel__in=channels).count()
        == channels_count * DEFAULT_POSTS_PER_CHANNEL
    )
    assert stats.count() == channels_count * DEFAULT_STATS_DAYS
    for channel in channels:
        assert (
            ChannelStats.objects.filter(channel=channel).count()
            == DEFAULT_STATS_DAYS
        )

    parsed_at_values = sorted(stats.values_list("parsed_at", flat=True))
    assert parsed_at_values[-1] - parsed_at_values[0] == timedelta(
        days=DEFAULT_STATS_DAYS - 1
    )


def test_seed_demo_removes_posts_beyond_default_range():
    call_command("seed_demo")

    channel = TelegramChannel.objects.filter(
        channel_id__gte=DEMO_CHANNEL_ID_MIN
    ).first()
    assert channel is not None
    stale_post = Post.objects.create(
        channel=channel,
        telegram_message_id=(
            channel.channel_id * 10000 + DEFAULT_POSTS_PER_CHANNEL + 1
        ),
        text="stale",
        published_at=timezone.now(),
    )

    call_command("seed_demo")

    assert not Post.objects.filter(pk=stale_post.pk).exists()


def _plan_snapshot() -> list[Any]:
    return list(
        Plan.objects.order_by("code").values(
            "id",
            "code",
            "name",
            "description",
            "monthly_price",
            "annual_price",
            "currency",
            "is_highlighted",
            "ordering",
            "channels_limit",
            "ai_requests_limit",
            "features",
        )
    )


def test_seed_demo_does_not_change_migration_plans():
    before = _plan_snapshot()

    call_command("seed_demo")

    assert _plan_snapshot() == before


def test_clear_demo_keeps_migration_plans():
    call_command("seed_demo")
    before = _plan_snapshot()

    call_command("clear_demo", force=True)

    assert Plan.objects.count() == 3
    assert _plan_snapshot() == before


def test_seed_demo_refuses_in_prod(monkeypatch):
    monkeypatch.setenv("PROD", "t")

    with pytest.raises(CommandError):
        call_command("seed_demo")

    assert not TelegramChannel.objects.filter(
        channel_id__gte=DEMO_CHANNEL_ID_MIN
    ).exists()


def test_seed_demo_fills_dashboard_for_demo_user(client):
    call_command("seed_demo")

    user = User.objects.get(username="demo_user")
    client.force_login(user)

    response = client.get(
        reverse("homepage:dashboard"),
        HTTP_ACCEPT="application/json",
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 200
    props = response.json()["props"]

    assert props["channel"]["name"]
    assert len(props["kpis"]) == 4
    assert len(props["growthData"]) == DEFAULT_STATS_DAYS
    assert len(props["posts"]) == DEFAULT_POSTS_PER_CHANNEL
