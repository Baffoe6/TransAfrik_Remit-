"""Tests for MVP modules: partners, waitlist, dashboard."""

import os
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.providers.partners.registry import get_partner_provider, list_partner_providers
from app.services.transfer_status_mapper import to_mvp_status
from app.models.enums import TransferStatus

client = TestClient(app)


def test_partner_mock_quote():
    provider = get_partner_provider("flutterwave")
    quote = provider.quote(corridor="ZA-GH", send_amount=Decimal("1000"))
    assert quote.payout_amount > 0
    assert quote.provider_code == "flutterwave"


def test_partner_registry():
    codes = list_partner_providers()
    assert "mukuru" in codes
    assert "flutterwave" in codes
    assert "onafriq" in codes
    assert "veengu" in codes


def test_transfer_mvp_status_mapping():
    assert to_mvp_status(TransferStatus.DRAFT) == "DRAFT"
    assert to_mvp_status(TransferStatus.COMPLETED) == "COMPLETED"
    assert to_mvp_status(TransferStatus.COMPLIANCE_REVIEW) == "UNDER_REVIEW"
    assert to_mvp_status(TransferStatus.PAYMENT_VERIFIED) == "FUNDS_RECEIVED"


@pytest.mark.skipif(
    "postgresql" not in os.environ.get("DATABASE_URL", ""),
    reason="Integration tests require PostgreSQL (set DATABASE_URL)",
)
def test_waitlist_join_integration():
    res = client.post("/api/v1/waitlist/join", json={
        "first_name": "Test",
        "last_name": "Lead",
        "mobile": "+27123456789",
        "email": "waitlist-test@example.com",
        "country_from": "ZA",
        "country_to": "GH",
        "estimated_monthly_volume": "Under R5,000",
    })
    assert res.status_code == 200
    assert res.json()["joined"] is True


@pytest.mark.skipif(
    "postgresql" not in os.environ.get("DATABASE_URL", ""),
    reason="Integration tests require PostgreSQL (set DATABASE_URL)",
)
def test_dashboard_summary_integration():
    login = client.post("/api/v1/auth/login", json={
        "identifier": os.environ.get("SEED_CUSTOMER_EMAIL", "customer@demo.co.za"),
        "password": os.environ.get("SEED_CUSTOMER_PASSWORD", "Customer@TransAfrik2024!"),
    })
    if login.status_code != 200:
        pytest.skip("Demo customer not seeded")
    token = login.json()["access_token"]
    res = client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "profile_completion" in data
    assert "kyc" in data
    assert "beneficiaries" in data
    assert "transfers" in data
    assert "referral_program" in data
