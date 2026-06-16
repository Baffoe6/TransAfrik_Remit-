"""Flutterwave webhook verif-hash verification tests."""

import json
import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.database import get_db
from app.main import app
from app.models.enums import WebhookStatus
from app.payment_providers.flutterwave import FlutterwaveProvider
from app.webhooks.security import (
    extract_flutterwave_external_id,
    secure_flutterwave_webhook_ingress,
    verify_flutterwave_verif_hash,
)

WEBHOOK_SECRET = "flutterwave-test-verif-hash-secret"


def _mock_db_no_events():
    db = MagicMock()
    query = MagicMock()
    query.filter.return_value.first.return_value = None
    db.query.return_value = query
    return db


def _charge_completed_payload(*, event_id: int | None = None, tx_ref: str = "TA_REF_001") -> dict:
    return {
        "event": "charge.completed",
        "data": {
            "id": event_id or int(uuid.uuid4().int % 1_000_000_000),
            "tx_ref": tx_ref,
            "flw_ref": f"FLW-{uuid.uuid4().hex[:8]}",
            "status": "successful",
            "amount": 1000,
            "currency": "ZAR",
        },
    }


@pytest.fixture(autouse=True)
def flutterwave_secret_env(monkeypatch):
    from app.redis.client import _memory_store

    _memory_store.clear()
    monkeypatch.setenv("FLUTTERWAVE_WEBHOOK_SECRET", WEBHOOK_SECRET)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
    _memory_store.clear()


def test_verify_flutterwave_verif_hash_valid():
    ok, err = verify_flutterwave_verif_hash(WEBHOOK_SECRET, WEBHOOK_SECRET)
    assert ok is True
    assert err is None


def test_verify_flutterwave_verif_hash_missing_header():
    ok, err = verify_flutterwave_verif_hash(None, WEBHOOK_SECRET)
    assert ok is False
    assert err == "Missing verif-hash header"


def test_verify_flutterwave_verif_hash_invalid():
    ok, err = verify_flutterwave_verif_hash("wrong-hash-value", WEBHOOK_SECRET)
    assert ok is False
    assert err == "Invalid verif-hash"


def test_extract_flutterwave_external_id_from_data():
    payload = _charge_completed_payload(event_id=424242)
    assert extract_flutterwave_external_id(payload) == "424242"


def test_secure_flutterwave_webhook_ingress_duplicate_delivery():
    db = _mock_db_no_events()
    payload = _charge_completed_payload()

    ok1, err1, ext1 = secure_flutterwave_webhook_ingress(
        db,
        provider_code="flutterwave",
        payload=payload,
        verif_hash=WEBHOOK_SECRET,
        secret=WEBHOOK_SECRET,
    )
    ok2, err2, ext2 = secure_flutterwave_webhook_ingress(
        db,
        provider_code="flutterwave",
        payload=payload,
        verif_hash=WEBHOOK_SECRET,
        secret=WEBHOOK_SECRET,
    )

    assert ok1 is True and err1 is None
    assert ext1 is not None
    assert ok2 is False
    assert "Duplicate" in (err2 or "") or "already processed" in (err2 or "").lower()
    assert ext2 == ext1


def test_flutterwave_process_webhook_only_charge_completed():
    provider = FlutterwaveProvider()

    paid = provider.process_webhook(_charge_completed_payload())
    assert paid.success is True
    assert paid.status == "paid"

    failed_event = provider.process_webhook(
        {
            "event": "charge.failed",
            "data": {"tx_ref": "TA_REF_FAIL", "status": "failed"},
        }
    )
    assert failed_event.success is False

    wrong_status = provider.process_webhook(
        {
            "event": "charge.completed",
            "data": {"tx_ref": "TA_REF_PENDING", "status": "pending"},
        }
    )
    assert wrong_status.success is False


@pytest.fixture
def webhook_client(monkeypatch):
    from app.redis.client import _memory_store

    _memory_store.clear()
    db = MagicMock()
    query = MagicMock()
    query.filter.return_value.first.return_value = None
    db.query.return_value = query

    processed_events: list = []

    def fake_record_webhook(db_session, **kwargs):
        event = MagicMock()
        event.id = 99
        event.status = WebhookStatus.PROCESSED
        return event

    def fake_process_webhook(db_session, event):
        processed_events.append(event)
        event.status = WebhookStatus.PROCESSED
        return event

    monkeypatch.setattr("app.routers.webhooks.record_webhook", fake_record_webhook)
    monkeypatch.setattr("app.routers.webhooks.process_webhook", fake_process_webhook)
    monkeypatch.setattr("app.routers.webhooks.get_provider_config", lambda _db, _code: None)
    monkeypatch.setattr("app.routers.webhooks.queue_webhook_for_processing", lambda *args, **kwargs: False)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client, processed_events
    app.dependency_overrides.clear()
    _memory_store.clear()


def test_flutterwave_webhook_endpoint_valid_verif_hash(webhook_client):
    client, processed = webhook_client
    payload = _charge_completed_payload()

    response = client.post(
        "/api/v1/webhooks/flutterwave",
        content=json.dumps(payload),
        headers={"Content-Type": "application/json", "verif-hash": WEBHOOK_SECRET},
    )

    assert response.status_code == 200
    assert response.json()["received"] is True
    assert len(processed) == 1


def test_flutterwave_webhook_endpoint_missing_verif_hash(webhook_client):
    client, processed = webhook_client
    payload = _charge_completed_payload()

    response = client.post(
        "/api/v1/webhooks/flutterwave",
        json=payload,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing verif-hash header"
    assert processed == []


def test_flutterwave_webhook_endpoint_invalid_verif_hash(webhook_client):
    client, processed = webhook_client
    payload = _charge_completed_payload()

    response = client.post(
        "/api/v1/webhooks/flutterwave",
        content=json.dumps(payload),
        headers={"Content-Type": "application/json", "verif-hash": "not-the-secret"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid verif-hash"
    assert processed == []


def test_flutterwave_webhook_endpoint_duplicate_delivery(webhook_client):
    client, _processed = webhook_client
    payload = _charge_completed_payload(event_id=555001)
    headers = {"Content-Type": "application/json", "verif-hash": WEBHOOK_SECRET}

    first = client.post("/api/v1/webhooks/flutterwave", content=json.dumps(payload), headers=headers)
    second = client.post("/api/v1/webhooks/flutterwave", content=json.dumps(payload), headers=headers)

    assert first.status_code == 200
    assert second.status_code == 409
    assert "Duplicate" in second.json()["detail"] or "already processed" in second.json()["detail"].lower()
