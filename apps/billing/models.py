import math
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    class Code(models.TextChoices):
        FREE = "Free", "Бесплатный"
        PRO = "Pro", "Продвинутый"
        AGENCY = "Agency", "Агентский"

    code = models.CharField(max_length=20, choices=Code.choices, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    monthly_price = models.DecimalField(max_digits=12, decimal_places=2)
    annual_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    is_highlighted = models.BooleanField(default=False)
    ordering = models.PositiveIntegerField(default=0)
    channels_limit = models.PositiveIntegerField()
    ai_requests_limit = models.PositiveIntegerField()
    features = models.JSONField(default=list)

    class Meta:
        ordering = ("ordering", "id")
        verbose_name = "тариф"
        verbose_name_plural = "тарифы"

    def __str__(self) -> str:
        return self.name

    @property
    def currency_symbol(self) -> str:
        return "₽"

    def clean(self) -> None:
        super().clean()
        if self.currency != "RUB":
            raise ValidationError(
                {"currency": "Поддерживается только валюта RUB."}
            )
        expected_annual_price = (
            self.monthly_price * 12 * Decimal("0.8")
        ).quantize(Decimal("0.01"))
        if self.annual_price != expected_annual_price:
            raise ValidationError(
                {
                    "annual_price": (
                        "Годовая цена должна быть равна "
                        "80% от стоимости 12 месяцев."
                    )
                }
            )
        if not isinstance(self.features, list) or not all(
            isinstance(feature, str) for feature in self.features
        ):
            raise ValidationError(
                {"features": "features должен быть списком строк."}
            )

    def get_data(self) -> dict[str, object]:
        return {
            "id": self.pk,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "monthlyPrice": self.monthly_price,
            "annualPrice": self.annual_price,
            "currency": self.currency,
            "features": [
                {"id": index, "text": feature}
                for index, feature in enumerate(self.features, start=1)
            ],
            "isHighlighted": self.is_highlighted,
            "channelsLimit": self.channels_limit,
            "aiRequestsLimit": self.ai_requests_limit,
        }


class Subscription(models.Model):
    """Состояние подписки пользователя.

    Для каждого пользователя предполагается одна подписка.
    Новая подписка по умолчанию создаётся на тарифе Free
    (см. ``apps.billing.signals``).
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Активна"
        CANCELED = "canceled", "Отменена"
        EXPIRED = "expired", "Истекла"

    class BillingPeriod(models.TextChoices):
        MONTHLY = "monthly", "Месячная"
        ANNUAL = "annual", "Годовая"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name="Пользователь",
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name="Тариф",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )
    billing_period = models.CharField(
        max_length=10,
        choices=BillingPeriod.choices,
        default=BillingPeriod.MONTHLY,
        verbose_name="Период оплаты",
    )
    started_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата начала",
    )
    current_period_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Конец текущего периода",
    )
    is_auto_renew = models.BooleanField(
        default=False,
        verbose_name="Автопродление",
    )

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
        ordering = ("-started_at", "id")

    def __str__(self) -> str:
        return f"{self.user} — {self.plan.code} ({self.get_status_display()})"

    @property
    def price(self) -> Decimal:
        """Стоимость текущего периода оплаты в рублях."""
        if self.billing_period == self.BillingPeriod.ANNUAL:
            return self.plan.annual_price
        return self.plan.monthly_price

    @property
    def days_left(self) -> int:
        """Сколько дней осталось до конца текущего периода.

        Возвращает 0 для неактивных подписок и подписок без даты
        следующего списания (например, Free).
        """
        if self.status != self.Status.ACTIVE or self.current_period_end is None:
            return 0

        remaining_seconds = (
            self.current_period_end - timezone.now()
        ).total_seconds()
        if remaining_seconds <= 0:
            return 0
        return math.ceil(remaining_seconds / 86400)

    @property
    def channels_used(self) -> int:
        """Количество каналов, которые ведет пользователь."""
        return self.user.moderated_channels.count()

    @property
    def ai_requests_used(self) -> int:
        """Количество использованных AI-запросов (инсайтов).

        Считается за все время; сброс лимита по периоду — вне рамок
        текущей задачи.
        """
        return self.user.ai_insights.count()

    def clean(self) -> None:
        super().clean()
        if (
            self.current_period_end is not None
            and self.started_at is not None
            and self.current_period_end < self.started_at
        ):
            raise ValidationError(
                {
                    "current_period_end": (
                        "Конец периода не может быть раньше даты начала."
                    )
                }
            )
