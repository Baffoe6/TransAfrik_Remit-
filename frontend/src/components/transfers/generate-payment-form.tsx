"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { api, ApiError } from "@/lib/api";
import type { PaymentMethod } from "@/types";

export function GeneratePaymentForm({
  transferId,
  onGenerated,
}: {
  transferId: number;
  onGenerated: () => void;
}) {
  const [methods, setMethods] = useState<PaymentMethod[]>([]);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api<PaymentMethod[]>("/payments/methods").then((m) => {
      const active = m.filter((x) => x.is_active && !x.is_instant);
      setMethods(active);
      if (active.length) setCode(active[0].code);
    });
  }, []);

  const submit = async () => {
    setLoading(true);
    setError("");
    try {
      await api(`/payments/transfers/${transferId}/generate`, {
        method: "POST",
        body: JSON.stringify({ payment_method_code: code }),
      });
      onGenerated();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to generate payment");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-[#1B5E3B]/30">
      <CardHeader>
        <CardTitle>Complete Your Payment</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-gray-600">
          Your transfer is ready. Select how you would like to pay and we will generate your payment reference.
        </p>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="space-y-2">
          <Label>Payment Method</Label>
          <select
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="flex h-10 w-full rounded-md border border-gray-300 px-3 text-sm"
          >
            {methods.map((m) => (
              <option key={m.code} value={m.code}>{m.name}</option>
            ))}
          </select>
        </div>
        <Button onClick={submit} disabled={loading || !code} className="w-full">
          {loading ? "Generating..." : "Generate Payment Reference"}
        </Button>
      </CardContent>
    </Card>
  );
}
