"use client";

import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import type { Beneficiary, BeneficiaryType } from "@/types";
import { BENEFICIARY_TYPES, MOBILE_MONEY_PROVIDERS } from "@/types";

const emptyForm = {
  beneficiary_type: "mobile_money" as BeneficiaryType,
  full_name: "",
  account_name: "",
  country: "GH",
  mobile_money_provider: MOBILE_MONEY_PROVIDERS[0],
  mobile_wallet_number: "",
  bank_name: "",
  bank_account_number: "",
  bank_branch: "",
  pickup_location: "",
  pickup_city: "",
  relationship_to_sender: "",
};

function beneficiarySummary(b: Beneficiary) {
  if (b.beneficiary_type === "bank_account") {
    return `${b.bank_name} · ${b.bank_account_number}`;
  }
  if (b.beneficiary_type === "cash_pickup") {
    return `${b.pickup_location}, ${b.pickup_city}`;
  }
  return `${b.mobile_money_provider} · ${b.mobile_wallet_number}`;
}

function beneficiaryTypeLabel(type: BeneficiaryType) {
  return BENEFICIARY_TYPES.find((t) => t.value === type)?.label ?? type;
}

export default function BeneficiariesPage() {
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);

  const load = () => api<Beneficiary[]>("/beneficiaries").then(setBeneficiaries).catch(() => {});
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, string> = {
      beneficiary_type: form.beneficiary_type,
      full_name: form.full_name,
      country: form.country,
      relationship_to_sender: form.relationship_to_sender,
    };
    if (form.account_name) payload.account_name = form.account_name;
    if (form.beneficiary_type === "mobile_money") {
      payload.mobile_money_provider = form.mobile_money_provider;
      payload.mobile_wallet_number = form.mobile_wallet_number;
    } else if (form.beneficiary_type === "bank_account") {
      payload.bank_name = form.bank_name;
      payload.bank_account_number = form.bank_account_number;
      if (form.bank_branch) payload.bank_branch = form.bank_branch;
    } else {
      payload.pickup_location = form.pickup_location;
      payload.pickup_city = form.pickup_city;
    }
    await api("/beneficiaries", { method: "POST", body: JSON.stringify(payload) });
    setShowForm(false);
    setForm(emptyForm);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Beneficiaries</h1>
        <Button onClick={() => setShowForm(!showForm)}><Plus className="h-4 w-4" /> Add Beneficiary</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader><CardTitle>New Beneficiary</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2 sm:col-span-2">
                <Label>Beneficiary Type</Label>
                <select
                  value={form.beneficiary_type}
                  onChange={(e) => setForm({ ...form, beneficiary_type: e.target.value as BeneficiaryType })}
                  className="flex h-10 w-full rounded-md border border-gray-300 px-3 text-sm"
                >
                  {BENEFICIARY_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label>Full Name</Label>
                <Input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label>Account Name (optional)</Label>
                <Input value={form.account_name} onChange={(e) => setForm({ ...form, account_name: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>Country</Label>
                <Input value="Ghana (GH)" disabled />
              </div>
              <div className="space-y-2">
                <Label>Relationship</Label>
                <Input value={form.relationship_to_sender} onChange={(e) => setForm({ ...form, relationship_to_sender: e.target.value })} placeholder="e.g. Family" required />
              </div>

              {form.beneficiary_type === "mobile_money" && (
                <>
                  <div className="space-y-2">
                    <Label>Mobile Money Provider</Label>
                    <select
                      value={form.mobile_money_provider}
                      onChange={(e) => setForm({ ...form, mobile_money_provider: e.target.value })}
                      className="flex h-10 w-full rounded-md border border-gray-300 px-3 text-sm"
                    >
                      {MOBILE_MONEY_PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label>Wallet Number</Label>
                    <Input value={form.mobile_wallet_number} onChange={(e) => setForm({ ...form, mobile_wallet_number: e.target.value })} placeholder="233..." required />
                  </div>
                </>
              )}

              {form.beneficiary_type === "bank_account" && (
                <>
                  <div className="space-y-2">
                    <Label>Bank Name</Label>
                    <Input value={form.bank_name} onChange={(e) => setForm({ ...form, bank_name: e.target.value })} required />
                  </div>
                  <div className="space-y-2">
                    <Label>Account Number</Label>
                    <Input value={form.bank_account_number} onChange={(e) => setForm({ ...form, bank_account_number: e.target.value })} required />
                  </div>
                  <div className="space-y-2 sm:col-span-2">
                    <Label>Branch (optional)</Label>
                    <Input value={form.bank_branch} onChange={(e) => setForm({ ...form, bank_branch: e.target.value })} />
                  </div>
                </>
              )}

              {form.beneficiary_type === "cash_pickup" && (
                <>
                  <div className="space-y-2">
                    <Label>Pickup Location</Label>
                    <Input value={form.pickup_location} onChange={(e) => setForm({ ...form, pickup_location: e.target.value })} placeholder="e.g. Mukuru agent" required />
                  </div>
                  <div className="space-y-2">
                    <Label>Pickup City</Label>
                    <Input value={form.pickup_city} onChange={(e) => setForm({ ...form, pickup_city: e.target.value })} placeholder="e.g. Accra" required />
                  </div>
                </>
              )}

              <div className="sm:col-span-2">
                <Button type="submit">Save Beneficiary</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {beneficiaries.map((b) => (
          <Card key={b.id}>
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold">{b.full_name}</p>
                  <p className="text-xs font-medium uppercase tracking-wide text-[#1B5E3B]">{beneficiaryTypeLabel(b.beneficiary_type)}</p>
                  <p className="text-sm text-gray-500">{beneficiarySummary(b)}</p>
                  <p className="mt-1 text-xs text-gray-400">{b.relationship_to_sender}</p>
                </div>
                <Badge variant={b.status === "approved" ? "success" : b.status === "rejected" ? "danger" : "warning"}>
                  {b.status}
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
        {beneficiaries.length === 0 && (
          <p className="text-gray-500 sm:col-span-2">No beneficiaries yet. Add one to start sending money.</p>
        )}
      </div>
    </div>
  );
}
