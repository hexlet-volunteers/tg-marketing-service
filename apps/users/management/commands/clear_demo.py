from __future__ import annotations

from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.billing.models import Plan, Subscription
from apps.blog.models import BlogArticle
from apps.group_channels.models import AutoGroupRule, Group, SavedCollection
from apps.homepage.models import HomePageComponent
from apps.parser.models import (
    AIInsight,
    ChannelModerator,
    ChannelStats,
    Post,
    PostReaction,
    TelegramChannel,
)
from apps.users.demo.constants import DEMO_CHANNEL_ID_MIN
from apps.users.models import User
from apps.users.roles import Role, UserRoleHistory
from mocks.blog import ARTICLES
from mocks.groups import MOCK_COLLECTIONS
from mocks.landing import LANDING_COMPONENTS
from mocks.users import DEMO_USERNAMES, ROLE_LABELS

DEMO_GROUP_NAMES = [group["name"] for group in MOCK_COLLECTIONS]
DEMO_ARTICLE_SLUGS = [article["slug"] for article in ARTICLES]
DEMO_COMPONENT_TYPES = [
    component["component_type"] for component in LANDING_COMPONENTS
]


class Command(BaseCommand):
    help = "Удаляет демо-данные, созданные командой seed_demo."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--force",
            action="store_true",
            help="Разрешить запуск вне DEBUG-режима.",
        )
        parser.add_argument(
            "--keep-roles",
            action="store_true",
            help="Не удалять демо-роли.",
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        if not settings.DEBUG and not options.get("force"):
            raise CommandError(
                "Команда clear_demo доступна только в DEBUG-режиме. "
                "Используйте --force для принудительного запуска."
            )

        summary = self._clear(keep_roles=options.get("keep_roles", False))
        self.stdout.write(self.style.SUCCESS(summary))

    def _clear(self, keep_roles: bool = False) -> str:
        # Reactions first
        PostReaction.objects.filter(
            post__channel__channel_id__gte=DEMO_CHANNEL_ID_MIN
        ).delete()
        Post.objects.filter(
            channel__channel_id__gte=DEMO_CHANNEL_ID_MIN
        ).delete()
        ChannelStats.objects.filter(
            channel__channel_id__gte=DEMO_CHANNEL_ID_MIN
        ).delete()
        ChannelModerator.objects.filter(
            channel__channel_id__gte=DEMO_CHANNEL_ID_MIN
        ).delete()

        # AI insights by demo users or channels
        AIInsight.objects.filter(user__username__in=DEMO_USERNAMES).delete()
        AIInsight.objects.filter(
            channel__channel_id__gte=DEMO_CHANNEL_ID_MIN
        ).delete()

        # Groups/saves/rules
        SavedCollection.objects.filter(
            group__name__in=DEMO_GROUP_NAMES
        ).delete()
        AutoGroupRule.objects.filter(group__name__in=DEMO_GROUP_NAMES).delete()
        Group.objects.filter(name__in=DEMO_GROUP_NAMES).delete()
        Group.objects.filter(owner__username__in=DEMO_USERNAMES).delete()
        Group.objects.filter(curator__username__in=DEMO_USERNAMES).delete()

        # Blog articles from seed
        BlogArticle.objects.filter(slug__in=DEMO_ARTICLE_SLUGS).delete()
        # Also remove if they came from demo author
        BlogArticle.objects.filter(author__username__in=DEMO_USERNAMES).delete()

        # Homepage components seeded from mocks
        HomePageComponent.objects.filter(
            component_type__in=DEMO_COMPONENT_TYPES
        ).delete()

        # Channels
        TelegramChannel.objects.filter(
            channel_id__gte=DEMO_CHANNEL_ID_MIN
        ).delete()

        # Roles history and roles
        if not keep_roles:
            UserRoleHistory.objects.filter(
                user__username__in=DEMO_USERNAMES
            ).delete()
            role_codes = list(ROLE_LABELS.keys())
            used_codes = set(
                UserRoleHistory.objects.exclude(
                    end_date__isnull=False
                ).values_list("role__code", flat=True)
            )
            for code in role_codes:
                if code in used_codes:
                    continue
                Role._default_manager.filter(code=code).delete()

        users = User.objects.filter(username__in=DEMO_USERNAMES)
        user_count = users.count()
        Subscription.objects.filter(user__in=users).delete()
        users.delete()

        return self._print_summary(user_count)

    def _print_summary(self, users_before: int) -> str:
        demo_channels = TelegramChannel.objects.filter(
            channel_id__gte=DEMO_CHANNEL_ID_MIN
        )
        components = HomePageComponent.objects.filter(
            component_type__in=DEMO_COMPONENT_TYPES
        )
        counts = {
            "Пользователи": User.objects.filter(
                username__in=DEMO_USERNAMES
            ).count(),
            "Каналы": demo_channels.count(),
            "Посты": Post.objects.filter(channel__in=demo_channels).count(),
            "Статистика": ChannelStats.objects.filter(
                channel__in=demo_channels
            ).count(),
            "Группы": Group.objects.filter(name__in=DEMO_GROUP_NAMES).count(),
            "Сохранения": SavedCollection.objects.filter(
                group__name__in=DEMO_GROUP_NAMES
            ).count(),
            "AI-инсайты": AIInsight.objects.filter(
                user__username__in=DEMO_USERNAMES
            ).count(),
            "Главная": components.count(),
            "Тарифы": Plan.objects.count(),
            "Статьи блога": BlogArticle.objects.filter(
                slug__in=DEMO_ARTICLE_SLUGS
            ).count(),
        }
        deleted = f"Удалено пользователей: {users_before}"
        parts = [f"{label}: {value}" for label, value in counts.items()]
        parts.append(deleted)
        return " | ".join(parts)
