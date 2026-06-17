"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { Beneficiary, CalculatorResult, PaymentMethod } from "@/types";
import { formatCurrency } from "@/lib/utils";
import { ApiError } from "@/lib/api";

function formatExchangeRate(rate: string, from: string, to: string): string {
  const n = parseFloat(rate);
  if (Number.isNaN(n)) return `1 ${from} = — ${to}`;
  return `1 ${from} = ${n.toFixed(4)} ${to}`;
}

export default function NewTransferPage() {
  const router = useRouter();
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [beneficiaryId, setBeneficiaryId] = useState("");
  const [paymentMethodCode, setPaymentMethodCode] = useState("");
  const [amount, setAmount] = useState("");
  const [quote, setQuote] = useState<CalculatorResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const selectedBeneficiary = beneficiaries.find((b) => String(b.id) === beneficiaryId);

  useEffect(() => {
    api<Beneficiary[]>("/beneficiaries").then((b) => {
      const active = b.filter((x) => x.status !== "rejected");
      setBeneficiaries(active);
      if (active.length) setBeneficiaryId(String(active[0].id));
    });
    api<PaymentMethod[]>("/payments/methods").then((m) => {
      const flutterwave = m.filter((x) => x.is_active && (x.code.startsWith("fw_") || x.code === "flutterwave"));
      setPaymentMethods(flutterwave);
      if (flutterwave.length) setPaymentMethodCode(flutterwave[0].code);
    });
  }, []);

  const calculate = async () => {
    if (!amount || parseFloat(amount) <= 0) return;
    const dest = selectedBeneficiary?.country ?? "GH";
    const result = await api<CalculatorResult>("/transfers/calculate", {
      method: "POST",
      body: JSON.stringify({ amount_to_pay_zar: amount, destination_country: dest }),
    });
    setQuote(result);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const transfer = await api<{ id: number }>("/transfers", {
        method: "POST",
        body: JSON.stringify({
          beneficiary_id: parseInt(beneficiaryId),
          amount_to_pay_zar: amount,
          payment_method_code: paymentMethodCode,
        }),
      });
      router.push(`/dashboard/transfers/${transfer.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create transfer");
    } finally {
      setLoading(false);
    }
  };

  const selectedMethod = paymentMethods.find((m) => m.code === paymentMethodCode);
  const deliveryMethod =
    selectedBeneficiary?.beneficiary_type === "bank_account"
      ? "Bank Transfer"
      : selectedBeneficiary?.beneficiary_type === "cash_pickup"
        ? "Cash Pickup"
        : quote?.delivery_method ?? "Mobile Money";

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">New Transfer</h1>

      <Card>
        <CardHeader><CardTitle>Transfer Details</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

            <div className="space-y-2">
              <Label>Beneficiary</Label>
              <select value={beneficiaryId} onChange={(e) => setBeneficiaryId(e.target.value)}
                className="flex h-10 w-full rounded-md border border-gray-300 px-3 text-sm" required>
                {beneficiaries.map((b) => (
                  <option key={b.id} value={b.id}>{b.full_name} — {b.mobile_wallet_number}</option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label>Payment Method</Label>
              <select value={paymentMethodCode} onChange={(e) => setPaymentMethodCode(e.target.value)}
                className="flex h-10 w-full rounded-md border border-gray-300 px-3 text-sm" required>
                {paymentMethods.map((m) => (
                  <option key={m.code} value={m.code}>{m.name}</option>
                ))}
              </select>
              {selectedMethod?.description && (
                <p className="text-xs text-gray-500">{selectedMethod.description}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label>Amount to Pay (ZAR)</Label>
              <p className="text-xs text-gray-500">Final amount — no extra charges at checkout</p>
              <div className="flex gap-2">
                <Input type="number" min="1" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} required />
                <Button type="button" variant="outline" onClick={calculate}>Get quote</Button>
              </div>
            </div>

            {quote && (
              <div className="rounded-lg bg-[#1B5E3B]/5 p-4 space-y-3 text-sm">
                <div className="flex justify-between font-semibold text-base">
                  <span>Amount to pay</span>
                  <span>{formatCurrency(quote.amount_to_pay_zar, "ZAR")}</span>
                </div>
                <div className="pl-2 space-y-1 border-l-2 border-[#1B5E3B]/20">
                  <p className="text-xs text-gray-500">Includes</p>
                  <div className="flex justify-between">
                    <span>Transfer fee</span>
                    <span>{formatCurrency(quote.fee_zar, "ZAR")}</span>
                  </div>
                </div>
                <div className="flex justify-between border-t pt-2 text-[#1B5E3B]">
                  <span>Recipient receives</span>
                  <span className="text-lg font-bold">{formatCurrency(quote.receive_amount, quote.to_currency)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Exchange rate</span>
                  <span>{formatExchangeRate(quote.exchange_rate, quote.from_currency, quote.to_currency)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Delivery method</span>
                  <span>{deliveryMethod}</span>
                </div>
                <div className="flex justify-between">
                  <span>Estimated delivery</span>
                  <span>{quote.estimated_delivery}</span>
                </div>
              </div>
            )}

            <Button type="submit" className="w-full" disabled={loading || !beneficiaryId}>
              {loading ? "Creating..." : "Create Transfer & Generate Payment"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
