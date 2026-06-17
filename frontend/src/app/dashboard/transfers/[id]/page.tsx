"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GeneratePaymentForm } from "@/components/transfers/generate-payment-form";
import { PaymentReferenceCard } from "@/components/transfers/payment-reference-card";
import { StatusBadge } from "@/components/transfers/status-badge";
import { LiveTransferTracking } from "@/components/transfers/live-transfer-tracking";
import { api, apiUpload, getApiBaseUrl } from "@/lib/api";
import type { Transfer } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";

const UNPAID_CANCELLABLE = new Set([
  "quote_created",
  "draft",
  "awaiting_payment",
  "payment_pending",
  "checkout_created",
]);

const CANCELLATION_LABELS: Record<string, string> = {
  customer_cancelled: "Customer cancelled",
  expired_unpaid_24h: "Expired unpaid after 24 hours",
  admin_cancelled: "Admin cancelled",
  late_payment_received: "Late payment received after cancellation",
};

export default function TransferDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [transfer, setTransfer] = useState<Transfer | null>(null);
  const [uploading, setUploading] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    setError("");
    api<Transfer>(`/transfers/${id}`)
      .then(setTransfer)
      .catch((e) => setError(e.message || "Failed to load transfer"));
  }, [id]);

  useEffect(() => { load(); }, [load]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      await apiUpload(`/transfers/${id}/payment-proof`, form);
      load();
    } finally {
      setUploading(false);
    }
  };

  const downloadVoucher = async () => {
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${getApiBaseUrl()}/api/v1/payments/transfers/${id}/voucher.pdf`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `voucher-${transfer?.reference}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const markPaidTest = async () => {
    await api(`/payments/transfers/${id}/mark-paid`, { method: "POST" });
    load();
  };

  const cancelTransfer = async () => {
    if (!confirm("Only unpaid transfers can be cancelled. If you have already made payment, please do not cancel and contact support.")) {
      return;
    }
    setCancelling(true);
    try {
      await api(`/transfers/${id}/cancel`, { method: "POST" });
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not cancel transfer");
    } finally {
      setCancelling(false);
    }
  };

  if (error) return <p className="text-red-600">{error}</p>;
  if (!transfer) return <p className="text-gray-500">Loading transfer...</p>;

  const ref = transfer.payment_reference;
  const canUpload = ["awaiting_payment", "payment_pending_verification"].includes(transfer.status);
  const needsPayment = ["draft", "quote_created"].includes(transfer.status) && !ref;
  const canCancel = UNPAID_CANCELLABLE.has(transfer.status);
  const cancellationLabel = transfer.cancellation_reason
    ? CANCELLATION_LABELS[transfer.cancellation_reason] ?? transfer.cancellation_reason
    : null;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">{transfer.reference}</h1>
        <StatusBadge status={transfer.status} />
      </div>

      {transfer.status === "cancelled" && transfer.cancellation_reason === "expired_unpaid_24h" && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          Cancelled automatically because payment was not received within 24 hours.
        </div>
      )}

      {cancellationLabel && transfer.status === "cancelled" && (
        <p className="text-sm text-gray-600">{cancellationLabel}</p>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Transfer Details</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">Created</span><span>{formatDate(transfer.created_at)}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Amount paid</span><span className="font-semibold">{formatCurrency(transfer.total_amount_zar, "ZAR")}</span></div>
            <div className="flex justify-between pl-3 text-gray-500"><span>Includes transfer fee</span><span>{formatCurrency(transfer.fee_zar, "ZAR")}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Exchange rate</span><span>1 ZAR = {parseFloat(transfer.exchange_rate).toFixed(4)} GHS</span></div>
            <div className="flex justify-between border-t pt-3">
              <span className="font-medium text-[#1B5E3B]">Recipient Receives</span>
              <span className="text-lg font-bold">{formatCurrency(transfer.receive_amount_ghs, "GHS")}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Track Transfer</CardTitle></CardHeader>
          <CardContent>
            <LiveTransferTracking transferId={transfer.id} initialStatus={transfer.status} />
          </CardContent>
        </Card>
      </div>

      {needsPayment && <GeneratePaymentForm transferId={transfer.id} onGenerated={load} />}

      {ref && (
        <PaymentReferenceCard
          transferReference={transfer.reference}
          transferId={transfer.id}
          transferStatus={transfer.status}
          paymentRef={ref}
          onMarkPaid={markPaidTest}
          onDownloadVoucher={downloadVoucher}
        />
      )}

      {transfer.aml_flags && transfer.aml_flags.length > 0 && (
        <Card className="border-amber-200 bg-amber-50">
          <CardHeader><CardTitle className="text-amber-800">AML Review (Risk: {transfer.risk_score})</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-1 text-sm text-amber-700">
              {transfer.aml_flags.map((f, i) => <li key={i}>• {f.message}</li>)}
            </ul>
          </CardContent>
        </Card>
      )}

      {canCancel && (
        <Card>
          <CardHeader><CardTitle>Cancel transfer</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-gray-600">
              Only unpaid transfers can be cancelled. If you have already made payment, please do not cancel and contact support.
            </p>
            <Button variant="outline" onClick={cancelTransfer} disabled={cancelling}>
              {cancelling ? "Cancelling…" : "Cancel transfer"}
            </Button>
          </CardContent>
        </Card>
      )}

      {canUpload && ref?.banking_instructions && (
        <Card>
          <CardHeader><CardTitle>Upload Proof of Payment</CardTitle></CardHeader>
          <CardContent>
            <label className="flex cursor-pointer items-center justify-center gap-2 rounded-lg border-2 border-dashed border-[#1B5E3B]/30 p-6 hover:border-[#1B5E3B]">
              <Upload className="h-5 w-5 text-[#1B5E3B]" />
              <span className="text-sm">{uploading ? "Uploading..." : "Upload EFT / Deposit Proof"}</span>
              <input type="file" className="hidden" accept=".pdf,.jpg,.jpeg,.png" onChange={handleUpload} disabled={uploading} />
            </label>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
