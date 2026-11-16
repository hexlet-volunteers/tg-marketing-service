from datetime import UTC, datetime, timedelta
from decimal import Decimal
from importlib import import_module
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.apps import apps
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.group_channels.models import Group, SavedCollection
from apps.parser.models import AIInsight, ChannelModerator, TelegramChannel
from apps.users.account_deletion import request_account_deletion
from apps.users.consents import serialize_user_consent_history
from apps.users.data_subject_requests import (
    add_working_days,
    complete_subject_request,
    create_subject_request,
    extend_subject_request,
    fail_subject_request,
)
from apps.users.models import (
    Consent,
    ConsentWithdrawal,
    DataSubjectRequestLog,
    PartnerProfile,
    User,
)


class SubjectRequestTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="subject",
            email="subject@example.com",
            password="StrongPass123!",
            first_name="Subject",
            last_name="Owner",
            bio="Private bio",
            role="user",
            avatar_image="https://example.com/avatar.png",
        )
        self.other = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass123!",
            role="user",
        )
        self.consent = Consent.objects.create(
            user=self.user,
            document_type=Consent.DocumentType.PERSONAL_DATA,
            version="2026-07-01",
            source=Consent.Source.EMAIL_REGISTRATION,
            ip="203.0.113.10",
            user_agent="Test/1.0",
        )
        self.url = reverse("users:consent_withdrawal")
        self.client.force_login(self.user)

    def test_withdrawal_cleans_own_data_and_preserves_evidence(
        self,
    ) -> None:
        channel = TelegramChannel.objects.create(
            channel_id=555, username="public"
        )
        Group.objects.create(name="Subject private group", owner=self.user)
        other_group = Group.objects.create(
            name="Other group", owner=self.other, curator=self.user
        )
        SavedCollection.objects.create(user=self.user, group=other_group)
        AIInsight.objects.create(
            user=self.user, channel=channel, insight_text="Private insight"
        )
        ChannelModerator.objects.create(user=self.user, channel=channel)
        SocialAccount.objects.create(
            user=self.user,
            provider="yandex",
            uid="123",
            extra_data={"email": self.user.email},
        )
        EmailAddress.objects.create(user=self.user, email=self.user.email)
        extra_client = Client()
        extra_client.force_login(self.user)
        session_key = extra_client.session.session_key
        before = Consent.objects.filter(pk=self.consent.pk).values().get()

        response = self.client.post(self.url, {"user_id": self.other.pk})

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertFalse(self.user.has_usable_password())
        self.assertEqual(self.user.first_name, "")
        self.assertEqual(self.user.last_name, "")
        self.assertEqual(self.user.bio, "")
        self.assertIsNone(self.user.avatar_image)
        self.assertNotEqual(self.user.email, "subject@example.com")
        self.assertIsNotNone(self.user.anonymized_at)
        self.assertTrue(self.user.retention_basis)
        self.assertFalse(self.user.owned_groups.exists())
        self.assertFalse(self.user.saved_collections.exists())
        self.assertFalse(self.user.ai_insights.exists())
        self.assertFalse(self.user.moderated_channels.exists())
        self.assertFalse(SocialAccount.objects.filter(user=self.user).exists())
        self.assertFalse(EmailAddress.objects.filter(user=self.user).exists())
        self.assertFalse(
            Session.objects.filter(session_key=session_key).exists()
        )
        other_group.refresh_from_db()
        self.assertIsNone(other_group.curator)
        self.other.refresh_from_db()
        self.assertTrue(self.other.is_active)
        self.assertEqual(self.other.email, "other@example.com")
        self.assertEqual(
            Consent.objects.filter(pk=self.consent.pk).values().get(), before
        )
        log = DataSubjectRequestLog.objects.get()
        self.assertEqual(log.request_type, "withdrawal")
        self.assertEqual(log.status, "completed")
        self.assertEqual(log.due_at - log.requested_at, timedelta(days=30))
        assert log.completed_at is not None
        self.assertLessEqual(log.completed_at, log.due_at)
        withdrawal = ConsentWithdrawal.objects.get()
        self.assertEqual(withdrawal.consent, self.consent)
        self.assertEqual(withdrawal.request_log, log)
        self.assertEqual(withdrawal.withdrawn_at, log.requested_at)
        self.assertEqual(
            serialize_user_consent_history(self.user)[0][
                "withdrawal_request_id"
            ],
            log.pk,
        )
        self.assertEqual(
            extra_client.get(reverse("users:personal_data_export")).status_code,
            302,
        )

    def test_retained_balance_is_marked_and_payment_identifiers_are_removed(
        self,
    ) -> None:
        profile = PartnerProfile.objects.create(
            user=self.user,
            balance=Decimal("123.45"),
            payment_details="Private bank details",
            partner_code="private-partner-code",
        )
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertEqual(profile.balance, Decimal("123.45"))
        self.assertEqual(profile.payment_details, "")
        self.assertNotEqual(profile.partner_code, "private-partner-code")
        self.assertEqual(profile.status, "suspended")
        self.assertIsNotNone(profile.anonymized_at)
        self.assertIn("Article 6", profile.retention_basis)
        self.assertTrue(response.json()["result"]["retained_financial_records"])

    def test_empty_partner_profile_is_deleted(self) -> None:
        PartnerProfile.objects.create(
            user=self.user, payment_details="Private details"
        )
        self.client.post(self.url)
        self.assertFalse(PartnerProfile.objects.filter(user=self.user).exists())

    def test_no_consent_does_not_erase_account(self) -> None:
        self.consent.delete()
        self.assertEqual(self.client.post(self.url).status_code, 409)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(DataSubjectRequestLog.objects.exists())

    def test_only_authenticated_owner_can_post_and_csrf_is_required(
        self,
    ) -> None:
        self.client.logout()
        self.assertEqual(self.client.post(self.url).status_code, 302)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        self.assertEqual(csrf_client.post(self.url).status_code, 403)
        self.assertFalse(DataSubjectRequestLog.objects.exists())

    def test_failure_preserves_receipt_blocks_processing_and_can_be_retried(
        self,
    ) -> None:
        with patch(
            "apps.users.account_deletion.delete_account",
            side_effect=RuntimeError("failure"),
        ):
            response = self.client.post(self.url)
        self.assertEqual(response.status_code, 503)
        log = DataSubjectRequestLog.objects.get()
        self.assertEqual(log.status, "failed")
        self.assertIsNone(log.completed_at)
        self.assertEqual(ConsentWithdrawal.objects.count(), 1)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(self.user.email, "subject@example.com")
        self.user.is_active = True
        with self.assertRaises(ValueError):
            self.user.save()
        call_command("check_subject_requests", retry=True, stdout=StringIO())
        log.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(log.status, "completed")
        self.assertIsNotNone(self.user.anonymized_at)
        self.assertEqual(ConsentWithdrawal.objects.count(), 1)
        call_command("check_subject_requests", retry=True, stdout=StringIO())
        self.assertEqual(DataSubjectRequestLog.objects.count(), 1)

    def test_partial_cleanup_is_rolled_back_on_failure(self) -> None:
        group = Group.objects.create(name="Private group", owner=self.user)
        with patch(
            "apps.users.account_deletion.EmailAddress.objects.filter",
            side_effect=RuntimeError("failure"),
        ):
            self.client.post(self.url)
        self.assertTrue(Group.objects.filter(pk=group.pk).exists())
        self.assertEqual(DataSubjectRequestLog.objects.get().status, "failed")
        self.assertEqual(ConsentWithdrawal.objects.count(), 1)

    def test_account_deletion_uses_same_journal_and_service(self) -> None:
        self.assertEqual(
            self.client.post(reverse("users:account_deletion")).status_code, 200
        )
        self.assertEqual(
            DataSubjectRequestLog.objects.get().request_type, "deletion"
        )
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.anonymized_at)
        with self.assertRaises(ValueError):
            request_account_deletion(self.user, "POST", withdraw_consent=True)
        self.assertEqual(DataSubjectRequestLog.objects.count(), 1)

    def test_withdrawal_evidence_cannot_be_updated(self) -> None:
        self.client.post(self.url)
        withdrawal = ConsentWithdrawal.objects.get()
        with self.assertRaises(ValueError):
            withdrawal.save()
        with self.assertRaises(ValueError):
            ConsentWithdrawal.objects.update(withdrawn_at=timezone.now())

    def test_stale_profile_write_cannot_restore_personal_data(self) -> None:
        stale = User.objects.get(pk=self.user.pk)
        self.client.post(self.url)
        stale.bio = "Restored private bio"
        with self.assertRaises(ValueError):
            stale.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "")

    def test_access_export_and_history_are_logged_and_owner_scoped(
        self,
    ) -> None:
        create_subject_request(self.other, "access", "GET")
        self.assertEqual(
            self.client.get(reverse("users:personal_data_access")).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(reverse("users:personal_data_export")).status_code,
            200,
        )
        logs = self.client.get(reverse("users:subject_request_history")).json()[
            "requests"
        ]
        self.assertEqual(
            {log["request_type"] for log in logs}, {"access", "export"}
        )
        self.assertTrue(all(log["status"] == "completed" for log in logs))
        self.assertTrue(
            all(
                log["due_at"] and log["completed_at"] and log["result"]
                for log in logs
            )
        )

    def test_export_failure_is_logged(self) -> None:
        with patch(
            "apps.users.views.build_personal_data_export",
            side_effect=RuntimeError("failure"),
        ):
            response = self.client.get(reverse("users:personal_data_export"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(DataSubjectRequestLog.objects.get().status, "failed")

    def test_overdue_requests_fail_monitoring_command(self) -> None:
        log = create_subject_request(self.user, "access", "GET")
        log.due_at = timezone.now() - timedelta(seconds=1)
        log.save(update_fields=["due_at"])
        with self.assertRaises(CommandError):
            call_command("check_subject_requests", stdout=StringIO())
        complete_subject_request(log, {"response_sent": True})
        call_command("check_subject_requests", stdout=StringIO())


class SubjectDeadlineTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="subject", email="subject@example.com", role="user"
        )
        self.staff = User.objects.create_user(
            username="staff", email="staff@example.com", is_staff=True
        )

    @override_settings(
        DATA_SUBJECT_WORK_CALENDAR={"2026-10-12": False, "2026-10-17": True}
    )
    def test_working_deadline_accounts_for_holidays_and_working_saturdays(
        self,
    ) -> None:
        start = datetime(2026, 10, 9, 12, tzinfo=UTC)
        self.assertEqual(
            add_working_days(start, 1), datetime(2026, 10, 13, 12, tzinfo=UTC)
        )
        self.assertEqual(
            add_working_days(start, 5), datetime(2026, 10, 17, 12, tzinfo=UTC)
        )
        self.assertEqual(
            add_working_days(start, 10), datetime(2026, 10, 23, 12, tzinfo=UTC)
        )

    @override_settings(DATA_SUBJECT_WORK_CALENDAR=None)
    def test_missing_calendar_uses_earlier_internal_deadline(self) -> None:
        start = datetime(2026, 10, 9, 12, tzinfo=UTC)
        self.assertEqual(
            add_working_days(start, 10), start + timedelta(days=10)
        )

    @override_settings(DATA_SUBJECT_WORK_CALENDAR={})
    def test_extension_requires_notification_and_is_allowed_only_once(
        self,
    ) -> None:
        log = create_subject_request(self.user, "access", "GET")
        original = log.due_at
        extended = extend_subject_request(
            log,
            responsible=self.staff,
            reason="Archive retrieval",
            notification_reference="outgoing-123",
            notified_at=timezone.now(),
        )
        self.assertEqual(extended.original_due_at, original)
        self.assertEqual(extended.due_at, add_working_days(original, 5))
        self.assertEqual(extended.responsible, self.staff)
        with self.assertRaises(ValueError):
            extend_subject_request(
                log,
                responsible=self.staff,
                reason="Again",
                notification_reference="outgoing-124",
                notified_at=timezone.now(),
            )

    def test_invalid_extensions_are_rejected(self) -> None:
        for request_type, reason, days, staff in [
            ("withdrawal", "Archive", 5, True),
            ("deletion", "Archive", 5, True),
            ("rectification", "Archive", 5, True),
            ("access", "", 5, True),
            ("access", "Archive", 6, True),
            ("access", "Archive", 5, False),
        ]:
            with self.subTest(
                request_type=request_type, reason=reason, days=days, staff=staff
            ):
                log = create_subject_request(self.user, request_type, "POST")
                with self.assertRaises(ValueError):
                    extend_subject_request(
                        log,
                        responsible=self.staff if staff else self.user,
                        reason=reason,
                        days=days,
                        notification_reference="outgoing-123",
                        notified_at=timezone.now(),
                    )

    def test_extension_cannot_be_applied_after_deadline_or_completion(
        self,
    ) -> None:
        for completed in (False, True):
            log = create_subject_request(self.user, "export", "GET")
            if completed:
                complete_subject_request(log, {"response_sent": True})
            else:
                log.due_at = timezone.now() - timedelta(seconds=1)
                log.save(update_fields=["due_at"])
            with self.assertRaises(ValueError):
                extend_subject_request(
                    log,
                    responsible=self.staff,
                    reason="Archive",
                    notification_reference="outgoing-123",
                    notified_at=timezone.now(),
                )

    def test_deadline_backfill_preserves_completed_export(self) -> None:
        log = create_subject_request(self.user, "export", "GET")
        complete_subject_request(log, {"format_version": "1.0"})
        completed = log.completed_at
        received = datetime(2026, 9, 1, 12, tzinfo=UTC)
        DataSubjectRequestLog.objects.filter(pk=log.pk).update(
            requested_at=received
        )
        migration = import_module(
            "apps.users.migrations.0010_subject_request_workflow"
        )
        migration.backfill_deadlines(
            apps, SimpleNamespace(connection=connection)
        )
        log.refresh_from_db()
        self.assertEqual(log.original_due_at, received + timedelta(days=10))
        self.assertEqual(log.due_at, log.original_due_at)
        self.assertEqual(log.status, "completed")
        self.assertEqual(log.completed_at, completed)
        self.assertTrue(log.result["legacy_export"])

    def test_late_failure_cannot_overwrite_completed_request(self) -> None:
        log = create_subject_request(self.user, "access", "GET")
        complete_subject_request(log, {"response_sent": True})
        fail_subject_request(log)
        self.assertEqual(log.status, "completed")
        self.assertEqual(log.result, {"response_sent": True})
