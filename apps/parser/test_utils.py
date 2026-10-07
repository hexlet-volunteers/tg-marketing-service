import pytest

from apps.parser.utils import normalize_channel_username


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("@Example_Channel", "example_channel"),
        ("Example_Channel", "example_channel"),
        ("t.me/Example_Channel", "example_channel"),
    ],
)
def test_normalize_channel_username(value: str, expected: str) -> None:
    assert normalize_channel_username(value) == expected