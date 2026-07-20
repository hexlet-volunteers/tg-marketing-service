from django.test import TestCase
from django.urls import reverse

from apps.homepage.models import HomePageComponent
from apps.users.models import User


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.component = HomePageComponent.objects.create(
            title="My Component Title",
            content={"content": "Some content here"},
            order=1,
            is_active=True,
        )

    def test_index_view_with_inertia_props(self):
        response = self.client.get(
            reverse("main_index"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)

        # Django test client автоматически декодирует JSON
        data = response.json()

        # Inertia-обёртка
        self.assertIn("component", data)
        self.assertIn("props", data)
        self.assertIn("url", data)
        self.assertIn("version", data)

        # Проверяем props
        props = data["props"]
        self.assertIn("components", props)

        components = props["components"]
        self.assertGreater(len(components), 0)

        first_component = components[0]["props"]
        self.assertEqual(first_component["title"], self.component.title)
        self.assertEqual(
            first_component["content"], self.component.content["content"]
        )
        self.assertEqual(first_component["order"], self.component.order)

    def test_guest_inertia_props_include_shared_auth_state(self):
        response = self.client.get(
            reverse("main_index"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)
        props = response.json()["props"]

        self.assertIsNone(props["auth"])
        self.assertEqual(props["role"], "guest")
        self.assertIn("csrfToken", props)
        self.assertIsNone(props["flash"])

    def test_authenticated_user_inertia_props_include_shared_auth_state(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="secret123",
            role="partner",
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse("main_index"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        props = response.json()["props"]

        self.assertEqual(props["auth"]["id"], user.id)
        self.assertEqual(props["auth"]["email"], user.email)
        self.assertEqual(props["auth"]["role"], "partner")
        self.assertEqual(props["role"], "partner")
        self.assertIn("csrfToken", props)
