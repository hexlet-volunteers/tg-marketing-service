from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        # фильтр при котором DEBUG установлен в True
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        # фильтр при котором DEBUG установлен в False
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "formatters": {
        "simple": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
        "verbose": {
            "format": "{levelname} {asctime} {module} {funcName} (line:{lineno}) - {message}",
            "style": "{",
        },
    },
    "handlers": {
        # вывод в консоль при DEBUG = True
        "debug_console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        # вывод в файл django.log
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "django.log",
            "maxBytes": 2 * 1024 * 1024,  # 2 MB максимальный размер
            "backupCount": 5,
            "formatter": "verbose",
        },
        # вывод в файл errors.log
        "error_file": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "errors.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB максимальный размер
            "backupCount": 5,
            "formatter": "verbose",
        },
        # письмо на email при критических ошибках
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
    },
    "loggers": {
        # корневой логгер
        "": {
            "handlers": ["debug_console", "file", "error_file"],
            "level": "DEBUG",
        },
        # логгер django
        "django": {
            "handlers": ["debug_console", "file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        # логгер приложения
        "myapp": {
            "handlers": ["debug_console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
