import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.parser.models import TelegramChannel
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
    try:
        if created:
            user = instance
            if not user.role:
                user.role = "user"
                user.save(update_fields=["role"])

    except Role.DoesNotExist:
        log.error("Роль 'moderated_channels' не найдена в базе")


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

        if user.role != "partner":
            user.role = "partner"

            user.save(update_fields=["role"])


"""Отлавливаем событие регистрации канала"""
"""присваеиваем роль - Moderator_channels"""


@receiver(post_save, sender=TelegramChannel)
def assign_role_moderator_channel(
    sender: type[TelegramChannel],
    instance: TelegramChannel,
    created: bool,
    **kwargs: Any,
) -> None:
    if not created:
        return  # только для нового канала

    try:
        owner_relation = instance.moderators.filter(is_owner=True).first()
        if not owner_relation:
            return  # владелец не найден

        user = owner_relation.user
        moderator_role = Role._default_manager.get(code="moderated_channels")

        # Проверяем текущую роль пользователя
        if user.role in ["moderated_channels", "partner"]:
            return  # уже модератор или партнер

        # Закрываем старую роль в истории
        old_role_obj = Role._default_manager.filter(code=user.role).first()
        if old_role_obj:
            UserRoleHistory.objects.create(
                user=user,
                role=old_role_obj,
                end_date=timezone.now(),
                reason="Назначена роль модератора канала",
            )

        # Назначаем новую роль
        user.role = moderator_role.code
        user.save(update_fields=["role"])

        # Создаем запись в истории
        UserRoleHistory.objects.create(
            user=user,
            role=moderator_role,
            reason="Назначена роль модератора канала",
        )

    except Role.DoesNotExist:
        log.error("Роль 'moderated_channels' не найдена в базе")
