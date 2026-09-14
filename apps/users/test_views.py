from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user
from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse

from apps.users.models import NotificationSettings, User
from apps.users.views import DEFAULT_AVATAR_URL


def inertia_json_response(request, component, props=None, **kwargs):
    return JsonResponse(
        {"component": component, "props": props or {}},
        **kwargs,
    )


class UserRegisterTest(TestCase):
    def valid_payload(self, **overrides: Any) -> dict[str, str]:
        payload = {
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "password1": "StrongPass12345!",
            "password2": "StrongPass12345!",
            "bio": "",
            "avatar_image": "",
        }
        payload.update(overrides)
        return payload

    def test_successful_registration_logs_in_and_redirects_to_dashboard(
        self,
    ) -> None:
        response = self.client.post(
            reverse("users:user_create"),
            data=self.valid_payload(),
        )

        self.assertRedirects(
            response,
            reverse("homepage:dashboard"),
            fetch_redirect_response=False,
        )

        user = User.objects.get(email="ada@example.com")
        self.assertEqual(user.role, "user")
        self.assertEqual(user.avatar_image, DEFAULT_AVATAR_URL)
        self.assertTrue(user.username.startswith("ada_"))
        self.assertEqual(get_user(self.client).pk, user.pk)

    @patch("apps.users.views.inertia_render", side_effect=inertia_json_response)
    def test_registration_errors_are_returned_as_field_errors(
        self, _render: Any
    ) -> None:
        User.objects.create_user(
            username="existing",
            email="taken@example.com",
            password="StrongPass12345!",
            role="user",
        )

        response = self.client.post(
            reverse("users:user_create"),
            data=self.valid_payload(
                email="taken@example.com",
                password1="short",
                password2="short",
            ),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["component"], "FormRegistration")
        self.assertEqual(
            payload["props"]["form"]["data"]["email"],
            "taken@example.com",
        )
        self.assertEqual(payload["props"]["form"]["data"]["password1"], "")
        self.assertEqual(payload["props"]["form"]["data"]["password2"], "")
        self.assertIn("email", payload["props"]["form"]["errors"])
        self.assertIn("password2", payload["props"]["form"]["errors"])
        self.assertEqual(
            User.objects.filter(email="taken@example.com").count(),
            1,
        )


class UserCabinetViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            password="StrongPass12345!",
            role="user",
            bio="Old bio",
            avatar_image="https://example.com/old-avatar.jpg",
        )
        self.client.force_login(self.user)

    @patch("apps.users.views.inertia_render", side_effect=inertia_json_response)
    def test_get_returns_full_user_profile(self, _render: Any) -> None:
        response = self.client.get(reverse("users:user_cabinet"))

        self.assertEqual(response.status_code, 200)

        data = response.json()
        user = data["props"]["user"]

        self.assertEqual(data["component"], "UserProfilePage")
        self.assertEqual(user["id"], self.user.id)
        self.assertEqual(user["first_name"], "Ivan")
        self.assertEqual(user["last_name"], "Ivanov")
        self.assertEqual(user["username"], "testuser")
        self.assertEqual(user["email"], "ivan@example.com")
        self.assertEqual(
            user["avatar"],
            "https://example.com/old-avatar.jpg",
        )
        self.assertEqual(user["role"], "user")
        self.assertEqual(user["bio"], "Old bio")
        self.assertIsNone(data["props"]["subscription"])
        self.assertEqual(
            data["props"]["notifications"],
            {
                "weekly_reports": True,
                "trend_notifications": True,
                "limit_exceeded": False,
                "new_features": True,
            },
        )

    def test_post_updates_user_profile(self) -> None:
        response = self.client.post(
            reverse("users:user_cabinet"),
            data={
                "first_name": "Petr",
                "last_name": "Petrov",
                "email": "petr@example.com",
                "bio": "New bio",
                "avatar_image": "https://example.com/new-avatar.jpg",
            },
        )

        self.assertRedirects(
            response,
            reverse("users:user_cabinet"),
            fetch_redirect_response=False,
        )

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "Petr")
        self.assertEqual(self.user.last_name, "Petrov")
        self.assertEqual(self.user.email, "petr@example.com")
        self.assertEqual(self.user.bio, "New bio")
        self.assertEqual(
            self.user.avatar_image,
            "https://example.com/new-avatar.jpg",
        )

    @patch("apps.users.views.inertia_render", side_effect=inertia_json_response)
    def test_post_returns_errors_for_invalid_email(self, _render: Any) -> None:
        response = self.client.post(
            reverse("users:user_cabinet"),
            data={
                "first_name": "Petr",
                "last_name": "Petrov",
                "email": "invalid-email",
                "bio": "New bio",
                "avatar_image": "https://example.com/avatar.jpg",
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["component"], "UserProfilePage")
        self.assertIn("email", data["props"]["errors"])

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "ivan@example.com")

    @patch("apps.users.views.inertia_render", side_effect=inertia_json_response)
    def test_get_returns_saved_notification_settings(
        self,
        _render: Any,
    ) -> None:
        settings = NotificationSettings.objects.create(user=self.user)
        settings.weekly_reports = False
        settings.trend_notifications = True
        settings.new_features = False
        settings.save()

        response = self.client.get(reverse("users:user_cabinet"))

        notifications = response.json()["props"]["notifications"]
        self.assertEqual(
            notifications,
            {
                "weekly_reports": False,
                "trend_notifications": True,
                "limit_exceeded": False,
                "new_features": False,
            },
        )

    def test_post_notifications_saves_settings_and_sets_success_flash(
        self,
    ) -> None:
        settings = NotificationSettings.objects.create(user=self.user)

        response = self.client.post(
            reverse("users:user_cabinet"),
            data={
                "action": "notifications",
                "weekly_reports": "false",
                "trend_notifications": "true",
                "new_features": "false",
            },
        )

        self.assertRedirects(
            response,
            reverse("users:user_cabinet"),
            fetch_redirect_response=False,
        )

        settings.refresh_from_db()
        self.assertFalse(settings.weekly_reports)
        self.assertTrue(settings.trend_notifications)
        self.assertFalse(settings.new_features)

        self.assertEqual(
            self.client.session.get("flash"),
            {"success": "Настройки уведомлений сохранены"},
        )

    @patch(
        "apps.users.views.NotificationSettingsForm.save",
        side_effect=Exception("Database error"),
    )
    def test_post_notifications_sets_error_flash_when_save_fails(
        self,
        _save: Any,
    ) -> None:
        settings = NotificationSettings.objects.create(user=self.user)

        response = self.client.post(
            reverse("users:user_cabinet"),
            data={
                "action": "notifications",
                "weekly_reports": "false",
                "trend_notifications": "true",
                "new_features": "false",
            },
        )

        self.assertRedirects(
            response,
            reverse("users:user_cabinet"),
            fetch_redirect_response=False,
        )

        self.assertEqual(
            self.client.session.get("flash"),
            {"error": "Не удалось сохранить настройки уведомлений."},
        )

        settings.refresh_from_db()
        self.assertTrue(settings.weekly_reports)
        self.assertTrue(settings.trend_notifications)
        self.assertTrue(settings.new_features)
