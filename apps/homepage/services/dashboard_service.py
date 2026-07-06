from django.db.models import Avg, OuterRef, Subquery

from apps.group_channels.models import Group
from apps.homepage.dto.dashboard_dto import (
    ChannelDTO,
    CollectionDTO,
    DashboardDTO,
    InsightDTO,
    StatsDTO,
)
from apps.parser.models import AIInsight, ChannelStats, TelegramChannel


class DashboardService:
    def __init__(self, user):
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

    def _get_channels_queryset(self):
        latest_stats = ChannelStats.objects.filter(
            channel=OuterRef("pk")
        ).order_by("-parsed_at")

        return (
            TelegramChannel.objects.filter(moderators__user=self.user)
            .distinct()
            .annotate(
                latest_growth=Subquery(latest_stats.values("daily_growth")[:1])
            )
        )

    # ------------------------
    # Stats
    # ------------------------

    def _build_stats(self, qs):
        channels_count = qs.count()

        posts_count = sum(len(c.last_messages or []) for c in qs)

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

    def _build_channels(self, qs):
        result = []

        for c in qs[:5]:
            subscribers = c.participants_count or 0
            views = c.average_views or 0

            # ✔ корректный engagement
            engagement = (views / subscribers) * 100 if subscribers > 0 else 0

            # ✔ рост
            growth = c.latest_growth or 0

            growth_percent = (
                (growth / max(1, subscribers - growth)) * 100 if growth else 0
            )

            result.append(
                ChannelDTO(
                    name=c.title,
                    subscribers=subscribers,
                    posts=len(c.last_messages or []),
                    views=views,
                    engagement=round(engagement, 2),
                    growth=round(growth_percent, 2),
                )
            )

        return result

    # ------------------------
    # AI insights
    # ------------------------

    def _build_insights(self, qs):
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
            if c.latest_growth and c.latest_growth > 50:
                result.append(
                    InsightDTO(
                        text=f"Канал «{c.title}» растёт (+{c.latest_growth})",
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

    def _build_collections(self):
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

    def _get_subscription_days_left(self):
        profile = getattr(self.user, "partner_profile", None)
        if profile and profile.status == "active":
            return 30
        return 0
