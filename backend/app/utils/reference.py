import secrets
from datetime import UTC, datetime


def generate_transfer_reference() -> str:
    date_part = datetime.now(UTC).strftime("%y%m%d")
    random_part = secrets.token_hex(3).upper()
    return f"TA{date_part}{random_part}"
