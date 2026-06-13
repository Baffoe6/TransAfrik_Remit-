"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

interface OpsDashboard {
  status: string;
  provider_health: { provider: string; healthy: boolean; latency_ms: number | null; checked_at: string }[];
  queues: { queue_name: string; pending_count: number; failed_count: number }[];
  failures_24h: { webhooks: number; fx_sync: number; settlements: number };
  last_fx_sync: { source: string | null; success: boolean | null; started_at: string | null };
}

export default function AdminOperationsPage() {
  const [data, setData] = useState<OpsDashboard | null>(null);

  const load = () => api<OpsDashboard>("/admin/operations").then(setData).catch(() => {});
  useEffect(() => { load(); }, []);

  const healthCheck = async () => {
    await api("/admin/operations/health-check", { method: "POST" });
    load();
  };

  if (!data) return <p className="text-gray-500">Loading operations center...</p>;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Operations Center</h1>
        <div className="flex gap-2">
          <Badge variant={data.status === "healthy" ? "success" : "warning"}>{data.status}</Badge>
          <Button size="sm" onClick={healthCheck}>Run Health Check</Button>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <Card><CardHeader><CardTitle className="text-sm">Webhook Failures (24h)</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.failures_24h.webhooks}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">FX Sync Failures (24h)</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.failures_24h.fx_sync}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Settlement Failures (24h)</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.failures_24h.settlements}</p></CardContent></Card>
      </div>
      <Card>
        <CardHeader><CardTitle>Provider Health</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {data.provider_health.map((h, i) => (
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
          {data.queues.map((q) => (
            <div key={q.queue_name} className="flex justify-between rounded border p-2 text-sm">
              <span>{q.queue_name}</span>
              <span className="text-gray-500">pending {q.pending_count} · failed {q.failed_count}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
