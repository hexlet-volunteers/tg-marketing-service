import pytest


@pytest.mark.parametrize(
    ("url", "component", "forbidden_keys"),
    [
        ("/channels/", "Channels", {"channels"}),
        ("/compare/", "Compare", {"metrics", "channels"}),
        ("/post/", "Post", set()),
    ],
)
def test_shell_views_render_component(client, url, component, forbidden_keys):
    response = client.get(url, HTTP_X_INERTIA="true")

    assert response.status_code == 200
    payload = response.json()
    assert payload["component"] == component
    # Плейсхолдер-DTO (кроме статичного /post/) создается пустым:
    # page-props минимальны, данные рендерит фронтенд.
    assert forbidden_keys.isdisjoint(payload["props"])
