from typing import Dict, List, Literal

from pydantic import BaseModel, Field


class IdeaDTO(BaseModel):
    """Идея поста в AI-кабинете."""

    title: str
    reason: str
    scope: int = Field(ge=0)
    date: str


class InsightDTO(BaseModel):
    """Инсайт недели; иконка/цвет выводятся на фронтенде по type."""

    type: Literal["recommendation", "trend", "warning", "positive"]
    text: str


class CompetitorDTO(BaseModel):
    """Конкурент в AI-кабинете."""

    name: str
    er: float
    delta: float


class AICabinetDTO(BaseModel):
    """Props страницы 'AICabinet' (/ai-cabinet/).

    Инсайты берутся из AIInsight, остальные поля — из мок-реестра
    mocks/ai.py, пока нет соответствующих данных в БД.
    """

    ideas: List[IdeaDTO] = Field(default_factory=list)
    insights: List[InsightDTO] = Field(default_factory=list)
    competitors: List[CompetitorDTO] = Field(default_factory=list)
    heatMapData: Dict[str, Dict[str, int]] = Field(default_factory=dict)
