from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


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
