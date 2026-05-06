
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from inertia import render as inertia_render
from apps.parser.models import TelegramChannel
from apps.group_channels.models import Group
from django.views.generic.base import View


class DashboardView(View):
    """
    Дашборд авторизованного пользователя.
    Доступен только после авторизации.
    
    Документация формата ответа:
    {
        "component": "Dashboard",
        "props": {
            "stats": {"channels": 47, "posts": 2347, "ai_suggestions": 89, "days_left": 23},
            "channels": [{"name": "Tech News RU", "subscribers": "45.2K", "posts": 24, "views": "156K", "engagement": "78%", "growth": "+12%"}],
            "ai_insights": [{"text": "Тренд: посты о новых ИИ инструментах набирают +45% просмотров"}],
            "collections": [{"name": "IT & Технологии", "channels_count": 23}],
            "quick_actions": ["Добавить канал", "Экспорт данных", "Настройки"],
            "csrfToken": "abc123..."
        },
        "url": "/dashboard/"
    }
    """
    
    # Собираем все данные в словарь props и рендерим страницу Dashboard через Inertia.js.
    def get(self, request, *args, **kwargs):
        # Если пользователь не авторизован - редирект на главную
        if not request.user.is_authenticated:
            return redirect('main_index')
        
        user = request.user
        
        # 1. Сбор статистики
        stats = self._get_user_stats(user)
        
        # 2. Получение каналов пользователя с метриками
        channels_data = self._get_user_channels(user)
        
        # 3. AI-инсайты (пока заглушка, можно интегрировать с AI сервисом позже)
        ai_insights = self._get_ai_insights(user)
        
        # 4. Подборки (коллекции) каналов пользователя
        collections = self._get_user_collections(user)
        
        # 5. Быстрые действия
        quick_actions = [
            "Добавить канал",
            "Экспорт данных", 
            "Настройки",
            "Создать подборку"
        ]
        
        # 6. CSRF токен для форм
        csrf_token = get_token(request)
        
        props = {
            "stats": stats,
            "channels": channels_data,
            "ai_insights": ai_insights,
            "collections": collections,
            "quick_actions": quick_actions,
            "csrfToken": csrf_token,
            "user": {
                "username": user.username,
                "full_name": user.get_full_name(),
                "avatar": user.avatar_image,
                "role": user.role
            }
        }
        
        return inertia_render(request, 'Dashboard', props=props)
    
    # Считает количество каналов, постов, AI-предложений и дней до конца подписки.
    def _get_user_stats(self, user):
        user_channels = TelegramChannel.objects.filter(
            moderators__user=user
            ).distinct()
        channels_count = user_channels.count()
        posts_count = sum(
            len(c.last_messages) for c in user_channels if c.last_messages
        )
        ai_suggestions_count = 0  # заглушка
        days_left = self._get_subscription_days_left(user)
        
        return {
            "channels": channels_count,
            "posts": posts_count,
            "ai_suggestions": ai_suggestions_count,
            "days_left": days_left
        }

    # Формирует список каналов пользователя с метриками (подписчики, просмотры, вовлечённость, рост).
    def _get_user_channels(self, user, limit=5):
        
        user_channels = TelegramChannel.objects.filter(
            moderators__user=user
            ).distinct()[:limit]
        
        channels_list = []
        for channel in user_channels:
            last_stat = channel.last_stat()
            engagement = "0%"
            
            if last_stat and channel.average_views > 0:
                growth_rate = (
                    last_stat.daily_growth / channel.participants_count * 100
                ) if channel.participants_count > 0 else 0
                engagement = f"{min(100, max(0, int(growth_rate)))}%"
            subscribers_formatted = self._format_number(
                channel.participants_count
            )
            views_formatted = self._format_number(channel.average_views)
            
            growth = "+0%"
            if last_stat and last_stat.daily_growth != 0:
                growth_percent = (
                    last_stat.daily_growth / max(
                        1, channel.participants_count - last_stat.daily_growth
                    )
                ) * 100
                growth = f"{'+' if growth_percent >= 0 else ''}{int(growth_percent)}%"
            
            channels_list.append({
                "name": channel.title,
                "subscribers": subscribers_formatted,
                "posts": len(channel.last_messages) if channel.last_messages else 0,
                "views": views_formatted,
                "engagement": engagement,
                "growth": growth,
                "id": channel.channel_id,
                "username": channel.username or ""
            })

        return channels_list
    
    # Генерирует AI-инсайты (рекомендации, тренды) на основе каналов пользователя.
    def _get_ai_insights(self, user, limit=3):
        insights = []
        user_channels = TelegramChannel.objects.filter(
            moderators__user=user
        ).distinct()
        
        if user_channels.exists():
            top_channel = max(
                user_channels,
                key=lambda c: c.average_views,
                default=None
            )
            
            if top_channel and top_channel.average_views > 0:
                insights.append({
                    "text": f"Ваш канал «{top_channel.title}» "
                            f"показывает наилучшую динамику просмотров: "
                            f"{self._format_number(top_channel.average_views)} "
                            f"средних просмотров на пост.",
                    "type": "positive"
                })
                
            categories = user_channels.exclude(
                category__isnull=True
                ).exclude(category='').values_list('category', flat=True).distinct()
            
            if categories:
                insights.append({
                    "text": f"Рекомендуем добавить каналы из категорий: "
                            f"{', '.join(list(categories)[:3])}. Это поможет расширить аналитику.",
                    "type": "recommendation"
                })
        insights.extend([
            {
                "text": "Тренд: посты с видео-контентом набирают на 67%" 
                "больше просмотров в Telegram.",
                "type": "trend"
            },
            {
                "text": "ИИ-анализ показывает, что лучшее время для публикаций"
                "- вторник и четверг с 18:00 до 20:00.", "type": "insight"
            }
        ])
        
        return insights[:limit]

    # Формирует список подборок (групп) каналов пользователя.
    def _get_user_collections(self, user):
        
        user_groups = Group.objects.filter(owner=user).distinct()
        
        collections = []
        
        for group in user_groups:
            collections.append({
                "name": group.name,
                "channels_count": group.channels.count(),
                "slug": group.slug,
                "description": group.description,
                "is_auto": hasattr(group, 'auto_rule')
            })
        
        if not collections:
            collections.append({
                "name": "Мои каналы",
                "channels_count": TelegramChannel.objects.filter(
                    moderators__user=user
                ).count(),
                "slug": "my-channels",
                "description": "Все ваши отслеживаемые каналы",
                "is_auto": False
            })
        
        return collections
    
    # Возвращает количество дней до окончания подписки (заглушка).
    def _get_subscription_days_left(self, user):
        if hasattr(user, 'partner_profile') and user.partner_profile.status == 'active':
            return 30
        return 0
    
    # Форматирует числа для красивого отображения (например, 12345 → 12.3K).
    def _format_number(self, num):
        
        if not num or num < 1000:
            return str(num) if num else "0"
        
        if num < 1000000:
            return f"{num/1000:.1f}K".replace('.0K', 'K')
        
        return f"{num/1000000:.1f}M".replace('.0M', 'M')
    
    # Для демо возвращает случайное значение вовлечённости (в реальном проекте — по данным)
    def _get_engagement_rate(self, channel):
        
        if channel.last_messages and channel.average_views > 0:
            import random
            random.seed(channel.channel_id)
            return random.randint(5, 25)
        return 0