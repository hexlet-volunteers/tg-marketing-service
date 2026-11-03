from django.test import TestCase

from apps.parser.models import ChannelModerator, TelegramChannel
from apps.users.constants import UserRole
from apps.users.models import User
from apps.users.roles import Role, UserRoleHistory


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
