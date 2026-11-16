from typing import Any
from unittest.mock import patch

from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse

from apps.users.models import PartnerProfile, User
from apps.users.roles import Role, UserRoleHistory


def inertia_json_response(request, component, props=None, **kwargs):
    return JsonResponse(
        {"component": component, "props": props or {}},
        **kwargs,
    )


class PartnerRoleSyncTest(TestCase):
    def setUp(self) -> None:
        # get_or_create: подойдёт, даже если роли уже созданы миграцией
        for code, name in (("user", "Пользователь"), ("partner", "Партнёр")):
            Role.objects.get_or_create(code=code, defaults={"name": name})

        self.user = User.objects.create_user(
            username="partner_user",
            email="partner@example.com",
            password="StrongPass12345!",
            role="user",
        )
        self.profile = PartnerProfile.objects.create(user=self.user)

    def set_status(self, status: str) -> None:
        self.profile.status = status
        self.profile.save()
        self.user.refresh_from_db()

    def test_role_follows_partner_status_cycle(self) -> None:
        self.assertEqual(self.user.role, "user")

        self.set_status("active")
        self.assertEqual(self.user.role, "partner")

        self.set_status("suspended")
        self.assertEqual(self.user.role, "user")

    def test_every_non_active_status_removes_partner_role(self) -> None:
        for status in ("pending", "rejected", "suspended"):
            with self.subTest(status=status):
                self.set_status("active")
                self.assertEqual(self.user.role, "partner")

                self.set_status(status)
                self.assertEqual(self.user.role, "user")

        def test_transitions_are_written_to_role_history(self) -> None:
            self.set_status("active")
            current = UserRoleHistory.objects.get(
                user=self.user, end_date__isnull=True
            )
            self.assertEqual(current.role.code, "partner")

            self.set_status("suspended")
            partner_entry = UserRoleHistory.objects.get(
                user=self.user, role__code="partner"
            )
            self.assertIsNotNone(partner_entry.end_date)

            current = UserRoleHistory.objects.get(
                user=self.user, end_date__isnull=True
            )
            self.assertEqual(current.role.code, "user")
            self.assertIn("Приостановлен", current.reason)
            self.assertEqual(
                UserRoleHistory.objects.current_role(self.user).code, "user"
            )

    def test_other_roles_are_not_overwritten(self) -> None:
        self.user.role = "admin"
        self.user.save(update_fields=["role"])

        self.set_status("suspended")

        self.assertEqual(self.user.role, "admin")

    @patch("apps.users.views.inertia_render", side_effect=inertia_json_response)
    def test_request_role_follows_partner_status(self, _render: Any) -> None:
        self.client.force_login(self.user)
        url = reverse("users:user_cabinet")

        self.set_status("active")
        response = self.client.get(url)
        self.assertEqual(response.wsgi_request.role, "partner")

        self.set_status("suspended")
        response = self.client.get(url)
        self.assertEqual(response.wsgi_request.role, "user")

    def test_debug(self) -> None:
        self.profile.status = "active"
        self.profile.save()
