"""Simulate signed inbound webhooks for integration tests."""

import hashlib
import hmac
import json
import time
import uuid


class WebhookSimulator:
    def __init__(self, provider_code: str, secret: str):
        self.provider_code = provider_code
        self.secret = secret

    def build_payload(
        self,
        event_type: str,
        *,
        reference: str | None = None,
        status: str = "paid",
        extra: dict | None = None,
    ) -> dict:
        payload = {
            "event_type": event_type,
            "type": event_type,
            "id": reference or f"evt_{uuid.uuid4().hex[:12]}",
            "reference": reference or f"TXN-{uuid.uuid4().hex[:8].upper()}",
            "status": status,
            "provider": self.provider_code,
        }
        if extra:
            payload.update(extra)
        return payload

    def sign(self, body: bytes) -> str:
        return hmac.new(self.secret.encode(), body, hashlib.sha256).hexdigest()

    def build_request(
        self,
        event_type: str,
        *,
        reference: str | None = None,
        status: str = "paid",
        extra: dict | None = None,
    ) -> tuple[bytes, dict, dict]:
        payload = self.build_payload(event_type, reference=reference, status=status, extra=extra)
        body = json.dumps(payload).encode()
        headers = {
            "X-Signature": self.sign(body),
            "X-Webhook-Timestamp": str(int(time.time())),
            "X-Webhook-Nonce": uuid.uuid4().hex,
        }
        return body, payload, headers
