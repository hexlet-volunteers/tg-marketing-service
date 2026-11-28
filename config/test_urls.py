import pytest
from django.test import override_settings

from apps.users.constants import UserRole
from apps.users.models import User


@override_settings(DEBUG=False)
def test_unknown_url_renders_not_found_page(client):
    response = client.get("/no-such-page/", HTTP_X_INERTIA="true")

    assert response.status_code == 404
    assert response.json()["component"] == "NotFound"


@override_settings(DEBUG=False)
def test_unknown_url_without_slash_redirects(client):
    # Inertia-ответ не требует собранного Vite-манифеста.
    response = client.get("/no-such-page", HTTP_X_INERTIA="true")

    assert response.status_code == 301
    assert response["Location"] == "/no-such-page/"


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_handler404_renders_not_found_page_for_http404(client):
    response = client.get(
        "/blog/no-such-article/",
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["component"] == "NotFound"
    assert payload["props"]["auth"] is None
    assert payload["url"] == "/blog/no-such-article/"


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_handler404_keeps_auth_props_for_authenticated_user(client):
    user = User.objects.create_user(
        username="reader",
        email="reader@example.com",
        password="secret123",
        role=UserRole.USER,
    )
    client.force_login(user)

    response = client.get(
        "/blog/no-such-article/",
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["component"] == "NotFound"
    assert payload["props"]["auth"]["id"] == user.id
