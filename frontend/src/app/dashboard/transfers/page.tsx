"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/transfers/status-badge";
import { api } from "@/lib/api";
import type { Transfer } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function TransfersPage() {
  const [transfers, setTransfers] = useState<Transfer[]>([]);

  useEffect(() => {
    api<Transfer[]>("/transfers").then(setTransfers).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Transfer History</h1>
        <Link href="/dashboard/transfers/new">
          <Button><Plus className="h-4 w-4" /> New Transfer</Button>
        </Link>
      </div>

      <Card>
        <CardHeader><CardTitle>All Transfers</CardTitle></CardHeader>
        <CardContent>
          {transfers.length === 0 ? (
            <p className="text-sm text-gray-500">No transfers yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-gray-500">
                    <th className="pb-3 pr-4">Reference</th>
                    <th className="pb-3 pr-4">Date</th>
                    <th className="pb-3 pr-4">Send (ZAR)</th>
                    <th className="pb-3 pr-4">Receive (GHS)</th>
                    <th className="pb-3 pr-4">Status</th>
                    <th className="pb-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {transfers.map((t) => (
                    <tr key={t.id} className="border-b">
                      <td className="py-3 pr-4 font-medium">{t.reference}</td>
                      <td className="py-3 pr-4">{formatDate(t.created_at)}</td>
                      <td className="py-3 pr-4">{formatCurrency(t.send_amount_zar, "ZAR")}</td>
                      <td className="py-3 pr-4">{formatCurrency(t.receive_amount_ghs, "GHS")}</td>
                      <td className="py-3 pr-4"><StatusBadge status={t.status} /></td>
                      <td className="py-3">
                        <Link href={`/dashboard/transfers/${t.id}`} className="text-[#1B5E3B] hover:underline">View</Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
