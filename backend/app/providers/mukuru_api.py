"""Mukuru API-ready remittance provider interface."""

from typing import Any

from app.providers.base import (
    BatchExportResult,
    ProviderStatusResult,
    ProviderTransferResult,
    ReconcileResult,
    RemittanceProvider,
    TransferRequest,
)
from app.providers.manual_mukuru import ManualMukuruProvider


class MukuruApiProvider(RemittanceProvider):
    """
    Mukuru API provider — API-ready interface with manual fallback.

    TODO: Implement OAuth2 authentication and live transfer submission
    when Mukuru Enterprise API credentials are available.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}
        self._manual = ManualMukuruProvider()

    @property
    def provider_code(self) -> str:
        return "mukuru_api"

    def validate_credentials(self) -> bool:
        return bool(self._config.get("client_id") and self._config.get("client_secret"))

    def get_api_status(self) -> dict[str, Any]:
        return {
            "provider": "mukuru_api",
            "configured": self.validate_credentials(),
            "mode": "api" if self.validate_credentials() else "manual_fallback",
        }

    def create_transfer(self, request: TransferRequest) -> ProviderTransferResult:
        if self.validate_credentials():
            return ProviderTransferResult(
                success=False,
                message="Mukuru API transfer submission not yet implemented",
            )
        return self._manual.create_transfer(request)

    def get_transfer_status(self, reference: str) -> ProviderStatusResult:
        if self.validate_credentials():
            return ProviderStatusResult(reference=reference, status="api_not_implemented")
        return self._manual.get_transfer_status(reference)

    def cancel_transfer(self, reference: str) -> ProviderTransferResult:
        return self._manual.cancel_transfer(reference)

    def export_batch(self, transfers: list[TransferRequest], output_dir: str) -> BatchExportResult:
        return self._manual.export_batch(transfers, output_dir)

    def reconcile_transfer(self, reference: str, provider_data: dict[str, Any]) -> ReconcileResult:
        return self._manual.reconcile_transfer(reference, provider_data)
