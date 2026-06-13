"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { SettlementDashboard } from "@/types";
import { formatCurrency } from "@/lib/utils";

export default function SettlementPage() {
  const [data, setData] = useState<SettlementDashboard | null>(null);

  const load = () => api<SettlementDashboard>("/admin/settlement/dashboard").then(setData).catch(() => {});
  useEffect(() => { load(); }, []);

  const reconcile = async (provider: string) => {
    await api(`/admin/settlement/reconcile/${provider}`, { method: "POST" });
    load();
  };

  if (!data) return <p className="text-gray-500">Loading settlement dashboard...</p>;

  const collections = [
    { label: "Pay@ Collections", data: data.pay_at_collections },
    { label: "EasyPay Collections", data: data.easy_pay_collections },
    { label: "EFT Collections", data: data.eft_collections },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Settlement Dashboard</h1>

      <div className="grid gap-4 sm:grid-cols-3">
        {collections.map((c) => (
          <Card key={c.label}>
            <CardHeader className="pb-2"><CardTitle className="text-sm">{c.label}</CardTitle></CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{formatCurrency(c.data.collected_zar, "ZAR")}</p>
              <p className="text-sm text-gray-500">{c.data.transaction_count} transactions</p>
              <Button size="sm" variant="outline" className="mt-2" onClick={() => reconcile(c.data.provider)}>Reconcile</Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>Mukuru Payouts & Variance</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <p>Total Mukuru payouts: <strong>{formatCurrency(data.mukuru_payouts_zar, "ZAR")}</strong></p>
          <p>Total variance: <strong className={Number(data.total_variance_zar) !== 0 ? "text-red-600" : "text-green-600"}>{formatCurrency(data.total_variance_zar, "ZAR")}</strong></p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Payment Settlements</CardTitle></CardHeader>
        <CardContent>
          {data.payment_settlements.length === 0 ? (
            <p className="text-sm text-gray-500">No settlement records yet.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {data.payment_settlements.map((s) => (
                <li key={s.id} className="flex justify-between rounded border p-2">
                  <span>{s.provider} · {s.settlement_date}</span>
                  <span>{formatCurrency(s.collected_zar, "ZAR")} · variance {formatCurrency(s.variance_zar, "ZAR")} · {s.status}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
