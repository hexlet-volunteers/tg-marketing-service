from django.core.validators import MaxLengthValidator, URLValidator

MAX_IMAGE_URL_LENGTH = 2048

_validate_length = MaxLengthValidator(
    MAX_IMAGE_URL_LENGTH,
    message="URL должен содержать не более %(limit_value)s символов.",
)
_validate_url = URLValidator(
    schemes=["http", "https"],
    message="Введите корректный URL с протоколом http:// или https://.",
)


def validate_http_url(value: str) -> None:
    _validate_length(value)
    _validate_url(value)
