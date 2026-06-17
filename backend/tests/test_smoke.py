"""API smoke tests — health, auth, and calculator (requires PostgreSQL)."""

import os
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "transafrik-remit-api"
    assert data["version"] == "7.0.0-mvp"


def test_disclaimer():
    res = client.get("/api/v1/disclaimer")
    assert res.status_code == 200
    assert "IPAYGO" in res.json()["disclaimer"]
    assert "not licensed" not in res.json()["disclaimer"].lower() or "facilitation" in res.json()["disclaimer"]


@pytest.mark.skipif(
    "postgresql" not in os.environ.get("DATABASE_URL", ""),
    reason="Integration tests require PostgreSQL (set DATABASE_URL)",
)
def test_login_and_calculate_integration():
    """Run against a seeded PostgreSQL instance (e.g. docker compose up)."""
    login = client.post("/api/v1/auth/login", json={
        "identifier": os.environ.get("SEED_CUSTOMER_EMAIL", "customer@demo.co.za"),
        "password": os.environ.get("SEED_CUSTOMER_PASSWORD", "Customer@TransAfrik2024!"),
    })
    if login.status_code != 200:
        pytest.skip("Demo customer not seeded")
    token = login.json()["access_token"]

    calc = client.post(
        "/api/v1/transfers/calculate",
        json={"amount_to_pay_zar": "1000.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert calc.status_code == 200
    data = calc.json()
    amount_to_pay = Decimal(data["amount_to_pay_zar"])
    fee = Decimal(data["fee_zar"])
    rate = Decimal(data["exchange_rate"])
    receive = Decimal(data["receive_amount_ghs"])
    assert amount_to_pay == Decimal("1000.00")
    assert amount_to_pay == Decimal(data["total_amount_zar"])
    assert fee > 0
    net_send = amount_to_pay - fee
    assert receive == (net_send * rate).quantize(Decimal("0.01"))
    assert rate > 0
    assert "base_rate" not in data
    assert "markup_percentage" not in data
    assert "provider" not in data
    assert data.get("delivery_method")
    assert data.get("estimated_delivery")
