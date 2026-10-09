import uuid
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string

from .constants import BIO_MAXLENGTH, ROLE_MAXLENGTH


# Create your models here.
class User(AbstractUser):
    anonymized_at = models.DateTimeField(null=True, blank=True, editable=False)
    retention_basis = models.TextField(blank=True, editable=False)
    avatar_image = models.CharField(
        verbose_name="url изображения профиля", blank=True, null=True
    )
    role = models.CharField(max_length=ROLE_MAXLENGTH)
    bio = models.CharField(
        max_length=BIO_MAXLENGTH, verbose_name="о себе", blank=True
    )
    email = models.EmailField(
        verbose_name="email адрес", blank=True, unique=True
    )

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_add_channel", "Может добавлять каналы"),
            ("can_apply_partnership", "Может подавать заявку на партнерство"),
        ]

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self._state.adding:
            super().save(*args, **kwargs)
            return
        # Lock profile writes so stale requests cannot restore erased data.
        with transaction.atomic():
            previous = (
                User.objects.select_for_update().filter(pk=self.pk).first()
            )
            if previous is not None:
                if previous.anonymized_at is not None:
                    raise ValueError("An anonymized account cannot be changed")
                if (
                    not previous.is_active
                    and self.is_active
                    and DataSubjectRequestLog.objects.filter(
                        subject_id=self.pk,
                        request_type__in=[
                            DataSubjectRequestLog.RequestType.DELETION,
                            DataSubjectRequestLog.RequestType.WITHDRAWAL,
                        ],
                    ).exists()
                ):
                    raise ValueError(
                        "Account processing has permanently stopped"
                    )
            super().save(*args, **kwargs)

    @property
    def is_partner(self) -> bool:
        """Проверка, является ли пользователь активным партнером."""
        return (
            hasattr(self, "partner_profile")
            and self.partner_profile.status == "active"
        )

    @property
    def is_channel_moderator(self) -> bool:
        """Проверка, является ли пользователь модератором какого-либо канала."""
        return self.moderated_channels.exists()


class ConsentQuerySet(models.QuerySet["Consent"]):
    def update(self, **kwargs: Any) -> int:
        raise ValueError("Consent records are immutable")


class Consent(models.Model):
    """Append-only log of personal-data processing consents."""

    class DocumentType(models.TextChoices):
        PRIVACY_POLICY = "privacy_policy", "Privacy policy"
        PERSONAL_DATA = "personal_data", "Personal data consent"
        COOKIE_ANALYTICS = "cookie_analytics", "Cookie analytics"

    class Source(models.TextChoices):
        EMAIL_REGISTRATION = "email_registration", "Email registration"
        YANDEX_OAUTH = "yandex_oauth", "Yandex OAuth"
        COOKIE_BANNER = "cookie_banner", "Cookie banner"

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="consents",
        verbose_name="User",
    )
    document_type = models.CharField(
        max_length=32,
        choices=DocumentType.choices,
        verbose_name="Document type",
    )
    version = models.CharField(max_length=32, verbose_name="Document version")
    timestamp = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Accepted at",
    )
    ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP address",
    )
    user_agent = models.TextField(blank=True, verbose_name="User agent")
    source = models.CharField(
        max_length=32,
        choices=Source.choices,
        verbose_name="Source",
    )
    objects = ConsentQuerySet.as_manager()

    class Meta:
        db_table = "user_consents"
        ordering = ["-timestamp", "-id"]
        indexes = [
            models.Index(fields=["user", "document_type", "version"]),
            models.Index(fields=["timestamp"]),
        ]
        verbose_name = "Consent"
        verbose_name_plural = "Consents"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValueError("Consent records are immutable")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.document_type} {self.version} at {self.timestamp}"


