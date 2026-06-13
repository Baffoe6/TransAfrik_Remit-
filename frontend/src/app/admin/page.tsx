"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { DashboardStats } from "@/types";
import { formatCurrency } from "@/lib/utils";

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    api<DashboardStats>("/admin/dashboard").then(setStats).catch(() => {});
  }, []);

  const cards = stats ? [
    { label: "Total Customers", value: stats.total_customers },
    { label: "Pending KYC", value: stats.pending_kyc },
    { label: "Pending Transfers", value: stats.pending_transfers },
    { label: "Completed Transfers", value: stats.completed_transfers },
    { label: "Monthly Volume", value: formatCurrency(stats.monthly_volume_zar, "ZAR") },
  ] : [];

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Admin Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {cards.map((c) => (
          <Card key={c.label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">{c.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{c.value}</p>
            </CardContent>
          </Card>
        ))}
        {!stats && <p className="text-gray-500">Loading dashboard...</p>}
      </div>
    </div>
  );
}
