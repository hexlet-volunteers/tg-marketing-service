from django.http import HttpRequest, HttpResponse
from django.views.generic.base import View
from inertia import render as inertia_render

from apps.legal.documents import LEGAL_DOCUMENTS


class LegalView(View):
    """
    Public legal page. Only document metadata is returned; document texts
    are static frontend content.

    InertiaJS component contract:
    [
        {
            "component": "Legal",
            "props": {
                "documents": {
                    "privacy": {"title": str, "updated_at": str},
                    "agreement": {"title": str, "updated_at": str},
                    "offer": {"title": str, "updated_at": str}
                }
            },
            "url": "/legal/"
        }
    ]
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return inertia_render(
            request,
            "Legal",
            props={
                "documents": LEGAL_DOCUMENTS,
            },
        )
