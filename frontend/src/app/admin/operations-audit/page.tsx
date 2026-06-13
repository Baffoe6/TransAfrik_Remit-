"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { OperationsAuditEntry } from "@/types";

const CATEGORIES = ["", "batch", "settlement", "treasury", "provider"];

export default function OperationsAuditPage() {
  const [logs, setLogs] = useState<OperationsAuditEntry[]>([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    const q = filter ? `?category=${filter}` : "";
    api<OperationsAuditEntry[]>(`/admin/operations-audit${q}`).then(setLogs).catch(() => {});
  }, [filter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Operations Audit Trail</h1>
        <select className="rounded border px-3 py-2 text-sm" value={filter} onChange={(e) => setFilter(e.target.value)}>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c || "All categories"}</option>
          ))}
        </select>
      </div>

      <Card>
        <CardHeader><CardTitle>Batch · Settlement · Treasury · Provider Actions</CardTitle></CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm max-h-[600px] overflow-y-auto">
            {logs.map((log) => (
              <li key={log.id} className="rounded border p-3">
                <div className="flex justify-between">
                  <span>
                    <span className="rounded bg-[#1B5E3B]/10 px-2 py-0.5 text-xs font-medium">{log.category}</span>
                    {" "}<strong>{log.action}</strong> on {log.entity_type}
                  </span>
                  <span className="text-gray-500">{new Date(log.created_at).toLocaleString()}</span>
                </div>
                {log.details && <pre className="mt-1 text-xs text-gray-600 overflow-x-auto">{JSON.stringify(log.details, null, 2)}</pre>}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
