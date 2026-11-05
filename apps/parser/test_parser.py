import os
import subprocess
import sys
import tempfile
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory
from django.test.utils import override_settings
from django.utils import timezone

from apps.admin.moderation.models import ModerationRequest
from apps.parser.models import ChannelStats, TelegramChannel
from apps.parser.tasks import parse_channel
from apps.parser.utils import get_telegram_credentials
from apps.parser.views import ParserView
from apps.users.models import User

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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "channel_identifier",
    [
        "@Example_Channel",
        "Example_Channel",
        "t.me/Example_Channel",
        "https://t.me/Example_Channel",
    ],
)
def test_parser_view_does_not_parse_existing_channel(
    channel_identifier: str,
) -> None:
    TelegramChannel.objects.create(
        channel_id=123456789,
        title="Existing Channel",
        username="example_channel",
        participants_count=100,
    )

    view = ParserView()

    with patch.object(view, "async_tg_parser") as mock_parser:
        mock_parser.return_value = None

        result = view.find_existing_channel(channel_identifier)

    assert result is not None
    assert result.username == "example_channel"
    mock_parser.assert_not_called()


@pytest.mark.django_db
def test_parser_view_uses_saved_data_during_cooldown() -> None:
    channel = TelegramChannel.objects.create(
        channel_id=123456789,
        title="Existing Channel",
        username="example_channel",
        participants_count=100,
    )

    original_parsed_at = channel.parsed_at

    view = ParserView()
    request = RequestFactory().post("/parser/")
    view.setup(request)
    user = User.objects.create_user(
        username="cooldown_test_user",
        email="cooldown_test_user@example.com",
        password="test-password",
    )
    request.user = user

    request.session = {}  # type: ignore
    setattr(request, "_messages", FallbackStorage(request))

    form = view.get_form_class()(
        data={
            "channel_identifier": "@Example_Channel",
            "category": "Технологии",
            "country": "RU",
            "language": "ru",
            "limit": 10,
        }
    )

    assert form.is_valid(), form.errors

    with patch.object(view, "async_tg_parser") as mock_parser:
        response = view.form_valid(form)

    assert not form.errors, form.errors
    mock_parser.assert_not_called()

    assert response.status_code in (200, 302)

    moderation_request = ModerationRequest.objects.get()

    assert moderation_request.channel_by == channel
    assert moderation_request.status == "pending"

    channel.refresh_from_db()
    assert channel.parsed_at == original_parsed_at
    assert channel.channelstats_set.count() == 0


@pytest.mark.django_db
def test_parser_view_creates_pending_moderation_request() -> None:
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="channel-author",
        email="author@example.com",
        password="password",
        role="user",
    )

    view = ParserView()
    request = RequestFactory().post("/parser/")
    request.user = user
    request.session = {}  # type: ignore
    setattr(request, "_messages", FallbackStorage(request))
    view.setup(request)

    form = view.get_form_class()(
        data={
            "channel_identifier": "@new_channel",
            "category": "Технологии",
            "country": "RU",
            "language": "ru",
            "limit": 10,
        }
    )

    assert form.is_valid(), form.errors

    parsed_data = {
        "title": "New Channel",
        "channel_id": 987654321,
        "username": "new_channel",
        "verified": False,
        "creation_date": None,
        "last_messages": [],
        "average_views": 0,
        "participants_count": 100,
        "description": "New channel",
        "pinned_messages": [],
    }

    with patch(
        "apps.parser.views.async_to_sync",
        return_value=lambda *args: parsed_data,
    ):
        response = view.form_valid(form)

    moderation_request = ModerationRequest.objects.get()

    assert response.status_code == 302
    assert moderation_request.status == "pending"
    assert moderation_request.submitted_by == user
    assert moderation_request.channel_by.channel_id == 987654321  # type: ignore
    assert moderation_request.channel_identifier == "new_channel"


