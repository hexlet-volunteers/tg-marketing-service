import math
from typing import Any, Optional, Tuple

from django.db.models import Count, F

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


def get_citation_index(channel: TelegramChannel) -> float:
    """
    Интерфейс для получения индекса цитируемости канала
    """
    return channel.citation_index


def _calculate_and_save_index(
    channel: TelegramChannel, repost_count: int, mention_count: int
) -> None:
    """
    Общая логика расчета и сохранения индекса.
    """
    new_index = compute_normalized_citation(repost_count, mention_count)
    if channel.citation_index != new_index:
        channel.citation_index = new_index
        channel.save(update_fields=["citation_index"])


def update_single_channel_citation_index(channel_id: int) -> None:
    """
    Точечный пересчет для одного канала.
    """
    try:
        channel = TelegramChannel.objects.get(channel_id=channel_id)
    except TelegramChannel.DoesNotExist:
        return

    # Считаем репосты
    repost_count = (
        Post.objects.filter(fwd_from=channel_id)
        .exclude(channel_id=F("fwd_from"))
        .count()
    )

    # Считаем упоминания (используем фильтр по списку)
    mention_count = 0
    # Ищем посты, где в поле mentions есть ID или username канала
    mention_posts = Post.objects.filter(mentions__contains=[str(channel_id)])
    if channel.username:
        mention_posts |= Post.objects.filter(
            mentions__contains=[channel.username.lstrip("@").casefold()]
        )

    for post in mention_posts.iterator():
        author_id = post.channel_id
        author_username = (
            post.channel.username.lstrip("@").casefold()
            if post.channel.username
            else None
        )

        for mention in post.mentions:
            m_key = (
                mention.lstrip("@").casefold()
                if isinstance(mention, str)
                else str(mention)
            )
            if not (m_key == author_username or m_key == str(author_id)):
                mention_count += 1

    _calculate_and_save_index(channel, repost_count, mention_count)


def update_channels_citation_indices() -> None:
    """
    Глобальный пересчет всех каналов.
    """
    # 1. Считаем репосты для всех сразу
    repost_stats = (
        Post.objects.filter(fwd_from__isnull=False)
        .exclude(channel_id=F("fwd_from"))
        .values("fwd_from")
        .annotate(count=Count("id"))
    )
    repost_map = {item["fwd_from"]: item["count"] for item in repost_stats}

    # 2. Считаем упоминания для всех
    mention_map: dict[Any, int] = {}
    posts = (
        Post.objects.filter(mentions__isnull=False)
        .exclude(mentions=[])
        .select_related("channel")
        .iterator()
    )
    for post in posts:
        author_id = post.channel_id
        author_username = (
            post.channel.username.lstrip("@").casefold()
            if post.channel.username
            else None
        )
        for mention in post.mentions:
            m_key = (
                mention.lstrip("@").casefold()
                if isinstance(mention, str)
                else str(mention)
            )
            if not (m_key == author_username or m_key == str(author_id)):
                mention_map[m_key] = mention_map.get(m_key, 0) + 1

    # 3. Применяем ко всем каналам через общую функцию
    for channel in TelegramChannel.objects.all():
        r_count = repost_map.get(channel.channel_id, 0)
        m_count = mention_map.get(str(channel.channel_id), 0)
        if channel.username:
            m_count += mention_map.get(
                channel.username.lstrip("@").casefold(), 0
            )

        _calculate_and_save_index(channel, r_count, m_count)
