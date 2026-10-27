from datetime import timedelta
from typing import Any

from django.db.models import (
    Avg,
    Count,
    F,
    IntegerField,
    OuterRef,
    QuerySet,
    Subquery,
    Sum,
)
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
from apps.parser.models import (
    AIInsight,
    ChannelStats,
    Post,
    PostReaction,
    TelegramChannel,
)
from apps.parser.services.metrics import engagement_rate, growth_30d
from apps.users.models import User
from mocks.landing import MOCK_KPIS
from mocks.parser import get_mock_channel


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
        """
        Иерархия OuterRef:
        1. reactions_sum_subquery ссылается на Post
        2. avg_interactions_subquery ссылается на TelegramChannel
        """

        # подзапрос суммы реакций конкретного поста
        reactions_sum_subquery = (
            PostReaction.objects.filter(post=OuterRef("pk"))
            .values("post")
            .annotate(total=Sum("count"))
            .values("total")
        )

        # подзапрос среднего взаимодействия по всем постам конкретного канала
        avg_interactions_subquery = (
            Post.objects.filter(channel=OuterRef("pk"))
            .annotate(
                tr_count=Coalesce(
                    Subquery(
                        reactions_sum_subquery, output_field=IntegerField()
                    ),
                    0,
                )
            )
            .values("channel")
            .annotate(
                avg_int=Avg(F("comments_count") + F("forwards") + F("tr_count"))
            )
            .values("avg_int")
        )

        # Подзапрос для получения последнего значения роста
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
                avg_interactions=Subquery(
                    avg_interactions_subquery, output_field=IntegerField()
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
    # Page props (FE dashboard)
    # ------------------------

    def build_page_props(self) -> dict[str, Any]:
        """Собирает FE-пропсы из БД, дополняя отсутствующие поля моками."""
        channel = self._get_primary_channel()

        return {
            "channel": self._build_channel_card(channel),
            "kpis": self._build_page_kpis(channel),
            "growthData": self._build_growth_data(channel),
            "posts": self._build_page_posts(channel),
        }

    def _get_primary_channel(self) -> TelegramChannel | None:
        return (
            TelegramChannel.objects.filter(moderators__user=self.user)
            .order_by("-participants_count", "pk")
            .first()
        )

    def _build_channel_card(
        self, channel: TelegramChannel | None
    ) -> dict[str, Any]:
        if channel is None:
            return {}

        username = channel.username or ""
        if username and not username.startswith("@"):
            username = f"@{username}"
        mock_channel = get_mock_channel(channel.username) or {}

        return {
            "id": channel.channel_id,
            "name": channel.title,
            "username": username,
            "type": mock_channel.get("type") or "channel",
            "subscribers": channel.participants_count or 0,
            "category": channel.category or "",
            "verified": channel.is_verified,
            "country": channel.country or "",
            "imageUrl": mock_channel.get("imageUrl") or "",
            "er": round(float(channel.citation_index or 0), 2),
            "growth30d": self._get_channel_growth_30d(channel),
        }

    def _build_page_kpis(
        self, channel: TelegramChannel | None
    ) -> list[dict[str, Any]]:
        if channel is None:
            return []

        recent_stats = list(channel.channelstats_set.order_by("-parsed_at")[:2])
        subscribers = channel.participants_count or 0
        previous = (
            recent_stats[1].participants_count
            if len(recent_stats) > 1
            else subscribers
        )
        delta = subscribers - previous
        percent_delta = round(delta / previous * 100, 2) if previous else 0.0

        aggregate = channel.posts.aggregate(
            total_views=Sum("views"),
            total_forwards=Sum("forwards"),
            total_comments=Sum("comments_count"),
        )
        total_views = aggregate["total_views"] or 0
        total_interactions = (
            (aggregate["total_forwards"] or 0)
            + (aggregate["total_comments"] or 0)
            + (
                PostReaction.objects.filter(post__channel=channel).aggregate(
                    total=Sum("count")
                )["total"]
                or 0
            )
        )
        er = engagement_rate(int(total_interactions), int(total_views)) * 100
        average_reach = channel.average_views or (
            round(total_views / channel.posts.count())
            if channel.posts.exists()
            else 0
        )
        citation_index = int(round(float(channel.citation_index or 0)))

        return [
            {
                "label": "Подписчики",
                "value": subscribers,
                "delta": delta,
                "percentDelta": percent_delta,
                "positive": delta >= 0,
            },
            self._merge_missing_kpi(
                {"label": "Ср. охват", "value": int(average_reach)},
                "Ср. охват",
            ),
            self._merge_missing_kpi(
                {"label": "ER", "value": round(er, 1)},
                "ER",
            ),
            self._merge_missing_kpi(
                {
                    "label": "Индекс цитирования",
                    "value": citation_index,
                },
                "Индекс цитирования",
            ),
        ]

    @staticmethod
    def _merge_missing_kpi(
        db_kpi: dict[str, Any],
        label: str,
    ) -> dict[str, Any]:
        """Дополняет KPI полями, которых нет в моделях, из мока."""
        mock_kpi = next(
            (item for item in MOCK_KPIS if item["label"] == label),
            None,
        )
        if mock_kpi is None:
            return db_kpi

        merged = dict(db_kpi)
        for key, value in mock_kpi.items():
            merged.setdefault(key, value)
        return merged

    def _build_growth_data(
        self, channel: TelegramChannel | None
    ) -> list[dict[str, Any]]:
        if channel is None:
            return []

        stats = list(channel.channelstats_set.order_by("-parsed_at")[:30])
        return [
            {
                "date": stat.parsed_at.strftime("%d.%m"),
                "подписчики": stat.participants_count,
            }
            for stat in reversed(stats)
        ]

    def _build_page_posts(
        self, channel: TelegramChannel | None
    ) -> list[dict[str, Any]]:
        if channel is None:
            return []

        posts = channel.posts.order_by("-published_at").prefetch_related(
            "reactions"
        )[:4]
        return [
            {
                "title": post.text[:80],
                "views": post.views,
                "reactions": post.total_reactions(),
                "forwards": post.forwards,
                "er": round(post.calculate_er() * 100, 1),
            }
            for post in posts
        ]

    def _get_channel_growth_30d(self, channel: TelegramChannel) -> float:
        latest = channel.channelstats_set.order_by("-parsed_at").first()
        if latest is None:
            return 0.0

        thirty_days_ago = latest.parsed_at - timedelta(days=30)
        past = (
            channel.channelstats_set.filter(parsed_at__lte=thirty_days_ago)
            .order_by("-parsed_at")
            .first()
        )
        _, growth_pct = growth_30d(
            latest.participants_count,
            past.participants_count if past else None,
        )
        return growth_pct

    # ------------------------
    # Utils
    # ------------------------

    def _get_subscription_days_left(self) -> int:
        return get_subscription(self.user).days_left
