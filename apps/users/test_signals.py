from typing import Any, cast
from unittest.mock import patch

from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse

from apps.parser.models import ChannelModerator, TelegramChannel
from apps.users.constants import UserRole
from apps.users.middleware import RoleRequest
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
        for code, name in (
            (UserRole.USER, "Пользователь"),
            (UserRole.PARTNER, "Партнёр"),
        ):
            Role.objects.get_or_create(code=code, defaults={"name": name})

        self.user = User.objects.create_user(
            username="partner_user",
            email="partner@example.com",
            password="StrongPass12345!",
            role=UserRole.USER,
        )
        self.profile = PartnerProfile.objects.create(user=self.user)

    def set_status(self, status: str) -> None:
        self.profile.status = status
        self.profile.save()
        self.user.refresh_from_db()

    def test_role_follows_partner_status_cycle(self) -> None:
        self.assertEqual(self.user.role, UserRole.USER)

        self.set_status("active")
        self.assertEqual(self.user.role, UserRole.PARTNER)

        self.set_status("suspended")
        self.assertEqual(self.user.role, UserRole.USER)

    def test_every_non_active_status_removes_partner_role(self) -> None:
        for status in ("pending", "rejected", "suspended"):
            with self.subTest(status=status):
                self.set_status("active")
                self.assertEqual(self.user.role, UserRole.PARTNER)

                self.set_status(status)
                self.assertEqual(self.user.role, UserRole.USER)

    def test_transitions_are_written_to_role_history(self) -> None:
        self.set_status("active")
        current = UserRoleHistory.objects.get(
            user=self.user, end_date__isnull=True
        )
        self.assertEqual(current.role.code, UserRole.PARTNER)

        self.set_status("suspended")
        partner_entry = UserRoleHistory.objects.get(
            user=self.user, role__code=UserRole.PARTNER
        )
        self.assertIsNotNone(partner_entry.end_date)

        current = UserRoleHistory.objects.get(
            user=self.user, end_date__isnull=True
        )
        self.assertEqual(current.role.code, UserRole.USER)
        self.assertIn("Приостановлен", current.reason or "")
        self.assertEqual(
            UserRoleHistory.objects.current_role(self.user), current.role
        )

    def test_other_roles_are_not_overwritten(self) -> None:
        self.user.role = UserRole.ADMIN
        self.user.save(update_fields=["role"])

        self.set_status("suspended")

        self.assertEqual(self.user.role, UserRole.ADMIN)

    def test_admin_keeps_admin_role_on_activation(self) -> None:
        self.user.role = UserRole.ADMIN
        self.user.save(update_fields=["role"])

        self.set_status("active")

        self.assertEqual(self.user.role, UserRole.ADMIN)

    @patch("apps.users.views.inertia_render", side_effect=inertia_json_response)
    def test_request_role_follows_partner_status(self, _render: Any) -> None:
        self.client.force_login(self.user)
        url = reverse("users:user_cabinet")

        self.set_status("active")
        response = self.client.get(url)
        request = cast(RoleRequest, response.wsgi_request)
        self.assertEqual(request.role, UserRole.PARTNER)

        self.set_status("suspended")
        response = self.client.get(url)
        request = cast(RoleRequest, response.wsgi_request)
        self.assertEqual(request.role, UserRole.USER)


class AssignRoleModeratorChannelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="channel_owner",
            email="owner@example.com",
            password="secret123",
            role=UserRole.USER,
        )
        self.channel = TelegramChannel.objects.create(
            channel_id=987654321,
            title="Тестовый канал",
        )

    def test_owner_receives_channel_moderator_role(self) -> None:
        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=True,
        )

        self.user.refresh_from_db()

        self.assertEqual(self.user.role, UserRole.CHANNEL_MODERATOR)
        self.assertTrue(
            UserRoleHistory.objects.filter(
                user=self.user,
                role__code=UserRole.CHANNEL_MODERATOR,
                end_date__isnull=True,
            ).exists()
        )

    def test_regular_moderator_does_not_receive_owner_role(self) -> None:
        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=False,
        )

        self.user.refresh_from_db()

        self.assertEqual(self.user.role, UserRole.USER)
        self.assertFalse(
            UserRoleHistory.objects.filter(
                user=self.user,
                role__code=UserRole.CHANNEL_MODERATOR,
            ).exists()
        )

    def test_partner_keeps_partner_role(self) -> None:
        self.user.role = UserRole.PARTNER
        self.user.save(update_fields=["role"])

        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=True,
        )

        self.user.refresh_from_db()

        self.assertEqual(self.user.role, UserRole.PARTNER)

    def test_existing_moderator_receives_owner_role_after_update(self) -> None:
        moderator = ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=False,
        )

        moderator.is_owner = True
        moderator.save(update_fields=["is_owner"])

        self.user.refresh_from_db()

        self.assertEqual(self.user.role, UserRole.CHANNEL_MODERATOR)
        self.assertTrue(
            UserRoleHistory.objects.filter(
                user=self.user,
                role__code=UserRole.CHANNEL_MODERATOR,
                end_date__isnull=True,
            ).exists()
        )

    def test_admin_keeps_admin_role(self) -> None:
        self.user.role = UserRole.ADMIN
        self.user.save(update_fields=["role"])

        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=True,
        )

        self.user.refresh_from_db()

        self.assertEqual(self.user.role, UserRole.ADMIN)
        self.assertFalse(
            UserRoleHistory.objects.filter(
                user=self.user,
                role__code=UserRole.CHANNEL_MODERATOR,
            ).exists()
        )

    def test_previous_active_role_history_is_closed(self) -> None:
        previous_role, _ = Role.objects.get_or_create(
            code=UserRole.USER,
            defaults={"name": "Пользователь"},
        )
        UserRoleHistory.objects.create(
            user=self.user,
            role=previous_role,
            reason="Начальная роль",
        )

        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=True,
        )

        self.user.refresh_from_db()

        self.assertEqual(self.user.role, UserRole.CHANNEL_MODERATOR)
        self.assertFalse(
            UserRoleHistory.objects.filter(
                user=self.user,
                role=previous_role,
                end_date__isnull=True,
            ).exists()
        )

    def test_repeated_owner_save_does_not_duplicate_history(self) -> None:
        """Повторное сохранение владельца не плодит записи истории."""
        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, UserRole.CHANNEL_MODERATOR)

        moderator = ChannelModerator.objects.get(
            user=self.user,
            channel=self.channel,
        )
        moderator.save(update_fields=["is_owner"])

        active = UserRoleHistory.objects.filter(
            user=self.user,
            role__code=UserRole.CHANNEL_MODERATOR,
            end_date__isnull=True,
        )
        self.assertEqual(active.count(), 1)
