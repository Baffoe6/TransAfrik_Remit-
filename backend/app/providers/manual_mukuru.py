import csv
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from app.providers.base import (
    BatchExportResult,
    ProviderStatusResult,
    ProviderTransferResult,
    ReconcileResult,
    RemittanceProvider,
    TransferRequest,
)

MUKURU_CSV_FIELDS = [
    "Transfer ID",
    "Customer Name",
    "Customer Phone",
    "Recipient Name",
    "Recipient Country",
    "Recipient Mobile Number",
    "Provider",
    "Amount ZAR",
    "Amount Destination Currency",
    "Reference Number",
    "Status",
]


class ManualMukuruProvider(RemittanceProvider):
    """
    Manual Mukuru Enterprise provider.
    Generates batch CSV/Excel files for manual processing — no API calls.

    TODO: Replace with MukuruProvider API integration when credentials are available.
    """

    @property
    def provider_code(self) -> str:
        return "manual_mukuru"

    def create_transfer(self, request: TransferRequest) -> ProviderTransferResult:
        provider_ref = f"MUK-MANUAL-{request.reference}"
        return ProviderTransferResult(
            success=True,
            provider_reference=provider_ref,
            message="Transfer queued for manual Mukuru Enterprise batch processing",
            metadata={"mode": "manual", "queued_at": datetime.now(UTC).isoformat()},
        )

    def get_transfer_status(self, reference: str) -> ProviderStatusResult:
        return ProviderStatusResult(
            reference=reference,
            status="pending_manual_processing",
            metadata={"message": "Awaiting manual Mukuru Enterprise processing"},
        )

    def cancel_transfer(self, reference: str) -> ProviderTransferResult:
        return ProviderTransferResult(success=True, message=f"Transfer {reference} marked for cancellation")

    def _row(self, batch_id: str, t: TransferRequest) -> dict[str, str]:
        return {
            "Transfer ID": str(t.transfer_id),
            "Customer Name": t.sender_name,
            "Customer Phone": t.sender_phone or "",
            "Recipient Name": t.beneficiary_name,
            "Recipient Country": t.beneficiary_country,
            "Recipient Mobile Number": t.mobile_wallet_number,
            "Provider": t.mobile_money_provider,
            "Amount ZAR": str(t.send_amount_zar),
            "Amount Destination Currency": str(t.receive_amount_ghs),
            "Reference Number": t.payment_reference or t.reference,
            "Status": t.status,
            "Batch_ID": batch_id,
        }

    def export_batch(self, transfers: list[TransferRequest], output_dir: str) -> BatchExportResult:
        batch_id = f"BATCH-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        csv_path = os.path.join(output_dir, f"{batch_id}.csv")
        fields = MUKURU_CSV_FIELDS + ["Batch_ID"]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for t in transfers:
                writer.writerow(self._row(batch_id, t))

        return BatchExportResult(
            success=True,
            batch_id=batch_id,
            file_path=csv_path,
            file_format="csv",
            transfer_count=len(transfers),
            message=f"Exported {len(transfers)} transfers to {csv_path}",
        )

    def export_excel(self, transfers: list[TransferRequest], output_dir: str) -> BatchExportResult:
        batch_id = f"BATCH-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        xlsx_path = os.path.join(output_dir, f"{batch_id}.xlsx")

        wb = Workbook()
        ws = wb.active
        ws.title = "Mukuru Batch"
        fields = MUKURU_CSV_FIELDS + ["Batch_ID"]
        ws.append(fields)
        for t in transfers:
            row = self._row(batch_id, t)
            ws.append([row[f] for f in fields])
        wb.save(xlsx_path)

        return BatchExportResult(
            success=True,
            batch_id=batch_id,
            file_path=xlsx_path,
            file_format="xlsx",
            transfer_count=len(transfers),
            message=f"Exported {len(transfers)} transfers to {xlsx_path}",
            excel_path=xlsx_path,
        )

    def reconcile_transfer(self, reference: str, provider_data: dict[str, Any]) -> ReconcileResult:
        matched = 1 if provider_data.get("reference") == reference else 0
        return ReconcileResult(
            success=matched > 0,
            matched=matched,
            unmatched=0 if matched else 1,
            details=[{"reference": reference, "status": provider_data.get("status", "completed")}],
        )

    def mark_as_submitted(self, reference: str) -> ProviderTransferResult:
        return ProviderTransferResult(
            success=True,
            provider_reference=f"MUK-SUB-{reference}",
            message=f"Transfer {reference} submitted to Mukuru Enterprise",
        )

    def mark_as_completed(self, reference: str) -> ProviderTransferResult:
        return ProviderTransferResult(
            success=True,
            message=f"Transfer {reference} marked as completed in Mukuru Enterprise",
        )
