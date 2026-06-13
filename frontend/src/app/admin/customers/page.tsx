"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { KycStatusBadge } from "@/components/transfers/status-badge";
import { api } from "@/lib/api";
import type { CustomerListItem } from "@/types";
import { formatDate } from "@/lib/utils";
import { formatPhoneNumber } from "@/lib/phone";

export default function AdminCustomersPage() {
  const [customers, setCustomers] = useState<CustomerListItem[]>([]);
  const [search, setSearch] = useState("");

  function load(q?: string) {
    const params = q ? `?search=${encodeURIComponent(q)}` : "";
    api<CustomerListItem[]>(`/admin/customers${params}`).then(setCustomers).catch(() => {});
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Customer Management</h1>
        <div className="flex gap-2">
          <Input placeholder="Search mobile, email, name, or ID..." value={search} onChange={(e) => setSearch(e.target.value)} />
          <Button variant="outline" onClick={() => load(search)}>Search</Button>
        </div>
      </div>
      <Card>
        <CardHeader><CardTitle>All Customers ({customers.length})</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-4">ID</th>
                  <th className="pb-3 pr-4">Name</th>
                  <th className="pb-3 pr-4">Mobile</th>
                  <th className="pb-3 pr-4">Email</th>
                  <th className="pb-3 pr-4">KYC</th>
                  <th className="pb-3 pr-4">Transfers</th>
                  <th className="pb-3">Joined</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((c) => (
                  <tr key={c.id} className="border-b">
                    <td className="py-3 pr-4 font-mono text-xs">{c.id}</td>
                    <td className="py-3 pr-4">{c.first_name} {c.last_name}</td>
                    <td className="py-3 pr-4">{c.mobile_number ? formatPhoneNumber(c.mobile_number) : "—"}</td>
                    <td className="py-3 pr-4">{c.email || "—"}</td>
                    <td className="py-3 pr-4">{c.kyc_status ? <KycStatusBadge status={c.kyc_status} /> : "—"}</td>
                    <td className="py-3 pr-4">{c.transfer_count}</td>
                    <td className="py-3">{formatDate(c.created_at)}</td>
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
