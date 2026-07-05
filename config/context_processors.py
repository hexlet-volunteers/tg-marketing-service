from django.conf import settings


def user_role(request):
    """
    Контекстный процессор, добавляющий информацию о роли пользователя в шаблоны.
    Возвращает:
    - user_role: строка с ролью (guest|user|partner)
    - is_authenticated: булево значение
    - is_partner: булево значение (только для авторизованных)
    """
    role = getattr(request, "role", None)

    if role is None:
        # Если роль еще не определена, вычисляем ее
        if not request.user.is_authenticated:
            role = "guest"
        else:
            role = (
                "partner"
                if getattr(request.user, "is_partner", False)
                else "user"
            )
        request.role = role  # Кэшируем роль в запросе

    context = {
        "user_role": role,
        "is_authenticated": request.user.is_authenticated,
        "is_partner": role == "partner",
    }

    # Добавляем отладочную информацию в режиме разработки
    if settings.DEBUG:
        context["user_role_debug"] = {
            "actual_role": role,
            "is_staff": getattr(request.user, "is_staff", False),
            "is_superuser": getattr(request.user, "is_superuser", False),
        }

    return context
