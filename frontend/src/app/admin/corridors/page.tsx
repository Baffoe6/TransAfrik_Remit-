"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

interface Corridor {
  id: number;
  code: string;
  source_country: string;
  destination_country: string;
  destination_currency: string;
  provider_code: string;
  status: string;
  priority: number;
}

export default function AdminCorridorsPage() {
  const [rows, setRows] = useState<Corridor[]>([]);
  const [form, setForm] = useState({
    code: "", destination_country: "", destination_currency: "", provider_code: "mock_mukuru", priority: "0",
  });

  const load = () => api<Corridor[]>("/admin/corridors").then(setRows).catch(() => {});
  useEffect(() => { load(); }, []);

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    await api("/admin/corridors", {
      method: "POST",
      body: JSON.stringify({ ...form, source_country: "ZA", priority: Number(form.priority) }),
    });
    load();
  };

  const toggle = async (id: number, status: string) => {
    await api(`/admin/corridors/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: status === "active" ? "inactive" : "active" }),
    });
    load();
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Corridor Management</h1>
      <Card>
        <CardHeader><CardTitle>Add Corridor</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={add} className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-2"><Label>Code</Label><Input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} placeholder="ZA-GH" required /></div>
            <div className="space-y-2"><Label>Destination</Label><Input value={form.destination_country} onChange={(e) => setForm({ ...form, destination_country: e.target.value })} maxLength={2} required /></div>
            <div className="space-y-2"><Label>Currency</Label><Input value={form.destination_currency} onChange={(e) => setForm({ ...form, destination_currency: e.target.value })} maxLength={3} required /></div>
            <div className="space-y-2"><Label>Provider</Label><Input value={form.provider_code} onChange={(e) => setForm({ ...form, provider_code: e.target.value })} required /></div>
            <Button type="submit" className="sm:col-span-2">Create Corridor</Button>
          </form>
        </CardContent>
      </Card>
      <div className="grid gap-4 sm:grid-cols-2">
        {rows.map((c) => (
          <Card key={c.id}>
            <CardContent className="flex items-center justify-between pt-6">
              <div>
                <p className="font-semibold">{c.code}</p>
                <p className="text-sm text-gray-500">ZA → {c.destination_country} ({c.destination_currency})</p>
                <p className="text-sm text-gray-500">Provider: {c.provider_code}</p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <Badge variant={c.status === "active" ? "success" : "warning"}>{c.status}</Badge>
                <Button size="sm" variant="outline" onClick={() => toggle(c.id, c.status)}>
                  {c.status === "active" ? "Disable" : "Enable"}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
