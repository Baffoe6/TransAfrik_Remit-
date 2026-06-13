"""Phase 6.1: webhook security tests."""

import uuid
from unittest.mock import MagicMock

from app.webhooks.security import (
    check_idempotency,
    check_nonce_replay,
    secure_webhook_ingress,
    verify_hmac_signature,
)
from tests.harness.webhook_simulator import WebhookSimulator


def _mock_db_no_events():
    db = MagicMock()
    query = MagicMock()
    query.filter.return_value.first.return_value = None
    db.query.return_value = query
    return db


def test_hmac_verification():
    secret = "webhook-secret-test"
    payload = b'{"event_type":"payment.paid","id":"evt_1"}'
    sim = WebhookSimulator("pay_at", secret)
    sig = sim.sign(payload)
    assert verify_hmac_signature(payload, sig, secret)
    assert not verify_hmac_signature(payload, "bad-sig", secret)


def test_replay_nonce_rejected():
    nonce = f"nonce-{uuid.uuid4().hex}"
    ok1, _ = check_nonce_replay(nonce)
    ok2, err = check_nonce_replay(nonce)
    assert ok1 is True
    assert ok2 is False
    assert "replay" in (err or "").lower()


def test_idempotency_duplicate():
    db = _mock_db_no_events()
    provider = "pay_at"
    external_id = f"ext-{uuid.uuid4().hex}"
    ok1, _ = check_idempotency(db, provider, external_id)
    ok2, err = check_idempotency(db, provider, external_id)
    assert ok1 is True
    assert ok2 is False
    assert "Duplicate" in (err or "")


def test_secure_webhook_ingress_valid():
    db = _mock_db_no_events()
    secret = "ingress-secret"
    sim = WebhookSimulator("pay_at", secret)
    body, payload, headers = sim.build_request("payment.paid", reference="REF-100")
    ok, err, ext_id = secure_webhook_ingress(
        db,
        provider_code="pay_at",
        body=body,
        payload=payload,
        signature=headers["X-Signature"],
        secret=secret,
        timestamp_header=headers["X-Webhook-Timestamp"],
        nonce_header=headers["X-Webhook-Nonce"],
    )
    assert ok is True
    assert err is None
    assert ext_id is not None
