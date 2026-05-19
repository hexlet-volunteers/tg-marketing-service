from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.views import View
from inertia import render as inertia_render

from .services.dashboard_service import DashboardService


class DashboardView(View):
    """
    Inertia view для дашборда авторизованного пользователя.
    
    Пример Inertia payload для фронтенда:
    
    {
        "component": "Dashboard",
        "props": {
            "stats": {
                "channels": 47,
                "posts": 2347,
                "ai_suggestions": 89,
                "days_left": 23
            },
            "channels": [
                {
                    "name": "Tech News RU",
                    "subscribers": 45200,
                    "posts": 24,
                    "views": 156000,
                    "engagement": 78.5,
                    "growth": 12.3
                },
                {
                    "name": "AI Weekly",
                    "subscribers": 28100,
                    "posts": 18,
                    "views": 89200,
                    "engagement": 74.2,
                    "growth": 8.7
                }
            ],
            "ai_insights": [
                {
                    "text": "Тренд: посты о новых ИИ инструментах набирают +45% просмотров",
                    "type": "trend",
                    "id": 1
                },
                {
                    "text": "Канал «Tech News RU» растёт (+156 подписчиков за день)",
                    "type": "positive",
                    "id": null
                }
            ],
            "collections": [
                {
                    "name": "IT & Технологии",
                    "channels_count": 23,
                    "slug": "it-tech",
                    "description": "Каналы про IT и технологии",
                    "is_auto": false
                },
                {
                    "name": "Мои каналы",
                    "channels_count": 47,
                    "slug": "my-channels",
                    "description": "Все каналы",
                    "is_auto": false
                }
            ],
            "quick_actions": [
                "Добавить канал",
                "Экспорт данных",
                "Настройки"
            ],
            "csrfToken": "abc123xyz456..."
        },
        "url": "/dashboard/"
    }
    
    Примечания:
    - channels ограничены первыми 5 каналами для производительности
    - ai_insights: до 5 непрочитанных из БД или сгенерированных fallback
    - engagement: процент (views / subscribers * 100)
    - growth: процентный рост подписчиков за последний период
    - days_left: 0 для неактивной подписки, иначе 30 (пример)
    - is_auto: признак автоматической/ручной коллекции
    """
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('main_index')
        
        service = DashboardService(request.user)
        dto = service.build()
        
        return inertia_render(
            request,
            'Dashboard',
            props={
                **dto.model_dump(mode="json"),
                "csrfToken": get_token(request),
            }
        )
