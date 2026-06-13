"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

interface AgentDashboard {
  agent_code: string;
  display_name: string;
  region: string | null;
  commission_rate: string;
  total_referrals: number;
  customer_referrals: number;
  transfer_referrals: number;
  pending_commission_zar: string;
  paid_commission_zar: string;
}

export default function AgentPortalPage() {
  const [data, setData] = useState<AgentDashboard | null>(null);

  useEffect(() => {
    api<AgentDashboard>("/agent/dashboard").then(setData).catch(() => {});
  }, []);

  if (!data) return <p className="text-gray-500">Loading agent dashboard...</p>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Agent Portal</h1>
        <p className="text-gray-600">{data.display_name} · Code: {data.agent_code}</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card><CardHeader><CardTitle className="text-sm">Total Referrals</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.total_referrals}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Customer Referrals</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.customer_referrals}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Transfer Referrals</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.transfer_referrals}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Commission Rate</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.commission_rate}%</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Pending Commission</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{formatCurrency(data.pending_commission_zar, "ZAR")}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Paid Commission</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{formatCurrency(data.paid_commission_zar, "ZAR")}</p></CardContent></Card>
      </div>
      <div className="flex gap-4">
        <Link href="/agent/commissions" className="text-sm font-medium text-[#1B5E3B] hover:underline">View commission report →</Link>
        <Link href="/agent/referrals" className="text-sm font-medium text-[#1B5E3B] hover:underline">View referrals →</Link>
      </div>
    </div>
  );
}
