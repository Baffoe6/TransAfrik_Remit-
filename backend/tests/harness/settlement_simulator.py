"""Simulate settlement reconciliation for integration tests."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class SettlementLine:
    reference: str
    amount_zar: Decimal
    status: str


class SettlementSimulator:
    def __init__(self, provider_code: str = "mukuru_api"):
        self.provider_code = provider_code

    def generate_report(self, references: list[str], amount: Decimal = Decimal("1000.00")) -> list[SettlementLine]:
        return [
            SettlementLine(reference=ref, amount_zar=amount, status="settled")
            for ref in references
        ]

    def reconcile(self, expected: list[str], report: list[SettlementLine]) -> dict:
        report_refs = {line.reference for line in report}
        matched = [r for r in expected if r in report_refs]
        missing = [r for r in expected if r not in report_refs]
        extra = [line.reference for line in report if line.reference not in expected]
        return {
            "provider": self.provider_code,
            "matched": matched,
            "missing": missing,
            "extra": extra,
            "balanced": len(missing) == 0 and len(extra) == 0,
        }
