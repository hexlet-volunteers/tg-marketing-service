import logging
from collections.abc import Callable
from typing import cast

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)
User = get_user_model()


class RoleRequest(HttpRequest):
    role: str


class RoleMiddleware:
    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponse],
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Получаем роль пользователя, если она известна
        Если роль пользователя не найдена, ставим гостевую роль
        """
        role_request = cast(RoleRequest, request)

        if request.user.is_authenticated:
            role_request.role = request.user.role or "guest"
        else:
            role_request.role = "guest"

        # logging-сообщение
        logger.debug(
            "Middleware: Current role of the user is '%s'", role_request.role
        )

        response = self.get_response(request)

        return response
