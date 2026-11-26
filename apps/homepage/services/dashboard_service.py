import logging
from datetime import timedelta
from typing import Any, List, Optional, cast

from django.db.models import (
    Avg,
    Count,
    F,
    FloatField,
    IntegerField,
    OuterRef,
    Prefetch,
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
    Growth30dDTO,
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
from apps.parser.services.metrics import (
    average_reach as calc_average_reach,
)
from apps.parser.services.metrics import (
    engagement_rate,
    get_citation_index,
    growth_30d,
)
from apps.users.models import User
from mocks.landing import MOCK_KPIS
from mocks.parser import get_mock_channel

logger = logging.getLogger(__name__)


class DashboardService:
    def __init__(self, user: User) -> None:
        self.user = user

    def build(self) -> DashboardDTO:
        reference_time = timezone.now()
        channels_qs = self._get_channels_queryset(reference_time)

        stats = self._build_stats(channels_qs)
        channels = self._build_channels(channels_qs, reference_time)
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

    def _get_channels_queryset(
        self, reference_time
    ) -> QuerySet[TelegramChannel]:
        thirty_days_ago = reference_time - timedelta(days=30)

        reactions_sum_sq = (
            PostReaction.objects.filter(post=OuterRef("pk"))
            .values("post")
            .annotate(total=Sum("count"))
            .values("total")
        )

        avg_interactions_sq = (
            Post.objects.filter(channel=OuterRef("pk"))
            .annotate(
                tr_count=Coalesce(
                    Subquery(reactions_sum_sq, output_field=IntegerField()), 0
                )
            )
            .values("channel")
            .annotate(
                avg_int=Avg(F("comments_count") + F("forwards") + F("tr_count"))
            )
            .values("avg_int")
        )

        latest_stats_sq = ChannelStats.objects.filter(
            channel=OuterRef("pk")
        ).order_by("-parsed_at")

        stats_prefetch = Prefetch(
            "channelstats_set",
            queryset=ChannelStats.objects.filter(parsed_at__lte=thirty_days_ago)
            .only("participants_count", "parsed_at", "channel_id")
            .order_by("-parsed_at"),
            to_attr="historical_stats_list",
        )

        return (
            TelegramChannel.objects.filter(moderators__user=self.user)
            .distinct()
            .annotate(
                latest_growth_val=Subquery(
                    latest_stats_sq.values("daily_growth")[:1],
                    output_field=FloatField(),
                ),
                posts_count_val=Count("posts", distinct=True),
                avg_views_val=Avg("posts__views"),
                avg_interactions_val=Subquery(
                    avg_interactions_sq, output_field=FloatField()
                ),
                total_views_sum=Subquery(
                    Post.objects.filter(channel=OuterRef("pk"))
                    .values("channel")
                    .annotate(t=Sum("views"))
                    .values("t"),
                    output_field=IntegerField(),
                ),
            )
            .prefetch_related(stats_prefetch)
        )

    def _build_stats(self, qs: QuerySet[TelegramChannel]) -> StatsDTO:
        agg = qs.aggregate(
            c_count=Count("id", distinct=True),
            p_count=Count("posts", distinct=True),
        )
        ai_count = AIInsight.objects.filter(user=self.user).count()

        return StatsDTO(
            channels=agg["c_count"] or 0,
            posts=agg["p_count"] or 0,
            ai_suggestions=ai_count,
            days_left=self._get_subscription_days_left(),
        )

    def _build_channels(
        self, qs: QuerySet[TelegramChannel], reference_time: Any
    ) -> List[ChannelDTO]:
        result = []
        channels = list(qs[:5])

        for channel in cast(List[Any], channels):
            try:
                subscribers = channel.participants_count or 0
                posts_count = getattr(channel, "posts_count_val", 0) or 0
                avg_views = getattr(channel, "avg_views_val", 0.0) or 0.0
                total_views = getattr(channel, "total_views_sum", 0) or 0
                interactions = (
                    getattr(channel, "avg_interactions_val", 0.0) or 0.0
                )

                er_val = (
                    engagement_rate(int(interactions), int(avg_views))
                    if avg_views > 0
                    else 0.0
                )
                avg_reach_val = (
                    calc_average_reach(int(total_views), int(posts_count))
                    if posts_count > 0
                    else 0.0
                )

                history = getattr(channel, "historical_stats_list", [])
                past_stat = history[0] if history else None
                past_count = past_stat.participants_count if past_stat else None

                abs_growth, pct_growth = growth_30d(subscribers, past_count)

                try:
                    citation_idx = get_citation_index(channel) or 0.0
                except Exception:
                    citation_idx = 0.0

                result.append(
                    ChannelDTO(
                        name=channel.title,
                        subscribers=subscribers,
                        posts=posts_count,
                        views=int(avg_views),
                        engagement=round(er_val * 100, 2),
                        growth=round(pct_growth, 2),
                        er_percent=round(er_val * 100, 2),
                        average_reach=avg_reach_val,
                        citation_index=citation_idx,
                        growth_30d=Growth30dDTO(
                            abs=abs_growth, percent=round(pct_growth, 2)
                        ),
                        is_verified=bool(channel.is_verified),
                    )
                )
            except Exception as e:
                logger.error(
                    f"Failed to build DTO for channel {channel.id}: {e}"
                )
                continue

        return result

    def _build_insights(
        self, qs: QuerySet[TelegramChannel]
    ) -> List[InsightDTO]:
        insights_qs = AIInsight.objects.filter(
            user=self.user, is_read=False
        ).order_by("-created_at")[:5]

        if insights_qs.exists():
            return [
                InsightDTO(text=i.insight_text, type=i.insight_type, id=i.id)
                for i in insights_qs
            ]

        result = []
        for c in list(qs[:3]):
            latest_growth = getattr(c, "latest_growth_val", 0) or 0
            if latest_growth > 50:
                result.append(
                    InsightDTO(
                        text=f"Канал «{c.title}» растёт (+{latest_growth})",
                        type="positive",
                    )
                )

        avg_v = qs.aggregate(avg=Avg("posts__views"))["avg"] or 0
        if avg_v > 5000:
            result.append(
                InsightDTO(
                    text=f"Средние просмотры: {int(avg_v)}", type="positive"
                )
            )

        if not result:
            result.append(
                InsightDTO(text="Недостаточно данных для анализа", type="trend")
            )

        return result

    def _build_collections(self) -> List[CollectionDTO]:
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

    def build_page_props(self) -> dict[str, Any]:
        channels_qs = self._get_channels_queryset(timezone.now())
        channel = self._get_primary_channel(channels_qs)

        return {
            "channel": self._build_channel_card(channel),
            "kpis": self._build_page_kpis(channel),
            "growthData": self._build_growth_data(channel),
            "posts": self._build_page_posts(channel),
        }

    def _get_primary_channel(
        self, qs: QuerySet[TelegramChannel]
    ) -> Optional[Any]:
        return qs.order_by("-participants_count", "pk").first()

    def _build_channel_card(self, channel: Optional[Any]) -> dict[str, Any]:
        if not channel:
            return {}

        username = channel.username or ""
        if username and not username.startswith("@"):
            username = f"@{username}"

        mock_channel = get_mock_channel(channel.username) or {}

        subscribers = channel.participants_count or 0
        avg_views = getattr(channel, "avg_views_val", 0.0) or 0.0
        total_views = getattr(channel, "total_views_sum", 0) or 0
        interactions = getattr(channel, "avg_interactions_val", 0.0) or 0.0
        posts_count = getattr(channel, "posts_count_val", 0) or 0

        er_val = (
            engagement_rate(int(interactions), int(avg_views))
            if avg_views > 0
            else 0.0
        )
        avg_reach_val = (
            calc_average_reach(int(total_views), int(posts_count))
            if posts_count > 0
            else 0.0
        )

        growth_dto = self._get_growth_30d_dict(channel)

        return {
            "id": channel.channel_id,
            "name": channel.title,
            "username": username,
            "type": mock_channel.get("type") or "channel",
            "subscribers": subscribers,
            "category": channel.category or "",
            "verified": bool(channel.is_verified),
            "country": channel.country or "",
            "imageUrl": mock_channel.get("imageUrl") or "",
            "er_percent": round(er_val * 100, 2),
            "average_reach": avg_reach_val,
            "citation_index": get_citation_index(channel) or 0.0,
            "growth_30d": growth_dto,
        }

    def _build_page_kpis(self, channel: Optional[Any]) -> List[dict[str, Any]]:
        if not channel:
            return []

        subscribers = channel.participants_count or 0
        recent_stats = list(channel.channelstats_set.order_by("-parsed_at")[:2])
        previous = (
            recent_stats[1].participants_count
            if len(recent_stats) > 1
            else subscribers
        )

        delta = subscribers - previous
        percent_delta = round(delta / previous * 100, 2) if previous else 0.0

        avg_views = getattr(channel, "avg_views_val", 0.0) or 0.0
        total_views = getattr(channel, "total_views_sum", 0) or 0
        interactions = getattr(channel, "avg_interactions_val", 0.0) or 0.0
        posts_count = getattr(channel, "posts_count_val", 0) or 0

        er_val = (
            engagement_rate(int(interactions), int(avg_views))
            if avg_views > 0
            else 0.0
        )
        avg_reach = (
            calc_average_reach(int(total_views), int(posts_count))
            if posts_count > 0
            else 0.0
        )

        growth_dict = self._get_growth_30d_dict(channel)

        return [
            {
                "label": "Подписчики",
                "value": subscribers,
                "delta": delta,
                "percentDelta": percent_delta,
                "positive": delta >= 0,
            },
            self._merge_missing_kpi(
                {"label": "Ср. охват", "value": int(avg_reach)}, "Ср. охват"
            ),
            self._merge_missing_kpi(
                {"label": "ER", "value": round(er_val * 100, 1)}, "ER"
            ),
            self._merge_missing_kpi(
                {
                    "label": "Индекс цитирования",
                    "value": int(get_citation_index(channel) or 0),
                },
                "Индекс цитирования",
            ),
            self._merge_missing_kpi(
                {
                    "label": "Прирост (30д)",
                    "value": growth_dict["abs"],
                    "percentDelta": growth_dict["percent"],
                    "positive": growth_dict["abs"] >= 0,
                },
                "Прирост (30д)",
            ),
        ]

    def _get_growth_30d_dict(self, channel: Any) -> dict[str, Any]:
        """Вспомогательный метод, возвращающий DICT вместо DTO для JSON."""
        history = getattr(channel, "historical_stats_list", [])
        latest = history[0] if history else None
        if not latest:
            return {"abs": 0, "percent": 0.0}

        thirty_days_ago = latest.parsed_at - timedelta(days=30)
        past = (
            channel.channelstats_set.filter(parsed_at__lte=thirty_days_ago)
            .order_by("-parsed_at")
            .first()
        )

        abs_val, pct_val = growth_30d(
            latest.participants_count,
            past.participants_count if past else None,
        )
        return {"abs": abs_val, "percent": round(pct_val, 2)}

    @staticmethod
    def _merge_missing_kpi(
        db_kpi: dict[str, Any], label: str
    ) -> dict[str, Any]:
        mock_kpi = next(
            (item for item in MOCK_KPIS if item["label"] == label), None
        )
        if not mock_kpi:
            return db_kpi
        merged = dict(db_kpi)
        for key, value in mock_kpi.items():
            merged.setdefault(key, value)
        return merged

    def _build_growth_data(
        self, channel: Optional[Any]
    ) -> List[dict[str, Any]]:
        if not channel:
            return []
        stats = list(channel.channelstats_set.order_by("-parsed_at")[:30])
        return [
            {
                "date": s.parsed_at.strftime("%d.%m"),
                "подписчики": s.participants_count,
            }
            for s in reversed(stats)
        ]

    def _build_page_posts(self, channel: Optional[Any]) -> List[dict[str, Any]]:
        if not channel:
            return []
        posts = channel.posts.order_by("-published_at")[:4]
        return [
            {
                "title": p.text[:80] if p.text else "",
                "views": p.views,
                "reactions": p.total_reactions(),
                "forwards": p.forwards,
                "er": round(p.calculate_er() * 100, 1),
            }
            for p in posts
        ]

    def _get_subscription_days_left(self) -> int:
        return get_subscription(self.user).days_left
