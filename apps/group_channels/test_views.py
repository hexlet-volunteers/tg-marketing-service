from django.test import TestCase
from django.urls import reverse

from apps.group_channels.mock_data import MOCK_COLLECTIONS
from apps.group_channels.models import Group
from apps.group_channels.services.collections_catalog_service import (
    CollectionsCatalogService,
)
from apps.group_channels.views import DEFAULT_AVATAR_GROUP
from apps.users.models import User


class CreateGroupViewTest(TestCase):
    def test_owner_creates_group_and_receives_inertia_response(self) -> None:
        user = User.objects.create_user(
            username="group-owner", email="owner@example.com", role="user"
        )
        self.client.force_login(user)
        url = reverse("group_channels:group_create")

        response = self.client.post(
            url,
            {"name": "My collection", "description": "Selected channels"},
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)
        group = Group.objects.get()
        self.assertEqual(group.owner, user)
        self.assertEqual(group.name, "My collection")
        self.assertEqual(group.description, "Selected channels")
        self.assertEqual(group.image_url, DEFAULT_AVATAR_GROUP)
        data = response.json()
        self.assertEqual(data["component"], "Channels")
        self.assertEqual(data["url"], url)
        self.assertEqual(data["props"]["group"], {"name": group.name})
        self.assertTrue(data["props"]["flash"]["success"])


class CollectionsCatalogViewTest(TestCase):
    def _get_catalog(self, query: str = "") -> dict:
        response = self.client.get(
            "/collections/" + query,
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["component"], "Collections")
        return data["props"]

    def test_renders_mock_catalog_without_db_rows(self) -> None:
        props = self._get_catalog()

        self.assertEqual(
            [item["name"] for item in props["collections"]],
            [item["name"] for item in MOCK_COLLECTIONS],
        )
        self.assertTrue(props["featured"])
        self.assertEqual(len(props["featured"]), 3)
        self.assertTrue(props["sections"])
        self.assertIn("country_options", props["filters"])

    def test_catalog_ignores_db_groups(self) -> None:
        Group.objects.create(
            name="Не показывать",
            owner=User.objects.create_user(
                username="catalog-owner",
                email="catalog-owner@example.com",
                role="user",
            ),
        )

        props = self._get_catalog()

        self.assertNotIn(
            "Не показывать",
            [item["name"] for item in props["collections"]],
        )
        self.assertEqual(
            props["collections"][0]["name"], MOCK_COLLECTIONS[0]["name"]
        )

    def test_catalog_applies_query_filter(self) -> None:
        props = self._get_catalog("?q=крипта")

        self.assertEqual(len(props["collections"]), 1)
        self.assertEqual(props["collections"][0]["name"], "Крипта без шума")
        self.assertEqual(props["filters"]["q"], "крипта")

    def test_catalog_applies_country_and_category_filters(self) -> None:
        by_country = self._get_catalog("?country=Казахстан")
        self.assertEqual(
            [item["name"] for item in by_country["collections"]],
            ["Крипта без шума"],
        )

        by_category = self._get_catalog("?category=Дизайн")
        self.assertEqual(
            [item["name"] for item in by_category["collections"]],
            ["Дизайн и продукт"],
        )


class CollectionsCatalogServiceTest(TestCase):
    def test_service_builds_catalog_from_db_groups(self) -> None:
        Group.objects.create(
            name="Игры",
            owner=User.objects.create_user(
                username="service-owner",
                email="service-owner@example.com",
                role="user",
            ),
        )

        dto = CollectionsCatalogService().build()

        self.assertEqual(dto.collections[0].name, "Игры")
