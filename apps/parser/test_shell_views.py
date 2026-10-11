import pytest


@pytest.mark.parametrize(
    ("url", "component"),
    [
        ("/channels/", "Channels"),
        ("/compare/", "Compare"),
        ("/post/", "Post"),
    ],
)
def test_shell_views_render_component(client, url, component):
    response = client.get(url, HTTP_X_INERTIA="true")

    assert response.status_code == 200
    assert response.json()["component"] == component
