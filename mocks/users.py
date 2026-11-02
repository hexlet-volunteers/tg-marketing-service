DEMO_PASSWORD = "demo123"  # noqa: S105

DEMO_USERNAMES = [
    "demo_admin",
    "demo_user",
    "demo_partner",
    "demo_moderator",
]

DEMO_LOGIN = {
    "demo_admin": {"password": DEMO_PASSWORD},
    "demo_user": {"password": DEMO_PASSWORD},
    "demo_partner": {"password": DEMO_PASSWORD},
    "demo_moderator": {"password": DEMO_PASSWORD},
}

ROLE_LABELS = {
    "user": "Пользователь",
    "guest": "Гость",
    "channel_moderator": "Модератор канала",
    "partner": "Партнёр",
}
