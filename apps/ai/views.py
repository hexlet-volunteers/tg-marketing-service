from typing import Any

from django.http import HttpRequest, HttpResponse
from django.views.generic.base import View

from apps.ai.dto.ai_cabinet_dto import (
    AICabinetDTO,
    CompetitorDTO,
    IdeaDTO,
    InsightDTO,
)
from apps.ai.mock_data import (
    MOCK_COMPETITORS,
    MOCK_HEAT_MAP,
    MOCK_IDEAS,
    MOCK_INSIGHTS,
)
from config.renderers import render_inertia_from_dto


class AICabinetView(View):
    """AI-кабинет автора (Inertia: AICabinet).

    Пока отдаются моки из реестра apps/ai/mock_data.py;
    данные БД подключатся позже (см. docs/inertia-contract.md).
    """

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        dto = AICabinetDTO(
            ideas=[IdeaDTO(**idea) for idea in MOCK_IDEAS],
            insights=[InsightDTO(**insight) for insight in MOCK_INSIGHTS],
            competitors=[
                CompetitorDTO(**competitor) for competitor in MOCK_COMPETITORS
            ],
            heatMapData=MOCK_HEAT_MAP,
        )

        return render_inertia_from_dto(
            request,
            "AICabinet",
            props=dto,
        )
