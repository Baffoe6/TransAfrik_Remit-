"""Voucher and barcode generation utilities for payment collection providers."""

import hashlib
import secrets
from datetime import date, datetime, timedelta, UTC
from decimal import Decimal


def generate_voucher_number(prefix: str = "V") -> str:
    return f"{prefix}{secrets.token_hex(4).upper()}"


def generate_reference_number(provider: str, transfer_reference: str) -> str:
    suffix = hashlib.sha256(f"{provider}:{transfer_reference}:{secrets.token_hex(4)}".encode()).hexdigest()[:8].upper()
    if provider == "pay_at":
        return f"PAYAT-{transfer_reference}-{suffix}"
    if provider == "easy_pay":
        return f"EP{suffix}"
    return f"{provider.upper()}-{suffix}"


def generate_barcode_data(provider: str, reference: str, voucher: str, amount: Decimal) -> str:
    """Code 128 compatible payload string for retailer scanners."""
    amount_cents = int(amount * 100)
    return f"|{provider.upper()}|{reference}|{voucher}|{amount_cents:010d}|"


def generate_qr_url(provider: str, reference: str) -> str:
    domains = {"pay_at": "payat.co.za", "easy_pay": "easypay.co.za"}
    domain = domains.get(provider, "transafrik.co.za")
    return f"https://{domain}/pay/{reference}"


def default_expiry(days: int = 3) -> date:
    return (datetime.now(UTC) + timedelta(days=days)).date()
