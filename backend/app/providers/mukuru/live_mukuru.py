from typing import Any

from app.providers.base import (
    BatchExportResult,
    ProviderStatusResult,
    ProviderTransferResult,
    ReconcileResult,
    TransferRequest,
)
from app.providers.manual_mukuru import ManualMukuruProvider
from app.providers.mukuru.interface import MukuruProvider


class LiveMukuruProvider(MukuruProvider):
    """Live Mukuru API connector placeholder — wire OAuth2 when credentials available."""

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}
        self._manual = ManualMukuruProvider()

    @property
    def provider_code(self) -> str:
        return "live_mukuru"

    def validate_credentials(self) -> bool:
        return bool(self._config.get("client_id") and self._config.get("client_secret") and self._config.get("api_base_url"))

    def get_api_status(self) -> dict[str, Any]:
        return {
            "provider": "live_mukuru",
            "configured": self.validate_credentials(),
            "mode": "live" if self.validate_credentials() else "not_configured",
            "api_base_url": self._config.get("api_base_url"),
        }

    def create_transfer(self, request: TransferRequest) -> ProviderTransferResult:
        if not self.validate_credentials():
            return ProviderTransferResult(success=False, message="Live Mukuru credentials not configured")
        # TODO: POST /transfers to Mukuru Enterprise API
        return ProviderTransferResult(
            success=False,
            message="Live Mukuru API submission pending partner certification",
            metadata={"fallback": "use_manual_batch"},
        )

    def get_transfer_status(self, reference: str) -> ProviderStatusResult:
        if not self.validate_credentials():
            return self._manual.get_transfer_status(reference)
        return ProviderStatusResult(reference=reference, status="api_pending", metadata={"live": True})

    def cancel_transfer(self, reference: str) -> ProviderTransferResult:
        return self._manual.cancel_transfer(reference)

    def export_batch(self, transfers: list[TransferRequest], output_dir: str) -> BatchExportResult:
        return self._manual.export_batch(transfers, output_dir)

    def reconcile_transfer(self, reference: str, provider_data: dict[str, Any]) -> ReconcileResult:
        return self._manual.reconcile_transfer(reference, provider_data)
