"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

interface DemoJourneys {
  warning: string;
  customer_journey: { step: number; action: string; path: string }[];
  admin_journey: { step: number; action: string; path: string }[];
  agent_journey: { step: number; action: string; path: string }[];
  founder_journey: { step: number; action: string; path: string }[];
}

export default function DemoModePage() {
  const [data, setData] = useState<DemoJourneys | null>(null);

  const load = () => api<DemoJourneys>("/admin/demo/journeys").then(setData).catch(() => {});
  useEffect(() => { load(); }, []);

  const enable = async () => { await api("/admin/demo/enable", { method: "POST" }); load(); };
  const disable = async () => { await api("/admin/demo/disable", { method: "POST" }); load(); };

  if (!data) return <p className="text-gray-500">Loading demo mode...</p>;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Demo Mode</h1>
        <div className="flex gap-2">
          <Button size="sm" onClick={enable}>Enable Demo</Button>
          <Button size="sm" variant="outline" onClick={disable}>Disable Demo</Button>
        </div>
      </div>
      <div className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">{data.warning}</div>
      {(["customer_journey", "admin_journey", "agent_journey", "founder_journey"] as const).map((key) => (
        <Card key={key}>
          <CardHeader><CardTitle className="capitalize">{key.replace("_", " ")}</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {data[key].map((j) => (
              <div key={j.step} className="flex justify-between text-sm">
                <span>{j.step}. {j.action}</span>
                <Link href={j.path} className="text-[#1B5E3B] hover:underline">{j.path}</Link>
              </div>
            ))}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
