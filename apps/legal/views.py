from django.http import HttpRequest, HttpResponse
from django.views.generic.base import View
from inertia import render as inertia_render

LEGAL_DOCUMENTS = {
    "privacy": {
        "title": "Политика конфиденциальности",
        "updated_at": "2026-07-01",
    },
    "agreement": {
        "title": "Пользовательское соглашение",
        "updated_at": "2026-07-01",
    },
    "offer": {
        "title": "Публичная оферта",
        "updated_at": "2026-07-01",
    },
}


class LegalView(View):
    """
    Cтраница правовых документов сайта.

    Публичная страница, доступна без авторизации.
    Отдаёт только метаданные документов (заголовок, дата обновления).

    Документация компонентов для InertiaJS:
    [
        {
            "component": "название компонента",
            "props": { пропсы },
            "url": "url"
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
