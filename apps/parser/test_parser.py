import os
import subprocess
import sys
import tempfile

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings

from apps.parser.models import TelegramChannel
from apps.parser.tasks import parse_channel
from apps.parser.utils import get_telegram_credentials
from apps.parser.views import ParserView

TELEGRAM_ENV_VARS = [
    "TELEGRAM_API_ID",
    "TELEGRAM_API_HASH",
    "TELEGRAM_SESSION_STRING",
]


def _clean_env() -> dict[str, str]:
    """Return a copy of the current env without Telegram variables."""
    return {
        key: value
        for key, value in os.environ.items()
        if key not in TELEGRAM_ENV_VARS
    }


def test_settings_imports_without_telegram_env() -> None:
    """settings.py must not raise on import when Telegram keys are absent."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    code = "import config.settings"
    env = _clean_env()
    env["PYTHONPATH"] = project_root
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=tmpdir,
            env=env,
            capture_output=True,
            text=True,
        )
    assert result.returncode == 0, result.stderr


@override_settings(
    TELEGRAM_API_ID="12345",
    TELEGRAM_API_HASH="abc",
    TELEGRAM_SESSION_STRING="session",
)
def test_get_telegram_credentials_returns_valid_values() -> None:
    api_id, api_hash, session = get_telegram_credentials()
    assert api_id == 12345
    assert api_hash == "abc"
    assert session == "session"


@override_settings(
    TELEGRAM_API_ID="",
    TELEGRAM_API_HASH="abc",
    TELEGRAM_SESSION_STRING="session",
)
def test_get_telegram_credentials_raises_without_api_id() -> None:
    with pytest.raises(
        ImproperlyConfigured, match="Нет конфигурации для Telegram API"
    ):
        get_telegram_credentials()


@override_settings(
    TELEGRAM_API_ID="12345",
    TELEGRAM_API_HASH="",
    TELEGRAM_SESSION_STRING="session",
)
def test_get_telegram_credentials_raises_without_api_hash() -> None:
    with pytest.raises(
        ImproperlyConfigured, match="Нет конфигурации для Telegram API"
    ):
        get_telegram_credentials()


@override_settings(
    TELEGRAM_API_ID="not-a-number",
    TELEGRAM_API_HASH="abc",
    TELEGRAM_SESSION_STRING="session",
)
def test_get_telegram_credentials_raises_on_invalid_api_id() -> None:
    with pytest.raises(
        ImproperlyConfigured, match="TELEGRAM_API_ID должен быть целым числом"
    ):
        get_telegram_credentials()


@override_settings(
    TELEGRAM_API_ID="12345",
    TELEGRAM_API_HASH="abc",
    TELEGRAM_SESSION_STRING="",
)
def test_credentials_raises_without_session_when_required() -> None:
    with pytest.raises(
        ImproperlyConfigured, match="TELEGRAM_SESSION_STRING не задан"
    ):
        get_telegram_credentials(require_session=True)


@override_settings(
    TELEGRAM_API_ID="12345",
    TELEGRAM_API_HASH="abc",
    TELEGRAM_SESSION_STRING="",
)
def test_parser_view_get_telegram_client_raises_without_session() -> None:
    view = ParserView()
    with pytest.raises(
        ImproperlyConfigured, match="TELEGRAM_SESSION_STRING не задан"
    ):
        view.get_telegram_client()


@pytest.mark.django_db
@override_settings(
    TELEGRAM_API_ID="",
    TELEGRAM_API_HASH="",
    TELEGRAM_SESSION_STRING="",
)
def test_parse_channel_raises_without_telegram_credentials() -> None:
    channel = TelegramChannel.objects.create(
        channel_id=123456789,
        title="Test Channel",
        participants_count=0,
    )
    with pytest.raises(
        ImproperlyConfigured, match="Нет конфигурации для Telegram API"
    ):
        parse_channel(channel.channel_id)
