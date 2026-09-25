from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SubscriptionLimitsDTO(BaseModel):
    """Лимиты тарифа подписки."""

    channels: int
    ai_requests: int


class SubscriptionStateDTO(BaseModel):
    """Сериализованное состояние подписки для dashboard и личного кабинета.

    ``price`` отдается в рублях (RUB) согласно дизайну и модели ``Plan``.
    """

    plan: str
    period: str
    price: Decimal
    current_period_end: datetime | None
    limits: SubscriptionLimitsDTO
    days_left: int
    channels_used: int
    ai_requests_used: int
