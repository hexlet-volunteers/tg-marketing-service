from functools import wraps

from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse


def role_required(allowed_roles, login_url=None, message=None):
    """
    Основной декоратор для проверки ролей.

    :param allowed_roles: Список разрешенных ролей (например, ['user', 'partner'])
    :param login_url: URL для перенаправления неавторизованных (по умолчанию None)
    :param message: Сообщение об ошибке (по умолчанию None)
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Определяем роль пользователя
            if not hasattr(request, 'role'):
                request.role = get_user_role(request)

            # Проверяем доступ
            if request.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # Обработка отказа в доступе
            return handle_access_denied(request, request.role, allowed_roles, login_url, message)

        return _wrapped_view

    return decorator


def get_user_role(request):
    """Динамически определяем роль пользователя"""
    if not request.user.is_authenticated:
        return 'guest'
    if hasattr(request.user, 'is_partner') and request.user.is_partner:
        return 'partner'
    if hasattr(request.user, 'is_channel_moderator') and request.user.is_channel_moderator:
        return 'channel_moderator'
    return 'user'


def handle_access_denied(request, current_role, allowed_roles, login_url=None, message=None):
    """
    Обработка отказа в доступе с учетом разных сценариев
    """
    default_messages = {
        'guest': "Требуется авторизация",
        'user': "Недостаточно прав",
        'partner': "Доступ только для партнеров",
        'channel_moderator': "Доступ только для модераторов каналов"
    }

    error_message = message or default_messages.get(current_role, "Доступ запрещен")

    # Для неавторизованных - редирект на страницу входа
    if current_role == 'guest' and login_url:
        messages.warning(request, error_message)
        return HttpResponseRedirect(login_url)

    # Для авторизованных - 403 ошибка
    if message:
        messages.error(request, error_message)
    return HttpResponseForbidden(error_message)


# Специализированные декораторы
def guest_required(view_func=None, login_url=None, message=None):
    """
    Только для неавторизованных пользователей.
    Авторизованных перенаправляет на главную.
    """
    actual_decorator = role_required(
        allowed_roles=['guest'],
        login_url=login_url,
        message=message or "Эта страница доступна только гостям"
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def user_required(view_func=None, login_url=None, message=None):
    """
    Для всех авторизованных пользователей (user и partner).
    Гостей перенаправляет на страницу входа.
    """
    actual_decorator = role_required(
        allowed_roles=['user', 'partner'],
        login_url=login_url or reverse('login'),
        message=message or "Требуется авторизация"
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def partner_required(view_func=None, login_url=None, message=None):
    """
    Только для активных партнеров.
    Всех остальных перенаправляет или показывает 403.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Сначала проверяем авторизацию
            if not request.user.is_authenticated:
                messages.warning(request, message or "Требуется авторизация")
                return HttpResponseRedirect(login_url or reverse('login'))

            # Затем проверяем партнерский статус
            if not getattr(request.user, 'is_partner', False):
                messages.error(request, message or "Доступ только для партнеров")
                return HttpResponseForbidden("Доступ только для партнеров")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if view_func:
        return decorator(view_func)
    return decorator


def channel_moderator_required(view_func=None, login_url=None, message=None):
    """
    Только для модераторов каналов.
    Всех остальных перенаправляет или показывает 403.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Сначала проверяем авторизацию
            if not request.user.is_authenticated:
                messages.warning(request, message or "Требуется авторизация")
                return HttpResponseRedirect(login_url or reverse('login'))

            # Затем проверяем статус модератора канала
            if not getattr(request.user, 'is_channel_moderator', False):
                messages.error(request, message or "Доступ только для модераторов каналов")
                return HttpResponseForbidden("Доступ только для модераторов каналов")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if view_func:
        return decorator(view_func)
    return decorator
