"""Flutterwave checkout payment_options per customer-facing method."""

from __future__ import annotations

# Flutterwave v3 payment_options values (South Africa checkout)
FLUTTERWAVE_ALL_OPTIONS = "card,banktransfer,ussd,account,capitecpay,1voucher"

FLUTTERWAVE_CHECKOUT_METHODS: tuple[dict[str, str], ...] = (
    {
        "code": "fw_card",
        "name": "Card payment",
        "description": "Debit or credit card via Flutterwave",
        "payment_options": "card",
    },
    {
        "code": "fw_eft",
        "name": "Bank transfer (EFT)",
        "description": "Pay by EFT from your South African bank account",
        "payment_options": "banktransfer",
    },
    {
        "code": "fw_capitec",
        "name": "Capitec Pay",
        "description": "Pay instantly with Capitec Pay",
        "payment_options": "capitecpay",
    },
    {
        "code": "fw_1voucher",
        "name": "1Voucher",
        "description": "Pay with a 1Voucher PIN",
        "payment_options": "1voucher",
    },
    {
        "code": "fw_ussd",
        "name": "USSD",
        "description": "Pay via mobile USSD banking",
        "payment_options": "ussd",
    },
    {
        "code": "fw_account",
        "name": "Bank account",
        "description": "Pay directly from your linked bank account",
        "payment_options": "account",
    },
)

FLUTTERWAVE_METHOD_CODES = frozenset(m["code"] for m in FLUTTERWAVE_CHECKOUT_METHODS) | frozenset({"flutterwave"})

_CODE_TO_OPTIONS: dict[str, str] = {m["code"]: m["payment_options"] for m in FLUTTERWAVE_CHECKOUT_METHODS}
_CODE_TO_OPTIONS["flutterwave"] = FLUTTERWAVE_ALL_OPTIONS


def resolve_flutterwave_payment_options(method_code: str) -> str:
    return _CODE_TO_OPTIONS.get(method_code, FLUTTERWAVE_ALL_OPTIONS)
