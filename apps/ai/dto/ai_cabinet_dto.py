from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AICabinetDTO(BaseModel):
    """Props страницы 'AICabinet' (/ai-cabinet/).

    Пока пустая заглушка: идеи, инсайты и метрики рендерятся
    на фронтенде из моков. Имена полей повторяют контракт props.
    """

    ideas: List[Dict[str, Any]] = Field(default_factory=list)
    insights: List[Dict[str, Any]] = Field(default_factory=list)
    competitors: List[Dict[str, Any]] = Field(default_factory=list)
    heatMapData: Dict[str, Any] = Field(default_factory=dict)
