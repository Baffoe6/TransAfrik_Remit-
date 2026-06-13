"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { MukuruBatch, MukuruReconciliation } from "@/types";
import { formatCurrency } from "@/lib/utils";

export default function MukuruOperationsPage() {
  const [batches, setBatches] = useState<MukuruBatch[]>([]);
  const [recon, setRecon] = useState<MukuruReconciliation | null>(null);

  const load = () => {
    api<MukuruBatch[]>("/admin/mukuru/batches").then(setBatches).catch(() => {});
    api<MukuruReconciliation>("/admin/mukuru/reconciliation").then(setRecon).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const approve = async (batchId: string) => {
    await api(`/admin/mukuru/batches/${batchId}/approve`, { method: "POST" });
    load();
  };

  const submit = async (batchId: string) => {
    await api(`/admin/mukuru/batches/${batchId}/submit`, { method: "POST" });
    load();
  };

  const statusColor = (s: string) => {
    if (s === "reconciled") return "bg-green-100 text-green-800";
    if (s === "submitted") return "bg-blue-100 text-blue-800";
    if (s === "pending_approval") return "bg-amber-100 text-amber-800";
    return "bg-gray-100 text-gray-700";
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Mukuru Operations</h1>

      {recon && (
        <div className="grid gap-4 sm:grid-cols-4">
          <Card><CardContent className="pt-6"><p className="text-sm text-gray-500">Pending Approval</p><p className="text-2xl font-bold">{recon.pending_approval}</p></CardContent></Card>
          <Card><CardContent className="pt-6"><p className="text-sm text-gray-500">Submitted</p><p className="text-2xl font-bold">{recon.submitted}</p></CardContent></Card>
          <Card><CardContent className="pt-6"><p className="text-sm text-gray-500">Reconciled</p><p className="text-2xl font-bold">{recon.reconciled}</p></CardContent></Card>
          <Card><CardContent className="pt-6"><p className="text-sm text-gray-500">Settlement Variance</p><p className="text-2xl font-bold">{formatCurrency(recon.settlement_variance_zar, "ZAR")}</p></CardContent></Card>
        </div>
      )}

      <Card>
        <CardHeader><CardTitle>Batch Export History</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {batches.length === 0 ? (
            <p className="text-sm text-gray-500">No batches yet. Export transfers from the Transfers page to create a batch.</p>
          ) : (
            batches.map((b) => (
              <div key={b.id} className="flex flex-wrap items-center justify-between gap-2 rounded border p-3 text-sm">
                <div>
                  <p className="font-medium">{b.batch_id}</p>
                  <p className="text-gray-500">{b.transfer_count} transfers · {formatCurrency(b.total_amount_zar, "ZAR")}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${statusColor(b.status)}`}>{b.status.replace(/_/g, " ")}</span>
                  {b.status === "pending_approval" && <Button size="sm" onClick={() => approve(b.batch_id)}>Approve</Button>}
                  {b.status === "approved" && <Button size="sm" onClick={() => submit(b.batch_id)}>Submit</Button>}
                  <a href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/admin/mukuru/batches/${b.batch_id}/download`} className="text-[#1B5E3B] underline text-xs" target="_blank" rel="noreferrer">Download</a>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
