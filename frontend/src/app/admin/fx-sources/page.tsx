"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

interface FxDashboard {
  current_rates: { pair: string; base_rate: string; effective_rate: string | null; margin_applied: string | null; source: string; last_sync: string }[];
  zar_ghs_effective: string;
  sync_history: { source: string; success: boolean; pairs_synced: number; error: string | null; started_at: string }[];
  available_feed_providers: string[];
}

export default function AdminFxSourcesPage() {
  const [data, setData] = useState<FxDashboard | null>(null);

  const load = () => api<FxDashboard>("/admin/fx-sources/dashboard").then(setData).catch(() => {});
  useEffect(() => { load(); }, []);

  const sync = async () => {
    await api("/admin/fx-sources/sync", { method: "POST" });
    load();
  };

  if (!data) return <p className="text-gray-500">Loading FX sources...</p>;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Live FX Feed Engine</h1>
        <Button onClick={sync}>Sync All Sources</Button>
      </div>
      <Card>
        <CardHeader><CardTitle>Current ZAR → GHS Effective Rate</CardTitle></CardHeader>
        <CardContent><p className="text-3xl font-bold">{data.zar_ghs_effective}</p></CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Rate Snapshots</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {data.current_rates.map((r) => (
            <div key={r.pair} className="flex justify-between rounded border p-2 text-sm">
              <span>{r.pair}: {r.base_rate} → {r.effective_rate || r.base_rate}</span>
              <span className="text-gray-500">{r.source} · {new Date(r.last_sync).toLocaleString()}</span>
            </div>
          ))}
          {data.current_rates.length === 0 && <p className="text-gray-500">No snapshots yet. Run a sync.</p>}
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Feed Providers</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {data.available_feed_providers.map((p) => (
            <span key={p} className="rounded-full bg-[#1B5E3B]/10 px-3 py-1 text-sm">{p}</span>
          ))}
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Sync History</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {data.sync_history.map((s, i) => (
            <div key={i} className="rounded border p-2 text-sm">
              {s.source}: {s.success ? `${s.pairs_synced} pairs` : s.error || "failed"} · {new Date(s.started_at).toLocaleString()}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
