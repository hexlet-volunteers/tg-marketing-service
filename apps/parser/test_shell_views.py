import pytest


@pytest.mark.parametrize(
    ("url", "component", "expected_keys"),
    [
        ("/channels/", "Channels", {"channels"}),
        ("/compare/", "Compare", {"metrics", "channels"}),
        ("/post/", "Post", {"analysis", "reactions"}),
    ],
)
def test_shell_views_render_mock_props(client, url, component, expected_keys):
    response = client.get(url, HTTP_X_INERTIA="true")

    assert response.status_code == 200
    payload = response.json()
    assert payload["component"] == component
    # Мок-данные отдаются бэкендом из реестра apps/parser/mock_data.py.
    assert expected_keys.issubset(payload["props"])


def test_channels_page_serves_mock_catalog(client):
    response = client.get("/channels/", HTTP_X_INERTIA="true")

    channels = response.json()["props"]["channels"]
    assert len(channels) == 10
    first = channels[0]
    assert first["name"] == "Tech News RU"
    assert first["type"] == "channel"
    assert first["subscribers"] == 125000


def test_compare_page_serves_mock_metrics_and_top3_channels(client):
    response = client.get("/compare/", HTTP_X_INERTIA="true")

    props = response.json()["props"]
    assert [m["key"] for m in props["metrics"]] == [
        "subscribers",
        "er",
        "growth30d",
        "avgReach",
        "reachPerSub",
    ]
    assert len(props["channels"]) == 3
    assert props["channels"][0]["name"] == "Tech News RU"


def test_post_page_serves_mock_analysis_and_reactions(client):
    response = client.get("/post/", HTTP_X_INERTIA="true")

    props = response.json()["props"]
    assert props["analysis"]["why_worked"]
    assert props["analysis"]["how_to_improve"]
    assert len(props["analysis"]["similar_posts"]) == 2
    assert len(props["reactions"]) == 4
