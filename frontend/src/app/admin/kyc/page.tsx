"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, downloadFile } from "@/lib/api";
import type { KycDocument } from "@/types";

interface PendingKyc {
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
  kyc_status: string;
  documents: KycDocument[];
}

export default function AdminKycPage() {
  const [pending, setPending] = useState<PendingKyc[]>([]);

  const load = () => api<PendingKyc[]>("/admin/kyc/pending").then(setPending).catch(() => {});
  useEffect(() => { load(); }, []);

  const review = async (userId: number, status: string, reason?: string) => {
    await api(`/admin/kyc/${userId}/review`, {
      method: "POST",
      body: JSON.stringify({ status, rejection_reason: reason }),
    });
    load();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">KYC Review</h1>
      {pending.length === 0 ? (
        <p className="text-gray-500">No pending KYC reviews.</p>
      ) : (
        pending.map((p) => (
          <Card key={p.user_id}>
            <CardHeader>
              <CardTitle>{p.first_name} {p.last_name} — {p.email}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                {p.documents.map((d) => (
                  <div key={d.id} className="flex justify-between rounded border p-2 text-sm">
                    <span>{d.document_type.replace(/_/g, " ")} — {d.original_filename}</span>
                    <button
                      type="button"
                      className="text-[#1B5E3B] hover:underline"
                      onClick={() => downloadFile(`/admin/kyc/documents/${d.id}/file`, d.original_filename)}
                    >
                      View
                    </button>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={() => review(p.user_id, "approved")}>Approve</Button>
                <Button size="sm" variant="destructive" onClick={() => {
                  const reason = prompt("Rejection reason:");
                  if (reason) review(p.user_id, "rejected", reason);
                }}>Reject</Button>
              </div>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}
