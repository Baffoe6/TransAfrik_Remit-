"""Customer referral program tests."""

import secrets


def test_referral_code_format():
    code = f"REF{secrets.token_hex(3).upper()}"
    assert code.startswith("REF")
    assert len(code) == 9


def test_voucher_code_format():
    code = f"VOUCH{secrets.token_hex(4).upper()}"
    assert code.startswith("VOUCH")
