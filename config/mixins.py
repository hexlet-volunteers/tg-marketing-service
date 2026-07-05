from django.views.generic import View
from django.shortcuts import reverse, redirect
from django.contrib.messages import add_message
from django.contrib import messages
from guardian.utils import get_anonymous_user
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.contrib.auth.mixins import AccessMixin


class CheckingUserRolesMixin:
    """
    Миксин для проверки статуса пользователя (анонимный / авторизованный)
    (в виду запуска миделвары RoleMiddleware после ее теста и проработки можно
    со временем избавиться от избыточной проверки на ананимность, но только после долгого тестирования миделвары)
    """

    def is_anonymous(self):
        # Получаем специальный анонимный экземпляр Guardian
        anonymous_guardian_user = get_anonymous_user()

        # Пользователь из текущего запроса
        user = self.request.user

        # Проверяем равенство текущего пользователя специальному анонимному экземпляру
        # или, что пользователь не прошёл аутентификацию
        if user == anonymous_guardian_user or not user.is_authenticated:
            return True
        else:
            return False


class UserAuthenticationCheckMixin(CheckingUserRolesMixin):
    """
    Класс-миксин для принудительной проверки аутентификации перед отображением страницы
    """

    def dispatch(self, request, *args, **kwargs):
        if self.is_anonymous():
            add_message(
                request,
                messages.ERROR,
                "Вы не авторизованы! Пожалуйста, выполните вход.",
            )
            return redirect(reverse("users:login"))
        return super().dispatch(request, *args, **kwargs)


class RoleRequiredMixin(AccessMixin):
    """
    Базовый миксин для проверки ролей.
    Наследуем от AccessMixin для стандартного поведения Django.
    """

    allowed_roles = None  # Обязательно переопределить в дочерних классах
    permission_denied_message = "У вас нет прав для доступа к этой странице"
    url_redirect = None  # Обязательно переопределить в дочерних классах при

    def dispatch(self, request, *args, **kwargs):
        if not self._test_role(request):
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def _test_role(self, request):
        """Проверяем соответствие роли"""
        if self.allowed_roles is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} требует определения allowed_roles"
            )
        return request.role in self.allowed_roles

    def handle_no_permission(self):
        """Обработка отказа в доступе"""
        messages.error(
            self.request, self.permission_denied_message
        )  # Показываем сообщение об ошибке
        next_param = self.request.GET.get("next", "")

        if self.url_redirect:  # Проверяем наличие переменной url_redirect
            return redirect(
                reverse(self.url_redirect)
            )  # Стандартное перенаправление
        elif next_param:
            return redirect(
                next_param
            )  # Перенаправляем на сохранённую страницу
        raise PermissionDenied(self.get_permission_denied_message())


"""Ниже примеры реализации организации доступа по ролям"""
"""при необходимости добавляем класс  с необходимыми аргументами и их значения"""
"""далее наследуем созданный класс в представлении котором нужно организовать доступ"""


class GuestRequiredMixin(RoleRequiredMixin):
    """Только для неавторизованных пользователей"""

    allowed_roles = ["guest"]
    permission_denied_message = "Эта страница доступна только гостям"


class UserRequiredMixin(RoleRequiredMixin):
    """Для всех авторизованных пользователей"""

    allowed_roles = ["user", "partner", "channel_moderator"]
    permission_denied_message = "Требуется авторизация"


class PartnerRequiredMixin(RoleRequiredMixin):
    """Только для активных партнеров"""

    allowed_roles = ["partner"]
    permission_denied_message = "Доступ только для партнеров"

    def _test_role(self, request):
        """Дополнительная проверка активного статуса партнера"""
        return (
            super()._test_role(request)
            and hasattr(request.user, "is_partner")
            and request.user.is_partner
        )


class ChannelModeratorRequiredMixin(RoleRequiredMixin):
    """Только для модераторов каналов"""

    allowed_roles = ["channel_moderator"]
    permission_denied_message = "Доступ только для модераторов каналов"

    def _test_role(self, request):
        """Дополнительная проверка статуса модератора канала"""
        return (
            super()._test_role(request)
            and hasattr(request.user, "is_channel_moderator")
            and request.user.is_channel_moderator
        )


class StaffRequiredMixin(RoleRequiredMixin):
    """Пример добавления новой роли - персонал"""

    allowed_roles = ["staff", "admin"]
    permission_denied_message = "Доступ только для сотрудников"
