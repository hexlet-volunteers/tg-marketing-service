from datetime import timedelta
from typing import Any

from django.db.models import Avg, Count, F, OuterRef, QuerySet, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.billing.services.subscription_service import get_subscription
from apps.group_channels.models import Group
from apps.homepage.dto.dashboard_dto import (
    ChannelDTO,
    CollectionDTO,
    DashboardDTO,
    InsightDTO,
    StatsDTO,
)
from apps.parser.models import AIInsight, ChannelStats, TelegramChannel
from apps.parser.services.metrics import engagement_rate, growth_30d
from apps.users.models import User


class DashboardService:
    def __init__(self, user: User) -> None:
        self.user = user

    # 🔹 публичный метод
    def build(self) -> DashboardDTO:
        channels_qs = self._get_channels_queryset()

        stats = self._build_stats(channels_qs)
        channels = self._build_channels(channels_qs)
        insights = self._build_insights(channels_qs)
        collections = self._build_collections()
        quick_actions = ["Добавить канал", "Экспорт данных", "Настройки"]

        return DashboardDTO(
            stats=stats,
            channels=channels,
            ai_insights=insights,
            collections=collections,
            quick_actions=quick_actions,
        )

    # ------------------------
    # QuerySet
    # ------------------------

    def _get_channels_queryset(self) -> QuerySet[TelegramChannel]:
        latest_stats = ChannelStats.objects.filter(
            channel=OuterRef("pk")
        ).order_by("-parsed_at")

        return (
            TelegramChannel.objects.filter(moderators__user=self.user)
            .distinct()
            .annotate(
                latest_growth=Subquery(latest_stats.values("daily_growth")[:1]),
                posts_count=Count("posts", distinct=True),
                avg_views=Avg("posts__views"),
                # Среднее количество взаимодействий
                avg_interactions=Avg(
                    F("posts__comments_count")
                    + F("posts__forwards")
                    + Coalesce(F("posts__postsreaction__count"), 0)
                ),
            )
        )

    # ------------------------
    # Stats
    # ------------------------

    def _build_stats(self, qs: QuerySet[TelegramChannel]) -> StatsDTO:
        channels_count = qs.count()

        posts_count = (
            qs.aggregate(total_posts=Count("posts"))["total_posts"] or 0
        )

        ai_count = AIInsight.objects.filter(user=self.user).count()

        return StatsDTO(
            channels=channels_count,
            posts=posts_count,
            ai_suggestions=ai_count,
            days_left=self._get_subscription_days_left(),
        )

    # ------------------------
    # Channels
    # ------------------------

    def _build_channels(
        self, qs: QuerySet[TelegramChannel]
    ) -> list[ChannelDTO]:
        """
        Формирует список каналов с использованием чистых функций метрик.
        """
        result = []
        thirty_days_ago = timezone.now() - timedelta(days=30)

        for c in qs[:5]:
            channel: Any = c
            subscribers = channel.participants_count or 0
            views = channel.average_views or 0
            interactions = channel.avg_interactions or 0
            er = engagement_rate(interactions, views)

            # Данные для Growth 30d
            past_stat = (
                channel.channelstats_set.filter(parsed_at__lte=thirty_days_ago)
                .order_by("-parsed_at")
                .first()
            )

            current_count = channel.participants_count
            past_count = past_stat.participants_count if past_stat else None

            _, growth_pct = growth_30d(current_count, past_count)

            result.append(
                ChannelDTO(
                    name=channel.title,
                    subscribers=subscribers,
                    posts=channel.posts_count,
                    views=views,
                    engagement=round(er * 100, 2),
                    growth=round(growth_pct, 2),
                    is_verified=channel.is_verified,
                )
            )

        return result

    # ------------------------
    # AI insights
    # ------------------------

    def _build_insights(
        self, qs: QuerySet[TelegramChannel]
    ) -> list[InsightDTO]:
        insights_qs = AIInsight.objects.filter(
            user=self.user, is_read=False
        ).order_by("-created_at")[:5]

        if insights_qs.exists():
            return [
                InsightDTO(text=i.insight_text, type=i.insight_type, id=i.id)
                for i in insights_qs
            ]

        # fallback генерация
        result = []

        for c in qs[:3]:
            latest_growth = getattr(c, "latest_growth", 0) or 0
            if latest_growth > 50:
                result.append(
                    InsightDTO(
                        text=f"Канал «{c.title}» растёт (+{latest_growth})",
                        type="positive",
                    )
                )

        avg_views = qs.aggregate(avg=Avg("average_views"))["avg"]

        if avg_views and avg_views > 5000:
            result.append(
                InsightDTO(
                    text=f"Средние просмотры: {int(avg_views)}", type="positive"
                )
            )

        if not result:
            result.append(
                InsightDTO(text="Недостаточно данных для анализа", type="trend")
            )

        return result

    # ------------------------
    # Collections
    # ------------------------

    def _build_collections(self) -> list[CollectionDTO]:
        groups = Group.objects.filter(owner=self.user)

        result = [
            CollectionDTO(
                name=g.name,
                channels_count=g.channels.count(),
                slug=g.slug,
                description=g.description,
                is_auto=False,
            )
            for g in groups
        ]

        if not result:
            result.append(
                CollectionDTO(
                    name="Мои каналы",
                    channels_count=TelegramChannel.objects.filter(
                        moderators__user=self.user
                    ).count(),
                    slug="my-channels",
                    description="Все каналы",
                    is_auto=False,
                )
            )

        return result

    # ------------------------
    # Utils
    # ------------------------

    def _get_subscription_days_left(self) -> int:
        return get_subscription(self.user).days_left
