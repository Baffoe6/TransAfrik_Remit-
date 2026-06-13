"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import type { ComplianceQueueItem } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function ComplianceDashboard() {
  const [queue, setQueue] = useState<ComplianceQueueItem[]>([]);

  const load = () => api<ComplianceQueueItem[]>("/admin/compliance/queue").then(setQueue).catch(() => {});
  useEffect(() => { load(); }, []);

  const approve = async (id: number) => {
    await api(`/admin/compliance/transfers/${id}/approve`, { method: "POST" });
    load();
  };

  const reject = async (id: number) => {
    const reason = prompt("Rejection reason:");
    if (reason) await api(`/admin/compliance/transfers/${id}/reject?reason=${encodeURIComponent(reason)}`, { method: "POST" });
    load();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Compliance Review Queue</h1>
      {queue.length === 0 ? (
        <p className="text-gray-500">No transfers awaiting compliance review.</p>
      ) : (
        queue.map((item) => (
          <Card key={item.transfer_id}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>{item.reference}</CardTitle>
              <Badge variant={item.risk_score >= 50 ? "danger" : "warning"}>Risk Score: {item.risk_score}</Badge>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-sm">
                <p><strong>{item.customer_name}</strong> — {item.customer_email}</p>
                <p>Amount: {formatCurrency(item.send_amount_zar, "ZAR")} · {formatDate(item.created_at)}</p>
              </div>
              {item.aml_flags && item.aml_flags.length > 0 && (
                <ul className="rounded bg-amber-50 p-3 text-sm text-amber-800 space-y-1">
                  {item.aml_flags.map((f, i) => <li key={i}>• {f.message}</li>)}
                </ul>
              )}
              <div className="flex gap-2">
                <Button size="sm" onClick={() => approve(item.transfer_id)}>Approve</Button>
                <Button size="sm" variant="destructive" onClick={() => reject(item.transfer_id)}>Reject</Button>
              </div>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}
