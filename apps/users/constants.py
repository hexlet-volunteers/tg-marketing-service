from enum import StrEnum

ROLE_MAXLENGTH = 50
BIO_MAXLENGTH = 200


class UserRole(StrEnum):
    """Коды ролей пользователей приложения."""

    GUEST = "guest"
    USER = "user"
    PARTNER = "partner"
    ADMIN = "admin"
    STAFF = "staff"
    CHANNEL_MODERATOR = "channel_moderator"
