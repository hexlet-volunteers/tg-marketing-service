"""Сборка props дашборда канала (Inertia: ``ChannelDashboard``).

Агрегация за период идёт из ``ChannelStats`` и ``Post``:
KPI считаются за выбранное окно и предыдущее окно такой же длины,
рост — по дням окна (пропуски переносятся вперёд).

Контракт — ``docs/inertia-contract.md``.
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

from django.db.models import Count, QuerySet, Sum
from django.utils import timezone

from apps.parser.dto.channel_dashboard_dto import (
    POST_TITLE_LIMIT,
    AdviceType,
    AiAdviceDTO,
    ChannelDashboardDTO,
    ChannelHeaderDTO,
    GrowthPointDTO,
    KpiDTO,
    KpiKey,
    LatestPostDTO,
)
from apps.parser.models import (
    AIInsight,
    ChannelStats,
    Post,
    PostReaction,
    TelegramChannel,
)
from apps.parser.services.metrics import engagement_rate
from apps.users.models import User

DASHBOARD_PERIODS = (7, 30, 90)
DEFAULT_PERIOD = 30

AI_ADVICE_LIMIT = 5
LATEST_POSTS_LIMIT = 10

ADVICE_TYPES: tuple[AdviceType, ...] = (
    "trend",
    "recommendation",
    "warning",
    "positive",
)

KPI_LABELS = {
    "subs": "Подписчики",
    "reach": "Ср. охват",
    "er": "ER",
    "citation": "Индекс цитирования",
}


def parse_dashboard_period(raw: Optional[str]) -> int:
    """Приводит ``?period=`` к одному из ``7/30/90``.

    Пустое, нечисловое или неподдерживаемое значение даёт 30.
    """
    try:
        period = int(raw or "")
    except (TypeError, ValueError):
        return DEFAULT_PERIOD
    return period if period in DASHBOARD_PERIODS else DEFAULT_PERIOD


def _window_bounds(period: int) -> tuple[datetime, datetime]:
    """Границы текущего окна и предыдущего окна той же длины.

    Текущее окно — ``period`` календарных дней, включая сегодняшний.
    """
    now = timezone.now()
    start = (now - timedelta(days=period - 1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    previous_start = start - timedelta(days=period)
    return start, previous_start


def _post_metrics(posts: QuerySet[Post]) -> Dict[str, float]:
    """Суммарные просмотры и ER по набору постов."""
    aggregate = posts.aggregate(
        posts=Count("id"),
        views=Sum("views"),
        comments=Sum("comments_count"),
        forwards=Sum("forwards"),
    )
    posts_count = int(aggregate["posts"] or 0)
    views = int(aggregate["views"] or 0)
    interactions = int(aggregate["comments"] or 0) + int(
        aggregate["forwards"] or 0
    )
    reactions = (
        PostReaction.objects.filter(post__in=posts).aggregate(
            total=Sum("count")
        )["total"]
        or 0
    )
    interactions += int(reactions)

    return {
        "posts": float(posts_count),
        "views": float(views),
        "er": engagement_rate(interactions, views),
    }


def _relative_delta(
    current: float, previous: Optional[float]
) -> tuple[float, float]:
    """Возвращает (delta, percentDelta); без базы — нули."""
    if previous is None or previous <= 0:
        return 0.0, 0.0
    delta = round(current - previous, 2)
    return delta, round(delta / previous * 100, 2)


def _latest_stats_value(
    channel: TelegramChannel, **filters: Any
) -> Optional[int]:
    """Последнее значение ``participants_count`` по фильтрам."""
    stat = (
        ChannelStats.objects.filter(channel=channel, **filters)
        .order_by("-parsed_at")
        .first()
    )
    return stat.participants_count if stat else None


def _build_kpis(channel: TelegramChannel, period: int) -> list[KpiDTO]:
    """KPI за период: подписчики, охват, ER и индекс цитирования.

    Дельты считаются к предыдущему окну такой же длины. Если данных
    для сравнения нет, дельта равна нулю.
    """
    start, previous_start = _window_bounds(period)
    now = timezone.now()

    current_posts = Post.objects.filter(
        channel=channel, published_at__gte=start, published_at__lte=now
    )
    previous_posts = Post.objects.filter(
        channel=channel,
        published_at__gte=previous_start,
        published_at__lt=start,
    )
    current = _post_metrics(current_posts)
    previous = _post_metrics(previous_posts)

    current_subs = _latest_stats_value(channel, parsed_at__gte=start)
    if current_subs is None:
        current_subs = channel.participants_count or 0
    previous_subs = _latest_stats_value(
        channel, parsed_at__gte=previous_start, parsed_at__lt=start
    )
    subs_delta, subs_pct = _relative_delta(
        float(current_subs),
        float(previous_subs) if previous_subs is not None else None,
    )

    if current["posts"]:
        reach = round(current["views"] / current["posts"], 2)
    else:
        reach = float(channel.average_views or 0)
    if current["posts"] and previous["posts"]:
        previous_reach = round(previous["views"] / previous["posts"], 2)
        reach_delta, reach_pct = _relative_delta(reach, previous_reach)
    else:
        reach_delta, reach_pct = 0.0, 0.0

    er = round(current["er"] * 100, 2) if current["posts"] else 0.0
    if current["posts"] and previous["posts"]:
        previous_er = previous["er"] * 100
        er_delta, er_pct = _relative_delta(er, previous_er)
    else:
        er_delta, er_pct = 0.0, 0.0

    citation = round(float(channel.citation_index or 0), 2)

    values: dict[KpiKey, tuple[float, float, float]] = {
        "subs": (float(current_subs), subs_delta, subs_pct),
        "reach": (reach, reach_delta, reach_pct),
        "er": (er, er_delta, er_pct),
        "citation": (citation, 0.0, 0.0),
    }
    return [
        KpiDTO(
            key=key,
            label=KPI_LABELS[key],
            value=value,
            delta=delta,
            percentDelta=percent_delta,
            positive=delta >= 0,
        )
        for key, (value, delta, percent_delta) in values.items()
    ]


def _build_growth(
    channel: TelegramChannel, period: int
) -> list[GrowthPointDTO]:
    """Ряд роста подписчиков: по точке на день окна (forward-fill).

    Если до начала окна статистики нет, ряд начинается с первой
    известной точки внутри окна: значения «из будущего» в начало
    окна не подставляются.
    """
    start, _ = _window_bounds(period)
    now = timezone.now()
    end_day = now.date()

    by_day: Dict[date, int] = {}
    stats = ChannelStats.objects.filter(
        channel=channel, parsed_at__gte=start, parsed_at__lte=now
    ).order_by("parsed_at")
    for stat in stats:
        by_day[stat.parsed_at.date()] = stat.participants_count

    anchor = (
        ChannelStats.objects.filter(channel=channel, parsed_at__lt=start)
        .order_by("-parsed_at")
        .first()
    )
    if not by_day and anchor is None:
        return []

    if anchor is not None:
        day = start.date()
        current = anchor.participants_count
    else:
        day = min(by_day)
        current = by_day[day]

    points: list[GrowthPointDTO] = []
    while day <= end_day:
        current = by_day.get(day, current)
        points.append(
            GrowthPointDTO(
                date=day.isoformat(), subscribers=max(0, int(current))
            )
        )
        day += timedelta(days=1)

    return points


def _public_username(channel: TelegramChannel) -> Optional[str]:
    """Username без ``@``; ``-`` и пустые значения — отсутствие username."""
    username = (channel.username or "").strip().lstrip("@").strip()
    if username == "-":
        return None
    return username or None


def _normalize_advice_type(value: str) -> AdviceType:
    """Приводит тип инсайта к контрактному; неизвестный — ``trend``."""
    if value in ADVICE_TYPES:
        return value
    return "trend"


def _build_ai_advice(
    channel: TelegramChannel, user: Optional[User]
) -> list[AiAdviceDTO]:
    """AI-советы текущего пользователя по каналу.

    Инсайты персональные (FK ``user``), поэтому анонимам и чужим
    пользователям они не отдаются.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return []

    insights = AIInsight.objects.filter(channel=channel, user=user).order_by(
        "-created_at"
    )[:AI_ADVICE_LIMIT]
    return [
        AiAdviceDTO(
            id=insight.pk,
            text=insight.insight_text,
            type=_normalize_advice_type(insight.insight_type),
            created_at=insight.created_at,
        )
        for insight in insights
    ]


