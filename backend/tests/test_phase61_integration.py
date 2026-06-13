"""Phase 6.1: integration harness end-to-end simulations."""

from decimal import Decimal

from tests.harness.provider_simulator import ProviderSimulator
from tests.harness.settlement_simulator import SettlementSimulator
from tests.harness.webhook_simulator import WebhookSimulator


def test_provider_simulator_flow():
    sim = ProviderSimulator("pay_at")
    intent = sim.create_payment_intent("500.00", "REF-SIM-001")
    assert intent.success
    assert intent.status == "pending"
    paid = sim.confirm_payment(intent.reference)
    assert paid.status == "paid"
    disbursed = sim.disburse_transfer(intent.reference)
    assert disbursed.status == "disbursed"


def test_webhook_simulator_signed_request():
    sim = WebhookSimulator("pay_at", "secret")
    body, payload, headers = sim.build_request("payment.paid", reference="REF-SIM-002")
    assert b"payment.paid" in body
    assert headers["X-Signature"]
    assert payload["reference"] == "REF-SIM-002"


def test_settlement_simulator_reconcile():
    refs = ["REF-A", "REF-B", "REF-C"]
    sim = SettlementSimulator()
    report = sim.generate_report(refs, amount=Decimal("1000"))
    result = sim.reconcile(refs, report)
    assert result["balanced"] is True
    assert len(result["matched"]) == 3
