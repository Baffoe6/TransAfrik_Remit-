from datetime import UTC, datetime
from typing import Any

from app.providers.base import ProviderStatusResult, ProviderTransferResult, TransferRequest
from app.providers.manual_mukuru import ManualMukuruProvider
from app.providers.mukuru.interface import MukuruProvider


class MockMukuruProvider(MukuruProvider):
    """Mock Mukuru provider for development and integration testing."""

    def __init__(self):
        self._manual = ManualMukuruProvider()

    @property
    def provider_code(self) -> str:
        return "mock_mukuru"

    def validate_credentials(self) -> bool:
        return True

    def get_api_status(self) -> dict[str, Any]:
        return {"provider": "mock_mukuru", "mode": "mock", "configured": True}

    def create_transfer(self, request: TransferRequest) -> ProviderTransferResult:
        return ProviderTransferResult(
            success=True,
            provider_reference=f"MUK-MOCK-{request.reference}",
            message="Mock Mukuru transfer accepted",
            metadata={"mode": "mock", "queued_at": datetime.now(UTC).isoformat()},
        )

    def get_transfer_status(self, reference: str) -> ProviderStatusResult:
        return ProviderStatusResult(reference=reference, status="processing", metadata={"mode": "mock"})

    def cancel_transfer(self, reference: str) -> ProviderTransferResult:
        return ProviderTransferResult(success=True, message=f"Mock cancel: {reference}")

    def export_batch(self, transfers, output_dir: str):
        return self._manual.export_batch(transfers, output_dir)

    def reconcile_transfer(self, reference: str, provider_data: dict[str, Any]):
        return self._manual.reconcile_transfer(reference, provider_data)