def _build_latest_posts(channel: TelegramChannel) -> list[LatestPostDTO]:
    """Последние посты из ``last_messages`` со ссылками на посты.

    ``last_messages`` — свободный JSONField, поэтому типы полей
    проверяются: грязные записи не должны ронять страницу.
    """
    username = _public_username(channel)
    entries = [
        message
        for message in (channel.last_messages or [])
        if isinstance(message, dict)
        and isinstance(message.get("post_id"), int)
        and not isinstance(message.get("post_id"), bool)
        and message["post_id"] > 0
    ]
    entries.sort(key=lambda message: message["post_id"], reverse=True)

    posts: list[LatestPostDTO] = []
    for message in entries[:LATEST_POSTS_LIMIT]:
        post_id = int(message["post_id"])
        raw_text = message.get("post_text")
        text = raw_text if isinstance(raw_text, str) else ""
        raw_views = message.get("post_views")
        views = raw_views if isinstance(raw_views, int) else 0
        if views < 0:
            views = 0

        posts.append(
            LatestPostDTO(
                id=post_id,
                title=text[:POST_TITLE_LIMIT],
                views=views,
                url=(
                    f"https://t.me/{username}/{post_id}" if username else None
                ),
            )
        )
    return posts


def _build_header(channel: TelegramChannel) -> ChannelHeaderDTO:
    """Собирает шапку канала.

    Аватар — атрибут канала, а не пользователя. В ``TelegramChannel``
    поля для изображения пока нет (``photo_url`` закомментирован),
    поэтому ``avatar`` равен ``None``: frontend рисует градиент с
    инициалами, как в дизайн-макете.
    """
    username = _public_username(channel)

    return ChannelHeaderDTO(
        title=channel.title,
        username=f"@{username}" if username else None,
        avatar=None,
        category=channel.category,
        country=channel.country,
        verified=channel.is_verified,
    )


def build_channel_dashboard(
    channel: TelegramChannel,
    period: int,
    user: Optional[User] = None,
) -> ChannelDashboardDTO:
    """Собирает props страницы ``ChannelDashboard`` для канала за период."""
    if period not in DASHBOARD_PERIODS:
        raise ValueError(
            f"Период должен быть одним из {DASHBOARD_PERIODS}, "
            f"получено {period}"
        )

    return ChannelDashboardDTO(
        header=_build_header(channel),
        period=period,
        kpis=_build_kpis(channel, period),
        growth=_build_growth(channel, period),
        ai_advice=_build_ai_advice(channel, user),
        latest_posts=_build_latest_posts(channel),
    )
