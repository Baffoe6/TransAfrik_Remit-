"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { ProviderConfigItem } from "@/types";

export default function ProvidersPage() {
  const [configs, setConfigs] = useState<ProviderConfigItem[]>([]);
  const [editing, setEditing] = useState<ProviderConfigItem | null>(null);
  const [form, setForm] = useState({
    display_name: "",
    is_enabled: false,
    is_sandbox: true,
    api_base_url: "",
    webhook_secret: "",
  });

  const load = () => api<ProviderConfigItem[]>("/admin/providers/config").then(setConfigs).catch(() => {});
  useEffect(() => { load(); }, []);

  const startEdit = (item: ProviderConfigItem) => {
    setEditing(item);
    setForm({
      display_name: item.display_name,
      is_enabled: item.is_enabled,
      is_sandbox: item.is_sandbox,
      api_base_url: item.api_base_url || "",
      webhook_secret: "",
    });
  };

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editing) return;
    await api(`/admin/providers/config/${editing.provider_code}`, {
      method: "PUT",
      body: JSON.stringify({
        display_name: form.display_name,
        is_enabled: form.is_enabled,
        is_sandbox: form.is_sandbox,
        api_base_url: form.api_base_url || null,
        webhook_secret: form.webhook_secret || null,
      }),
    });
    setEditing(null);
    load();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Provider Configuration</h1>
      <p className="text-sm text-gray-600">
        Configure payment collection (Pay@, EasyPay) and remittance (Mukuru) providers. API integrations are stubbed for production wiring.
      </p>

      <div className="grid gap-4 md:grid-cols-2">
        {configs.map((c) => (
          <Card key={c.provider_code}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">{c.display_name}</CardTitle>
              <span className={`text-xs font-medium ${c.is_enabled ? "text-green-600" : "text-gray-400"}`}>
                {c.is_enabled ? "Enabled" : "Disabled"}
              </span>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p><span className="text-gray-500">Code:</span> {c.provider_code}</p>
              <p><span className="text-gray-500">Type:</span> {c.provider_type}</p>
              <p><span className="text-gray-500">Mode:</span> {c.is_sandbox ? "Sandbox" : "Production"}</p>
              {c.api_base_url && <p><span className="text-gray-500">API:</span> {c.api_base_url}</p>}
              <div className="flex flex-wrap gap-2">
                <Button size="sm" variant="outline" onClick={() => startEdit(c)}>Configure</Button>
                <Button size="sm" variant="ghost" onClick={async () => { const r = await api<{ valid: boolean; message: string }>(`/admin/providers/${c.provider_code}/validate`, { method: "POST" }); alert(r.message); }}>Validate</Button>
                <Button size="sm" variant="ghost" onClick={async () => { const r = await api<{ healthy: boolean }>(`/admin/providers/${c.provider_code}/health`, { method: "POST" }); alert(r.healthy ? "Healthy" : "Unhealthy"); load(); }}>Health</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {editing && (
        <Card>
          <CardHeader>
            <CardTitle>Edit {editing.provider_code}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={save} className="space-y-4 max-w-lg">
              <div className="space-y-2">
                <Label>Display Name</Label>
                <Input value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })} required />
              </div>
              <div className="space-y-2">
                <Label>API Base URL</Label>
                <Input value={form.api_base_url} onChange={(e) => setForm({ ...form, api_base_url: e.target.value })} placeholder="https://api.example.com" />
              </div>
              <div className="space-y-2">
                <Label>Webhook Secret (leave blank to keep existing)</Label>
                <Input type="password" value={form.webhook_secret} onChange={(e) => setForm({ ...form, webhook_secret: e.target.value })} />
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={form.is_enabled} onChange={(e) => setForm({ ...form, is_enabled: e.target.checked })} />
                Enabled
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={form.is_sandbox} onChange={(e) => setForm({ ...form, is_sandbox: e.target.checked })} />
                Sandbox mode
              </label>
              <div className="flex gap-2">
                <Button type="submit">Save</Button>
                <Button type="button" variant="ghost" onClick={() => setEditing(null)}>Cancel</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
