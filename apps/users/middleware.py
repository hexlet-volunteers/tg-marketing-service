from django.contrib.auth import get_user_model

from apps.users.roles import Role

User = get_user_model()


class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Получаем роль пользователя, если она известна
        user_role = getattr(request.user, "role", None)
        role_obj = Role.objects.filter(code=user_role).first()

        # Если роль пользователя не найдена, ставим гостевую роль
        if role_obj:
            final_role = role_obj.code
        elif user_role:
            final_role = user_role
        else:
            final_role = "guest"

        # Ставим роль в запрос
        request.role = final_role
        response = self.get_response(request)

        return response
