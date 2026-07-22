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

    def _get_inertia_props(self, url_name="main_index"):
        response = self.client.get(
            reverse(url_name),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["props"]

    def test_guest_inertia_props_include_shared_auth_state(self):
        props = self._get_inertia_props()

        self.assertIsNone(props["auth"])
        self.assertEqual(props["role"], "guest")
        self.assertFalse(props["is_admin"])
        self.assertIn("csrfToken", props)
        self.assertTrue(props["csrfToken"])
        self.assertIsNone(props["flash"])

    def test_authenticated_user_inertia_props_include_shared_auth_state(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="secret123",
            role="partner",
        )
        self.client.force_login(user)

        props = self._get_inertia_props("homepage:dashboard")

        self.assertEqual(props["auth"]["id"], user.id)
        self.assertEqual(props["auth"]["email"], user.email)
        self.assertEqual(props["auth"]["role"], "partner")
        self.assertEqual(props["role"], "partner")
        self.assertFalse(props["is_admin"])
        self.assertIn("csrfToken", props)

    def test_admin_user_shared_props(self):
        user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="secret123",
            role="admin",
            is_staff=True,
        )
        self.client.force_login(user)

        props = self._get_inertia_props("homepage:dashboard")

        self.assertEqual(props["role"], "admin")
        self.assertEqual(props["auth"]["role"], "admin")
        self.assertTrue(props["is_admin"])

    def test_channel_moderator_user_shared_props(self):
        user = User.objects.create_user(
            username="moderator",
            email="moderator@example.com",
            password="secret123",
            role="channel_moderator",
        )
        self.client.force_login(user)

        props = self._get_inertia_props("homepage:dashboard")

        self.assertEqual(props["role"], "channel_moderator")
        self.assertEqual(props["auth"]["role"], "channel_moderator")
        self.assertFalse(props["is_admin"])

    def test_flash_message_persists_after_redirect(self):
        session = self.client.session
        session["flash"] = {"success": "Пользователь успешно зарегистрирован"}
        session.save()

        response = self.client.get(
            reverse("main_index"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        props = response.json()["props"]

        self.assertEqual(
            props["flash"], {"success": "Пользователь успешно зарегистрирован"}
        )

        # Flash должен быть извлечён из сессии однократно
        self.assertIsNone(self.client.session.get("flash"))

    def test_flash_survives_chain_of_redirects(self):
        """Flash не теряется на промежуточном редиректе."""
        user = User.objects.create_user(
            username="redirectuser",
            email="redirect@example.com",
            password="secret123",
            role="user",
        )
        self.client.force_login(user)
        session = self.client.session
        session["flash"] = {"success": "Сообщение через redirect"}
        session.save()

        # /home перенаправляет авторизованных на /dashboard
        response = self.client.get(
            reverse("main_index"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        final_url = response.redirect_chain[-1][0]
        self.assertIn("dashboard", final_url)

        props = response.json()["props"]
        self.assertEqual(
            props["flash"], {"success": "Сообщение через redirect"}
        )

    def test_unknown_role_fallback_to_user(self):
        user = User.objects.create_user(
            username="unknownrole",
            email="unknown@example.com",
            password="secret123",
            role="something_weird",
        )
        self.client.force_login(user)

        props = self._get_inertia_props("homepage:dashboard")

        self.assertEqual(props["role"], "user")
        self.assertEqual(props["auth"]["role"], "user")
        self.assertFalse(props["is_admin"])

    def test_is_admin_true_for_superuser(self):
        user = User.objects.create_user(
            username="superuser",
            email="super@example.com",
            password="secret123",
            role="user",
            is_superuser=True,
        )
        self.client.force_login(user)

        props = self._get_inertia_props("homepage:dashboard")

        self.assertEqual(props["role"], "user")
        self.assertTrue(props["is_admin"])

    def test_invalid_flash_values_normalized_to_none(self):
        for invalid_flash in ["", "plain string", {}, []]:
            with self.subTest(flash=invalid_flash):
                session = self.client.session
                session["flash"] = invalid_flash
                session.save()

                props = self._get_inertia_props()
                self.assertIsNone(props["flash"])
                self.assertIsNone(self.client.session.get("flash"))

    def test_registration_flash_survives_redirect_chain(self):
        """Регистрация устанавливает flash и редиректит на главную."""
        response = self.client.post(
            reverse("users:user_create"),
            data={
                "first_name": "Test",
                "last_name": "User",
                "username": "testregister",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
                "email": "testregister@example.com",
                "bio": "",
                "avatar_image": "",
                "terms": "on",
            },
            follow=True,
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)

        props = response.json()["props"]
        self.assertEqual(
            props["flash"], {"success": "Пользователь успешно зарегистрирован"}
        )
        self.assertTrue(User.objects.filter(username="testregister").exists())
