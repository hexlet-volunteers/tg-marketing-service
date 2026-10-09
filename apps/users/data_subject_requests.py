from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.users.models import DataSubjectRequestLog, User


def add_working_days(start: datetime, days: int) -> datetime:
    calendar = getattr(settings, "DATA_SUBJECT_WORK_CALENDAR", None)
    # Without a verified production calendar, use an earlier internal deadline.
    if calendar is None:
        return start + timedelta(days=days)
    current = start.astimezone(ZoneInfo("Europe/Moscow"))
    remaining = days
    while remaining:
        current += timedelta(days=1)
        if calendar.get(current.date().isoformat(), current.weekday() < 5):
            remaining -= 1
    return current.astimezone(UTC)


def create_subject_request(
    user: User, request_type: str, http_method: str
) -> DataSubjectRequestLog:
    if request_type not in DataSubjectRequestLog.RequestType.values:
        raise ValueError("Unknown subject request type")
    received = timezone.now()
    if request_type in (
        DataSubjectRequestLog.RequestType.DELETION,
        DataSubjectRequestLog.RequestType.WITHDRAWAL,
    ):
        due = received + timedelta(days=30)
    else:
        due = add_working_days(
            received,
            7
            if request_type == DataSubjectRequestLog.RequestType.RECTIFICATION
            else 10,
        )
    return DataSubjectRequestLog.objects.create(
        subject=user,
        subject_id_snapshot=user.pk,
        request_type=request_type,
        http_method=http_method,
        requested_at=received,
        due_at=due,
        original_due_at=due,
    )


def complete_subject_request(
    request_log: DataSubjectRequestLog, result: dict[str, Any]
) -> None:
    request_log.status = DataSubjectRequestLog.Status.COMPLETED
    request_log.completed_at = timezone.now()
    request_log.result = result
    request_log.save(update_fields=["status", "completed_at", "result"])


def fail_subject_request(request_log: DataSubjectRequestLog) -> None:
    DataSubjectRequestLog.objects.filter(pk=request_log.pk).exclude(
        status=DataSubjectRequestLog.Status.COMPLETED
    ).update(
        status=DataSubjectRequestLog.Status.FAILED,
        result={"error": "processing_failed", "retry_required": True},
    )
    request_log.refresh_from_db()


@transaction.atomic
def extend_subject_request(
    request_log: DataSubjectRequestLog,
    *,
    responsible: User,
    reason: str,
    notification_reference: str,
    notified_at: datetime,
    days: int = 5,
) -> DataSubjectRequestLog:
    if not responsible.is_active or not responsible.is_staff:
        raise ValueError("Only active staff may extend a request")
    locked = DataSubjectRequestLog.objects.select_for_update().get(
        pk=request_log.pk
    )
    now = timezone.now()
    if (
        locked.request_type
        not in (
            DataSubjectRequestLog.RequestType.ACCESS,
            DataSubjectRequestLog.RequestType.EXPORT,
        )
        or locked.status == DataSubjectRequestLog.Status.COMPLETED
        or locked.extended_at is not None
        or not 1 <= days <= 5
        or not reason.strip()
        or not notification_reference.strip()
        or timezone.is_naive(notified_at)
        or not locked.requested_at <= notified_at <= now <= locked.due_at
    ):
        raise ValueError(
            "Extension requires timely notification and an eligible request"
        )
    locked.due_at = add_working_days(locked.original_due_at, days)
    locked.extension_reason = reason.strip()
    locked.extension_notification_reference = notification_reference.strip()
    locked.extension_notified_at = notified_at
    locked.extended_at = now
    locked.responsible = responsible
    locked.save(
        update_fields=[
            "due_at",
            "extension_reason",
            "extension_notification_reference",
            "extension_notified_at",
            "extended_at",
            "responsible",
        ]
    )
    return locked


def serialize_subject_request(
    request_log: DataSubjectRequestLog,
) -> dict[str, Any]:
    return {
        "id": request_log.pk,
        "request_type": request_log.request_type,
        "requested_at": request_log.requested_at.isoformat(),
        "due_at": request_log.due_at.isoformat(),
        "original_due_at": request_log.original_due_at.isoformat(),
        "completed_at": (
            request_log.completed_at.isoformat()
            if request_log.completed_at
            else None
        ),
        "status": request_log.status,
        "result": request_log.result,
        "extension_reason": request_log.extension_reason,
    }
