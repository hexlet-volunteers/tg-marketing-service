from typing import Any

from django.http import HttpRequest, HttpResponse
from django.views.generic.base import View

from apps.ai.services.ai_cabinet_service import AICabinetService
from config.renderers import render_inertia_from_dto


class AICabinetView(View):
    """AI-кабинет автора (Inertia: AICabinet).

    Данные собираются из AIInsight, Post, TelegramChannel и ChannelStats.
    """

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        dto = AICabinetService(request.user).build()

        return render_inertia_from_dto(
            request,
            "AICabinet",
            props=dto,
        )
