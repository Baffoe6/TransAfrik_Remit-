"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { CorridorFeeRule, FeeRuleV2, RateHistoryEntry } from "@/types";
import { formatCurrency } from "@/lib/utils";

interface FxSource {
  id: number;
  code: string;
  name: string;
  source_type: string;
  is_active: boolean;
  priority: number;
}

interface FxMarkup {
  id: number;
  from_currency: string;
  to_currency: string;
  markup_type: string;
  markup_value: string;
  priority: number;
  is_active: boolean;
}

export default function AdminRatesPage() {
  const [history, setHistory] = useState<RateHistoryEntry[]>([]);
  const [fees, setFees] = useState<FeeRuleV2[]>([]);
  const [fxSources, setFxSources] = useState<FxSource[]>([]);
  const [fxMarkup, setFxMarkup] = useState<FxMarkup[]>([]);
  const [retailNetworks, setRetailNetworks] = useState<string[]>([]);
  const [fxSourceForm, setFxSourceForm] = useState({ code: "", name: "", source_type: "manual", priority: "0" });
  const [fxMarkupForm, setFxMarkupForm] = useState({ from_currency: "ZAR", to_currency: "GHS", markup_type: "percentage", markup_value: "2", priority: "0" });
  const [rateForm, setRateForm] = useState({ rate: "0.72", effective_from: new Date().toISOString().slice(0, 10), change_reason: "" });
  const [corridorFees, setCorridorFees] = useState<CorridorFeeRule[]>([]);
  const [tierForm, setTierForm] = useState({
    rule_id: "",
    min_amount_zar: "0",
    max_amount_zar: "",
    fee_zar: "20",
    label: "",
  });
  const [feeForm, setFeeForm] = useState({
    name: "",
    min_amount_zar: "0",
    fee_type: "flat",
    fee_value: "49",
    destination_country: "",
    priority: "0",
  });

  const load = () => {
    api<RateHistoryEntry[]>("/admin/exchange-rates/history").then(setHistory).catch(() => {});
    api<FeeRuleV2[]>("/admin/fee-rules/v2").then(setFees).catch(() => {});
    api<CorridorFeeRule[]>("/admin/corridor-fee-rules").then(setCorridorFees).catch(() => {});
    api<FxSource[]>("/admin/fx/sources").then(setFxSources).catch(() => {});
    api<FxMarkup[]>("/admin/fx/markup").then(setFxMarkup).catch(() => {});
    api<{ networks: string[] }>("/admin/retail-networks").then((r) => setRetailNetworks(r.networks)).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const addRate = async (e: React.FormEvent) => {
    e.preventDefault();
    await api("/admin/exchange-rates/v2", {
      method: "POST",
      body: JSON.stringify({
        rate: rateForm.rate,
        effective_from: rateForm.effective_from,
        change_reason: rateForm.change_reason || null,
      }),
    });
    load();
  };

  const addFxSource = async (e: React.FormEvent) => {
    e.preventDefault();
    await api("/admin/fx/sources", {
      method: "POST",
      body: JSON.stringify({ ...fxSourceForm, priority: Number(fxSourceForm.priority) }),
    });
    setFxSourceForm({ code: "", name: "", source_type: "manual", priority: "0" });
    load();
  };

  const addFxMarkup = async (e: React.FormEvent) => {
    e.preventDefault();
    await api("/admin/fx/markup", {
      method: "POST",
      body: JSON.stringify({ ...fxMarkupForm, priority: Number(fxMarkupForm.priority) }),
    });
    load();
  };

  const addFee = async (e: React.FormEvent) => {
    e.preventDefault();
    await api("/admin/fee-rules/v2", {
      method: "POST",
      body: JSON.stringify({
        ...feeForm,
        destination_country: feeForm.destination_country || null,
        priority: Number(feeForm.priority),
      }),
    });
    load();
  };

  const addCorridorTier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tierForm.rule_id) return;
    await api(`/admin/corridor-fee-rules/${tierForm.rule_id}/tiers`, {
      method: "POST",
      body: JSON.stringify({
        min_amount_zar: tierForm.min_amount_zar,
        max_amount_zar: tierForm.max_amount_zar || null,
        fee_zar: tierForm.fee_zar,
        label: tierForm.label || null,
      }),
    });
    setTierForm({ rule_id: tierForm.rule_id, min_amount_zar: "0", max_amount_zar: "", fee_zar: "20", label: "" });
    load();
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Rates & Fees</h1>

      <Card>
        <CardHeader>
          <CardTitle>Corridor fee tiers (customer-facing)</CardTitle>
          <p className="text-sm text-gray-500">Fee-inclusive bands per corridor. Customer amount is final at checkout.</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {corridorFees.map((rule) => (
            <div key={rule.id} className="rounded-lg border p-4 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <p className="font-semibold text-[#1B5E3B]">{rule.name}</p>
                  <p className="text-xs text-gray-500">
                    {rule.corridor_code} · provider cost {rule.provider_cost_pct}%
                    {rule.provider_cost_flat_zar ? ` or R${rule.provider_cost_flat_zar} flat` : ""}
                    {rule.is_active ? "" : " · inactive"}
                  </p>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-gray-500">
                      <th className="pb-2 pr-4">Amount band (ZAR)</th>
                      <th className="pb-2 pr-4">Transfer fee</th>
                      <th className="pb-2">Label</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rule.tiers.filter((t) => t.is_active).map((t) => (
                      <tr key={t.id} className="border-b">
                        <td className="py-2 pr-4">
                          R{t.min_amount_zar}
                          {t.max_amount_zar ? ` – R${t.max_amount_zar}` : "+"}
                        </td>
                        <td className="py-2 pr-4 font-medium">{formatCurrency(t.fee_zar, "ZAR")}</td>
                        <td className="py-2 text-gray-500">{t.label ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
          <form onSubmit={addCorridorTier} className="space-y-3 border-t pt-4">
            <p className="text-sm font-medium">Add tier to corridor</p>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
              <div className="space-y-2">
                <Label>Corridor rule</Label>
                <select
                  value={tierForm.rule_id}
                  onChange={(e) => setTierForm({ ...tierForm, rule_id: e.target.value })}
                  className="flex h-10 w-full rounded-md border border-gray-300 px-3 text-sm"
                  required
                >
                  <option value="">Select…</option>
                  {corridorFees.map((r) => (
                    <option key={r.id} value={r.id}>{r.corridor_code}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label>Min ZAR</Label>
                <Input value={tierForm.min_amount_zar} onChange={(e) => setTierForm({ ...tierForm, min_amount_zar: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>Max ZAR</Label>
                <Input value={tierForm.max_amount_zar} onChange={(e) => setTierForm({ ...tierForm, max_amount_zar: e.target.value })} placeholder="optional" />
              </div>
              <div className="space-y-2">
                <Label>Fee ZAR</Label>
                <Input value={tierForm.fee_zar} onChange={(e) => setTierForm({ ...tierForm, fee_zar: e.target.value })} required />
              </div>
              <div className="space-y-2">
                <Label>Label</Label>
                <Input value={tierForm.label} onChange={(e) => setTierForm({ ...tierForm, label: e.target.value })} placeholder="R501 – R1,000" />
              </div>
            </div>
            <Button type="submit" size="sm">Add tier</Button>
          </form>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Corridor exchange rates</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={addRate} className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-2">
                  <Label>Rate</Label>
                  <Input value={rateForm.rate} onChange={(e) => setRateForm({ ...rateForm, rate: e.target.value })} type="number" step="0.000001" required />
                </div>
                <div className="space-y-2">
                  <Label>Effective From</Label>
                  <Input type="date" value={rateForm.effective_from} onChange={(e) => setRateForm({ ...rateForm, effective_from: e.target.value })} required />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Change Reason</Label>
                <Input value={rateForm.change_reason} onChange={(e) => setRateForm({ ...rateForm, change_reason: e.target.value })} placeholder="e.g. Market adjustment" />
              </div>
              <Button type="submit" size="sm">Set Rate</Button>
            </form>
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-600">Rate History</p>
              {history.map((r) => (
                <div key={r.id} className="flex justify-between rounded border p-2 text-sm">
                  <span>1 {r.from_currency} = {r.rate} {r.to_currency}</span>
                  <span className="text-gray-500">{r.effective_from}{r.change_reason ? ` · ${r.change_reason}` : ""}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Legacy fee rules (fallback)</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={addFee} className="space-y-3">
              <div className="space-y-2">
                <Label>Name</Label>
                <Input value={feeForm.name} onChange={(e) => setFeeForm({ ...feeForm, name: e.target.value })} required />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-2">
                  <Label>Min Amount (ZAR)</Label>
                  <Input value={feeForm.min_amount_zar} onChange={(e) => setFeeForm({ ...feeForm, min_amount_zar: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label>Fee Value</Label>
                  <Input value={feeForm.fee_value} onChange={(e) => setFeeForm({ ...feeForm, fee_value: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-2">
                  <Label>Country (optional)</Label>
                  <Input value={feeForm.destination_country} onChange={(e) => setFeeForm({ ...feeForm, destination_country: e.target.value })} placeholder="GH" maxLength={2} />
                </div>
                <div className="space-y-2">
                  <Label>Priority</Label>
                  <Input value={feeForm.priority} onChange={(e) => setFeeForm({ ...feeForm, priority: e.target.value })} type="number" />
                </div>
              </div>
              <Button type="submit" size="sm">Add Fee Rule</Button>
            </form>
            <div className="space-y-2">
              {fees.map((f) => (
                <div key={f.id} className="rounded border p-2 text-sm">
                  <p className="font-medium">{f.name} {f.is_active ? "" : "(inactive)"}</p>
                  <p className="text-gray-500">
                    From R{f.min_amount_zar} — {f.fee_type}: {f.fee_value}
                    {f.destination_country ? ` · ${f.destination_country}` : ""}
                    {f.priority ? ` · priority ${f.priority}` : ""}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>FX Rate Sources (v4 engine)</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={addFxSource} className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-2">
                  <Label>Code</Label>
                  <Input value={fxSourceForm.code} onChange={(e) => setFxSourceForm({ ...fxSourceForm, code: e.target.value })} required />
                </div>
                <div className="space-y-2">
                  <Label>Name</Label>
                  <Input value={fxSourceForm.name} onChange={(e) => setFxSourceForm({ ...fxSourceForm, name: e.target.value })} required />
                </div>
              </div>
              <Button type="submit" size="sm">Add Source</Button>
            </form>
            <div className="space-y-2">
              {fxSources.map((s) => (
                <div key={s.id} className="rounded border p-2 text-sm">
                  <p className="font-medium">{s.name} ({s.code})</p>
                  <p className="text-gray-500">{s.source_type} · priority {s.priority}{s.is_active ? "" : " · inactive"}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>FX Markup Rules</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={addFxMarkup} className="space-y-3">
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                <div className="space-y-2">
                  <Label>Markup %</Label>
                  <Input value={fxMarkupForm.markup_value} onChange={(e) => setFxMarkupForm({ ...fxMarkupForm, markup_value: e.target.value })} type="number" step="0.01" required />
                </div>
                <div className="space-y-2">
                  <Label>From</Label>
                  <Input value={fxMarkupForm.from_currency} onChange={(e) => setFxMarkupForm({ ...fxMarkupForm, from_currency: e.target.value })} maxLength={3} />
                </div>
                <div className="space-y-2">
                  <Label>To</Label>
                  <Input value={fxMarkupForm.to_currency} onChange={(e) => setFxMarkupForm({ ...fxMarkupForm, to_currency: e.target.value })} maxLength={3} />
                </div>
              </div>
              <Button type="submit" size="sm">Add Markup Rule</Button>
            </form>
            <div className="space-y-2">
              {fxMarkup.map((m) => (
                <div key={m.id} className="rounded border p-2 text-sm">
                  <p className="font-medium">{m.from_currency} → {m.to_currency}</p>
                  <p className="text-gray-500">{m.markup_type}: {m.markup_value} · priority {m.priority}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Retail Payment Networks</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {retailNetworks.map((n) => (
              <span key={n} className="rounded-full bg-[#1B5E3B]/10 px-3 py-1 text-sm font-medium text-[#1B5E3B]">{n}</span>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
