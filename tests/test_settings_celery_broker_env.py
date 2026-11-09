"""Env-driven Celery broker settings (issue #381).

Container-ized development (docker compose) needs the broker and result
backend to point at the ``redis`` service instead of ``localhost``. The
settings must therefore read ``CELERY_BROKER_URL`` /
``CELERY_RESULT_BACKEND`` from the environment while keeping the
historical localhost default for bare-metal development.
"""

import importlib
import os

import pytest

CELERY_ENV_KEYS = ("CELERY_BROKER_URL", "CELERY_RESULT_BACKEND")


@pytest.fixture
def reload_settings(monkeypatch: pytest.MonkeyPatch):
    """Deterministic reload: .env loading is excluded from the test."""

    import config.settings as settings_module

    original_env = {key: os.environ.get(key) for key in CELERY_ENV_KEYS}

    import dotenv

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **k: None)

    def _do_reload(env: dict[str, str]):
        # Чистим env, чтобы вскрыть дефолт, затем подмешиваем ожидаемое.
        for key in CELERY_ENV_KEYS:
            monkeypatch.delenv(key, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        return importlib.reload(settings_module)

    yield _do_reload

    # Возвращаем settings-модуль к исходному состоянию до undo env.
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    importlib.reload(settings_module)


def test_broker_defaults_to_localhost(reload_settings):
    settings = reload_settings({})

    assert settings.CELERY_BROKER_URL == "redis://localhost:6379/0"
    assert settings.CELERY_RESULT_BACKEND == "redis://localhost:6379/0"


def test_broker_reads_env_for_compose(reload_settings):
    settings = reload_settings(
        {
            "CELERY_BROKER_URL": "redis://redis:6379/0",
            "CELERY_RESULT_BACKEND": "redis://redis:6379/1",
        }
    )

    assert settings.CELERY_BROKER_URL == "redis://redis:6379/0"
    assert settings.CELERY_RESULT_BACKEND == "redis://redis:6379/1"


def test_compose_points_services_at_interpolated_redis():
    """Compose может переопределить broker через .env-интерполяцию, но
    дефолт в контейнерах обязан быть redis-сервисом, а не localhost."""
    from pathlib import Path

    compose_path = Path(__file__).resolve().parents[1] / "compose.yml"
    compose = compose_path.read_text(encoding="utf-8")

    assert "redis://localhost" not in compose
    assert compose.count("${CELERY_BROKER_URL:-") == 4  # web/worker/beat/flower
    # Beat пишет расписание в /tmp, а не в репозиторий root-файлом.
    assert "--schedule=/tmp/celerybeat-schedule" in compose


def test_static_root_is_env_driven(monkeypatch: pytest.MonkeyPatch):
    """statics collects into /tmp in containers via STATIC_ROOT env."""
    import config.settings as settings_module

    monkeypatch.setenv("STATIC_ROOT", "tmp/staticfiles-test")
    importlib.reload(settings_module)
    assert settings_module.STATIC_ROOT == "tmp/staticfiles-test"

    monkeypatch.delenv("STATIC_ROOT", raising=False)
    importlib.reload(settings_module)
    assert str(settings_module.STATIC_ROOT).endswith("staticfiles")
