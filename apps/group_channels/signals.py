from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.group_channels.models import Group, SavedCollection


@receiver(post_save, sender=SavedCollection)
def increment_group_saves_count(
    sender: type[SavedCollection],
    instance: SavedCollection,
    created: bool,
    **kwargs: object,
) -> None:
    if not created:
        return
    Group.objects.filter(pk=instance.group_id).update(
        saves_count=F("saves_count") + 1
    )


@receiver(post_delete, sender=SavedCollection)
def decrement_group_saves_count(
    sender: type[SavedCollection],
    instance: SavedCollection,
    **kwargs: object,
) -> None:
    Group.objects.filter(pk=instance.group_id, saves_count__gt=0).update(
        saves_count=F("saves_count") - 1
    )
