"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

interface PilotCustomer { id: number; user_id: number; status: string; invite_code_used: string | null }
interface PilotInvite { id: number; code: string; email: string | null; status: string; uses: number }

export default function AdminPilotPage() {
  const [customers, setCustomers] = useState<PilotCustomer[]>([]);
  const [invites, setInvites] = useState<PilotInvite[]>([]);
  const [email, setEmail] = useState("");

  const load = () => {
    api<PilotCustomer[]>("/admin/pilot/customers").then(setCustomers).catch(() => {});
    api<PilotInvite[]>("/admin/pilot/invites").then(setInvites).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const createInvite = async () => {
    await api("/admin/pilot/invites", { method: "POST", body: JSON.stringify({ email: email || null, max_uses: 5 }) });
    setEmail("");
    load();
  };

  const approve = async (id: number) => {
    await api(`/admin/pilot/customers/${id}/approve`, { method: "POST", body: JSON.stringify({}) });
    load();
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Pilot Programme Admin</h1>
      <Card>
        <CardHeader><CardTitle>Create Invite</CardTitle></CardHeader>
        <CardContent className="flex gap-2">
          <Input placeholder="Email (optional)" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Button onClick={createInvite}>Generate Invite</Button>
        </CardContent>
      </Card>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Invites</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {invites.map((i) => (
              <div key={i.id} className="flex justify-between rounded border p-2 text-sm">
                <span className="font-mono">{i.code}</span>
                <span className="text-gray-500">{i.uses} uses · {i.status}</span>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Pilot Customers</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {customers.map((c) => (
              <div key={c.id} className="flex items-center justify-between rounded border p-2 text-sm">
                <span>User #{c.user_id}</span>
                <div className="flex items-center gap-2">
                  <Badge variant={c.status === "approved" ? "success" : "warning"}>{c.status}</Badge>
                  {c.status === "pending" && <Button size="sm" onClick={() => approve(c.id)}>Approve</Button>}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
