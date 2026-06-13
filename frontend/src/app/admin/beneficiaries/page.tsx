"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { Beneficiary } from "@/types";

export default function AdminBeneficiariesPage() {
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);

  const load = () => api<Beneficiary[]>("/admin/beneficiaries/pending").then(setBeneficiaries).catch(() => {});
  useEffect(() => { load(); }, []);

  const review = async (id: number, status: string, reason?: string) => {
    await api(`/admin/beneficiaries/${id}/review`, {
      method: "POST",
      body: JSON.stringify({ status, rejection_reason: reason }),
    });
    load();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Beneficiary Review</h1>
      {beneficiaries.length === 0 ? (
        <p className="text-gray-500">No pending beneficiary reviews.</p>
      ) : (
        beneficiaries.map((b) => (
          <Card key={b.id}>
            <CardHeader><CardTitle>{b.full_name}</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="text-sm text-gray-600">
                <p>{b.mobile_money_provider} — {b.mobile_wallet_number}</p>
                <p>Relationship: {b.relationship_to_sender}</p>
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={() => review(b.id, "approved")}>Approve</Button>
                <Button size="sm" variant="destructive" onClick={() => {
                  const reason = prompt("Rejection reason:");
                  if (reason) review(b.id, "rejected", reason);
                }}>Reject</Button>
              </div>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}
