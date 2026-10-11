import json
from decimal import Decimal
from typing import Any, Literal, cast

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from apps.group_channels.models import Group
from apps.parser.models import AIInsight, ChannelModerator, TelegramChannel
from apps.users.models import DataSubjectRequestLog, PartnerProfile, User


class PersonalDataExportTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
            first_name="Ivan",
            last_name="Owner",
            bio="Owner bio",
            avatar_image="https://example.com/owner.png",
            role="user",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass123!",
            first_name="Other",
            last_name="Person",
            role="user",
        )
        self.channel = TelegramChannel.objects.create(
            channel_id=1001,
            username="public_channel",
            title="Public channel",
        )
        self.other_channel = TelegramChannel.objects.create(
            channel_id=1002,
            username="other_channel",
            title="Other channel",
        )
        self.group = Group.objects.create(
            name="Owner group",
            description="Owner description",
            owner=self.user,
        )
        self.group.channels.add(self.channel)
        Group.objects.create(name="Other group", owner=self.other_user)
        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=True,
            can_manage_moderators=True,
        )
        ChannelModerator.objects.create(
            user=self.other_user,
            channel=self.channel,
        )
        AIInsight.objects.create(
            user=self.user,
            channel=self.channel,
            insight_text="Owner insight",
            insight_type="recommendation",
        )
        AIInsight.objects.create(
            user=self.other_user,
            channel=self.other_channel,
            insight_text="Other subject secret insight",
            insight_type="warning",
        )
        self.url = reverse("users:personal_data_export")

    def _download(
        self,
        method: Literal["get", "post"] = "get",
    ) -> tuple[HttpResponse, dict[str, Any]]:
        self.client.force_login(self.user)
        request = self.client.get if method == "get" else self.client.post
        response = cast(HttpResponse, request(self.url))
        return response, json.loads(response.content)

    def test_owner_downloads_only_own_personal_data(self) -> None:
        response, payload = self._download()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"], "application/json; charset=utf-8"
        )
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(payload["format_version"], "1.0")

        data = payload["personal_data"]
        self.assertIn("consents", data)
        self.assertEqual(
            set(data["profile"]),
            {
                "email",
                "first_name",
                "last_name",
                "bio",
                "avatar_image",
                "role",
                "date_joined",
                "last_login",
            },
        )
        self.assertNotIn("partner_profile", data)
        self.assertEqual(
            [group["name"] for group in data["owned_groups"]],
            ["Owner group"],
        )
        self.assertEqual(len(data["channel_moderator_assignments"]), 1)
        self.assertEqual(
            data["ai_insights"][0]["insight_text"], "Owner insight"
        )

        serialized = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn(self.other_user.email, serialized)
        self.assertNotIn("Other group", serialized)
        self.assertNotIn("Other subject secret insight", serialized)
        processing = payload["processing_information"]
        self.assertTrue(processing["purposes"])
        self.assertTrue(processing["legal_basis"])
        self.assertTrue(processing["retention_terms"])
        self.assertIn("personal_data_fields", processing)

    def test_partner_receives_own_payment_details_and_balance(self) -> None:
        PartnerProfile.objects.create(
            user=self.user,
            status="active",
            balance=Decimal("1250.40"),
            payment_details="Счёт 40702810000000000001",
            partner_code="partner-owner",
        )

        _, payload = self._download(method="post")

        partner = payload["personal_data"]["partner_profile"]
        self.assertEqual(partner["balance"], "1250.40")
        self.assertEqual(
            partner["payment_details"], "Счёт 40702810000000000001"
        )

    def test_export_is_available_only_to_authenticated_subject(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(DataSubjectRequestLog.objects.count(), 0)

    def test_successful_export_is_written_to_subject_request_log(self) -> None:
        self._download(method="post")

        log = DataSubjectRequestLog.objects.get()
        self.assertEqual(log.subject, self.user)
        self.assertEqual(log.subject_id_snapshot, self.user.pk)
        self.assertEqual(log.request_type, "export")
        self.assertEqual(log.http_method, "POST")
        self.assertEqual(log.status, "completed")
