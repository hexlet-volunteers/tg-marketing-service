from django.http import HttpRequest, HttpResponse
from django.views.generic.base import View
from inertia import render as inertia_render

from apps.legal.documents import LEGAL_DOCUMENTS


class LegalView(View):
    """Public page with legal document metadata."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return inertia_render(
            request,
            "Legal",
            props={
                "documents": LEGAL_DOCUMENTS,
            },
        )
