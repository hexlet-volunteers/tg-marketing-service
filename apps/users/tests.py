from unittest.mock import patch

from django.contrib.auth import get_user
from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse

from apps.users.models import User
from apps.users.views import DEFAULT_AVATAR_URL


def inertia_json_response(request, component, props=None, **kwargs):
    return JsonResponse(
        {"component": component, "props": props or {}},
        **kwargs,
    )


class UserRegisterTest(TestCase):
    def valid_payload(self, **overrides):
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

    def test_successful_registration_logs_in_and_redirects_to_dashboard(self):
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
    def test_registration_errors_are_returned_as_field_errors(self, _render):
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
        self.assertIn("email", payload["props"]["form"]["errors"])
        self.assertIn("password2", payload["props"]["form"]["errors"])
        self.assertEqual(
            User.objects.filter(email="taken@example.com").count(),
            1,
        )
