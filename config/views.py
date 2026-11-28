from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import View
from inertia import render as inertia_render

from apps.billing.models import Plan
from apps.homepage.models import HomePageComponent


class IndexView(View):
    """
    Главная страница сайта.

    Авторизованные пользователи перенаправляются на /dashboard/

    Документация компонентов для InertiaJS:
    [
        {
            "component": "название компонента",
            "props": { пропсы },
            "url": "url"
        }
    ]
    """

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        # Если пользователь авторизован - редирект на дашборд
        if request.user.is_authenticated:
            return redirect("homepage:dashboard")

        # Получаем все активные компоненты, сортируем по порядку
        components = HomePageComponent.objects.filter(is_active=True).order_by(
            "order"
        )

        # Формируем данные для фронтенда в правильном формате
        components_data = []
        for component in components:
            # Базовые пропсы из модели
            base_props = {
                "id": component.id,
                "title": component.title,
                "type": component.component_type,
                "order": component.order,
            }

            # Добавляем JSON-содержимое в пропсы
            # (распаковываем content)
            # ВАЖНО: эта операция должна быть ВНУТРИ цикла
            # для каждого компонента
            component_props = {**base_props, **component.content}

            # Добавляем компонент в итоговый массив в нужном формате
            components_data.append(
                {
                    "component": component.component_type,
                    "props": component_props,
                    "url": request.path,
                }
            )

        page_props = {
            "components": components_data,
            "tariffs": [
                plan.to_tariff_payload() for plan in Plan.objects.all()
            ],
            "stats": [
                {"value": "2.4M", "label": "каналов в базе"},
                {"value": "18 млрд", "label": "проанализ. постов"},
                {"value": "120K", "label": "авторов"},
            ],
        }

        # коментируем до изменеий в UserRegister
        # page_props = {
        #    'components': components_data,
        # }

        # Возвращаем Inertia Response с шаблоном 'Landing' и данными компонентов
        return inertia_render(request, "Landing", props=page_props)


def render_not_found(request: HttpRequest) -> HttpResponse:
    """Рендерит Inertia-страницу 404 со статусом HTTP 404.

    Документация компонента для InertiaJS:
    {
        "component": "NotFound",
        "props": {},
        "url": "<request.path>"
    }

    Используется и catch-all-маршрутом ``NotFoundView``, и кастомным
    ``handler404`` для ``Http404``, поднятых внутри view.
    """
    response = inertia_render(request, "NotFound")
    response.status_code = 404
    return response


def handler404(
    request: HttpRequest, exception: Exception | None = None
) -> HttpResponse:
    """Кастомный Django handler404 (Inertia: NotFound).

    Вызывается Django при ``DEBUG=False``, когда view поднимает
    ``Http404``. Возвращает тот же ответ, что и catch-all:

    {
        "component": "NotFound",
        "props": {},
        "url": "<request.path>"
    }

    Статус ответа — HTTP 404; общие props (``auth``, ``role`` и т. д.)
    добавляет ``SharedInertiaPropsMiddleware``.
    """
    return render_not_found(request)


class NotFoundView(View):
    """Catch-all для несопоставленных URL (Inertia: NotFound).

    Перехватывает URL, не совпавшие ни с одним маршрутом. Для ``Http404``,
    поднятых внутри view, используется ``handler404``; оба пути отдают
    одинаковую React-страницу со статусом 404.
    """

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        return render_not_found(request)
