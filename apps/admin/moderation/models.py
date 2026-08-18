from django.db import models

from apps.parser.models import TelegramChannel
from apps.users.models import User


class ModerationRequestQuerySet(models.QuerySet):
    def pending_queue(self):
        return (
            self.filter(status="pending")
            .select_related("submitted_by", "channel_by")
            .order_by("created_at", "id")
        )


class ModerationRequest(models.Model):
    status_choices = [
        ("pending", "В ожидании"),
        ("approved", "Одобрено"),
        ("rejected", "Отклонено"),
        ("duplicate", "Дубликат"),
    ]

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="moderation_requests",
        verbose_name="Пользователь, отправивший запрос",
    )

    channel_identifier = models.CharField(
        max_length=255,
        verbose_name="Идентификатор канала (username или url)",
    )

    channel_by = models.ForeignKey(
        TelegramChannel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderation_requests",
        verbose_name="Канал, к которому относится запрос",
    )

    category = models.CharField(
        max_length=255,
        verbose_name="Категория запроса",
    )

    country = models.CharField(
        max_length=255,
        verbose_name="Страна, к которой относится запрос",
    )

    language = models.CharField(
        max_length=255,
        verbose_name="Язык, к которому относится запрос",
    )

    status = models.CharField(
        max_length=255,
        choices=status_choices,
        verbose_name="Статус запроса",
        default="pending",
        db_index=True,
    )

    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_requests",
        verbose_name="Модератор, обработавший запрос",
    )

    reject_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name="Причина отклонения запроса",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время создания запроса",
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата и время обработки запроса",
    )

    objects = ModerationRequestQuerySet.as_manager()
