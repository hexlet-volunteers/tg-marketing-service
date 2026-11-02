from typing import Any, cast

from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.contrib.messages import add_message
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import (
    HttpRequest,
    HttpResponseBase,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from guardian.utils import get_anonymous_user

from apps.group_channels.models import Group
from apps.users.constants import UserRole


class CheckingUserRolesMixin:
    """
    Миксин для проверки статуса пользователя (анонимный / авторизованный)
    (в виду запуска миделвары RoleMiddleware после ее теста и
    проработки можно со временем избавиться от избыточной проверки на
    ананимность, но только после долгого тестирования миделвары)
    """

    request: HttpRequest

    def is_anonymous(self) -> bool:
        # Получаем специальный анонимный экземпляр Guardian
        anonymous_guardian_user = get_anonymous_user()

        # Пользователь из текущего запроса
        user = self.request.user

        # Проверяем равенство текущего пользователя специальному
        # анонимному экземпляру
        # или, что пользователь не прошёл аутентификацию
        if user == anonymous_guardian_user or not user.is_authenticated:
            return True
        else:
            return False


class GroupOwnerRequiredMixin:
    """
    Разрешает dispatch только владельцу группы из URL-параметра ``slug``.

    ВАЖНО: должен идти в MRO ПОСЛЕ миксина, отсекающего анонимов
    (``UserAuthenticationCheckMixin``), чтобы:
      * аноним получал redirect на логин, а не 403;
      * существование группы не проверялось для неаутентифицированных
        (иначе ``get_object_or_404`` утечёт 404 vs 403).

    После успешной проверки у вью доступен ``self.group``.
    """

    group: Group

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        self.group = get_object_or_404(Group, slug=kwargs["slug"])
        if self.group.owner != request.user:
            return HttpResponseForbidden("Недостаточно прав")
        return cast(
            HttpResponseBase,
            super().dispatch(request, *args, **kwargs),  # type: ignore[misc]
        )


class UserAuthenticationCheckMixin(CheckingUserRolesMixin):
    """
    Класс-миксин для принудительной проверки аутентификации перед
    отображением страницы
    """

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if self.is_anonymous():
            add_message(
                request,
                messages.ERROR,
                "Вы не авторизованы! Пожалуйста, выполните вход.",
            )
            return redirect(reverse("users:login"))
        return super().dispatch(  # type: ignore[misc]
            request, *args, **kwargs
        )


class RoleRequiredMixin(AccessMixin):
    """
    Базовый миксин для проверки ролей.
    Наследуем от AccessMixin для стандартного поведения Django.
    """

    allowed_roles: list[str] | None = (
        None  # Обязательно переопределить в дочерних классах
    )
    permission_denied_message = "У вас нет прав для доступа к этой странице"
    url_redirect = None  # Обязательно переопределить в дочерних классах при
    request: HttpRequest

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        if not self._test_role(request):
            return self.handle_no_permission()

        return cast(
            HttpResponseBase,
            super().dispatch(request, *args, **kwargs),  # type: ignore[misc]
        )

    def _test_role(self, request: HttpRequest) -> bool:
        """Проверяем соответствие роли"""
        if self.allowed_roles is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} требует определения allowed_roles"
            )
        return getattr(request, "role", None) in self.allowed_roles

    def handle_no_permission(self) -> HttpResponseRedirect:
        """Обработка отказа в доступе"""
        # Показываем сообщение об ошибке
        messages.error(self.request, self.permission_denied_message)
        next_param = self.request.GET.get("next", "")

        # Проверяем наличие переменной url_redirect
        if self.url_redirect:
            # Стандартное перенаправление
            return redirect(reverse(self.url_redirect))
        elif next_param:
            # Перенаправляем на сохранённую страницу
            return redirect(next_param)
        raise PermissionDenied(self.get_permission_denied_message())


# Ниже примеры реализации организации доступа по ролям
# при необходимости добавляем класс с необходимыми аргументами и их значения
# далее наследуем созданный класс в представлении, в котором нужно
# организовать доступ


class GuestRequiredMixin(RoleRequiredMixin):
    """Только для неавторизованных пользователей"""

    allowed_roles = [UserRole.GUEST]
    permission_denied_message = "Эта страница доступна только гостям"


class UserRequiredMixin(RoleRequiredMixin):
    """Для всех авторизованных пользователей"""

    allowed_roles = [
        UserRole.USER,
        UserRole.PARTNER,
        UserRole.ADMIN,
        UserRole.CHANNEL_MODERATOR,
    ]
    permission_denied_message = "Требуется авторизация"


class PartnerRequiredMixin(RoleRequiredMixin):
    """Только для активных партнеров"""

    allowed_roles = [UserRole.PARTNER]
    permission_denied_message = "Доступ только для партнеров"

    def _test_role(self, request: HttpRequest) -> bool:
        """Дополнительная проверка активного статуса партнера"""
        return (
            super()._test_role(request)
            and hasattr(request.user, "is_partner")
            and request.user.is_partner
        )


class ChannelModeratorRequiredMixin(RoleRequiredMixin):
    """Только для модераторов каналов"""

    allowed_roles = [UserRole.CHANNEL_MODERATOR, UserRole.PARTNER]
    permission_denied_message = "Доступ только для модераторов каналов"

    def _test_role(self, request: HttpRequest) -> bool:
        """Дополнительная проверка статуса модератора канала"""
        return (
            super()._test_role(request)
            and hasattr(request.user, "is_channel_moderator")
            and request.user.is_channel_moderator
        )


class StaffRequiredMixin(RoleRequiredMixin):
    """Пример добавления новой роли - персонал"""

    allowed_roles = [UserRole.STAFF, UserRole.ADMIN]
    permission_denied_message = "Доступ только для сотрудников"


class AdminRequiredMixin(RoleRequiredMixin):
    """Только для администраторов"""

    allowed_roles = [UserRole.ADMIN]
    permission_denied_message = "Доступ только для администраторов"

    def _test_role(self, request: HttpRequest) -> bool:
        """Дополнительная проверка статуса администратора"""
        return super()._test_role(request) and (
            getattr(request, "role", None) == UserRole.ADMIN
            or getattr(request.user, "is_staff", False)
            or getattr(request.user, "is_superuser", False)
        )
