from typing import Any

from apps.billing.dto.subscription_dto import (
    SubscriptionLimitsDTO,
    SubscriptionStateDTO,
)
from apps.billing.models import Plan, Subscription
from apps.users.models import User


def get_subscription(user: User) -> Subscription:
    """Возвращает подписку пользователя.

    Если подписки еще нет (например, пользователь был создан до
    появления ``Subscription``), лениво создает подписку на тарифе Free.
    """
    subscription = (
        Subscription.objects.select_related("plan").filter(user=user).first()
    )
    if subscription is not None:
        subscription.user = user
        return subscription

    return create_default_subscription(user)


def create_default_subscription(user: User) -> Subscription:
    """Создает (идемпотентно) подписку пользователя на тарифе Free."""
    free_plan = Plan.objects.get(code=Plan.Code.FREE)
    subscription, _ = Subscription.objects.get_or_create(
        user=user,
        defaults={
            "plan": free_plan,
            "status": Subscription.Status.ACTIVE,
            "billing_period": Subscription.BillingPeriod.MONTHLY,
            "is_auto_renew": False,
        },
    )
    return subscription


def serialize_subscription(subscription: Subscription) -> dict[str, Any]:
    """Сериализует подписку в frontend-контракт.

    Контракт: ``{plan, period, price, current_period_end, limits}`` плюс
    текущее потребление. Цена отдается в рублях (RUB).
    """
    state = SubscriptionStateDTO(
        plan=subscription.plan.code,
        period=subscription.billing_period,
        price=subscription.price,
        current_period_end=subscription.current_period_end,
        limits=SubscriptionLimitsDTO(
            channels=subscription.plan.channels_limit,
            ai_requests=subscription.plan.ai_requests_limit,
        ),
        days_left=subscription.days_left,
        channels_used=subscription.channels_used,
        ai_requests_used=subscription.ai_requests_used,
    )
    return state.model_dump(mode="json")
