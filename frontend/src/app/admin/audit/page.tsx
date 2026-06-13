"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { AuditLog } from "@/types";
import { formatDate } from "@/lib/utils";

export default function AdminAuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);

  useEffect(() => {
    api<AuditLog[]>("/admin/audit-logs").then(setLogs).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Audit Logs</h1>
      <Card>
        <CardHeader><CardTitle>Recent Admin Actions</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-4">Time</th>
                  <th className="pb-3 pr-4">Action</th>
                  <th className="pb-3 pr-4">Entity</th>
                  <th className="pb-3 pr-4">User ID</th>
                  <th className="pb-3">IP</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} className="border-b">
                    <td className="py-3 pr-4">{formatDate(log.created_at)}</td>
                    <td className="py-3 pr-4 font-medium">{log.action}</td>
                    <td className="py-3 pr-4">{log.entity_type} #{log.entity_id}</td>
                    <td className="py-3 pr-4">{log.user_id ?? "—"}</td>
                    <td className="py-3">{log.ip_address ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
