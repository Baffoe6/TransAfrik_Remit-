"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

type MvpOpsDashboard = {
  total_customers: number;
  pending_kyc: number;
  pending_transfers: number;
  completed_transfers: number;
  failed_transfers: number;
  daily_volume_zar: string;
  monthly_volume_zar: string;
  waitlist_leads: number;
};

interface InfraDashboard {
  status: string;
  provider_health: { provider: string; healthy: boolean; latency_ms: number | null; checked_at: string }[];
  queues: { queue_name: string; pending_count: number; failed_count: number }[];
  failures_24h: { webhooks: number; fx_sync: number; settlements: number };
  last_fx_sync: { source: string | null; success: boolean | null; started_at: string | null };
}

export default function AdminOperationsPage() {
  const [mvp, setMvp] = useState<MvpOpsDashboard | null>(null);
  const [infra, setInfra] = useState<InfraDashboard | null>(null);

  const load = () => {
    api<MvpOpsDashboard>("/admin/operations/dashboard").then(setMvp).catch(() => {});
    api<InfraDashboard>("/admin/operations").then(setInfra).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const healthCheck = async () => {
    await api("/admin/operations/health-check", { method: "POST" });
    load();
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1B5E3B]">Operations Dashboard</h1>
          <p className="text-gray-500">Platform metrics and infrastructure health</p>
        </div>
        {infra && (
          <div className="flex gap-2">
            <Badge variant={infra.status === "healthy" ? "success" : "warning"}>{infra.status}</Badge>
            <Button size="sm" onClick={healthCheck}>Run Health Check</Button>
          </div>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">Total Customers</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{mvp?.total_customers ?? "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">Pending KYC</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{mvp?.pending_kyc ?? "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">Pending Transfers</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{mvp?.pending_transfers ?? "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">Waitlist Leads</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{mvp?.waitlist_leads ?? "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">Completed Transfers</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold text-green-700">{mvp?.completed_transfers ?? "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">Failed Transfers</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold text-red-700">{mvp?.failed_transfers ?? "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">Daily Volume</CardTitle></CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{mvp ? formatCurrency(mvp.daily_volume_zar, "ZAR") : "—"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm text-gray-500">Monthly Volume</CardTitle></CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{mvp ? formatCurrency(mvp.monthly_volume_zar, "ZAR") : "—"}</p>
          </CardContent>
        </Card>
      </div>

      {infra && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Card>
              <CardHeader><CardTitle className="text-sm">Webhook Failures (24h)</CardTitle></CardHeader>
              <CardContent><p className="text-2xl font-bold">{infra.failures_24h.webhooks}</p></CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle className="text-sm">FX Sync Failures (24h)</CardTitle></CardHeader>
              <CardContent><p className="text-2xl font-bold">{infra.failures_24h.fx_sync}</p></CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle className="text-sm">Settlement Failures (24h)</CardTitle></CardHeader>
              <CardContent><p className="text-2xl font-bold">{infra.failures_24h.settlements}</p></CardContent>
            </Card>
          </div>
          <Card>
            <CardHeader><CardTitle>Provider Health</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {infra.provider_health.map((h, i) => (
                <div key={i} className="flex justify-between rounded border p-2 text-sm">
                  <span>{h.provider}</span>
                  <Badge variant={h.healthy ? "success" : "danger"}>{h.healthy ? "healthy" : "down"}</Badge>
                </div>
              ))}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Queue Status</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {infra.queues.map((q) => (
                <div key={q.queue_name} className="flex justify-between rounded border p-2 text-sm">
                  <span>{q.queue_name}</span>
                  <span className="text-gray-500">pending {q.pending_count} · failed {q.failed_count}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
