"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { PaymentDashboardStats } from "@/types";
import { formatCurrency } from "@/lib/utils";

export default function AdminPaymentsDashboard() {
  const [stats, setStats] = useState<PaymentDashboardStats | null>(null);

  useEffect(() => {
    api<PaymentDashboardStats>("/admin/payments/dashboard").then(setStats).catch(() => {});
  }, []);

  const cards = stats ? [
    { label: "Pending Payments", value: stats.pending_payments, href: "/admin/transfers?status=awaiting_payment" },
    { label: "Pending Verifications", value: stats.pending_verifications, href: "/admin/payments/verify" },
    { label: "Expired References", value: stats.expired_references },
    { label: "Paid Today", value: stats.paid_today },
    { label: "Daily Volume", value: formatCurrency(stats.daily_volume_zar, "ZAR") },
    { label: "Monthly Volume", value: formatCurrency(stats.monthly_volume_zar, "ZAR") },
  ] : [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Payment Dashboard</h1>
        <Link href="/admin/payments/verify"><Button>Verify Payments</Button></Link>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((c) => (
          <Card key={c.label}>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-gray-500">{c.label}</CardTitle></CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{c.value}</p>
              {c.href && <Link href={c.href} className="mt-2 text-xs text-[#1B5E3B] hover:underline">View →</Link>}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
