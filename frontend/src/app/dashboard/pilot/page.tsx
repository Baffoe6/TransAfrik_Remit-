"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

interface PilotDashboard {
  pilot_mode_active: boolean;
  status: string;
  limits: { max_transfer_zar: string | null; daily_transfer_limit: number | null; monthly_volume_zar: string | null; allowed_corridors: string[] };
  kyc_status: string;
  transfer_count: number;
  first_transfer_checklist: { step: string; done: boolean }[];
  support_contact: { email: string; whatsapp: string };
  demo_warning?: string;
}

export default function PilotDashboardPage() {
  const [data, setData] = useState<PilotDashboard | null>(null);

  useEffect(() => {
    api<PilotDashboard>("/pilot/dashboard").then(setData).catch(() => {});
  }, []);

  if (!data) return <p className="text-gray-500">Loading pilot status...</p>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Pilot Programme</h1>
        <p className="text-gray-600">Your controlled launch onboarding status</p>
      </div>

      {data.demo_warning && (
        <div className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
          {data.demo_warning}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader><CardTitle className="text-sm">Pilot Status</CardTitle></CardHeader>
          <CardContent><Badge variant={data.status === "approved" ? "success" : "warning"}>{data.status}</Badge></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">KYC Progress</CardTitle></CardHeader>
          <CardContent><p className="font-semibold capitalize">{data.kyc_status.replace(/_/g, " ")}</p></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-sm">Transfers</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{data.transfer_count}</p></CardContent>
        </Card>
      </div>

      {data.limits.max_transfer_zar && (
        <Card>
          <CardHeader><CardTitle>Transfer Limits</CardTitle></CardHeader>
          <CardContent className="grid gap-2 text-sm sm:grid-cols-3">
            <p>Max per transfer: {formatCurrency(data.limits.max_transfer_zar, "ZAR")}</p>
            <p>Daily limit: {data.limits.daily_transfer_limit} transfers</p>
            <p>Monthly volume: {formatCurrency(data.limits.monthly_volume_zar || "0", "ZAR")}</p>
            <p className="sm:col-span-3">Corridors: {data.limits.allowed_corridors.join(", ") || "All"}</p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>First Transfer Checklist</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {data.first_transfer_checklist.map((item) => (
            <div key={item.step} className="flex items-center justify-between rounded border p-2 text-sm">
              <span>{item.step}</span>
              <Badge variant={item.done ? "success" : "warning"}>{item.done ? "Done" : "Pending"}</Badge>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Support</CardTitle></CardHeader>
        <CardContent className="text-sm text-gray-600">
          <p>Email: {data.support_contact.email}</p>
          <Link href="/dashboard/support" className="mt-2 inline-block text-[#1B5E3B] hover:underline">Open support ticket →</Link>
        </CardContent>
      </Card>
    </div>
  );
}
