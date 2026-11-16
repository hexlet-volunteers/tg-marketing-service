import pytest
from django.core.exceptions import ValidationError

from apps.users.validators import MAX_IMAGE_URL_LENGTH, validate_http_url

URL_PREFIX = "https://example.com/"
MAX_LENGTH_URL = URL_PREFIX + "a" * (MAX_IMAGE_URL_LENGTH - len(URL_PREFIX))
INVALID_IMAGE_URLS = (
    "javascript:alert(1)",
    "data:image/svg+xml,<svg onload=alert(1)></svg>",
    "ftp://example.com/avatar.jpg",
    "ftps://example.com/avatar.jpg",
    "vbscript:msgbox(1)",
    "//example.com/avatar.jpg",
    "/static/avatar.jpg",
    "not-a-url",
    MAX_LENGTH_URL + "a",
)
VALID_IMAGE_URLS = (
    "http://example.com/avatar.jpg",
    "https://example.com/avatar.jpg?size=128#image",
    "HTTPS://example.com/avatar.jpg",
    MAX_LENGTH_URL,
)


@pytest.mark.parametrize("url", VALID_IMAGE_URLS)
def test_http_url_validator_accepts_http_and_https(url: str) -> None:
    validate_http_url(url)


@pytest.mark.parametrize("url", (*INVALID_IMAGE_URLS, ""))
def test_http_url_validator_rejects_unsafe_or_malformed_urls(url: str) -> None:
    with pytest.raises(ValidationError):
        validate_http_url(url)


def test_http_url_validator_has_clear_length_error() -> None:
    with pytest.raises(ValidationError) as raised:
        validate_http_url(MAX_LENGTH_URL + "a")
    assert raised.value.code == "max_length"
    assert "2048" in str(raised.value)
