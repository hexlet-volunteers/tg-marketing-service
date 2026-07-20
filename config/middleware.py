from django.middleware.csrf import get_token
from inertia.share import share


class InertiaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _get_auth_payload(self, request):
        if not request.user.is_authenticated:
            return None

        user = request.user
        role = getattr(user, "role", None) or "user"
        normalized_role = str(role).strip().lower()

        return {
            "id": user.id,
            "name": user.get_full_name() or user.username,
            "email": user.email,
            "avatar_url": user.avatar_image or "",
            "role": normalized_role,
        }

    def _get_role(self, request):
        if not request.user.is_authenticated:
            return "guest"

        role = getattr(request.user, "role", None) or getattr(
            request, "role", None
        )
        if role is None:
            return "user"

        normalized_role = str(role).strip().lower()
        if normalized_role in {"guest", "user", "partner"}:
            return normalized_role

        return "user"

    def __call__(self, request):
        flash = request.session.pop("flash", None)
        if isinstance(flash, dict) and not flash:
            flash = None

        share(
            request,
            auth=self._get_auth_payload(request),
            role=self._get_role(request),
            csrfToken=get_token(request),
            flash=flash,
        )
        response = self.get_response(request)
        return response
