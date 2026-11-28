import pytest
from django.urls import reverse

from apps.parser.models import (
    AIInsight,
    ChannelModerator,
    TelegramChannel,
)
from apps.users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def owner() -> User:
    return User.objects.create_user(
        username="owner",
        email="owner@example.com",
        password="secret123",
    )


@pytest.fixture
def moderator() -> User:
    return User.objects.create_user(
        username="moderator",
        email="moderator@example.com",
        password="secret123",
    )


@pytest.fixture
def outsider() -> User:
    return User.objects.create_user(
        username="outsider",
        email="outsider@example.com",
        password="secret123",
    )


@pytest.fixture
def channel() -> TelegramChannel:
    return TelegramChannel.objects.create(
        channel_id=1000001,
        title="Канал автора",
        username="author_channel",
    )


@pytest.fixture
def foreign_channel() -> TelegramChannel:
    return TelegramChannel.objects.create(
        channel_id=1000002,
        title="Чужой канал",
        username="foreign_channel",
    )


@pytest.fixture
def owner_assignment(
    owner: User,
    channel: TelegramChannel,
) -> ChannelModerator:
    return ChannelModerator.objects.create(
        user=owner,
        channel=channel,
        is_owner=True,
        can_edit=True,
        can_delete=True,
        can_manage_moderators=True,
    )


@pytest.fixture
def moderator_assignment(
    moderator: User,
    channel: TelegramChannel,
) -> ChannelModerator:
    return ChannelModerator.objects.create(
        user=moderator,
        channel=channel,
        is_owner=False,
        can_edit=True,
    )


@pytest.fixture
def channel_insight(owner_assignment: ChannelModerator) -> AIInsight:
    return AIInsight.objects.create(
        user=owner_assignment.user,
        channel=owner_assignment.channel,
        insight_type="recommendation",
        insight_text="Инсайт канала автора",
    )


def test_anonymous_user_is_redirected_to_login(client) -> None:
    response = client.get(
        reverse("ai:ai_cabinet"),
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 302
    assert response.url == reverse("users:login")


def test_outsider_cannot_open_cabinet(client, outsider: User) -> None:
    client.force_login(outsider)

    response = client.get(
        reverse("ai:ai_cabinet"),
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 403


def test_owner_can_open_cabinet(
    client,
    owner: User,
    owner_assignment: ChannelModerator,
) -> None:
    client.force_login(owner)

    response = client.get(
        reverse("ai:ai_cabinet"),
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 200
    assert response.headers["X-Inertia"] == "true"

    page = response.json()
    assert page["component"] == "AICabinet"
    assert page["url"] == reverse("ai:ai_cabinet")
    assert set(page["props"]) >= {
        "channel",
        "ideas",
        "insights",
        "competitors",
        "heatMapData",
        "csrfToken",
    }


def test_moderator_can_open_cabinet(
    client,
    moderator: User,
    moderator_assignment: ChannelModerator,
) -> None:
    client.force_login(moderator)

    response = client.get(
        reverse("ai:ai_cabinet"),
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 200


def test_owner_receives_empty_state(
    client,
    owner: User,
    owner_assignment: ChannelModerator,
) -> None:
    client.force_login(owner)

    response = client.get(
        reverse("ai:ai_cabinet"),
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 200
    props = response.json()["props"]
    assert props["ideas"] == []
    assert props["insights"] == []
    assert props["competitors"] == []
    assert props["heatMapData"] == {}


def test_owner_receives_selected_channel_insights(
    client,
    owner: User,
    owner_assignment: ChannelModerator,
    channel_insight: AIInsight,
) -> None:
    client.force_login(owner)

    response = client.get(
        reverse("ai:ai_cabinet"),
        {"channel_id": owner_assignment.channel_id},
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 200
    assert response.json()["props"]["insights"] == [
        {
            "type": "recommendation",
            "text": "Инсайт канала автора",
        }
    ]


def test_user_cannot_select_foreign_channel(
    client,
    owner: User,
    owner_assignment: ChannelModerator,
    foreign_channel: TelegramChannel,
) -> None:
    client.force_login(owner)

    response = client.get(
        reverse("ai:ai_cabinet"),
        {"channel_id": foreign_channel.pk},
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 404
