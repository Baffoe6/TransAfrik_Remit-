"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

interface ChecklistItem { id: string; label: string; passed: boolean; detail?: string }
interface LaunchChecklist { items: ChecklistItem[]; passed: number; total: number; launch_ready: boolean; pilot_mode_enabled: boolean }

export default function LaunchChecklistPage() {
  const [data, setData] = useState<LaunchChecklist | null>(null);

  useEffect(() => {
    api<LaunchChecklist>("/admin/launch-checklist").then(setData).catch(() => {});
  }, []);

  if (!data) return <p className="text-gray-500">Loading launch checklist...</p>;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Launch Checklist</h1>
        <Badge variant={data.launch_ready ? "success" : "warning"}>
          {data.passed}/{data.total} — {data.launch_ready ? "Launch Ready" : "Not Ready"}
        </Badge>
      </div>
      <Card>
        <CardHeader><CardTitle>Pilot Launch Readiness</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {data.items.map((item) => (
            <div key={item.id} className="flex items-center justify-between rounded border p-3 text-sm">
              <div>
                <p className="font-medium">{item.label}</p>
                {item.detail && <p className="text-gray-500">{item.detail}</p>}
              </div>
              <Badge variant={item.passed ? "success" : "danger"}>{item.passed ? "Pass" : "Fail"}</Badge>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
