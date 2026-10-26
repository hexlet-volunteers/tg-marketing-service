import pytest

from apps.ai.dto.ai_cabinet_dto import AICabinetDTO
from apps.ai.services.ai_cabinet_service import AICabinetService
from apps.parser.models import AIInsight
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
        role="user",
    )


def test_build_empty_database_returns_empty_dto():
    dto = AICabinetService().build()

    assert isinstance(dto, AICabinetDTO)
    assert dto.ideas == []
    assert dto.insights == []
    assert dto.competitors == []
    assert dto.heatMapData == {}


def test_non_demo_insight_does_not_enable_mocks():
    user = _create_user("author", "author@example.com")
    AIInsight.objects.create(
        user=user,
        insight_type="trend",
        insight_text="Реальный инсайт",
    )

    dto = AICabinetService().build()

    assert [(item.type, item.text) for item in dto.insights] == [
        ("trend", "Реальный инсайт")
    ]
    assert dto.ideas == []
    assert dto.competitors == []
    assert dto.heatMapData == {}


def test_demo_insight_enables_mock_data():
    user = _create_user(DEMO_USERNAME, "demo_user@example.com")
    AIInsight.objects.create(
        user=user,
        insight_type="recommendation",
        insight_text="Демо-инсайт",
    )

    dto = AICabinetService().build()

    assert [item.model_dump() for item in dto.ideas] == ai_mocks.MOCK_IDEAS
    assert [
        item.model_dump() for item in dto.competitors
    ] == ai_mocks.MOCK_COMPETITORS
    assert dto.heatMapData == ai_mocks.MOCK_HEAT_MAP
    assert [(item.type, item.text) for item in dto.insights] == [
        ("recommendation", "Демо-инсайт")
    ]


def test_authenticated_user_sees_only_own_insights():
    demo_user = _create_user(DEMO_USERNAME, "demo_user@example.com")
    other_user = _create_user("other", "other@example.com")
    AIInsight.objects.create(
        user=demo_user,
        insight_type="trend",
        insight_text="Свой инсайт",
    )
    AIInsight.objects.create(
        user=other_user,
        insight_type="warning",
        insight_text="Чужой инсайт",
    )

    dto = AICabinetService(demo_user).build()

    assert [(item.type, item.text) for item in dto.insights] == [
        ("trend", "Свой инсайт")
    ]
