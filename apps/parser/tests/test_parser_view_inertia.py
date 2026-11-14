"""Inertia-контракт формы добавления канала (``Parser``)."""

import json
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def client() -> Client:
    user = get_user_model().objects.create_user(
        username="parser-view-user",
        email="parser@example.com",
        password="password",
    )
    client = Client(HTTP_X_INERTIA="true")
    client.force_login(user)
    return client


def get_page(response: Any) -> dict[str, Any]:
    assert response.status_code == 200
    page: dict[str, Any] = json.loads(response.content)
    return page


def test_parser_view_renders_inertia_form(client: Client) -> None:
    page = get_page(client.get(reverse("parser:parser")))

    assert page["component"] == "Parser"
    props = page["props"]
    assert props["form"]["data"]["limit"] == 10
    assert props["form"]["errors"] == {}
    assert "Технологии" in props["options"]["categories"]
    assert props["options"]["limit_min"] == 1
    assert props["options"]["limit_max"] == 20


def test_parser_view_invalid_post_echoes_values(client: Client) -> None:
    response = client.post(
        reverse("parser:parser"),
        data={"channel_identifier": "@my_channel"},
    )
    page = get_page(response)

    assert page["component"] == "Parser"
    form = page["props"]["form"]
    assert form["data"]["channel_identifier"] == "@my_channel"
    assert "category" in form["errors"]
    assert form["errors"]["category"][0]["message"]
    assert form["errors"]["category"][0]["code"]
