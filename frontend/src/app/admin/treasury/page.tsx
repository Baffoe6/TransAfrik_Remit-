"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { TreasuryDashboard } from "@/types";
import { formatCurrency } from "@/lib/utils";

export default function TreasuryPage() {
  const [data, setData] = useState<TreasuryDashboard | null>(null);

  useEffect(() => {
    api<TreasuryDashboard>("/admin/treasury/dashboard").then(setData).catch(() => {});
  }, []);

  if (!data) return <p className="text-gray-500">Loading treasury dashboard...</p>;

  const cards = [
    { label: "Collected Today", value: formatCurrency(data.funds_collected_today_zar, "ZAR"), color: "text-green-700" },
    { label: "Pending Processing", value: formatCurrency(data.funds_pending_processing_zar, "ZAR"), color: "text-amber-700" },
    { label: "Paid Out", value: formatCurrency(data.funds_paid_out_zar, "ZAR"), color: "text-blue-700" },
    { label: "Outstanding Liabilities", value: formatCurrency(data.outstanding_liabilities_zar, "ZAR"), color: "text-red-700" },
    { label: "Revenue Today", value: formatCurrency(data.revenue_today_zar, "ZAR"), color: "text-[#1B5E3B]" },
    { label: "Revenue This Month", value: formatCurrency(data.revenue_month_zar, "ZAR"), color: "text-[#1B5E3B]" },
    { label: "Awaiting Payment", value: formatCurrency(data.awaiting_payment_zar, "ZAR"), color: "text-orange-700" },
    { label: "Completed Transfers", value: String(data.completed_transfer_count), color: "text-gray-800" },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Treasury Dashboard</h1>
      <p className="text-sm text-gray-600">Real-time view of funds collected, pending processing, payouts, and platform revenue.</p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((c) => (
          <Card key={c.label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">{c.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className={`text-2xl font-bold ${c.color}`}>{c.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
