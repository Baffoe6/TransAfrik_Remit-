"""Compliance pack generator tests."""

from app.legal.content import DISCLAIMER, LEGAL_PAGES


def test_legal_disclaimer_content():
    assert "iPayGo" in DISCLAIMER
    assert "third-party" in DISCLAIMER.lower()


def test_all_compliance_pack_types_documented():
    assert "partner-disclaimer" in LEGAL_PAGES
    assert len(LEGAL_PAGES) >= 7
