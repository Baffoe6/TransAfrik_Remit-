"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

interface Referral {
  id: number;
  referral_type: string;
  customer_user_id: number | null;
  transfer_id: number | null;
  referral_code_used: string;
  created_at: string;
}

export default function AgentReferralsPage() {
  const [rows, setRows] = useState<Referral[]>([]);

  useEffect(() => {
    api<Referral[]>("/agent/referrals").then(setRows).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <Link href="/agent" className="text-sm text-[#1B5E3B] hover:underline">← Back to dashboard</Link>
        <h1 className="mt-2 text-2xl font-bold text-[#1B5E3B]">Referrals</h1>
      </div>
      <Card>
        <CardHeader><CardTitle>Customer & Transfer Referrals</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {rows.length === 0 && <p className="text-sm text-gray-500">No referrals recorded yet.</p>}
          {rows.map((r) => (
            <div key={r.id} className="flex flex-wrap items-center justify-between gap-2 rounded border p-3 text-sm">
              <div>
                <p className="font-medium capitalize">{r.referral_type.replace("_", " ")}</p>
                <p className="text-gray-500">
                  Code: {r.referral_code_used}
                  {r.customer_user_id ? ` · Customer #${r.customer_user_id}` : ""}
                  {r.transfer_id ? ` · Transfer #${r.transfer_id}` : ""}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-gray-500">{new Date(r.created_at).toLocaleDateString()}</span>
                <Badge>{r.referral_type === "customer" ? "Customer" : "Transfer"}</Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
