"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/transfers/status-badge";
import { TransferNotificationLog } from "@/components/admin/TransferNotificationLog";
import { api } from "@/lib/api";
import type { Transfer } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function AdminTransferDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [transfer, setTransfer] = useState<Transfer | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Transfer>(`/admin/transfers/${id}`)
      .then(setTransfer)
      .catch((e) => setError(e.message));
  }, [id]);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!transfer) return <p className="text-gray-500">Loading…</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/admin/transfers" className="text-sm text-[#1B5E3B] hover:underline">← Back to transfers</Link>
          <h1 className="text-2xl font-bold text-[#1B5E3B]">{transfer.reference}</h1>
        </div>
        <StatusBadge status={transfer.status} />
      </div>

      <Card>
        <CardHeader><CardTitle>Transfer summary</CardTitle></CardHeader>
        <CardContent className="grid gap-2 text-sm sm:grid-cols-2">
          <div>Created: {formatDate(transfer.created_at)}</div>
          <div>Paid: {formatCurrency(transfer.total_amount_zar, "ZAR")}</div>
          <div>Fee: {formatCurrency(transfer.fee_zar, "ZAR")}</div>
          <div>Recipient receives: {formatCurrency(transfer.receive_amount_ghs, "GHS")}</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Notification log</CardTitle></CardHeader>
        <CardContent>
          <TransferNotificationLog transferId={transfer.id} />
        </CardContent>
      </Card>
    </div>
  );
}
