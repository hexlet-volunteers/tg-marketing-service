from typing import Any

from django.http import HttpRequest, HttpResponse
from django.views.generic.base import View

from apps.ai.dto.ai_cabinet_dto import AICabinetDTO
from config.renderers import render_inertia_from_dto


class AICabinetView(View):
    """AI-кабинет автора (Inertia: AICabinet).

    Идеи, инсайты и метрики пока моковые — на стороне frontend.
    """

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        return render_inertia_from_dto(
            request,
            "AICabinet",
            props=AICabinetDTO(),
            exclude_unset=True,
        )
