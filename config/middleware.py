from django.middleware.csrf import get_token
from inertia.share import share


class SharedInertiaPropsMiddleware:
    """Канонический слой общих Inertia-props.

    См. docs/inertia-shared-props.md
    """

    VALID_ROLES = {
        "guest",
        "user",
        "partner",
        "admin",
        "channel_moderator",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def _get_role(self, request):
        if not request.user.is_authenticated:
            return "guest"

        # Канонический источник — request.role (устанавливается RoleMiddleware).
        role = getattr(request, "role", None)
        if role is None:
            role = getattr(request.user, "role", None)

        normalized_role = str(role).strip().lower() if role else "user"
        if normalized_role in self.VALID_ROLES:
            return normalized_role

        return "user"

    def _is_admin(self, request):
        if not request.user.is_authenticated:
            return False

        role = self._get_role(request)
        return (
            role == "admin"
            or getattr(request.user, "is_staff", False)
            or getattr(request.user, "is_superuser", False)
        )

    def _get_auth_payload(self, request):
        if not request.user.is_authenticated:
            return None

        user = request.user
        role = self._get_role(request)

        return {
            "id": user.id,
            "name": user.get_full_name() or user.username,
            "email": user.email,
            "avatar_url": user.avatar_image or "",
            "role": role,
        }

    def __call__(self, request):
        flash = request.session.pop("flash", None)
        if not isinstance(flash, dict) or not flash:
            flash = None

        share(
            request,
            auth=self._get_auth_payload(request),
            role=self._get_role(request),
            is_admin=self._is_admin(request),
            csrfToken=get_token(request),
            flash=flash,
        )
        response = self.get_response(request)

        # Flash не должен теряться на промежуточных редиректах:
        # если ответ — redirect, возвращаем flash в сессию,
        # чтобы следующий запрос мог его извлечь.
        if flash is not None and 300 <= response.status_code < 400:
            request.session["flash"] = flash

        return response
