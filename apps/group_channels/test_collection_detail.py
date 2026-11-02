import pytest

from apps.group_channels.models import Group
from apps.parser.models import TelegramChannel
from apps.users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def collection():
    owner = User.objects.create_user(
        username="collection-owner",
        email="collection-owner@example.com",
        role="user",
    )
    group = Group.objects.create(
        name="Топ IT-каналов",
        description="Лучшие каналы",
        owner=owner,
        is_editorial=True,
    )
    for channel_id, title, username in (
        (1, "Product Radar", "productradar"),
        (2, "Tech News", "technews"),
        (3, "Dev Tools", "devtools"),
    ):
        group.channels.add(
            TelegramChannel.objects.create(
                channel_id=channel_id,
                title=title,
                username=username,
                participants_count=1000 + channel_id,
                citation_index=5.5,
            )
        )
    return group


def test_collection_detail_renders_db_group(client, collection):
    response = client.get(
        f"/collections/{collection.pk}/",
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["component"] == "Collection"
    props = payload["props"]
    assert props["title"] == "Топ IT-каналов"
    assert props["description"] == "Лучшие каналы"
    assert props["channel_count"] == 3
    assert len(props["channels"]) == 3
    assert props["channels"][0]["name"] == "Product Radar"
    assert props["channels"][0]["color"]


def test_collection_detail_missing_group_returns_404(client):
    response = client.get("/collections/999/", HTTP_X_INERTIA="true")

    assert response.status_code == 404
