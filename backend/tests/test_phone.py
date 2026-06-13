"""Tests for phone number utilities."""

import pytest

from app.utils.phone import format_phone_number, is_email_identifier, normalize_phone_number, validate_phone_number


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("+27721234567", "+27721234567"),
        ("0721234567", "+27721234567"),
        ("+233201234567", "+233201234567"),
        ("+263771234567", "+263771234567"),
        ("+254712345678", "+254712345678"),
        ("+256701234567", "+256701234567"),
    ],
)
def test_normalize_phone_number(raw, expected):
    assert normalize_phone_number(raw) == expected


def test_validate_phone_number_rejects_invalid():
    with pytest.raises(ValueError):
        validate_phone_number("123")


def test_format_phone_number():
    assert "+27" in format_phone_number("+27721234567")


def test_is_email_identifier():
    assert is_email_identifier("user@example.com")
    assert not is_email_identifier("+27721234567")
