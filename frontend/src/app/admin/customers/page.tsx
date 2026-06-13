"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { KycStatusBadge } from "@/components/transfers/status-badge";
import { api } from "@/lib/api";
import type { CustomerListItem } from "@/types";
import { formatDate } from "@/lib/utils";

export default function AdminCustomersPage() {
  const [customers, setCustomers] = useState<CustomerListItem[]>([]);

  useEffect(() => {
    api<CustomerListItem[]>("/admin/customers").then(setCustomers).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Customer Management</h1>
      <Card>
        <CardHeader><CardTitle>All Customers</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 pr-4">Name</th>
                  <th className="pb-3 pr-4">Email</th>
                  <th className="pb-3 pr-4">KYC</th>
                  <th className="pb-3 pr-4">Transfers</th>
                  <th className="pb-3">Joined</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((c) => (
                  <tr key={c.id} className="border-b">
                    <td className="py-3 pr-4">{c.first_name} {c.last_name}</td>
                    <td className="py-3 pr-4">{c.email}</td>
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
