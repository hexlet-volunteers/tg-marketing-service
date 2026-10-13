from typing import List

from pydantic import BaseModel, Field

from apps.parser.dto.channel_catalog_dto import ChannelCardDTO


class CompareMetricDTO(BaseModel):
    """Метрика сравнения каналов (страница Compare)."""

    key: str
    label: str


class CompareDTO(BaseModel):
    """Props страницы 'Compare' (/compare/).

    Пока пустая заглушка: метрики и каналы рендерятся на фронтенде из моков.
    """

    metrics: List[CompareMetricDTO] = Field(default_factory=list)
    channels: List[ChannelCardDTO] = Field(default_factory=list)
