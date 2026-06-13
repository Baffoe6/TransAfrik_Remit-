"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api, getApiBaseUrl } from "@/lib/api";

type Lead = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  mobile: string | null;
  country_to: string;
  estimated_monthly_volume: string | null;
  created_at: string;
};

export default function AdminWaitlistPage() {
  const [search, setSearch] = useState("");
  const [data, setData] = useState<{ count: number; leads: Lead[] } | null>(null);

  function load(q?: string) {
    const params = q ? `?search=${encodeURIComponent(q)}` : "";
    api<{ count: number; leads: Lead[] }>(`/admin/waitlist${params}`).then(setData).catch(() => {});
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#1B5E3B]">Waitlist</h1>
          <p className="text-gray-500">{data?.count ?? 0} leads</p>
        </div>
        <div className="flex gap-2">
          <Input placeholder="Search..." value={search} onChange={(e) => setSearch(e.target.value)} />
          <Button variant="outline" onClick={() => load(search)}>Search</Button>
          <a href={`${getApiBaseUrl()}/api/v1/admin/waitlist/export`} target="_blank" rel="noreferrer">
            <Button>Export CSV</Button>
          </a>
        </div>
      </div>
      <Card>
        <CardHeader><CardTitle>Leads</CardTitle></CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="p-2">Name</th><th className="p-2">Email</th><th className="p-2">Mobile</th>
                <th className="p-2">To</th><th className="p-2">Volume</th><th className="p-2">Joined</th>
              </tr>
            </thead>
            <tbody>
              {(data?.leads ?? []).map((l) => (
                <tr key={l.id} className="border-b">
                  <td className="p-2">{l.first_name} {l.last_name}</td>
                  <td className="p-2">{l.email}</td>
                  <td className="p-2">{l.mobile || "—"}</td>
                  <td className="p-2">{l.country_to}</td>
                  <td className="p-2">{l.estimated_monthly_volume || "—"}</td>
                  <td className="p-2">{new Date(l.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
