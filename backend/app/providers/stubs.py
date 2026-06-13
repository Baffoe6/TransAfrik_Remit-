"""Remittance provider stubs — no live API integrations."""

from datetime import UTC, datetime
from typing import Any

from app.providers.base import (
    BatchExportResult,
    ProviderStatusResult,
    ProviderTransferResult,
    ReconcileResult,
    RemittanceProvider,
    TransferRequest,
)


class _StubRemittanceProvider(RemittanceProvider):
    def __init__(self, code: str):
        self._code = code

    @property
    def provider_code(self) -> str:
        return self._code

    def create_transfer(self, request: TransferRequest) -> ProviderTransferResult:
        return ProviderTransferResult(
            success=False,
            message=f"{self._code} API integration not yet implemented",
            metadata={"mode": "stub"},
        )

    def get_transfer_status(self, reference: str) -> ProviderStatusResult:
        return ProviderStatusResult(reference=reference, status="not_implemented")

    def cancel_transfer(self, reference: str) -> ProviderTransferResult:
        return ProviderTransferResult(success=False, message="Not implemented")

    def export_batch(self, transfers: list[TransferRequest], output_dir: str) -> BatchExportResult:
        return BatchExportResult(
            success=False, batch_id="", file_path="", file_format="", transfer_count=0, message="Not implemented"
        )

    def reconcile_transfer(self, reference: str, provider_data: dict[str, Any]) -> ReconcileResult:
        return ReconcileResult(success=False, matched=0, unmatched=1)


class MukuruProvider(_StubRemittanceProvider):
    def __init__(self):
        super().__init__("mukuru_api")


class VeenguProvider(_StubRemittanceProvider):
    def __init__(self):
        super().__init__("veengu")


class OnafriqProvider(_StubRemittanceProvider):
    def __init__(self):
        super().__init__("onafriq")


class FlutterwaveProvider(_StubRemittanceProvider):
    def __init__(self):
        super().__init__("flutterwave")


class StitchRemittanceProvider(_StubRemittanceProvider):
    def __init__(self):
        super().__init__("stitch_remit")
