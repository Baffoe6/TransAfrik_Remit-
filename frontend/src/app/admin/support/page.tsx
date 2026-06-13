"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

interface Ticket {
  id: number;
  email: string | null;
  subject: string;
  message: string;
  status: string;
  resolution: string | null;
  created_at: string;
}

export default function AdminSupportPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);

  const load = () => api<Ticket[]>("/admin/support/tickets").then(setTickets).catch(() => {});
  useEffect(() => { load(); }, []);

  const resolve = async (id: number) => {
    const resolution = prompt("Resolution notes:");
    if (!resolution) return;
    await api(`/admin/support/tickets/${id}?status=resolved&resolution=${encodeURIComponent(resolution)}`, {
      method: "PATCH",
    });
    load();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Support Tickets</h1>
      {tickets.length === 0 ? (
        <p className="text-gray-500">No support tickets.</p>
      ) : (
        tickets.map((t) => (
          <Card key={t.id}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">{t.subject}</CardTitle>
              <span className="text-xs text-gray-500">{t.status}</span>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p className="text-gray-500">{t.email} · {formatDate(t.created_at)}</p>
              <p>{t.message}</p>
              {t.resolution && <p className="text-green-700">Resolved: {t.resolution}</p>}
              {t.status === "open" && (
                <Button size="sm" onClick={() => resolve(t.id)}>Mark Resolved</Button>
              )}
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}