@pytest.mark.parametrize(
    ("channel_identifier", "expected"),
    [
        ("@durov", "durov"),
        ("durov", "durov"),
        ("t.me/durov", "durov"),
        ("https://t.me/durov", "durov"),
        ("https://t.me/s/durov", "durov"),
        ("@Example_Channel", "example_channel"),
    ],
)
def test_channel_parse_form_accepts_valid_username(
    channel_identifier: str,
    expected: str,
) -> None:
    from apps.parser.forms import ChannelParseForm

    form = ChannelParseForm(
        data={
            "channel_identifier": channel_identifier,
            "category": "Технологии",
            "country": "RU",
            "language": "ru",
            "limit": 10,
        }
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["channel_identifier"] == expected


@pytest.mark.parametrize(
    "channel_identifier",
    [
        "+79991234567",
        "t.me/+AbCdEf",
        "https://t.me/+AbCdEf",
        "t.me/joinchat/xxx",
        "https://t.me/joinchat/xxx",
        "https://evil.com/foo",
        "du",
        "a" * 33,
        "bad-name",
    ],
)
def test_channel_parse_form_rejects_invalid_username(
    channel_identifier: str,
) -> None:
    from apps.parser.forms import ChannelParseForm

    form = ChannelParseForm(
        data={
            "channel_identifier": channel_identifier,
            "category": "Технологии",
            "country": "RU",
            "language": "ru",
            "limit": 10,
        }
    )

    assert not form.is_valid()
    assert "channel_identifier" in form.errors


@pytest.mark.django_db
def test_parser_view_does_not_parse_invalid_channel() -> None:
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="invalid-channel-user",
        email="invalid@example.com",
        password="password",
        role="user",
    )

    view = ParserView()
    request = RequestFactory().post("/parser/")
    request.user = user
    request.session = {}
    setattr(request, "_messages", FallbackStorage(request))
    view.setup(request)

    form = view.get_form_class()(
        data={
            "channel_identifier": "https://evil.com/foo",
            "category": "Технологии",
            "country": "RU",
            "language": "ru",
            "limit": 10,
        }
    )

    with patch("apps.parser.views.async_to_sync") as parser_mock:
        response = view.form_invalid(form)

    assert not form.is_valid()
    assert response.status_code == 200
    parser_mock.assert_not_called()


@pytest.mark.django_db
@override_settings(
    PARSER_RATE_LIMIT="5/hour",
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    },
)
def test_parser_view_limits_sixth_submission() -> None:
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="rate-limit-user",
        email="rate-limit@example.com",
        password="password",
        role="user",
    )

    cache.clear()

    form_data = {
        "channel_identifier": "@new_channel",
        "category": "Технологии",
        "country": "RU",
        "language": "ru",
        "limit": 10,
    }

    for attempt in range(1, 7):
        request = RequestFactory().post("/parser/", data=form_data)
        request.user = user

        view = ParserView()
        view.setup(request)

        with (
            patch.object(
                view,
                "form_valid",
                return_value=None,
            ) as valid_mock,
            patch.object(
                view,
                "form_invalid",
                return_value=None,
            ) as invalid_mock,
        ):
            view.post(request)

        if attempt <= 5:
            valid_mock.assert_called_once()
            invalid_mock.assert_not_called()
        else:
            valid_mock.assert_not_called()
            invalid_mock.assert_called_once()

            form = invalid_mock.call_args.args[0]
            assert (
                "Вы отправили слишком много запросов. Попробуйте позже."
                in form.non_field_errors()
            )

    cache.clear()


@pytest.mark.django_db
def test_parser_view_parses_channel_after_cooldown() -> None:
    channel = TelegramChannel.objects.create(
        channel_id=123456789,
        title="Existing Channel",
        username="example_channel",
        participants_count=100,
    )
    TelegramChannel.objects.filter(pk=channel.pk).update(
        parsed_at=timezone.now() - timedelta(hours=25)
    )

    parsed_data = {
        "title": "Updated Channel",
        "channel_id": 123456789,
        "username": "example_channel",
        "verified": False,
        "creation_date": None,
        "last_messages": [],
        "average_views": 150,
        "participants_count": 150,
        "description": "Updated description",
        "pinned_messages": [],
    }

    view = ParserView()
    request = RequestFactory().post("/parser/")
    view.setup(request)

    user = User.objects.create_user(
        username="cooldown_expired_user",
        email="cooldown_expired_user@example.com",
        password="test-password",
    )
    request.user = user
    request.session = {}  # type: ignore
    setattr(request, "_messages", FallbackStorage(request))

    form = view.get_form_class()(
        data={
            "channel_identifier": "@Example_Channel",
            "category": "Технологии",
            "country": "RU",
            "language": "ru",
            "limit": 10,
        }
    )
    assert form.is_valid(), form.errors

    with patch.object(
        view,
        "async_tg_parser",
        return_value=parsed_data,
    ) as mock_parser:
        view.form_valid(form)

    mock_parser.assert_called_once_with("example_channel", 10)
    assert not form.errors, form.errors

    channel.refresh_from_db()
    assert channel.title == "Updated Channel"
    assert channel.participants_count == 150
    assert channel.parsed_at > timezone.now() - timedelta(minutes=1)
    assert ChannelStats.objects.filter(channel=channel).count() == 1


