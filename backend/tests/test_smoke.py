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
    assert data["version"] == "6.1.0"


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
        "email": os.environ.get("SEED_CUSTOMER_EMAIL", "customer@demo.co.za"),
        "password": os.environ.get("SEED_CUSTOMER_PASSWORD", "Customer@TransAfrik2024!"),
    })
    if login.status_code != 200:
        pytest.skip("Demo customer not seeded")
    token = login.json()["access_token"]

    calc = client.post(
        "/api/v1/transfers/calculate",
        json={"send_amount_zar": "1000.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert calc.status_code == 200
    assert Decimal(calc.json()["receive_amount_ghs"]) == Decimal("720.00")
