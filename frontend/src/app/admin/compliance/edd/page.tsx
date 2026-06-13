"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import type { EddCase } from "@/types";
import { formatDate } from "@/lib/utils";

export default function EddQueuePage() {
  const [cases, setCases] = useState<EddCase[]>([]);
  const [filter, setFilter] = useState("open");

  const load = () => {
    const q = filter ? `?status_filter=${filter}` : "";
    api<EddCase[]>(`/admin/compliance/edd${q}`).then(setCases).catch(() => {});
  };
  useEffect(() => { load(); }, [filter]);

  const updateStatus = async (id: number, status: string) => {
    const notes = status === "rejected" ? prompt("Rejection notes:") : undefined;
    await api(`/admin/compliance/edd/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status, resolution_notes: notes }),
    });
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Enhanced Due Diligence Queue</h1>
        <select
          className="rounded border px-3 py-2 text-sm"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="open">Open</option>
          <option value="in_review">In Review</option>
          <option value="cleared">Cleared</option>
          <option value="escalated">Escalated</option>
          <option value="rejected">Rejected</option>
          <option value="">All</option>
        </select>
      </div>

      {cases.length === 0 ? (
        <p className="text-gray-500">No EDD cases in this queue.</p>
      ) : (
        cases.map((c) => (
          <Card key={c.id}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">Case #{c.id} · User {c.user_id}</CardTitle>
              <Badge variant={c.risk_score >= 50 ? "danger" : "warning"}>Risk {c.risk_score}</Badge>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>{c.reason}</p>
              <p className="text-gray-500">Transfer: {c.transfer_id ?? "—"} · {formatDate(c.created_at)}</p>
              <p className="text-gray-500">Status: <strong>{c.status}</strong></p>
              {c.aml_flags && Array.isArray(c.aml_flags) && c.aml_flags.length > 0 && (
                <ul className="rounded bg-amber-50 p-3 text-amber-800 space-y-1">
                  {c.aml_flags.map((f: { message?: string }, i: number) => (
                    <li key={i}>• {f.message || JSON.stringify(f)}</li>
                  ))}
                </ul>
              )}
              {c.status === "open" && (
                <div className="flex flex-wrap gap-2">
                  <Button size="sm" onClick={() => updateStatus(c.id, "in_review")}>Start Review</Button>
                  <Button size="sm" onClick={() => updateStatus(c.id, "cleared")}>Clear</Button>
                  <Button size="sm" onClick={() => updateStatus(c.id, "escalated")}>Escalate</Button>
                  <Button size="sm" variant="destructive" onClick={() => updateStatus(c.id, "rejected")}>Reject</Button>
                </div>
              )}
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}
