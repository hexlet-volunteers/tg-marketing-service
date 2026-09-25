from typing import Optional, Tuple


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
    """
    if past_count is None or past_count <= 0:
        return current_count, 0.0

    diff = current_count - past_count
    percentage = (diff / past_count) * 100
    return diff, round(percentage, 2)
