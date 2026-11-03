import logging
from typing import Any

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.parser.models import ChannelModerator
from apps.users.constants import UserRole
from apps.users.models import PartnerProfile, User
from apps.users.roles import Role, UserRoleHistory

log = logging.getLogger(__name__)


"""Отлавливаем событие регистрации пользователя"""
"""присваеиваем роль - User"""


@receiver(post_save, sender=User)
def assign_role_partner(
    sender: type[User],
    instance: User,
    created: bool,
    **kwargs: Any,
) -> None:
    """Назначает роль обычного пользователя при регистрации."""
    if created and not instance.role:
        instance.role = UserRole.USER
        instance.save(update_fields=["role"])


"""Отлавливаем событие при изменении статуса партнера на Активный"""
"""присваеиваем роль - Partner"""


@receiver(post_save, sender=PartnerProfile)
def assign_role_channel_moderator(
    sender: type[PartnerProfile],
    instance: PartnerProfile,
    created: bool,
    **kwargs: Any,
) -> None:
    if created:
        return

    if instance.status == PartnerProfile.STATUS_CHOICES[0][0]:
        user = instance.user

        if user.role not in {UserRole.ADMIN, UserRole.PARTNER}:
            user.role = UserRole.PARTNER
            user.save(update_fields=["role"])


"""Отлавливаем событие регистрации канала"""
"""присваеиваем роль - Moderator_channels"""


@receiver(post_save, sender=ChannelModerator)
def assign_role_moderator_channel(
    sender: type[ChannelModerator],
    instance: ChannelModerator,
    created: bool,
    **kwargs: Any,
) -> None:
    """Назначает владельцу канала роль модератора."""
    if not instance.is_owner:
        return

    user = instance.user

    # Партнёр, модератор и админ сохраняют свою роль
    if user.role in (
        UserRole.CHANNEL_MODERATOR,
        UserRole.PARTNER,
        UserRole.ADMIN,
    ):
        return

    with transaction.atomic():
        # Получаем роль или создаём её, если она ещё не зарегистрирована.
        moderator_role, _ = Role.objects.get_or_create(
            code=UserRole.CHANNEL_MODERATOR,
            defaults={"name": "Модератор канала"},
        )

        # Закрываем все активные записи истории прежних ролей.
        UserRoleHistory.objects.filter(
            user=user,
            end_date__isnull=True,
        ).update(
            end_date=timezone.now(),
            reason="Назначена роль модератора канала",
        )

        user.role = moderator_role.code
        user.save(update_fields=["role"])

        UserRoleHistory.objects.create(
            user=user,
            role=moderator_role,
            reason="Назначена роль модератора канала",
        )
