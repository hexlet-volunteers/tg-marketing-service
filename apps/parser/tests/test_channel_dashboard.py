"""Тесты дашборда канала (Inertia: ChannelDashboard) — #254."""

import json
from datetime import timedelta
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.parser.models import (
    AIInsight,
    ChannelStats,
    Post,
    PostReaction,
    TelegramChannel,
)
from apps.parser.services.channel_dashboard import (
    DEFAULT_PERIOD,
    build_channel_dashboard,
    parse_dashboard_period,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def client() -> Client:
    return Client(HTTP_X_INERTIA="true")


@pytest.fixture
def channel() -> TelegramChannel:
    return TelegramChannel.objects.create(
        channel_id=123456,
        title="Test Channel",
        username="testchannel",
        participants_count=10000,
        average_views=5000,
        category="Технологии",
        country="Россия",
        citation_index=2.5,
        last_messages=[
            {"post_id": 102, "post_text": "Второй пост", "post_views": 700},
            {"post_id": 101, "post_text": "Первый пост", "post_views": 600},
            {"post_id": 103, "post_text": "Третий пост", "post_views": 800},
        ],
    )


def make_stat(
    channel: TelegramChannel, participants: int, days_ago: float
) -> ChannelStats:
    stat = ChannelStats.objects.create(
        channel=channel, participants_count=participants
    )
    ChannelStats.objects.filter(pk=stat.pk).update(
        parsed_at=timezone.now() - timedelta(days=days_ago)
    )
    return stat


def make_post(
    channel: TelegramChannel,
    days_ago: float,
    views: int = 1000,
    reactions: int = 0,
    forwards: int = 10,
    comments: int = 5,
) -> Post:
    post = Post.objects.create(
        channel=channel,
        telegram_message_id=int(days_ago * 1000) or 1,
        text=f"Пост {days_ago}",
        published_at=timezone.now() - timedelta(days=days_ago),
        views=views,
        forwards=forwards,
        comments_count=comments,
    )
    if reactions:
        PostReaction.objects.create(post=post, emoji="👍", count=reactions)
    return post


def get_props(response: HttpResponse) -> dict[str, Any]:
    assert response.status_code == 200

    page: dict[str, Any] = json.loads(response.content)
    assert page["component"] == "ChannelDashboard"

    props = page["props"]
    assert isinstance(props, dict)
    return props


def kpis_by_key(props: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {kpi["key"]: kpi for kpi in props["kpis"]}


def test_period_parser() -> None:
    assert parse_dashboard_period(None) == DEFAULT_PERIOD
    assert parse_dashboard_period("") == DEFAULT_PERIOD
    assert parse_dashboard_period("abc") == DEFAULT_PERIOD
    assert parse_dashboard_period("14") == DEFAULT_PERIOD
    assert parse_dashboard_period("7") == 7
    assert parse_dashboard_period("30") == 30
    assert parse_dashboard_period("90") == 90


def test_detail_view_contract(client: Client, channel: TelegramChannel) -> None:
    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))

    props = get_props(response)
    assert props["period"] == 30
    assert props["csrfToken"]
    assert set(props) >= {
        "header",
        "period",
        "kpis",
        "growth",
        "ai_advice",
        "latest_posts",
        "csrfToken",
    }
    assert [kpi["key"] for kpi in props["kpis"]] == [
        "subs",
        "reach",
        "er",
        "citation",
    ]


def test_channels_catalog_exposes_pk(
    client: Client, channel: TelegramChannel
) -> None:
    response = client.get(reverse("channels_catalog"))
    assert response.status_code == 200

    cards = json.loads(response.content)["props"]["channels"]
    card = next(item for item in cards if item["name"] == channel.title)
    assert card["pk"] == channel.pk
    assert card["id"] == channel.channel_id


def test_header_props(client: Client, channel: TelegramChannel) -> None:
    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))

    header = get_props(response)["header"]
    assert header["title"] == "Test Channel"
    assert header["username"] == "@testchannel"
    assert header["avatar"] is None
    assert header["category"] == "Технологии"
    assert header["country"] == "Россия"
    assert header["verified"] is False


