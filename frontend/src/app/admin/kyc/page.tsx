"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, downloadFile, ApiError } from "@/lib/api";
import type { KycDocument } from "@/types";

interface PendingKyc {
  user_id: number;
  email: string | null;
  mobile_number: string | null;
  first_name: string;
  last_name: string;
  kyc_status: string;
  documents: KycDocument[];
}

export default function AdminKycPage() {
  const [pending, setPending] = useState<PendingKyc[]>([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setError("");
    try {
      const data = await api<PendingKyc[]>("/admin/kyc/pending");
      setPending(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load KYC queue");
    }
  };

  useEffect(() => { load(); }, []);

  const review = async (userId: number, status: string, reason?: string) => {
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await api(`/admin/kyc/${userId}/review`, {
        method: "POST",
        body: JSON.stringify({ status, rejection_reason: reason }),
      });
      setSuccess(`KYC ${status} for user #${userId}`);
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "KYC review failed");
    } finally {
      setLoading(false);
    }
  };

  const customerLabel = (p: PendingKyc) => {
    const name = `${p.first_name} ${p.last_name}`.trim();
    const contact = p.mobile_number || p.email || "No contact";
    return `${name} — ${contact}`;
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">KYC Review</h1>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {success ? <p className="text-sm text-green-700">{success}</p> : null}
      {pending.length === 0 ? (
        <p className="text-gray-500">No pending KYC reviews.</p>
      ) : (
        pending.map((p) => (
          <Card key={p.user_id}>
            <CardHeader>
              <CardTitle>{customerLabel(p)}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                {p.documents.length === 0 ? (
                  <p className="text-sm text-gray-500">No documents uploaded yet.</p>
                ) : (
                  p.documents.map((d) => (
                    <div key={d.id} className="flex justify-between rounded border p-2 text-sm">
                      <span>{d.document_type.replace(/_/g, " ")} — {d.original_filename}</span>
                      <button
                        type="button"
                        className="text-[#1B5E3B] hover:underline"
                        onClick={() => downloadFile(`/admin/kyc/documents/${d.id}/file`, d.original_filename).catch(() => setError("Could not open document"))}
                      >
                        View
                      </button>
                    </div>
                  ))
                )}
              </div>
              <div className="flex gap-2">
                <Button size="sm" disabled={loading} onClick={() => review(p.user_id, "approved")}>Approve</Button>
                <Button size="sm" variant="destructive" disabled={loading} onClick={() => {
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
