import math
from typing import Any, Optional, Tuple

from django.db.models import Count

from apps.parser.models import Post, TelegramChannel


def engagement_rate(interactions: int, views: int) -> float:
    """
    Вычисляет ER: (reactions + comments + forwards) / views.
    """
    if views <= 0:
        return 0.0
    return round(interactions / views, 4)


def average_reach(total_reach: int, count: int) -> float:
    """
    Вычисляет средний охват.
    """
    if count <= 0:
        return 0.0
    return round(total_reach / count, 2)


def growth_30d(
    current_count: int, past_count: Optional[int]
) -> Tuple[int, float]:
    """
    Вычисляет дельту прироста за 30 дней.
    Возвращает кортеж (абсолютное значение, процентное значение).

    Если данных о прошлом (past_count) нет, возвращает (0, 0.0),
    так как прирост невозможно вычислить.
    """
    if past_count is None or past_count <= 0:
        return 0, 0.0

    diff = current_count - past_count

    percentage = (diff / past_count) * 100
    return diff, round(percentage, 2)


def compute_normalized_citation(
    reposts_count: int, mentions_count: int
) -> float:
    """
    Детерминированная нормализация.
    """
    total = reposts_count + mentions_count
    return round(math.log1p(total), 4)


def update_channels_citation_indices() -> None:
    # репосты (fwd_from)
    repost_stats = (
        Post.objects.filter(fwd_from__isnull=False)
        .values("fwd_from")
        .annotate(count=Count("id"))
    )
    repost_map = {
        int(item["fwd_from"]): item["count"]
        for item in repost_stats
        if item["fwd_from"]
    }

    # проход по всем постам с упоминаниями
    mention_map: dict[Any, int] = {}
    for post in (
        Post.objects.filter(mentions__isnull=False)
        .exclude(mentions=[])
        .iterator()
    ):
        for m in post.mentions:
            m_key = m
            if isinstance(m, str):
                m_key = m.lstrip("@")

            try:
                m_key = int(m_key)
            except (ValueError, TypeError):
                pass

            mention_map[m_key] = mention_map.get(m_key, 0) + 1

    channels = TelegramChannel.objects.all()
    for channel in channels:
        r_count = repost_map.get(channel.channel_id, 0)

        m_count = mention_map.get(channel.channel_id, 0)
        if channel.username:
            m_count += mention_map.get(channel.username.lstrip("@"), 0)

        new_index = compute_normalized_citation(r_count, m_count)

        if channel.citation_index != new_index:
            channel.citation_index = new_index
            channel.save(update_fields=["citation_index"])
