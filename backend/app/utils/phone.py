"""International mobile number normalization, validation, and formatting."""

import re

# Supported corridor / onboarding country calling codes (E.164)
SUPPORTED_COUNTRY_CODES = ("27", "233", "263", "254", "256", "260", "234")

_E164_RE = re.compile(r"^\+[1-9]\d{7,14}$")


def normalize_phone_number(raw: str, default_country_code: str = "27") -> str:
    """Normalize to E.164 (+{country}{national_number})."""
    if not raw or not str(raw).strip():
        raise ValueError("Mobile number is required")

    cleaned = re.sub(r"[^\d+]", "", str(raw).strip())
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    if cleaned.startswith("+"):
        digits = cleaned[1:]
    elif cleaned.startswith("0"):
        digits = default_country_code + cleaned[1:]
    else:
        digits = cleaned

    if not digits.isdigit():
        raise ValueError("Mobile number must contain only digits")

    for code in sorted(SUPPORTED_COUNTRY_CODES, key=len, reverse=True):
        if digits.startswith(code) and len(digits) >= len(code) + 7:
            return f"+{digits}"

    if len(digits) >= 9:
        return f"+{default_country_code}{digits}" if not any(
            digits.startswith(c) for c in SUPPORTED_COUNTRY_CODES
        ) else f"+{digits}"

    raise ValueError("Mobile number is too short")


def validate_phone_number(raw: str, default_country_code: str = "27") -> str:
    """Normalize and validate; returns E.164 string."""
    normalized = normalize_phone_number(raw, default_country_code)
    if not _E164_RE.match(normalized):
        raise ValueError("Invalid mobile number format")
    national = normalized[1:]
    if not any(national.startswith(code) for code in SUPPORTED_COUNTRY_CODES):
        raise ValueError(
            "Unsupported country code. Supported: South Africa (+27), Ghana (+233), "
            "Zimbabwe (+263), Kenya (+254), Uganda (+256), Zambia (+260), Nigeria (+234)"
        )
    return normalized


def format_phone_number(e164: str) -> str:
    """Human-readable display for E.164 numbers."""
    if not e164:
        return ""
    normalized = e164 if e164.startswith("+") else f"+{e164}"
    for code in sorted(SUPPORTED_COUNTRY_CODES, key=len, reverse=True):
        if normalized[1:].startswith(code):
            rest = normalized[1 + len(code) :]
            if len(rest) <= 3:
                return f"+{code} {rest}"
            return f"+{code} {rest[:3]} {rest[3:]}"
    return normalized


def is_email_identifier(value: str) -> bool:
    return "@" in value.strip()
