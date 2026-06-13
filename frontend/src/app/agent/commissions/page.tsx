"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

interface Commission {
  id: number;
  transfer_id: number;
  transfer_amount_zar: string;
  commission_amount_zar: string;
  status: string;
  created_at: string;
}

export default function AgentCommissionsPage() {
  const [rows, setRows] = useState<Commission[]>([]);

  useEffect(() => {
    api<Commission[]>("/agent/commissions").then(setRows).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <Link href="/agent" className="text-sm text-[#1B5E3B] hover:underline">← Back to dashboard</Link>
        <h1 className="mt-2 text-2xl font-bold text-[#1B5E3B]">Commission Report</h1>
      </div>
      <Card>
        <CardHeader><CardTitle>Recent Commissions</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {rows.length === 0 && <p className="text-sm text-gray-500">No commissions recorded yet.</p>}
          {rows.map((c) => (
            <div key={c.id} className="flex flex-wrap items-center justify-between gap-2 rounded border p-3 text-sm">
              <div>
                <p className="font-medium">Transfer #{c.transfer_id}</p>
                <p className="text-gray-500">
                  {formatCurrency(c.transfer_amount_zar, "ZAR")} transfer · {new Date(c.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-semibold text-[#1B5E3B]">{formatCurrency(c.commission_amount_zar, "ZAR")}</span>
                <Badge variant={c.status === "paid" ? "success" : "warning"}>{c.status}</Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
