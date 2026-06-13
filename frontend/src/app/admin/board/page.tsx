"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

interface BoardDashboard {
  metrics: {
    monthly_volume_zar: string;
    revenue_month_zar: string;
    active_customers: number;
    active_agents: number;
    compliance_cases: number;
    referral_growth: number;
    referral_conversion_rate: number;
  };
  charts: {
    monthly_growth: { month: string; volume_zar: string; transaction_count: number }[];
    revenue_trend: { month: string; revenue_zar: string }[];
  };
  top_corridors: { code: string; destination: string; priority: number }[];
  top_providers: { provider: string; corridor_count: number }[];
}

export default function BoardDashboardPage() {
  const [data, setData] = useState<BoardDashboard | null>(null);

  useEffect(() => {
    api<BoardDashboard>("/admin/board/dashboard").then(setData).catch(() => {});
  }, []);

  if (!data) return <p className="text-gray-500">Loading board dashboard...</p>;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Board & Investor Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card><CardHeader><CardTitle className="text-sm">Monthly Volume</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{formatCurrency(data.metrics.monthly_volume_zar, "ZAR")}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Monthly Revenue</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{formatCurrency(data.metrics.revenue_month_zar, "ZAR")}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Active Customers</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.metrics.active_customers}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Active Agents</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.metrics.active_agents}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Referral Growth</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.metrics.referral_growth}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Referral Conversion</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.metrics.referral_conversion_rate}%</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Compliance Cases</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.metrics.compliance_cases}</p></CardContent></Card>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Monthly Growth</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {data.charts.monthly_growth.map((m) => (
              <div key={m.month} className="flex justify-between text-sm">
                <span>{m.month}</span>
                <span>{formatCurrency(m.volume_zar, "ZAR")} · {m.transaction_count} txns</span>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Revenue Trend</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {data.charts.revenue_trend.map((m) => (
              <div key={m.month} className="flex justify-between text-sm">
                <span>{m.month}</span>
                <span>{formatCurrency(m.revenue_zar, "ZAR")}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Top Corridors</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {data.top_corridors.map((c) => (
              <div key={c.code} className="flex justify-between text-sm"><span>{c.code}</span><span>{c.destination}</span></div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Top Providers</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {data.top_providers.map((p) => (
              <div key={p.provider} className="flex justify-between text-sm"><span>{p.provider}</span><span>{p.corridor_count} corridors</span></div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
