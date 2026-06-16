"""Flutterwave Checkout — card, bank transfer, Capitec Pay, 1Voucher, and more."""

import logging
import secrets
from typing import Any

import httpx

from app.config import get_settings
from app.payment_providers.base import (
    PaymentProvider,
    PaymentReferenceRequest,
    PaymentReferenceResult,
    PaymentStatusResult,
    WebhookResult,
)

logger = logging.getLogger(__name__)

FLUTTERWAVE_API = "https://api.flutterwave.com/v3"
# SA checkout payment options supported by Flutterwave
DEFAULT_PAYMENT_OPTIONS = "card,banktransfer,ussd,account,capitecpay,1voucher,mpesa"


class FlutterwaveProvider(PaymentProvider):
    PROVIDER = "flutterwave"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        settings = get_settings()
        self.secret_key = self.config.get("secret_key") or settings.flutterwave_secret_key
        self.public_key = self.config.get("public_key") or settings.flutterwave_public_key
        self.redirect_url = self.config.get("redirect_url") or settings.flutterwave_redirect_url
        self.is_live = bool(self.secret_key)

    @property
    def provider_code(self) -> str:
        return self.PROVIDER

    def generate_reference(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        return self.initiate_payment(request)

    def initiate_payment(self, request: PaymentReferenceRequest) -> PaymentReferenceResult:
        tx_ref = f"TA_{request.transfer_reference}_{secrets.token_hex(4)}"
        if self.is_live:
            return self._initiate_live(request, tx_ref)
        return self._initiate_sandbox(request, tx_ref)

    def _initiate_live(self, request: PaymentReferenceRequest, tx_ref: str) -> PaymentReferenceResult:
        payload = {
            "tx_ref": tx_ref,
            "amount": float(request.amount),
            "currency": request.currency or "ZAR",
            "redirect_url": self.redirect_url,
            "payment_options": DEFAULT_PAYMENT_OPTIONS,
            "customer": {
                "email": request.customer_email or f"{tx_ref}@ipaygo.co.za",
                "phonenumber": request.customer_phone or "",
                "name": request.customer_name,
            },
            "customizations": {
                "title": "TransAfrik Remit",
                "description": f"Transfer {request.transfer_reference}",
                "logo": "https://app.ipaygo.co.za/logo.png",
            },
            "meta": {
                "transfer_reference": request.transfer_reference,
                **(request.metadata or {}),
            },
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    f"{FLUTTERWAVE_API}/payments",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.secret_key}"},
                )
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            logger.exception("Flutterwave payment initiation failed")
            return PaymentReferenceResult(
                success=False,
                reference_number=tx_ref,
                message=f"Flutterwave error: {exc}",
            )

        data = body.get("data") or {}
        link = data.get("link")
        if not link:
            return PaymentReferenceResult(
                success=False,
                reference_number=tx_ref,
                message=body.get("message", "No checkout link returned"),
            )

        return PaymentReferenceResult(
            success=True,
            reference_number=tx_ref,
            message="Complete payment on Flutterwave Checkout",
            metadata={
                "payment_url": link,
                "tx_ref": tx_ref,
                "flw_ref": data.get("flw_ref"),
                "mode": "live",
                "payment_options": DEFAULT_PAYMENT_OPTIONS,
            },
        )

    def _initiate_sandbox(self, request: PaymentReferenceRequest, tx_ref: str) -> PaymentReferenceResult:
        base = get_settings().cors_origins.split(",")[0].strip() if get_settings().cors_origins else "https://app.ipaygo.co.za"
        payment_url = f"{base}/payment/flutterwave?tx_ref={tx_ref}&amount={request.amount}"
        return PaymentReferenceResult(
            success=True,
            reference_number=tx_ref,
            message="Sandbox Flutterwave checkout — configure FLUTTERWAVE_SECRET_KEY for live payments",
            metadata={
                "payment_url": payment_url,
                "tx_ref": tx_ref,
                "mode": "sandbox",
                "payment_options": DEFAULT_PAYMENT_OPTIONS,
                "amount_zar": str(request.amount),
            },
        )

    def check_payment_status(self, reference_number: str) -> PaymentStatusResult:
        if not self.is_live:
            return PaymentStatusResult(reference_number=reference_number, status="awaiting_payment")
        try:
            with httpx.Client(timeout=20.0) as client:
                resp = client.get(
                    f"{FLUTTERWAVE_API}/transactions/verify_by_reference",
                    params={"tx_ref": reference_number},
                    headers={"Authorization": f"Bearer {self.secret_key}"},
                )
                resp.raise_for_status()
                data = resp.json().get("data") or {}
        except Exception:
            return PaymentStatusResult(reference_number=reference_number, status="awaiting_payment")

        status = "paid" if data.get("status") == "successful" else "awaiting_payment"
        return PaymentStatusResult(reference_number=reference_number, status=status, metadata=data)

    def process_webhook(self, payload: dict) -> WebhookResult:
        event = payload.get("event") or payload.get("event_type") or ""
        if event != "charge.completed":
            return WebhookResult(success=False, raw_payload=payload)

        data = payload.get("data") or {}
        if not isinstance(data, dict) or data.get("status") != "successful":
            return WebhookResult(success=False, raw_payload=payload)

        ref = data.get("tx_ref") or data.get("reference")
        if not ref:
            return WebhookResult(success=False, raw_payload=payload)

        return WebhookResult(
            success=True,
            reference_number=str(ref),
            status="paid",
            raw_payload=payload,
        )

    def validate_credentials(self) -> bool:
        return self.is_live
