import re
from typing import Literal, overload
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@overload
def get_telegram_credentials(
    require_session: Literal[True],
) -> tuple[int, str, str]: ...


@overload
def get_telegram_credentials(
    require_session: bool = False,
) -> tuple[int, str, str | None]: ...


def get_telegram_credentials(
    require_session: bool = False,
) -> tuple[int, str, str | None]:
    """Return Telegram API credentials from Django settings.

    Validates that TELEGRAM_API_ID and TELEGRAM_API_HASH are configured
    and casts TELEGRAM_API_ID to int. Raises ImproperlyConfigured with a
    clear message when credentials are missing or invalid.

    Args:
        require_session: If True, also require TELEGRAM_SESSION_STRING.

    Returns:
        tuple: (api_id: int, api_hash: str, session_string: str | None)
    """
    api_id = settings.TELEGRAM_API_ID
    api_hash = settings.TELEGRAM_API_HASH
    session_string = settings.TELEGRAM_SESSION_STRING

    if not api_id or not api_hash:
        raise ImproperlyConfigured(
            "Нет конфигурации для Telegram API. "
            "Установи TELEGRAM_API_ID и TELEGRAM_API_HASH."
        )

    try:
        api_id_int = int(api_id)
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured(
            f"TELEGRAM_API_ID должен быть целым числом, получено: {api_id!r}"
        ) from exc

    if require_session and not session_string:
        raise ImproperlyConfigured(
            "TELEGRAM_SESSION_STRING не задан. "
            "Запусти `uv run python manage.py start_telegram_session`"
        )

    return api_id_int, api_hash, session_string


def normalize_channel_username(username: str) -> str:
    """Normalize a Telegram channel username."""
    value = username.strip()

    if value.startswith("@"):
        value = value[1:]

    elif value.lower().startswith(("http://", "https://")):
        parsed_url = urlsplit(value)

        if parsed_url.netloc.lower() != "t.me":
            return ""

        value = parsed_url.path.strip("/")

    elif value.lower().startswith("t.me/"):
        value = value[5:]

    if value.startswith("s/"):
        value = value[2:]

    value = value.lower()

    if not re.fullmatch(r"[a-z0-9_]{5,32}", value):
        return ""

    return value
