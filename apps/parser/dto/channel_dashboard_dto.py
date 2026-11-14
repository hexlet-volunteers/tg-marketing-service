"""DTO дашборда канала (Inertia: ``ChannelDashboard``).

Контракт зафиксирован в ``docs/inertia-contract.md``, серверная сборка —
``apps/parser/services/channel_dashboard.py``.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, computed_field

KpiKey = Literal["subs", "reach", "er", "citation"]
"""Ключи KPI дашборда — фиксированный набор экрана."""

AdviceType = Literal["trend", "recommendation", "warning", "positive"]
"""Типы AI-советов — соответствуют ``AIInsight.insight_type``."""

POST_TITLE_LIMIT = 300
"""Максимальная длина фрагмента текста поста в props."""


class ChannelHeaderDTO(BaseModel):
    """Шапка канала: название, username, аватар, категория, страна."""

    title: str
    username: Optional[str] = None
    avatar: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    verified: bool = False


class KpiDTO(BaseModel):
    """KPI за период и его дельты к предыдущему окну.

    ``delta`` — абсолютное изменение, ``percentDelta`` — относительное
    изменение в процентах. ``delta_pct`` — alias для контракта смежных
    задач (#252/#259), сериализуется тем же значением.
    """

    key: KpiKey
    label: str
    value: float = 0.0
    delta: float = 0.0
    percentDelta: float = 0.0
    positive: bool = True

    @computed_field  # type: ignore[prop-decorator]
    @property
    def delta_pct(self) -> float:
        """Относительная дельта в процентах (alias ``percentDelta``)."""
        return self.percentDelta


class GrowthPointDTO(BaseModel):
    """Точка временного ряда роста подписчиков (AreaChart)."""

    date: str
    subscribers: int = Field(ge=0)


class AiAdviceDTO(BaseModel):
    """AI-совет (``AIInsight``) по каналу для текущего пользователя."""

    id: int
    text: str
    type: AdviceType
    created_at: datetime


class LatestPostDTO(BaseModel):
    """Последний пост канала из ``last_messages`` со ссылкой на пост."""

    id: int
    title: str = ""
    views: int = Field(ge=0)
    url: Optional[str] = None


class ChannelDashboardDTO(BaseModel):
    """Props страницы ``ChannelDashboard`` (``GET /parser/<pk>/``)."""

    header: ChannelHeaderDTO
    period: int
    kpis: List[KpiDTO] = Field(default_factory=list)
    growth: List[GrowthPointDTO] = Field(default_factory=list)
    ai_advice: List[AiAdviceDTO] = Field(default_factory=list)
    latest_posts: List[LatestPostDTO] = Field(default_factory=list)
