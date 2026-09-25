from typing import Any

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.billing.services.subscription_service import (
    create_default_subscription,
)
from apps.users.models import User


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_free_subscription(
    sender: type[User],
    instance: User,
    created: bool,
    **kwargs: Any,
) -> None:
    """Назначает новому пользователю тариф Free."""
    if not created:
        return

    create_default_subscription(instance)
