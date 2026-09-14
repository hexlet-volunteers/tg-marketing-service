from datetime import timedelta

from django.db.models import QuerySet
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.admin.moderation.models import ModerationRequest
from apps.admin.moderation.services.moderation import (
    ModerationError,
    ModerationService,
)
from apps.admin.moderation.services.queue import ModerationQueue
from apps.parser.models import TelegramChannel
from apps.users.models import User


class ModerationRequestTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="moderator-requester",
            email="requester@example.com",
            password="password",
            role="user",
        )
        self.channel = TelegramChannel.objects.create(
            channel_id=1001,
            username="tech_channel",
            title="Tech channel",
        )

    def create_request(self, **overrides: object) -> ModerationRequest:
        data: dict[str, object] = {
            "submitted_by": self.user,
            "channel_identifier": "@tech_channel",
            "category": "technology",
            "country": "RU",
            "language": "ru",
        }
        data.update(overrides)
        return ModerationRequest.objects.create(**data)

    def test_pending_status_is_used_by_default(self) -> None:
        moderation_request = self.create_request()

        self.assertEqual(moderation_request.status, "pending")
        self.assertIsNone(moderation_request.channel_by)
        self.assertIsNone(moderation_request.moderator)
        self.assertIsNone(moderation_request.reject_reason)
        self.assertIsNone(moderation_request.resolved_at)

    def test_pending_queue_is_ordered_by_created_at_then_id(self) -> None:
        older_request = self.create_request(channel_by=self.channel)
        newer_request = self.create_request(channel_identifier="@new_channel")
        tied_request = self.create_request(channel_identifier="@tied_channel")
        self.create_request(status="approved")
        self.create_request(status="rejected")
        self.create_request(status="duplicate")

        now = timezone.now()
        ModerationRequest.objects.filter(pk=older_request.pk).update(
            created_at=now + timedelta(minutes=1)
        )
        ModerationRequest.objects.filter(pk=newer_request.pk).update(
            created_at=now
        )
        ModerationRequest.objects.filter(pk=tied_request.pk).update(
            created_at=now
        )

        queue = list(ModerationRequest.objects.pending_queue())

        self.assertEqual(
            [request.id for request in queue],
            [newer_request.id, tied_request.id, older_request.id],
        )

    def test_empty_queue_returns_empty_list(self) -> None:
        queue = ModerationQueue().get_queue()

        self.assertIsInstance(queue, QuerySet)
        self.assertEqual(list(queue), [])

    def test_queue_serializes_requests_with_and_without_channel(self) -> None:
        request_with_channel = self.create_request(channel_by=self.channel)
        resolved_at = timezone.now()
        request_without_channel = self.create_request(
            channel_identifier="https://t.me/new_channel",
            category="business",
            country="US",
            language="en",
            reject_reason="Needs review",
            resolved_at=resolved_at,
        )
        self.create_request(status="approved")
        self.create_request(status="rejected")
        self.create_request(status="duplicate")

        moderation_queue = ModerationQueue()
        self.assertIsInstance(moderation_queue.get_queue(), QuerySet)
        queue = [
            moderation_queue.get_queue_data(moderation_request)
            for moderation_request in moderation_queue.get_queue()
        ]

        self.assertEqual(
            [item["id"] for item in queue],
            [request_with_channel.id, request_without_channel.id],
        )
        self.assertEqual(
            queue[0]["submitted_by"],
            {"id": self.user.id, "username": self.user.username},
        )
        self.assertEqual(
            queue[0]["channel"],
            {
                "id": self.channel.id,
                "username": self.channel.username,
                "title": self.channel.title,
            },
        )
        self.assertIsNone(queue[1]["channel"])
        self.assertEqual(
            queue[1]["channel_identifier"], "https://t.me/new_channel"
        )
        self.assertEqual(
            {
                "category": queue[0]["category"],
                "country": queue[0]["country"],
                "language": queue[0]["language"],
                "status": queue[0]["status"],
            },
            {
                "category": "technology",
                "country": "RU",
                "language": "ru",
                "status": "pending",
            },
        )
        self.assertIsNone(queue[0]["reject_reason"])
        self.assertEqual(
            queue[0]["created_at"], request_with_channel.created_at.isoformat()
        )
        self.assertIsNone(queue[0]["resolved_at"])
        self.assertEqual(
            {
                "category": queue[1]["category"],
                "country": queue[1]["country"],
                "language": queue[1]["language"],
                "status": queue[1]["status"],
            },
            {
                "category": "business",
                "country": "US",
                "language": "en",
                "status": "pending",
            },
        )
        self.assertEqual(queue[1]["reject_reason"], "Needs review")
        self.assertEqual(
            queue[1]["created_at"],
            request_without_channel.created_at.isoformat(),
        )
        self.assertEqual(queue[1]["resolved_at"], resolved_at.isoformat())

    def test_approve_publishes_channel_and_records_moderator(self) -> None:
        moderator = User.objects.create_user(
            username="moderator",
            email="moderator@example.com",
            password="password",
            role="admin",
        )
        moderation_request = self.create_request(channel_by=self.channel)

        result = ModerationService.approve(
            moderation_request.id,
            moderator,
            category="business",
            is_verified=True,
        )

        result.refresh_from_db()
        self.channel.refresh_from_db()
        self.assertEqual(result.status, "approved")
        self.assertEqual(result.category, "business")
        self.assertEqual(result.moderator, moderator)
        self.assertIsNotNone(result.resolved_at)
        self.assertTrue(self.channel.is_verified)
        self.assertEqual(self.channel.category, "business")

    def test_approve_marks_request_as_duplicate_by_username(self) -> None:
        duplicate_channel = TelegramChannel.objects.create(
            channel_id=1002,
            username="tech_channel",
            title="Another tech channel",
        )
        moderation_request = self.create_request(channel_by=duplicate_channel)
        moderator = User.objects.create_user(
            username="admin-moderator",
            email="admin-moderator@example.com",
            password="password",
            role="admin",
        )

        result = ModerationService.approve(
            moderation_request.id,
            moderator,
            category="technology",
            is_verified=False,
        )

        result.refresh_from_db()
        self.assertEqual(result.status, "duplicate")
        self.assertEqual(result.moderator, moderator)
        self.assertIsNotNone(result.resolved_at)
        duplicate_channel.refresh_from_db()
        self.assertFalse(duplicate_channel.is_verified)

    def test_reject_records_reason_moderator_and_time(self) -> None:
        moderation_request = self.create_request(channel_by=self.channel)
        moderator = User.objects.create_user(
            username="reject-moderator",
            email="reject-moderator@example.com",
            password="password",
            role="admin",
        )

        result = ModerationService.reject(
            moderation_request.id,
            moderator,
            reason="Неверная тематика",
        )

        result.refresh_from_db()
        self.assertEqual(result.status, "rejected")
        self.assertEqual(result.reject_reason, "Неверная тематика")
        self.assertEqual(result.moderator, moderator)
        self.assertIsNotNone(result.resolved_at)

    def test_service_rejects_empty_values_and_reprocessed_request(self) -> None:
        moderation_request = self.create_request(channel_by=self.channel)
        moderator = User.objects.create_user(
            username="validation-moderator",
            email="validation-moderator@example.com",
            password="password",
            role="admin",
        )

        with self.assertRaises(ModerationError):
            ModerationService.approve(
                moderation_request.id,
                moderator,
                category=" ",
                is_verified=False,
            )
        with self.assertRaises(ModerationError):
            ModerationService.reject(
                moderation_request.id,
                moderator,
                reason=" ",
            )

        ModerationService.reject(
            moderation_request.id,
            moderator,
            reason="Причина",
        )
        with self.assertRaises(ModerationError):
            ModerationService.reject(
                moderation_request.id,
                moderator,
                reason="Повторно",
            )

    def create_admin(self) -> User:
        return User.objects.create_user(
            username="view-admin",
            email="view-admin@example.com",
            password="password",
            role="admin",
        )

    def test_moderation_view_requires_admin(self) -> None:
        response = self.client.get(reverse("admin_moderation:list"))

        self.assertEqual(response.status_code, 403)

    def test_moderation_view_paginates_pending_requests(self) -> None:
        admin = self.create_admin()
        self.client.force_login(admin)
        for index in range(11):
            self.create_request(channel_identifier=f"@channel_{index}")

        response = self.client.get(
            reverse("admin_moderation:list") + "?page=2",
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)
        props = response.json()["props"]
        self.assertEqual(props["pendingCount"], 11)
        self.assertEqual(len(props["pendingRequests"]), 1)
        self.assertEqual(props["pagination"]["page"], 2)
        self.assertTrue(props["pagination"]["hasPrevious"])
        self.assertFalse(props["pagination"]["hasNext"])

    def test_moderation_view_normalizes_invalid_page(self) -> None:
        admin = self.create_admin()
        self.client.force_login(admin)

        response = self.client.get(
            reverse("admin_moderation:list") + "?page=invalid",
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["props"]["pagination"]["page"], 1)

    def test_moderation_view_approve_sets_is_verified_and_redirects(
        self,
    ) -> None:
        admin = self.create_admin()
        self.client.force_login(admin)
        moderation_request = self.create_request(channel_by=self.channel)

        response = self.client.post(
            reverse("admin_moderation:list"),
            data={
                "action": "approve",
                "request_id": moderation_request.id,
                "category": "business",
                "is_verified": "true",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.channel.refresh_from_db()
        self.assertTrue(self.channel.is_verified)

    def test_moderation_view_returns_no_content_with_service_error(
        self,
    ) -> None:
        admin = self.create_admin()
        self.client.force_login(admin)
        moderation_request = self.create_request(channel_by=self.channel)

        response = self.client.post(
            reverse("admin_moderation:list"),
            data={
                "action": "approve",
                "request_id": moderation_request.id,
                "category": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("X-Inertia-Location", response)
        moderation_request.refresh_from_db()
        self.assertEqual(moderation_request.status, "pending")
