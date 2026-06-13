"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function FounderDashboardPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    api<Record<string, unknown>>("/admin/founder/dashboard").then(setData).catch(() => {});
  }, []);

  if (!data) return <p className="text-gray-500">Loading executive dashboard...</p>;

  const collections = data.collections as Record<string, string>;
  const revenue = data.revenue as Record<string, string>;
  const compliance = data.compliance as Record<string, number>;
  const agents = data.agent_performance as Record<string, unknown>;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Founder Executive Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card><CardHeader><CardTitle className="text-sm">Daily Collections</CardTitle></CardHeader><CardContent><p className="text-xl font-bold">{formatCurrency(collections.daily_volume_zar, "ZAR")}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Monthly Collections</CardTitle></CardHeader><CardContent><p className="text-xl font-bold">{formatCurrency(collections.monthly_volume_zar, "ZAR")}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Revenue Today</CardTitle></CardHeader><CardContent><p className="text-xl font-bold">{formatCurrency(revenue.today_zar, "ZAR")}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Revenue Month</CardTitle></CardHeader><CardContent><p className="text-xl font-bold">{formatCurrency(revenue.month_zar, "ZAR")}</p></CardContent></Card>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Compliance</CardTitle></CardHeader>
          <CardContent className="text-sm space-y-1">
            <p>Open EDD cases: <strong>{compliance.open_edd_cases}</strong></p>
            <p>High-risk customers: <strong>{compliance.high_risk_customers}</strong></p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Agent Performance</CardTitle></CardHeader>
          <CardContent className="text-sm space-y-1">
            <p>Active agents: <strong>{agents.active_agents as number}</strong></p>
            <p>Total referrals: <strong>{agents.total_referrals as number}</strong></p>
            <p>Pending commissions: <strong>{formatCurrency(String(agents.pending_commissions_zar), "ZAR")}</strong></p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