def test_header_avatar_is_channel_attribute(
    client: Client, channel: TelegramChannel
) -> None:
    """Аватар в шапке — канала, а не текущего пользователя.

    У ``TelegramChannel`` нет поля изображения, поэтому backend отдаёт
    ``null``; frontend рисует градиент с инициалами.
    """
    user = get_user_model().objects.create_user(
        username="avatar-user",
        email="avatar@example.com",
        password="x",
        avatar_image="https://example.com/avatar.png",
    )

    client.force_login(user)
    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))

    assert get_props(response)["header"]["avatar"] is None


def test_kpis_with_deltas(client: Client, channel: TelegramChannel) -> None:
    make_post(channel, days_ago=45, views=1000, reactions=5)
    make_post(channel, days_ago=5, views=2000, reactions=50)
    make_stat(channel, participants=9000, days_ago=40)
    make_stat(channel, participants=10000, days_ago=1)

    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))
    kpis = kpis_by_key(get_props(response))

    assert kpis["subs"]["value"] == 10000
    assert kpis["subs"]["delta"] == 1000
    assert kpis["subs"]["percentDelta"] == 11.11
    assert kpis["subs"]["delta_pct"] == 11.11
    assert kpis["subs"]["positive"] is True

    assert kpis["reach"]["value"] == 2000
    assert kpis["reach"]["delta"] == 1000
    assert kpis["reach"]["percentDelta"] == 100.0

    # ER = (reactions + comments + forwards) / views * 100
    assert kpis["er"]["value"] == 3.25
    assert kpis["er"]["delta"] == 1.25
    assert kpis["er"]["percentDelta"] == 62.5

    assert kpis["citation"]["value"] == 2.5
    assert kpis["citation"]["delta"] == 0


def test_subs_delta_uses_only_previous_window(
    client: Client, channel: TelegramChannel
) -> None:
    """Статистика старше предыдущего окна не даёт ложную дельту."""
    make_stat(channel, participants=5000, days_ago=100)

    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))
    subs = kpis_by_key(get_props(response))["subs"]

    assert subs["value"] == 10000
    assert subs["delta"] == 0
    assert subs["percentDelta"] == 0


def test_period_changes_recalculation(
    client: Client, channel: TelegramChannel
) -> None:
    make_post(channel, days_ago=45, views=1000)
    make_post(channel, days_ago=5, views=2000)
    stats_url = reverse("parser:detail", kwargs={"pk": channel.pk})

    props_30 = get_props(client.get(stats_url))
    props_90 = get_props(client.get(stats_url, data={"period": 90}))
    props_7 = get_props(client.get(stats_url, data={"period": 7}))

    reach_30 = kpis_by_key(props_30)["reach"]["value"]
    reach_90 = kpis_by_key(props_90)["reach"]["value"]
    reach_7 = kpis_by_key(props_7)["reach"]["value"]

    assert props_30["period"] == 30
    assert props_90["period"] == 90
    assert props_7["period"] == 7
    assert reach_30 == 2000
    assert reach_90 == 1500
    assert reach_7 == 2000


def test_invalid_period_falls_back_to_default(
    client: Client, channel: TelegramChannel
) -> None:
    url = reverse("parser:detail", kwargs={"pk": channel.pk})
    for period in ("14", "abc", "-5"):
        props = get_props(client.get(url, data={"period": period}))
        assert props["period"] == 30


def test_growth_series_is_daily(
    client: Client, channel: TelegramChannel
) -> None:
    make_stat(channel, participants=9000, days_ago=40)
    make_stat(channel, participants=12000, days_ago=5)
    make_stat(channel, participants=15000, days_ago=1)

    response = client.get(
        reverse("parser:detail", kwargs={"pk": channel.pk}),
        data={"period": 7},
    )
    growth = get_props(response)["growth"]

    assert len(growth) == 7
    assert growth[-1]["date"] == timezone.now().date().isoformat()
    assert growth[-1]["subscribers"] == 15000
    # Значение последней точки перед окном переносится вперёд.
    assert growth[0]["subscribers"] == 9000
    assert growth[1]["subscribers"] == 12000


