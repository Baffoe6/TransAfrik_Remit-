"""Flutterwave per-method payment_options mapping."""

from app.payment_providers.flutterwave_options import (
    FLUTTERWAVE_METHOD_CODES,
    resolve_flutterwave_payment_options,
)


def test_flutterwave_method_codes_include_split_methods():
    assert "fw_card" in FLUTTERWAVE_METHOD_CODES
    assert "fw_capitec" in FLUTTERWAVE_METHOD_CODES


def test_resolve_flutterwave_payment_options_per_method():
    assert resolve_flutterwave_payment_options("fw_card") == "card"
    assert resolve_flutterwave_payment_options("fw_eft") == "banktransfer"
    assert resolve_flutterwave_payment_options("fw_capitec") == "capitecpay"
    assert resolve_flutterwave_payment_options("fw_1voucher") == "1voucher"
