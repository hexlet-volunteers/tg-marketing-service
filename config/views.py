from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import View
from inertia import render as inertia_render

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

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
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

        # Flach сообщение временное явление, пока не будет готова
        # на фронте страница login. Сейчас представление UserRegister
        # делает редирект с сообщением на главную страницу

        flash = {}
        if "flash_success" in request.session:
            flash["success"] = request.session.pop("flash_success")

        page_props = {"components": components_data, "flash": flash}

        # коментируем до изменеий в UserRegister
        # page_props = {
        #    'components': components_data,
        # }

        # Возвращаем Inertia Response с шаблоном 'Home' и данными компонентов
        return inertia_render(request, "Home", props=page_props)
