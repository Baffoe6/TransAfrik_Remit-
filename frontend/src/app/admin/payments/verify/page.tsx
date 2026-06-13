"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/transfers/status-badge";
import { api, downloadFile } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

interface PaymentDetail {
  transfer: { id: number; reference: string; status: string; total_amount_zar: string };
  customer: { email: string; phone: string | null; name: string | null };
  beneficiary: { full_name: string; mobile_money_provider: string; mobile_wallet_number: string };
  payment_reference: { reference_number: string; voucher_number: string | null; amount: string } | null;
  payment_proof: { filename: string; status: string } | null;
}

export default function PaymentVerificationPage() {
  const [items, setItems] = useState<PaymentDetail[]>([]);

  const load = () => api<PaymentDetail[]>("/admin/payments/pending-verification").then(setItems).catch(() => {});
  useEffect(() => { load(); }, []);

  const verify = async (id: number, status: string, reason?: string) => {
    await api(`/admin/payments/transfers/${id}/verify`, {
      method: "POST",
      body: JSON.stringify({ status, rejection_reason: reason, notes: reason }),
    });
    load();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Payment Verification</h1>
      {items.length === 0 ? (
        <p className="text-gray-500">No payments pending verification.</p>
      ) : (
        items.map((item) => (
          <Card key={item.transfer.id}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>{item.transfer.reference}</CardTitle>
              <StatusBadge status={item.transfer.status} />
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-3 text-sm">
                <div>
                  <p className="font-medium text-gray-500">Customer</p>
                  <p>{item.customer.name}</p>
                  <p className="text-gray-500">{item.customer.email}</p>
                </div>
                <div>
                  <p className="font-medium text-gray-500">Beneficiary</p>
                  <p>{item.beneficiary.full_name}</p>
                  <p className="text-gray-500">{item.beneficiary.mobile_wallet_number}</p>
                </div>
                <div>
                  <p className="font-medium text-gray-500">Amount</p>
                  <p className="text-lg font-semibold">{formatCurrency(item.transfer.total_amount_zar, "ZAR")}</p>
                  {item.payment_reference && <p className="font-mono text-xs">{item.payment_reference.reference_number}</p>}
                </div>
              </div>
              {item.payment_proof && (
                <p className="text-sm">
                  Receipt: <strong>{item.payment_proof.filename}</strong> ({item.payment_proof.status})
                  <button
                    type="button"
                    className="ml-2 text-[#1B5E3B] hover:underline"
                    onClick={() => downloadFile(`/admin/transfers/${item.transfer.id}/payment-proof/file`, item.payment_proof!.filename)}
                  >
                    Download
                  </button>
                </p>
              )}
              <div className="flex gap-2">
                <Button size="sm" onClick={() => verify(item.transfer.id, "verified")}>Verify Payment</Button>
                <Button size="sm" variant="destructive" onClick={() => {
                  const r = prompt("Rejection reason:");
                  if (r) verify(item.transfer.id, "rejected", r);
                }}>Reject</Button>
                <Button size="sm" variant="outline" onClick={() => verify(item.transfer.id, "more_info", "More information required")}>
                  Request More Info
                </Button>
              </div>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}
