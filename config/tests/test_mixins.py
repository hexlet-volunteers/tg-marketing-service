from typing import Any

from django.http import HttpRequest, HttpResponse
from django.test import TestCase, override_settings
from django.urls import path
from django.views import View

from apps.users.models import User
from config.mixins import AdminRequiredMixin


class AdminOnlyView(AdminRequiredMixin, View):
    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        return HttpResponse("ok")


urlpatterns = [
    path("admin-only/", AdminOnlyView.as_view(), name="test_admin_only"),
]


@override_settings(ROOT_URLCONF=__name__)
class AdminRequiredMixinTests(TestCase):
    url = "/admin-only/"

    def create_user(self, role: str) -> User:
        return User.objects.create_user(
            username=f"user-{role}",
            email=f"{role}@example.com",
            password="password",
            role=role,
        )

    def test_admin_is_allowed(self) -> None:
        self.client.force_login(self.create_user("admin"))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_guest_is_denied(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_non_admin_roles_are_denied(self) -> None:
        for role in ("user", "partner", "channel_moderator"):
            with self.subTest(role=role):
                self.client.logout()
                self.client.force_login(self.create_user(role))

                response = self.client.get(self.url)

                self.assertEqual(response.status_code, 403)

    def test_staff_without_admin_role_is_denied(self) -> None:
        user = User.objects.create_user(
            username="staff-only",
            email="staff-only@example.com",
            password="password",
            role="user",
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_superuser_without_admin_role_is_denied(self) -> None:
        user = User.objects.create_user(
            username="superuser-only",
            email="superuser-only@example.com",
            password="password",
            role="user",
            is_superuser=True,
        )
        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
