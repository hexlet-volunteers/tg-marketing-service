from typing import List

from pydantic import BaseModel, Field

from apps.parser.dto.channel_catalog_dto import ChannelCardDTO


class CompareMetricDTO(BaseModel):
    """Метрика сравнения каналов (страница Compare)."""

    key: str
    label: str


class CompareDTO(BaseModel):
    """Props страницы 'Compare' (/compare/).

    Каналы берутся из БД с fallback полей из mocks/parser.py;
    определения метрик приходят из мока, форматирование — на фронтенде.
    """

    metrics: List[CompareMetricDTO] = Field(default_factory=list)
    channels: List[ChannelCardDTO] = Field(default_factory=list)
