import uuid
from typing import Any

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from django.db import transaction
from django.utils import timezone
from guardian.models import UserObjectPermission

from apps.admin.moderation.models import ModerationRequest
from apps.billing.models import Subscription
from apps.blog.models import BlogArticle
from apps.group_channels.models import Group, SavedCollection
from apps.parser.models import AIInsight, ChannelModerator
from apps.users.data_subject_requests import (
    complete_subject_request,
    create_subject_request,
    fail_subject_request,
)
from apps.users.models import (
    Consent,
    ConsentWithdrawal,
    DataSubjectRequestLog,
    PartnerProfile,
    User,
)
from apps.users.roles import UserRoleHistory

AUDIT_RETENTION_BASIS = (
    "152-FZ Article 9(1): evidence of consent and subject request handling"
)
FINANCIAL_RETENTION_BASIS = (
    "152-FZ Article 6(1)(5): settlement of outstanding contractual obligations"
)


@transaction.atomic
def delete_account(
    user: User, request_log: DataSubjectRequestLog
) -> dict[str, Any]:
    locked = User.objects.select_for_update().get(pk=user.pk)
    if request_log.subject_id != locked.pk or request_log.request_type not in (
        DataSubjectRequestLog.RequestType.DELETION,
        DataSubjectRequestLog.RequestType.WITHDRAWAL,
    ):
        raise ValueError("Subject request does not belong to this user")
    if locked.anonymized_at is not None:
        return {"account_anonymized": True, "already_processed": True}
    now = timezone.now()
    Group.objects.filter(owner=locked).delete()
    Group.objects.filter(curator=locked).update(curator=None)
    SavedCollection.objects.filter(user=locked).delete()
    AIInsight.objects.filter(user=locked).delete()
    ChannelModerator.objects.filter(user=locked).delete()
    ModerationRequest.objects.filter(submitted_by=locked).delete()
    ModerationRequest.objects.filter(moderator=locked).update(moderator=None)
    BlogArticle.objects.filter(author=locked).update(author=None)
    EmailAddress.objects.filter(user=locked).delete()
    SocialAccount.objects.filter(user=locked).delete()
    UserObjectPermission.objects.filter(user=locked).delete()
    LogEntry.objects.filter(user=locked).delete()
    locked.groups.clear()
    locked.user_permissions.clear()
    UserRoleHistory.objects.filter(user=locked).delete()
    Subscription.objects.filter(user=locked).delete()

    retained_financial_records = []
    profile = PartnerProfile.objects.filter(user=locked).first()
    if profile is not None:
        if profile.balance == 0:
            profile.delete()
        else:
            profile.payment_details = ""
            profile.partner_code = f"anonymized-{uuid.uuid4().hex}"
            profile.status = "suspended"
            profile.anonymized_at = now
            profile.retention_basis = FINANCIAL_RETENTION_BASIS
            profile.save(
                update_fields=[
                    "payment_details",
                    "partner_code",
                    "status",
                    "anonymized_at",
                    "retention_basis",
                ]
            )
            retained_financial_records.append(
                {
                    "model": "users.PartnerProfile",
                    "id": profile.pk,
                    "anonymized_at": now.isoformat(),
                    "legal_basis": FINANCIAL_RETENTION_BASIS,
                }
            )

    for session in Session.objects.filter(expire_date__gt=now).iterator():
        if session.get_decoded().get("_auth_user_id") == str(locked.pk):
            session.delete()
    token = uuid.uuid4().hex
    locked.username = f"deleted-{token}"
    locked.email = f"{token}@deleted.invalid"
    locked.first_name = ""
    locked.last_name = ""
    locked.bio = ""
    locked.avatar_image = None
    locked.role = ""
    locked.last_login = None
    locked.is_active = False
    locked.is_staff = False
    locked.is_superuser = False
    locked.set_unusable_password()
    locked.anonymized_at = now
    locked.retention_basis = AUDIT_RETENTION_BASIS
    locked.save(
        update_fields=[
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "avatar_image",
            "role",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
            "password",
            "anonymized_at",
            "retention_basis",
        ]
    )
    return {
        "account_anonymized": True,
        "processing_stopped_at": request_log.requested_at.isoformat(),
        "retained_financial_records": retained_financial_records,
        "audit_retention_basis": AUDIT_RETENTION_BASIS,
    }


def process_account_deletion(request_log: DataSubjectRequestLog) -> None:
    try:
        with transaction.atomic():
            locked_log = DataSubjectRequestLog.objects.select_for_update().get(
                pk=request_log.pk
            )
            if locked_log.status == DataSubjectRequestLog.Status.COMPLETED:
                return
            if (
                locked_log.request_type
                not in (
                    DataSubjectRequestLog.RequestType.DELETION,
                    DataSubjectRequestLog.RequestType.WITHDRAWAL,
                )
                or locked_log.subject is None
            ):
                raise ValueError("Not an account deletion request")
            result = delete_account(locked_log.subject, locked_log)
            complete_subject_request(locked_log, result)
    except Exception:
        fail_subject_request(request_log)
    request_log.refresh_from_db()


def request_account_deletion(
    user: User, http_method: str, *, withdraw_consent: bool = False
) -> DataSubjectRequestLog:
    # Persist receipt and stop processing even if the subsequent cleanup fails.
    with transaction.atomic():
        locked = User.objects.select_for_update().get(pk=user.pk)
        if not locked.is_active or locked.anonymized_at is not None:
            raise ValueError("Account processing is already stopped")
        consents = Consent.objects.filter(user=locked, withdrawal__isnull=True)
        if (
            withdraw_consent
            and not consents.filter(
                document_type=Consent.DocumentType.PERSONAL_DATA
            ).exists()
        ):
            raise ValueError("No active personal data consent")
        request_log = create_subject_request(
            locked,
            DataSubjectRequestLog.RequestType.WITHDRAWAL
            if withdraw_consent
            else DataSubjectRequestLog.RequestType.DELETION,
            http_method,
        )
        for consent in consents:
            ConsentWithdrawal.objects.create(
                consent=consent,
                request_log=request_log,
                withdrawn_at=request_log.requested_at,
            )
        locked.is_active = False
        locked.save(update_fields=["is_active"])
        request_log.status = DataSubjectRequestLog.Status.PROCESSING
        request_log.save(update_fields=["status"])
    process_account_deletion(request_log)
    return request_log
