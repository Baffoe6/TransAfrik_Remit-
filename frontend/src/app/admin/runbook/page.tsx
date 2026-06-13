"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

interface RunbookSection { id: string; title: string; steps: string[] }

export default function RunbookPage() {
  const [sections, setSections] = useState<RunbookSection[]>([]);

  useEffect(() => {
    api<{ sections: RunbookSection[] }>("/admin/runbook").then((r) => setSections(r.sections)).catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Operations Runbook</h1>
      <div className="grid gap-6 md:grid-cols-2">
        {sections.map((s) => (
          <Card key={s.id}>
            <CardHeader><CardTitle className="text-base">{s.title}</CardTitle></CardHeader>
            <CardContent>
              <ol className="list-decimal space-y-2 pl-5 text-sm text-gray-700">
                {s.steps.map((step, i) => <li key={i}>{step}</li>)}
              </ol>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
