"""Legal page tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_legal_pages_list():
    res = client.get("/api/v1/legal/pages")
    assert res.status_code == 200
    slugs = [p["slug"] for p in res.json()]
    assert "terms" in slugs
    assert "privacy" in slugs
    assert "popia" in slugs


def test_legal_page_terms():
    res = client.get("/api/v1/legal/pages/terms")
    assert res.status_code == 200
    data = res.json()
    assert "iPayGo" in data["disclaimer"]
    assert data["title"] == "Terms of Use"


def test_health_v6():
    res = client.get("/health")
    assert res.json()["version"] == "6.1.0"