def test_growth_is_empty_without_stats(
    client: Client, channel: TelegramChannel
) -> None:
    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))
    assert get_props(response)["growth"] == []


def test_ai_advice_for_owner(client: Client, channel: TelegramChannel) -> None:
    user = get_user_model().objects.create_user(
        username="adviser", email="a@example.com", password="x"
    )
    AIInsight.objects.create(
        user=user,
        channel=channel,
        insight_text="Посты с видео набирают охват",
        insight_type="recommendation",
    )

    client.force_login(user)
    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))

    advice = get_props(response)["ai_advice"]
    assert len(advice) == 1
    assert advice[0]["text"] == "Посты с видео набирают охват"
    assert advice[0]["type"] == "recommendation"
    assert advice[0]["created_at"]


def test_ai_advice_hidden_from_anonymous_and_other_user(
    client: Client, channel: TelegramChannel
) -> None:
    owner = get_user_model().objects.create_user(
        username="owner", email="owner@example.com", password="x"
    )
    AIInsight.objects.create(
        user=owner,
        channel=channel,
        insight_text="Секретный совет владельца",
        insight_type="recommendation",
    )

    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))
    assert get_props(response)["ai_advice"] == []

    other = get_user_model().objects.create_user(
        username="other", email="other@example.com", password="x"
    )
    client.force_login(other)
    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))
    assert get_props(response)["ai_advice"] == []


def test_latest_posts_sorted_with_links(
    client: Client, channel: TelegramChannel
) -> None:
    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))

    posts = get_props(response)["latest_posts"]
    assert [post["id"] for post in posts] == [103, 102, 101]
    assert posts[0]["title"] == "Третий пост"
    assert posts[0]["views"] == 800
    assert posts[0]["url"] == "https://t.me/testchannel/103"


def test_latest_posts_guards_and_truncation(
    client: Client,
) -> None:
    channel = TelegramChannel.objects.create(
        channel_id=654323,
        title="Guarded",
        username="-",
        last_messages=[
            {"post_id": 1, "post_text": "А" * 500, "post_views": 100},
            {"post_id": 2, "post_text": 42, "post_views": "abc"},
            {"post_id": 3, "post_views": 100},
            "не словарь",
            {"post_id": "4", "post_text": "str id"},
        ],
    )

    response = client.get(reverse("parser:detail", kwargs={"pk": channel.pk}))

    props = get_props(response)
    posts = props["latest_posts"]
    assert [post["id"] for post in posts] == [3, 2, 1]
    assert posts[0]["url"] is None
    assert len(posts[2]["title"]) == 300
    assert posts[2]["views"] == 100
    assert props["header"]["username"] is None


def test_empty_channel_sections(client: Client) -> None:
    empty = TelegramChannel.objects.create(
        channel_id=654321,
        title="Empty",
        average_views=5000,
        last_messages=[],
    )

    response = client.get(reverse("parser:detail", kwargs={"pk": empty.pk}))
    props = get_props(response)
    kpis = kpis_by_key(props)

    assert kpis["reach"]["value"] == 5000
    assert kpis["reach"]["delta"] == 0
    assert kpis["subs"]["delta"] == 0
    assert props["growth"] == []
    assert props["ai_advice"] == []
    assert props["latest_posts"] == []


def test_404_for_missing_and_private_channel(client: Client) -> None:
    missing = client.get(reverse("parser:detail", kwargs={"pk": 999999}))
    assert missing.status_code == 404

    private = TelegramChannel.objects.create(
        channel_id=654322,
        title="Private",
        is_public=False,
        last_messages=[],
    )
    hidden = client.get(reverse("parser:detail", kwargs={"pk": private.pk}))
    assert hidden.status_code == 404


def test_service_rejects_unknown_period(channel: TelegramChannel) -> None:
    """Сервис принимает только нормализованный период."""
    with pytest.raises(ValueError):
        build_channel_dashboard(channel, 45)
