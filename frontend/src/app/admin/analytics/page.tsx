"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import type { AnalyticsDashboard } from "@/types";

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsDashboard | null>(null);

  useEffect(() => {
    api<AnalyticsDashboard>("/admin/analytics/dashboard").then(setData).catch(() => {});
  }, []);

  if (!data) {
    return <p className="text-gray-500">Loading analytics...</p>;
  }

  const volumeCards = [
    { label: "Daily Volume", value: formatCurrency(data.daily_volume_zar, "ZAR") },
    { label: "Monthly Volume", value: formatCurrency(data.monthly_volume_zar, "ZAR") },
    { label: "Daily Revenue", value: formatCurrency(data.daily_revenue_zar, "ZAR") },
    { label: "Monthly Revenue", value: formatCurrency(data.monthly_revenue_zar, "ZAR") },
    { label: "Completed Today", value: String(data.completed_today) },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Analytics Dashboard</h1>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {volumeCards.map((c) => (
          <Card key={c.label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">{c.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{c.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Transfers by Country</CardTitle>
          </CardHeader>
          <CardContent>
            {data.transfers_by_country.length === 0 ? (
              <p className="text-sm text-gray-500">No transfer data yet.</p>
            ) : (
              <ul className="space-y-2">
                {data.transfers_by_country.map((row) => (
                  <li key={row.country} className="flex justify-between rounded border p-3 text-sm">
                    <span className="font-medium">{row.country}</span>
                    <span>{row.count} transfers · {formatCurrency(row.volume_zar, "ZAR")}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Transfers by Payment Method</CardTitle>
          </CardHeader>
          <CardContent>
            {data.transfers_by_payment_method.length === 0 ? (
              <p className="text-sm text-gray-500">No payment method data yet.</p>
            ) : (
              <ul className="space-y-2">
                {data.transfers_by_payment_method.map((row) => (
                  <li key={row.method} className="flex justify-between rounded border p-3 text-sm">
                    <span className="font-medium">{row.method}</span>
                    <span>{row.count} transfers · {formatCurrency(row.volume_zar, "ZAR")}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Transfers by Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {Object.entries(data.transfers_by_status).map(([status, count]) => (
              <span key={status} className="rounded-full bg-[#1B5E3B]/10 px-3 py-1 text-sm">
                {status.replace(/_/g, " ")}: <strong>{count}</strong>
              </span>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
