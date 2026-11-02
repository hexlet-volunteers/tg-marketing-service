import pytest
from django.core.management import call_command


@pytest.fixture(autouse=True)
def seed_demo_data(settings):
    settings.DEBUG = True
    call_command("seed_demo")


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("url", "component", "expected_keys"),
    [
        ("/channels/", "Channels", {"channels"}),
        ("/compare/", "Compare", {"metrics", "channels"}),
        ("/post/", "Post", {"analysis", "reactions"}),
    ],
)
def test_shell_views_render_db_props(client, url, component, expected_keys):
    response = client.get(url, HTTP_X_INERTIA="true")

    assert response.status_code == 200
    payload = response.json()
    assert payload["component"] == component
    assert expected_keys.issubset(payload["props"])


def test_channels_page_serves_catalog(client):
    response = client.get("/channels/", HTTP_X_INERTIA="true")

    channels = response.json()["props"]["channels"]
    assert len(channels) == 10
    assert channels[0]["name"] == "Психология и жизнь"
    by_name = {channel["name"]: channel for channel in channels}
    assert by_name["Marketing Hub"]["type"] == "group"
    assert all(channel["imageUrl"] == "" for channel in channels)


def test_compare_page_serves_metrics_and_top_channels(client):
    response = client.get("/compare/", HTTP_X_INERTIA="true")

    props = response.json()["props"]
    assert [m["key"] for m in props["metrics"]] == [
        "subscribers",
        "er",
        "growth30d",
        "avgReach",
        "reachPerSub",
    ]
    assert len(props["channels"]) == 5
    assert props["channels"][0]["name"] == "Психология и жизнь"
    assert props["channels"][0]["type"] == "channel"
    assert all(channel["imageUrl"] == "" for channel in props["channels"])


def test_post_page_serves_analysis_and_reactions(client):
    response = client.get("/post/", HTTP_X_INERTIA="true")

    props = response.json()["props"]
    assert props["analysis"]["why_worked"]
    assert props["analysis"]["how_to_improve"]
    assert len(props["analysis"]["similar_posts"]) == 2
    assert len(props["reactions"]) == 4
