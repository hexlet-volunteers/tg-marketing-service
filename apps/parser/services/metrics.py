import math
from typing import Dict, Optional, Tuple

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
    """Нормализация через log1p."""
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
    """Сохраняет индекс в БД, если он изменился."""
    new_index = compute_normalized_citation(repost_count, mention_count)
    if channel.citation_index != new_index:
        channel.citation_index = new_index
        channel.save(update_fields=["citation_index"])


def _get_mention_counts() -> Dict[int, int]:
    """
    Единый хелпер для подсчета упоминаний.
    Возвращает словарь {channel_id: count_of_posts}.
    """
    mention_counts: Dict[int, int] = {}

    key_to_id: Dict[str, int] = {}
    for ch in TelegramChannel.objects.all():
        key_to_id[str(ch.channel_id)] = ch.channel_id
        if ch.username:
            key_to_id[ch.username.lstrip("@").casefold()] = ch.channel_id

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

        # Набор ID каналов, которые упомянуты в ЭТОМ посте
        mentioned_ids_in_post = set()

        for m in post.mentions:
            m_key = str(m).lstrip("@").casefold()

            # Пропускаем, если это автор поста (самоцитирование)
            if m_key == str(author_id) or m_key == author_username:
                continue

            # Находим, какому каналу принадлежит этот ключ
            target_id = key_to_id.get(m_key)
            if target_id and target_id != author_id:
                mentioned_ids_in_post.add(target_id)

        for ch_id in mentioned_ids_in_post:
            mention_counts[ch_id] = mention_counts.get(ch_id, 0) + 1

    return mention_counts


def update_single_channel_citation_index(channel_id: int) -> None:
    """
    Точечный пересчет для одного канала.
    """
    try:
        channel = TelegramChannel.objects.get(channel_id=channel_id)
    except TelegramChannel.DoesNotExist:
        return

    repost_count = (
        Post.objects.filter(fwd_from=channel.channel_id)
        .exclude(channel__channel_id=F("fwd_from"))
        .count()
    )

    all_mentions = _get_mention_counts()
    mention_count = all_mentions.get(channel.channel_id, 0)

    _calculate_and_save_index(channel, repost_count, mention_count)


def update_channels_citation_indices() -> None:
    """
    Глобальный пересчет всех каналов.
    """
    repost_stats = (
        Post.objects.filter(fwd_from__isnull=False)
        .exclude(channel__channel_id=F("fwd_from"))
        .values("fwd_from")
        .annotate(count=Count("id"))
    )
    repost_map = {item["fwd_from"]: item["count"] for item in repost_stats}

    mention_map = _get_mention_counts()

    for channel in TelegramChannel.objects.all().iterator():
        r_count = repost_map.get(channel.channel_id, 0)
        m_count = mention_map.get(channel.channel_id, 0)

        _calculate_and_save_index(channel, r_count, m_count)
