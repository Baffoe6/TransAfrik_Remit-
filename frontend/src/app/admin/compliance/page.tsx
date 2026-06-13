"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, getApiBaseUrl } from "@/lib/api";
import type { ComplianceQueueItem } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";

type ComplianceDashboard = {
  kyc_queue_count: number;
  kyc_queue: { user_id: number; email: string; name: string; kyc_status: string }[];
  high_risk_customers: number;
  high_risk_transactions: number;
  edd_open_cases: number;
  daily_volume_zar: string;
  monthly_volume_zar: string;
};

export default function ComplianceDashboardPage() {
  const [metrics, setMetrics] = useState<ComplianceDashboard | null>(null);
  const [queue, setQueue] = useState<ComplianceQueueItem[]>([]);

  const load = () => {
    api<ComplianceDashboard>("/admin/compliance/dashboard").then(setMetrics).catch(() => {});
    api<ComplianceQueueItem[]>("/admin/compliance/queue").then(setQueue).catch(() => {});
  };

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
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#1B5E3B]">Compliance Dashboard</h1>
          <p className="text-gray-500">KYC queue, risk monitoring, and transfer review</p>
        </div>
        <a href={`${getApiBaseUrl()}/api/v1/admin/compliance/export`} target="_blank" rel="noreferrer">
          <Button variant="outline">Export CSV</Button>
        </a>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">KYC Queue</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{metrics?.kyc_queue_count ?? "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">High-Risk Transactions</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{metrics?.high_risk_transactions ?? "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">Daily Volume</CardTitle></CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {metrics ? formatCurrency(metrics.daily_volume_zar, "ZAR") : "—"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">Monthly Volume</CardTitle></CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {metrics ? formatCurrency(metrics.monthly_volume_zar, "ZAR") : "—"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>KYC Review Queue</CardTitle>
          <Link href="/admin/kyc"><Button variant="ghost" size="sm">Open KYC Admin</Button></Link>
        </CardHeader>
        <CardContent>
          {(metrics?.kyc_queue.length ?? 0) === 0 ? (
            <p className="text-sm text-gray-500">No pending KYC submissions.</p>
          ) : (
            <div className="space-y-2">
              {metrics?.kyc_queue.map((item) => (
                <div key={item.user_id} className="flex items-center justify-between rounded border p-3 text-sm">
                  <div>
                    <p className="font-medium">{item.name}</p>
                    <p className="text-gray-500">{item.email}</p>
                  </div>
                  <Badge variant="warning">{item.kyc_status}</Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-[#1B5E3B]">Transfer Review Queue</h2>
        {queue.length === 0 ? (
          <p className="text-gray-500">No transfers awaiting compliance review.</p>
        ) : (
          queue.map((item) => (
            <Card key={item.transfer_id} className="mb-4">
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
                  <ul className="space-y-1 rounded bg-amber-50 p-3 text-sm text-amber-800">
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
    </div>
  );
}
