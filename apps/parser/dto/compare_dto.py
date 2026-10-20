from typing import List

from pydantic import BaseModel, Field

from apps.parser.dto.channel_catalog_dto import ChannelCardDTO


class CompareMetricDTO(BaseModel):
    """Метрика сравнения каналов (страница Compare)."""

    key: str
    label: str


class CompareDTO(BaseModel):
    """Props страницы 'Compare' (/compare/).

    Пока отдаются моки из реестра apps/parser/mock_data.py;
    форматирование значений метрик остаётся на фронтенде.
    """

    metrics: List[CompareMetricDTO] = Field(default_factory=list)
    channels: List[ChannelCardDTO] = Field(default_factory=list)
