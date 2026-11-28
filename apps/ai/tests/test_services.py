import pytest

from apps.ai.dto.ai_cabinet_dto import AICabinetDTO
from apps.ai.services.ai_cabinet_service import AICabinetService
from apps.parser.models import AIInsight, TelegramChannel
from apps.users.models import User
from mocks import ai as ai_mocks
from mocks.users import DEMO_USERNAMES

pytestmark = pytest.mark.django_db

DEMO_USERNAME = DEMO_USERNAMES[1]


def _create_user(username: str, email: str) -> User:
    return User.objects.create_user(
        username=username,
        email=email,
        password="secret123",
    )


def _create_channel(
    channel_id: int,
    title: str,
) -> TelegramChannel:
    return TelegramChannel.objects.create(
        channel_id=channel_id,
        title=title,
    )


def test_build_returns_selected_channel_and_empty_sections() -> None:
    user = _create_user("author", "author@example.com")
    channel = _create_channel(100001, "Канал автора")

    dto = AICabinetService(
        user=user,
        channel=channel,
    ).build()

    assert isinstance(dto, AICabinetDTO)
    assert dto.channel.id == channel.pk
    assert dto.channel.title == "Канал автора"
    assert dto.ideas == []
    assert dto.insights == []
    assert dto.competitors == []
    assert dto.heatMapData == {}


def test_build_returns_only_selected_channel_insights() -> None:
    user = _create_user("author", "author@example.com")
    other_user = _create_user("other", "other@example.com")

    selected_channel = _create_channel(100001, "Выбранный канал")
    other_channel = _create_channel(100002, "Другой канал")

    AIInsight.objects.create(
        user=user,
        channel=selected_channel,
        insight_type="recommendation",
        insight_text="Нужный инсайт",
    )
    AIInsight.objects.create(
        user=user,
        channel=other_channel,
        insight_type="trend",
        insight_text="Инсайт другого канала",
    )
    AIInsight.objects.create(
        user=other_user,
        channel=selected_channel,
        insight_type="warning",
        insight_text="Инсайт другого пользователя",
    )

    dto = AICabinetService(
        user=user,
        channel=selected_channel,
    ).build()

    assert [(item.type, item.text) for item in dto.insights] == [
        ("recommendation", "Нужный инсайт")
    ]


def test_demo_data_enables_mock_sections() -> None:
    demo_user = _create_user(DEMO_USERNAME, "demo@example.com")
    demo_channel = _create_channel(100001, "Демо-канал")

    AIInsight.objects.create(
        user=demo_user,
        channel=demo_channel,
        insight_type="recommendation",
        insight_text="Демо-инсайт",
    )

    author = _create_user("author", "author@example.com")
    author_channel = _create_channel(100002, "Канал автора")

    dto = AICabinetService(
        user=author,
        channel=author_channel,
    ).build()

    assert [item.model_dump() for item in dto.ideas] == ai_mocks.MOCK_IDEAS
    assert [
        item.model_dump() for item in dto.competitors
    ] == ai_mocks.MOCK_COMPETITORS
    assert dto.heatMapData == ai_mocks.MOCK_HEAT_MAP
    assert dto.insights == []
