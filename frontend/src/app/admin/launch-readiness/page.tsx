"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

type Check = { id: string; label: string; passed: boolean; detail?: string };

export default function LaunchReadinessPage() {
  const [data, setData] = useState<{
    readiness_percent: number;
    ready: boolean;
    checks: Check[];
    passed: number;
    total: number;
  } | null>(null);

  useEffect(() => {
    api<typeof data>("/admin/launch-readiness").then(setData).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Launch Readiness</h1>
        <p className="text-gray-500">Production go-live checklist</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Readiness Score</span>
            <span className={`text-3xl ${data && data.readiness_percent >= 80 ? "text-green-600" : "text-amber-600"}`}>
              {data?.readiness_percent ?? 0}%
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 h-3 w-full rounded-full bg-gray-100">
            <div className="h-3 rounded-full bg-[#1B5E3B]" style={{ width: `${data?.readiness_percent ?? 0}%` }} />
          </div>
          <p className="text-sm text-gray-500">{data?.passed}/{data?.total} checks passed</p>
        </CardContent>
      </Card>
      <div className="grid gap-3">
        {(data?.checks ?? []).map((c) => (
          <Card key={c.id} className={c.passed ? "border-green-200" : "border-red-200"}>
            <CardContent className="flex items-center justify-between py-4">
              <div>
                <p className="font-medium">{c.label}</p>
                {c.detail && <p className="text-xs text-gray-500">{c.detail}</p>}
              </div>
              <span className={c.passed ? "text-green-600" : "text-red-600"}>{c.passed ? "Pass" : "Fail"}</span>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
