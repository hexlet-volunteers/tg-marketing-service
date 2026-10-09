"""Build the versioned personal data export owned by one user."""

from datetime import datetime
from typing import Any

from apps.group_channels.models import Group
from apps.parser.models import AIInsight, ChannelModerator
from apps.users.consents import serialize_user_consent_history
from apps.users.data_subject_requests import serialize_subject_request
from apps.users.models import PartnerProfile, User

EXPORT_FORMAT_VERSION = "1.0"


def _isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _profile_data(user: User) -> dict[str, Any]:
    return {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "bio": user.bio,
        "avatar_image": user.avatar_image,
        "role": user.role,
        "date_joined": _isoformat(user.date_joined),
        "last_login": _isoformat(user.last_login),
    }


def _partner_data(user: User) -> dict[str, Any] | None:
    try:
        profile = user.partner_profile
    except PartnerProfile.DoesNotExist:
        return None

    return {
        "status": profile.status,
        "balance": str(profile.balance),
        "payment_details": profile.payment_details,
        "partner_code": profile.partner_code,
        "partner_since": _isoformat(profile.partner_since),
    }


def _owned_groups(user: User) -> list[dict[str, Any]]:
    groups = (
        Group.objects.filter(owner=user)
        .prefetch_related("channels")
        .order_by("pk")
    )
    return [
        {
            "id": group.pk,
            "name": group.name,
            "slug": group.slug,
            "description": group.description,
            "is_editorial": group.is_editorial,
            "order": group.order,
            "image_url": group.image_url,
            "created_at": _isoformat(group.created_at),
            "channel_ids": [channel.pk for channel in group.channels.all()],
        }
        for group in groups
    ]


def _moderator_assignments(user: User) -> list[dict[str, Any]]:
    assignments = ChannelModerator.objects.filter(user=user).order_by("pk")
    return [
        {
            "id": assignment.pk,
            "channel_id": assignment.channel_id,
            "is_owner": assignment.is_owner,
            "can_edit": assignment.can_edit,
            "can_delete": assignment.can_delete,
            "can_manage_moderators": assignment.can_manage_moderators,
            "created_at": _isoformat(assignment.created_at),
        }
        for assignment in assignments
    ]


def _ai_insights(user: User) -> list[dict[str, Any]]:
    insights = AIInsight.objects.filter(user=user).order_by("pk")
    return [
        {
            "id": insight.pk,
            "channel_id": insight.channel_id,
            "insight_text": insight.insight_text,
            "insight_type": insight.insight_type,
            "created_at": _isoformat(insight.created_at),
            "is_read": insight.is_read,
        }
        for insight in insights
    ]


def _processing_information(
    has_partner_profile: bool,
) -> dict[str, Any]:
    fields: dict[str, list[str]] = {
        "subject": ["subject_id"],
        "profile": [
            "email",
            "first_name",
            "last_name",
            "bio",
            "avatar_image",
            "role",
            "date_joined",
            "last_login",
        ],
        "owned_groups": [
            "id",
            "name",
            "slug",
            "description",
            "is_editorial",
            "order",
            "image_url",
            "created_at",
            "channel_ids",
        ],
        "channel_moderator_assignments": [
            "id",
            "channel_id",
            "is_owner",
            "can_edit",
            "can_delete",
            "can_manage_moderators",
            "created_at",
        ],
        "ai_insights": [
            "id",
            "channel_id",
            "insight_text",
            "insight_type",
            "created_at",
            "is_read",
        ],
        "consents": [
            "id",
            "document_type",
            "version",
            "timestamp",
            "ip",
            "user_agent",
            "source",
            "withdrawn_at",
            "withdrawal_request_id",
        ],
    }
    if has_partner_profile:
        fields["partner_profile"] = [
            "status",
            "balance",
            "payment_details",
            "partner_code",
            "partner_since",
        ]

    return {
        "processing_confirmed": True,
        "purposes": [
            "Регистрация, аутентификация и ведение профиля пользователя",
            "Предоставление функций сервиса и пользовательских настроек",
            "Управление партнёрской программой и расчётами для партнёров",
            "Формирование персональных аналитических рекомендаций",
        ],
        "legal_basis": [
            "Согласие субъекта персональных данных: пункт 1 части 1 "
            "статьи 6 Федерального закона от 27.07.2006 № 152-ФЗ",
            "Исполнение договора с субъектом персональных данных: пункт 5 "
            "части 1 статьи 6 Федерального закона от 27.07.2006 № 152-ФЗ",
        ],
        "retention_terms": [
            "Данные хранятся в течение срока использования учётной записи "
            "и достижения заявленных целей обработки.",
            "После прекращения обработки данные удаляются или "
            "обезличиваются, кроме случаев, когда обязательный срок "
            "хранения установлен законодательством РФ.",
        ],
        "personal_data_fields": fields,
    }


def build_personal_data_export(
    user: User,
    exported_at: datetime,
) -> dict[str, Any]:
    partner_data = _partner_data(user)
    personal_data: dict[str, Any] = {
        "profile": _profile_data(user),
        "owned_groups": _owned_groups(user),
        "channel_moderator_assignments": _moderator_assignments(user),
        "ai_insights": _ai_insights(user),
        "consents": serialize_user_consent_history(user),
        "subject_requests": [
            serialize_subject_request(log)
            for log in user.personal_data_request_logs.all()
        ],
    }
    if partner_data is not None:
        personal_data["partner_profile"] = partner_data

    return {
        "format_version": EXPORT_FORMAT_VERSION,
        "exported_at": _isoformat(exported_at),
        "subject_id": user.pk,
        "personal_data": personal_data,
        "processing_information": _processing_information(
            has_partner_profile=partner_data is not None
        ),
    }
