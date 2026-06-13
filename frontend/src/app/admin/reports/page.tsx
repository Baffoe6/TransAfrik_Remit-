"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

interface ReportSummary {
  transfers_by_status: Record<string, number>;
  total_completed_volume_zar: string;
  aml_flagged_transfers: number;
}

export default function AdminReportsPage() {
  const [report, setReport] = useState<ReportSummary | null>(null);

  useEffect(() => {
    api<ReportSummary>("/admin/reports/summary").then(setReport).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Reports</h1>
      {report && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader><CardTitle>Transfers by Status</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(report.transfers_by_status).map(([status, count]) => (
                  <div key={status} className="flex justify-between rounded border p-2 text-sm">
                    <span className="capitalize">{status.replace(/_/g, " ")}</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Summary</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Total Completed Volume</span>
                <span className="font-semibold">R {report.total_completed_volume_zar}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>AML Flagged Transfers</span>
                <span className="font-semibold">{report.aml_flagged_transfers}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
