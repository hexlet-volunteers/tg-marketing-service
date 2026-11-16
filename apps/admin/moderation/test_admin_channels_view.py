from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from apps.admin.moderation.models import ModerationRequest
from apps.parser.models import TelegramChannel
from apps.users.models import User


class AdminChannelsViewTests(TestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_user(
            username="channels-view-admin",
            email="channels-view-admin@example.com",
            password="password",
            role="admin",
        )
        self.url = reverse("admin_channels")

    def test_view_requires_admin(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_view_returns_approved_channels_and_categories(self) -> None:
        self.client.force_login(self.admin)

        approved_channel = TelegramChannel.objects.create(
            channel_id=2001,
            username="approved_for_admin",
            title="Approved for admin",
            participants_count=1250,
            category="Технологии",
            is_verified=True,
        )
        pending_channel = TelegramChannel.objects.create(
            channel_id=2002,
            username="pending_for_admin",
            title="Pending for admin",
        )

        ModerationRequest.objects.create(
            submitted_by=self.admin,
            channel_identifier="@approved_for_admin",
            channel_by=approved_channel,
            category="Технологии",
            country="Россия",
            language="Русский",
            status="approved",
        )
        ModerationRequest.objects.create(
            submitted_by=self.admin,
            channel_identifier="@pending_for_admin",
            channel_by=pending_channel,
            category="Технологии",
            country="Россия",
            language="Русский",
            status="pending",
        )

        response = self.client.get(
            self.url,
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["component"], "AdminChannels")
        self.assertEqual(
            payload["props"]["channels"],
            [
                {
                    "channelId": 2001,
                    "username": "approved_for_admin",
                    "title": "Approved for admin",
                    "category": "Технологии",
                    "isVerified": True,
                    "subscribers": 1250,
                }
            ],
        )
        self.assertIn("Технологии", payload["props"]["categories"])
        self.assertNotIn(
            "Выберите категорию...",
            payload["props"]["categories"],
        )
        self.assertNotIn("Все категории", payload["props"]["categories"])

    def test_update_category_saves_valid_category(self) -> None:
        self.client.force_login(self.admin)
        channel = TelegramChannel.objects.create(
            channel_id=2003,
            username="category_update_test",
            title="Category update test",
            category="Новости и СМИ",
        )
        ModerationRequest.objects.create(
            submitted_by=self.admin,
            channel_identifier="@category_update_test",
            channel_by=channel,
            category="Новости и СМИ",
            country="Россия",
            language="Русский",
            status="approved",
        )

        response = self.client.post(
            reverse("admin_moderation:channel_category"),
            {
                "channel_id": channel.channel_id,
                "category": "Технологии",
            },
        )

        self.assertEqual(response.status_code, 302)
        channel.refresh_from_db()
        self.assertEqual(channel.category, "Технологии")

    def test_update_category_rejects_invalid_category(self) -> None:
        self.client.force_login(self.admin)
        channel = TelegramChannel.objects.create(
            channel_id=2004,
            username="invalid_category_test",
            title="Invalid category test",
            category="Новости и СМИ",
        )

        response = self.client.post(
            reverse("admin_moderation:channel_category"),
            {
                "channel_id": channel.channel_id,
                "category": "Несуществующая категория",
            },
        )

        self.assertEqual(response.status_code, 400)
        channel.refresh_from_db()
        self.assertEqual(channel.category, "Новости и СМИ")

    def test_update_category_requires_admin(self) -> None:
        channel = TelegramChannel.objects.create(
            channel_id=2005,
            username="category_rbac_test",
            title="Category RBAC test",
        )
        response = self.client.post(
            reverse("admin_moderation:channel_category"),
            {
                "channel_id": channel.channel_id,
                "category": "Технологии",
            },
        )

        self.assertEqual(response.status_code, 403)
        channel.refresh_from_db()
        self.assertIsNone(channel.category)

    def test_toggle_verified_enables_verification(self) -> None:
        self.client.force_login(self.admin)
        channel = TelegramChannel.objects.create(
            channel_id=2006,
            username="verified_enable_test",
            title="Verified enable test",
            is_verified=False,
        )

        response = self.client.post(
            reverse("admin_moderation:channel_verified"),
            {"channel_id": channel.channel_id},
        )

        self.assertEqual(response.status_code, 302)
        channel.refresh_from_db()
        self.assertTrue(channel.is_verified)
        self.assertIsNotNone(channel.verified_at)

    def test_toggle_verified_disables_verification(self) -> None:
        self.client.force_login(self.admin)
        channel = TelegramChannel.objects.create(
            channel_id=2007,
            username="verified_disable_test",
            title="Verified disable test",
            is_verified=True,
        )

        response = self.client.post(
            reverse("admin_moderation:channel_verified"),
            {"channel_id": channel.channel_id},
        )

        self.assertEqual(response.status_code, 302)
        channel.refresh_from_db()
        self.assertFalse(channel.is_verified)
        self.assertIsNone(channel.verified_at)

    def test_toggle_verified_requires_admin(self) -> None:
        channel = TelegramChannel.objects.create(
            channel_id=2008,
            username="verified_rbac_test",
            title="Verified RBAC test",
            is_verified=False,
        )

        response = self.client.post(
            reverse("admin_moderation:channel_verified"),
            {"channel_id": channel.channel_id},
        )

        self.assertEqual(response.status_code, 403)
        channel.refresh_from_db()
        self.assertFalse(channel.is_verified)

    @patch(
        "apps.admin.moderation.services.admin_channels."
        "AdminChannelsService._fetch_channel"
    )
    def test_add_channel_creates_approved_channel(
        self,
        fetch_channel,
    ) -> None:
        self.client.force_login(self.admin)
        fetch_channel.return_value = {
            "channel_id": 3001,
            "username": "new_admin_channel",
            "title": "New admin channel",
        }

        response = self.client.post(
            reverse("admin_moderation:channel_add"),
            {
                "identifier": "@new_admin_channel",
                "category": "Технологии",
            },
        )

        self.assertEqual(response.status_code, 302)
        channel = TelegramChannel.objects.get(channel_id=3001)
        self.assertEqual(channel.username, "new_admin_channel")
        self.assertEqual(channel.category, "Технологии")

        moderation_request = ModerationRequest.objects.get(
            channel_by=channel,
        )
        self.assertEqual(moderation_request.status, "approved")
        self.assertEqual(moderation_request.submitted_by, self.admin)
        self.assertEqual(moderation_request.moderator, self.admin)

    @patch(
        "apps.admin.moderation.services.admin_channels."
        "AdminChannelsService._fetch_channel"
    )
    def test_add_channel_rejects_duplicate_username(
        self,
        fetch_channel,
    ) -> None:
        self.client.force_login(self.admin)
        TelegramChannel.objects.create(
            channel_id=3002,
            username="existing_admin_channel",
            title="Existing admin channel",
        )
        fetch_channel.return_value = {
            "channel_id": 3003,
            "username": "existing_admin_channel",
            "title": "Duplicate admin channel",
        }

        response = self.client.post(
            reverse("admin_moderation:channel_add"),
            {
                "identifier": "@existing_admin_channel",
                "category": "Технологии",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            TelegramChannel.objects.filter(
                username__iexact="existing_admin_channel",
            ).count(),
            1,
        )
        self.assertFalse(
            ModerationRequest.objects.filter(
                channel_identifier="@existing_admin_channel",
                status="approved",
            ).exists(),
        )

    @patch(
        "apps.admin.moderation.services.admin_channels."
        "AdminChannelsService._fetch_channel"
    )
    def test_add_channel_requires_admin(self, fetch_channel) -> None:
        response = self.client.post(
            reverse("admin_moderation:channel_add"),
            {
                "identifier": "@forbidden_channel",
                "category": "Технологии",
            },
        )

        self.assertEqual(response.status_code, 403)
        fetch_channel.assert_not_called()
        self.assertFalse(
            TelegramChannel.objects.filter(
                username="forbidden_channel",
            ).exists(),
        )
