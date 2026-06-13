"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, FileCheck, Send, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/transfers/status-badge";
import { KycStatusBadge } from "@/components/transfers/status-badge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Profile, Transfer } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function CustomerDashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [transfers, setTransfers] = useState<Transfer[]>([]);

  useEffect(() => {
    api<Profile>("/profile").then(setProfile).catch(() => {});
    api<Transfer[]>("/transfers").then(setTransfers).catch(() => {});
  }, []);

  const recent = transfers.slice(0, 5);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Dashboard</h1>
        <p className="text-gray-500">Welcome back{profile ? `, ${profile.first_name}` : ""}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">KYC Status</CardTitle>
          </CardHeader>
          <CardContent>
            {profile ? <KycStatusBadge status={profile.kyc_status} /> : <span className="text-sm">Loading...</span>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Total Transfers</CardTitle>
          </CardHeader>
          <CardContent><p className="text-2xl font-bold">{transfers.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Email Verified</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{user?.email_verified ? "Yes" : "Pending — verify in Profile"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Quick Action</CardTitle>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/transfers/new">
              <Button size="sm"><Send className="h-4 w-4" /> New Transfer</Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Transfers</CardTitle>
            <Link href="/dashboard/transfers"><Button variant="ghost" size="sm">View all <ArrowRight className="h-4 w-4" /></Button></Link>
          </CardHeader>
          <CardContent>
            {recent.length === 0 ? (
              <p className="text-sm text-gray-500">No transfers yet. Create your first transfer to get started.</p>
            ) : (
              <div className="space-y-3">
                {recent.map((t) => (
                  <div key={t.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <p className="font-medium">{t.reference}</p>
                      <p className="text-sm text-gray-500">{formatDate(t.created_at)}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">{formatCurrency(t.send_amount_zar, "ZAR")}</p>
                      <StatusBadge status={t.status} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><FileCheck className="h-5 w-5" /> Complete KYC</CardTitle></CardHeader>
            <CardContent>
              <p className="mb-3 text-sm text-gray-500">Upload your ID and proof of address to start sending.</p>
              <Link href="/dashboard/kyc"><Button variant="outline" className="w-full">Upload Documents</Button></Link>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><Users className="h-5 w-5" /> Beneficiaries</CardTitle></CardHeader>
            <CardContent>
              <p className="mb-3 text-sm text-gray-500">Add recipients in Ghana with mobile money details.</p>
              <Link href="/dashboard/beneficiaries"><Button variant="outline" className="w-full">Manage Beneficiaries</Button></Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
