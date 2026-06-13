"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/transfers/status-badge";
import { api, downloadFile } from "@/lib/api";
import type { Transfer } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";

function TransfersContent() {
  const searchParams = useSearchParams();
  const statusFilter = searchParams.get("status") || "";
  const [transfers, setTransfers] = useState<Transfer[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [error, setError] = useState("");

  const load = () => {
    const q = statusFilter ? `?status_filter=${statusFilter}` : "";
    api<Transfer[]>(`/admin/transfers${q}`)
      .then(setTransfers)
      .catch((e) => setError(e.message));
  };
  useEffect(() => { load(); }, [statusFilter]);

  const toggle = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const updateStatus = async (id: number, status: string) => {
    await api(`/admin/transfers/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) });
    load();
  };

  const verifyPayment = async (id: number) => {
    await api(`/admin/payments/transfers/${id}/verify`, {
      method: "POST",
      body: JSON.stringify({ status: "verified" }),
    });
    load();
  };

  const exportBatch = async () => {
    if (selected.size === 0) return;
    const result = await api<{ batch_id: string }>("/admin/mukuru/batches", {
      method: "POST",
      body: JSON.stringify({ transfer_ids: Array.from(selected) }),
    });
    alert(`Batch ${result.batch_id} created — pending approval. View in Mukuru Operations.`);
    setSelected(new Set());
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1B5E3B]">Transfer Management</h1>
          {statusFilter && <p className="text-sm text-gray-500">Filter: {statusFilter.replace(/_/g, " ")}</p>}
        </div>
        <Button onClick={exportBatch} disabled={selected.size === 0}>
          <Download className="h-4 w-4" /> Export Mukuru Batch ({selected.size})
        </Button>
      </div>
      {error && <p className="text-red-600">{error}</p>}
      <Card>
        <CardHeader><CardTitle>All Transfers</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-2" />
                  <th className="pb-3 pr-4">Reference</th>
                  <th className="pb-3 pr-4">Amount</th>
                  <th className="pb-3 pr-4">Status</th>
                  <th className="pb-3 pr-4">Risk</th>
                  <th className="pb-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {transfers.map((t) => (
                  <tr key={t.id} className="border-b">
                    <td className="py-3 pr-2">
                      <input type="checkbox" checked={selected.has(t.id)} onChange={() => toggle(t.id)} />
                    </td>
                    <td className="py-3 pr-4">
                      <p className="font-medium">{t.reference}</p>
                      <p className="text-xs text-gray-400">{formatDate(t.created_at)}</p>
                    </td>
                    <td className="py-3 pr-4">{formatCurrency(t.send_amount_zar, "ZAR")}</td>
                    <td className="py-3 pr-4"><StatusBadge status={t.status} /></td>
                    <td className="py-3 pr-4">{t.risk_score || "—"}</td>
                    <td className="py-3">
                      <div className="flex flex-wrap gap-1">
                        {t.status === "payment_pending_verification" && (
                          <Button size="sm" variant="outline" onClick={() => verifyPayment(t.id)}>Verify</Button>
                        )}
                        {t.status === "submitted_to_mukuru" && (
                          <Button size="sm" variant="outline" onClick={() => updateStatus(t.id, "processing")}>Processing</Button>
                        )}
                        {t.status === "processing" && (
                          <Button size="sm" variant="outline" onClick={() => updateStatus(t.id, "completed")}>Complete</Button>
                        )}
                        <Button size="sm" variant="ghost" onClick={() => {
                          const reason = prompt("Rejection reason:");
                          if (reason) api(`/admin/transfers/${t.id}/status`, {
                            method: "PATCH",
                            body: JSON.stringify({ status: "failed", rejection_reason: reason }),
                          }).then(load);
                        }}>Reject</Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function AdminTransfersPage() {
  return (
    <Suspense fallback={<p>Loading transfers...</p>}>
      <TransfersContent />
    </Suspense>
  );
}
