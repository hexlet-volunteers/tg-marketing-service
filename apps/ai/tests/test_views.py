import pytest
from django.core.management import call_command

from apps.parser.models import AIInsight
from apps.users.models import User
from mocks import ai as ai_mocks
from mocks.users import DEMO_USERNAMES

pytestmark = pytest.mark.django_db

DEMO_USERNAME = DEMO_USERNAMES[1]


def _props(client) -> dict:
    response = client.get("/ai-cabinet/", HTTP_X_INERTIA="true")

    assert response.status_code == 200
    payload = response.json()
    assert payload["component"] == "AICabinet"
    return payload["props"]


def _create_demo_insight() -> None:
    user = User.objects.create_user(
        username=DEMO_USERNAME,
        email="demo_user@example.com",
        password="secret123",
        role="user",
    )
    AIInsight.objects.create(
        user=user,
        insight_type="recommendation",
        insight_text="Демо-инсайт",
    )


def test_ai_cabinet_view_empty(client):
    props = _props(client)

    assert props["ideas"] == []
    assert props["insights"] == []
    assert props["competitors"] == []
    assert props["heatMapData"] == {}


def test_ai_cabinet_view_uses_db_insights_and_mock_fallback(client):
    _create_demo_insight()

    props = _props(client)

    assert props["ideas"] == ai_mocks.MOCK_IDEAS
    assert props["competitors"] == ai_mocks.MOCK_COMPETITORS
    assert props["heatMapData"] == ai_mocks.MOCK_HEAT_MAP
    assert props["insights"] == [
        {"type": "recommendation", "text": "Демо-инсайт"}
    ]


def test_clear_demo_empties_ai_cabinet(client):
    _create_demo_insight()
    assert _props(client)["ideas"]

    call_command("clear_demo", force=True)

    props = _props(client)
    assert props["ideas"] == []
    assert props["insights"] == []
    assert props["competitors"] == []
    assert props["heatMapData"] == {}