class PartnerProfile(models.Model):
    """Расширенный профиль для партнеров."""

    anonymized_at = models.DateTimeField(null=True, blank=True, editable=False)
    retention_basis = models.TextField(blank=True, editable=False)

    STATUS_CHOICES = [
        ("active", "Активен"),
        ("pending", "На рассмотрении"),
        ("rejected", "Отклонён"),
        ("suspended", "Приостановлен"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="partner_profile",
        verbose_name="Пользователь",
    )
    status = models.CharField(
        verbose_name="Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    partner_since = models.DateTimeField(
        verbose_name="Партнёр с", auto_now_add=True
    )
    balance = models.DecimalField(
        verbose_name="Баланс", max_digits=10, decimal_places=2, default=0
    )
    payment_details = models.TextField(
        verbose_name="Платёжные реквизиты", blank=True
    )
    partner_code = models.CharField(
        verbose_name="Партнерский код",
        max_length=50,
        unique=True,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Профиль партнёра"
        verbose_name_plural = "Профили партнёров"
        permissions = [
            ("access_partner_dashboard", "Доступ к партнерскому кабинету"),
            ("request_payout", "Может запрашивать выплаты"),
            ("view_traffic_analytics", "Может просматривать аналитику трафика"),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} ({self.get_status_display()})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Переопределенный метод сохранения объекта, который генерирует
        уникальный партнерский код при создании нового профиля.

        Метод обеспечивает:
        - Автоматическую генерацию партнерского кода
        - Проверку уникальности сгенерированного кода
        - Безопасное сохранение объекта в базе данных
        """

        # Проверяем, существует ли уже партнерский код
        if not self.partner_code:
            """
            Если партнерский код отсутствует, начинаем генерацию
            уникального кода. Используем бесконечный цикл для гарантии
            уникальности.
            """
            while True:
                # Генерируем случайную строку длиной 6 символов
                random_part = get_random_string(length=6)
                """
                get_random_string генерирует криптографически
                безопасную случайную строку, которая делает код более
                уникальным.
                """

                # Создаем уникальный идентификатор на основе UUID
                unique_id = uuid.uuid4().hex[:8]
                """
                uuid.uuid4() генерирует случайный UUID.
                .hex преобразует его в шестнадцатеричную строку.
                [:8] берет первые 8 символов для компактности.
                """

                # Формируем финальный партнерский код
                self.partner_code = (
                    f"partner-{self.user_id}-{unique_id}-{random_part}"
                )
                """
                Структура кода:
                - Префикс "partner-" для идентификации
                - ID пользователя для связи с профилем
                - Уникальный идентификатор
                - Случайная строка для дополнительной уникальности
                """

                # Проверяем уникальность сгенерированного кода
                if not PartnerProfile.objects.filter(
                    partner_code=self.partner_code
                ).exists():
                    """
                    Проверяем, существует ли такой код в базе данных.
                    Если код уникален, выходим из цикла.
                    """
                    break

        # Вызываем родительский метод save для сохранения объекта
        super().save(*args, **kwargs)


class DataSubjectRequestLog(models.Model):
    """Audit log for requests made by a personal data subject."""

    class RequestType(models.TextChoices):
        ACCESS = "access", "Access"
        RECTIFICATION = "rectification", "Rectification"
        DELETION = "deletion", "Deletion"
        WITHDRAWAL = "withdrawal", "Consent withdrawal"
        EXPORT = "export", "Экспорт персональных данных"

    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        PROCESSING = "processing", "Processing"
        FAILED = "failed", "Failed"
        COMPLETED = "completed", "Выполнен"

    subject = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="personal_data_request_logs",
        verbose_name="Субъект персональных данных",
    )
    subject_id_snapshot = models.PositiveBigIntegerField(
        verbose_name="ID субъекта на момент запроса"
    )
    request_type = models.CharField(
        max_length=20,
        choices=RequestType.choices,
        default=RequestType.EXPORT,
        verbose_name="Тип запроса",
    )
    http_method = models.CharField(max_length=4, verbose_name="HTTP-метод")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
        verbose_name="Статус",
    )
    requested_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Дата запроса",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата выполнения",
    )
    due_at = models.DateTimeField()
    original_due_at = models.DateTimeField(editable=False)
    result = models.JSONField(default=dict, blank=True)
    extension_reason = models.TextField(blank=True)
    extended_at = models.DateTimeField(null=True, blank=True)
    extension_notified_at = models.DateTimeField(null=True, blank=True)
    extension_notification_reference = models.CharField(
        max_length=255, blank=True
    )
    responsible = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_data_subject_requests",
    )

    class Meta:
        db_table = "data_subject_request_logs"
        ordering = ["-requested_at"]
        indexes = [models.Index(fields=["status", "due_at"])]
        verbose_name = "Запрос субъекта персональных данных"
        verbose_name_plural = "Запросы субъектов персональных данных"

    def __str__(self) -> str:
        return (
            f"{self.request_type} for subject {self.subject_id_snapshot} "
            f"at {self.requested_at}"
        )


class ConsentWithdrawalQuerySet(models.QuerySet["ConsentWithdrawal"]):
    def update(self, **kwargs: Any) -> int:
        raise ValueError("Consent withdrawals are immutable")


class ConsentWithdrawal(models.Model):
    consent = models.OneToOneField(
        Consent, on_delete=models.PROTECT, related_name="withdrawal"
    )
    request_log = models.ForeignKey(
        DataSubjectRequestLog,
        on_delete=models.PROTECT,
        related_name="consent_withdrawals",
    )
    withdrawn_at = models.DateTimeField(default=timezone.now, editable=False)
    objects = ConsentWithdrawalQuerySet.as_manager()

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValueError("Consent withdrawals are immutable")
        super().save(*args, **kwargs)
