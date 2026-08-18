from __future__ import annotations

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.admin.moderation.models import ModerationRequest
from apps.parser.models import TelegramChannel
from apps.users.models import User


class ModerationError(ValueError):
    """Ошибка бизнес-правил обработки заявки."""


class ModerationService:
    """Изменяет заявки и связанные каналы в одной транзакции."""

    @classmethod
    def approve(
        cls,
        request_id: int,
        moderator: User,
        *,
        category: str,
        is_verified: bool,
    ) -> ModerationRequest:
        category = category.strip()
        if not category:
            raise ModerationError("Категория обязательна")
        if len(category) > 255:
            raise ModerationError("Категория слишком длинная")

        try:
            with transaction.atomic():
                moderation_request = cls._get_pending(request_id)
                channel = moderation_request.channel_by
                if channel is None:
                    raise ModerationError(
                        "Нельзя одобрить заявку без связанного канала"
                    )

                username = channel.username
                duplicate = cls._find_duplicate(channel, username)
                resolved_at = timezone.now()

                if duplicate is not None:
                    return cls._mark_duplicate(moderation_request, moderator)

                channel.category = category
                channel.is_verified = is_verified
                channel.verified_at = resolved_at if is_verified else None
                channel.save(
                    update_fields=["category", "is_verified", "verified_at"]
                )

                moderation_request.status = "approved"
                moderation_request.category = category
                moderation_request.moderator = moderator
                moderation_request.resolved_at = resolved_at
                moderation_request.reject_reason = None
                moderation_request.save(
                    update_fields=[
                        "status",
                        "category",
                        "moderator",
                        "resolved_at",
                        "reject_reason",
                    ]
                )
        except IntegrityError:
            # Вторая параллельная транзакция уже опубликовала такой username.
            with transaction.atomic():
                moderation_request = cls._get_pending(request_id)
                return cls._mark_duplicate(
                    moderation_request,
                    moderator,
                )

        return moderation_request

    @staticmethod
    def reject(
        request_id: int,
        moderator: User,
        *,
        reason: str,
    ) -> ModerationRequest:
        reason = reason.strip()
        if not reason:
            raise ModerationError("Причина отклонения обязательна")

        with transaction.atomic():
            moderation_request = ModerationService._get_pending(request_id)
            moderation_request.status = "rejected"
            moderation_request.reject_reason = reason
            moderation_request.moderator = moderator
            moderation_request.resolved_at = timezone.now()
            moderation_request.save(
                update_fields=[
                    "status",
                    "reject_reason",
                    "moderator",
                    "resolved_at",
                ]
            )
            return moderation_request

    @staticmethod
    def _get_pending(request_id: int) -> ModerationRequest:
        moderation_request = (
            ModerationRequest.objects.select_for_update()
            .select_related("channel_by")
            .filter(pk=request_id)
            .first()
        )
        if moderation_request is None:
            raise ModerationError("Заявка не найдена")
        if moderation_request.status != "pending":
            raise ModerationError("Заявка уже обработана")
        return moderation_request

    @classmethod
    def _find_duplicate(
        cls, channel: TelegramChannel, username: str | None
    ) -> TelegramChannel | None:
        if not username:
            return None
        return (
            TelegramChannel.objects.filter(username__iexact=username)
            .exclude(pk=channel.pk)
            .first()
        )

    @staticmethod
    def _mark_duplicate(
        moderation_request: ModerationRequest,
        moderator: User,
    ) -> ModerationRequest:
        moderation_request.status = "duplicate"
        moderation_request.moderator = moderator
        moderation_request.resolved_at = timezone.now()
        moderation_request.save(
            update_fields=[
                "status",
                "moderator",
                "resolved_at",
            ],
        )
        return moderation_request