@pytest.mark.django_db
@override_settings(PARSER_MAX_PENDING_REQUESTS=10)
def test_parser_view_rejects_submission_when_pending_limit_reached() -> None:
    user = User.objects.create_user(
        username="queue-limit-user",
        email="queue-limit@example.com",
        password="password",
    )

    for index in range(10):
        ModerationRequest.objects.create(
            submitted_by=user,
            channel_identifier=f"channel_{index}",
            category="Технологии",
            country="RU",
            language="ru",
            status="pending",
        )

    view = ParserView()
    request = RequestFactory().post("/parser/")
    request.user = user
    request.session = {}
    setattr(request, "_messages", FallbackStorage(request))
    view.setup(request)

    form = view.get_form_class()(
        data={
            "channel_identifier": "@new_channel",
            "category": "Технологии",
            "country": "RU",
            "language": "ru",
            "limit": 10,
        }
    )
    assert form.is_valid(), form.errors

    with patch.object(view, "async_tg_parser") as mock_parser:
        response = view.form_valid(form)

    assert response.status_code == 200
    assert ModerationRequest.objects.filter(submitted_by=user).count() == 10
    assert (
        "У вас уже максимальное количество необработанных заявок. "
        "Дождитесь рассмотрения предыдущих заявок." in form.non_field_errors()
    )
    mock_parser.assert_not_called()


@pytest.mark.django_db
@override_settings(PARSER_MAX_PENDING_REQUESTS=10)
def test_parser_view_counts_only_current_users_pending_requests() -> None:
    user = User.objects.create_user(
        username="queue-user",
        email="queue-user@example.com",
        password="password",
    )
    other_user = User.objects.create_user(
        username="other-queue-user",
        email="other-queue-user@example.com",
        password="password",
    )

    for index in range(10):
        ModerationRequest.objects.create(
            submitted_by=other_user,
            channel_identifier=f"other_channel_{index}",
            category="Технологии",
            country="RU",
            language="ru",
            status="pending",
        )

    view = ParserView()
    request = RequestFactory().post("/parser/")
    request.user = user
    request.session = {}
    setattr(request, "_messages", FallbackStorage(request))
    view.setup(request)

    form = view.get_form_class()(
        data={
            "channel_identifier": "@new_channel",
            "category": "Технологии",
            "country": "RU",
            "language": "ru",
            "limit": 10,
        }
    )
    assert form.is_valid(), form.errors

    parsed_data = {
        "title": "New Channel",
        "channel_id": 987654321,
        "username": "new_channel",
        "verified": False,
        "creation_date": None,
        "last_messages": [],
        "average_views": 0,
        "participants_count": 100,
        "description": "New channel",
        "pinned_messages": [],
    }

    with patch.object(
        view,
        "async_tg_parser",
        return_value=parsed_data,
    ) as mock_parser:
        response = view.form_valid(form)

    assert response.status_code == 302
    mock_parser.assert_called_once_with("new_channel", 10)
    assert ModerationRequest.objects.filter(submitted_by=user).count() == 1
    assert (
        ModerationRequest.objects.filter(submitted_by=other_user).count() == 10
    )


@pytest.mark.django_db
@override_settings(PARSER_MAX_PENDING_REQUESTS=10)
def test_parser_view_allows_submission_below_pending_limit() -> None:
    user = User.objects.create_user(
        username="queue-below-limit-user",
        email="queue-below-limit@example.com",
        password="password",
    )

    for index in range(9):
        ModerationRequest.objects.create(
            submitted_by=user,
            channel_identifier=f"channel_{index}",
            category="Технологии",
            country="RU",
            language="ru",
            status="pending",
        )

    view = ParserView()
    request = RequestFactory().post("/parser/")
    request.user = user
    request.session = {}
    setattr(request, "_messages", FallbackStorage(request))
    view.setup(request)

    form = view.get_form_class()(
        data={
            "channel_identifier": "@new_channel",
            "category": "Технологии",
            "country": "RU",
            "language": "ru",
            "limit": 10,
        }
    )
    assert form.is_valid(), form.errors

    parsed_data = {
        "title": "New Channel",
        "channel_id": 987654321,
        "username": "new_channel",
        "verified": False,
        "creation_date": None,
        "last_messages": [],
        "average_views": 0,
        "participants_count": 100,
        "description": "New channel",
        "pinned_messages": [],
    }

    with patch.object(
        view,
        "async_tg_parser",
        return_value=parsed_data,
    ) as mock_parser:
        response = view.form_valid(form)

    assert response.status_code == 302
    mock_parser.assert_called_once_with("new_channel", 10)
    assert (
        ModerationRequest.objects.filter(
            submitted_by=user,
            status="pending",
        ).count()
        == 10
    )
