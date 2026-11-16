from __future__ import annotations

from apps.group_channels.models import (
    AutoGroupRule,
    Group,
    SavedCollection,
)
from apps.users.demo.base import BaseSeedStep
from apps.users.demo.context import DemoSeedContext
from mocks import groups as groups_mocks
from mocks import users as users_mocks


class GroupsStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        groups: list[Group] = []
        owner = ctx.users.get("demo_admin") or next(iter(ctx.users.values()))
        regular_owner = ctx.users.get("demo_user") or owner
        curator = ctx.users.get("demo_moderator") or owner

        for index, item in enumerate(groups_mocks.MOCK_COLLECTIONS):
            is_editorial = bool(
                item.get("is_editorial", item.get("isEditorial", False))
            )
            group, _ = Group.objects.update_or_create(
                name=item["name"],
                defaults={
                    "slug": item["slug"],
                    "description": item.get("description", ""),
                    "owner": owner if is_editorial else regular_owner,
                    "curator": curator if is_editorial else None,
                    "is_editorial": is_editorial,
                    "order": index,
                    "image_url": (
                        item.get("cover") or item.get("imageUrl") or ""
                    ),
                    "saves_count": item.get("savesCount", 0),
                    "views_count": item.get("viewsCount", 0),
                },
            )
            AutoGroupRule.objects.filter(group=group).delete()
            category = str(item.get("category") or "").lower()
            selected = [
                channel
                for channel in ctx.channels
                if (channel.category or "").lower() == category
            ] or ctx.channels[:2]
            group.channels.set(selected)
            groups.append(group)

        demo_user = ctx.users.get("demo_user")
        if demo_user is not None:
            for group in groups[:2]:
                SavedCollection.objects.get_or_create(
                    user=demo_user, group=group
                )

    def summary(self, ctx: DemoSeedContext) -> str | None:
        group_names = [group["name"] for group in groups_mocks.MOCK_COLLECTIONS]
        groups_count = Group.objects.filter(name__in=group_names).count()
        saves_count = SavedCollection.objects.filter(
            user__username__in=users_mocks.DEMO_USERNAMES
        ).count()
        return f"Группы: {groups_count} | Сохранения: {saves_count}"
