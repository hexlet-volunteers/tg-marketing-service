from typing import Any

from django.http import HttpRequest, HttpResponse
from django.views.generic.base import View
from inertia import render as inertia_render


class AICabinetView(View):
    """AI-кабинет автора (Inertia: AICabinet).

    Идеи, инсайты и метрики пока моковые — на стороне frontend.
    """

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        return inertia_render(request, "AICabinet")
