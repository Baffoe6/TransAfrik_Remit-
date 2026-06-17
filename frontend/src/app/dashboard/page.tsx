"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  FileCheck,
  Gift,
  History,
  Send,
  UserCircle,
  Users,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge, KycStatusBadge } from "@/components/transfers/status-badge";
import { api } from "@/lib/api";
import type { DashboardSummary } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Smartphone } from "lucide-react";
import { useAuth } from "@/lib/auth";

export default function CustomerDashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<DashboardSummary>("/dashboard/summary")
      .then(setSummary)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-gray-500">Loading dashboard...</p>;
  }

  const profilePct = summary?.profile_completion.percent ?? 0;
  const kycRaw = summary?.kyc.raw_status ?? "not_submitted";

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Dashboard</h1>
        <p className="text-gray-500">Your remittance overview</p>
      </div>

      <Card className="border-[#1B5E3B]/25 bg-gradient-to-r from-[#1B5E3B]/5 to-transparent">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base text-[#1B5E3B]">
            <Smartphone className="h-5 w-5" /> Your Mobile Identity
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xl font-semibold">
              {summary?.mobile_identity.formatted_mobile || summary?.mobile_identity.mobile_number || "—"}
            </p>
            <p className="text-sm text-gray-500">Customer ID: {user?.id ?? "—"}</p>
          </div>
          <div className="text-right">
            <p className={`text-sm font-medium ${summary?.mobile_identity.verified ? "text-green-700" : "text-amber-700"}`}>
              {summary?.mobile_identity.verification_status ?? "Pending verification"}
            </p>
            {!summary?.mobile_identity.verified && (
              <Link href="/dashboard/profile" className="text-xs text-[#1B5E3B] underline">Verify mobile</Link>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-gray-500">
              <UserCircle className="h-4 w-4" /> Profile
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{profilePct}%</p>
            <p className="text-xs text-gray-500">completion</p>
            {profilePct < 100 && (
              <Link href="/dashboard/profile" className="mt-2 inline-block text-xs text-[#1B5E3B] underline">
                Complete profile
              </Link>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-gray-500">
              <FileCheck className="h-4 w-4" /> KYC
            </CardTitle>
          </CardHeader>
          <CardContent>
            <KycStatusBadge status={kycRaw} />
            <p className="mt-1 text-xs text-gray-500">{summary?.kyc.status ?? "Draft"}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-gray-500">
              <Users className="h-4 w-4" /> Beneficiaries
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{summary?.beneficiaries.count ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-gray-500">
              <Send className="h-4 w-4" /> Transfers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{summary?.transfers.count ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-gray-500">
              <History className="h-4 w-4" /> History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{summary?.transaction_history.length ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-gray-500">
              <Gift className="h-4 w-4" /> Referrals
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{summary?.referral_program.referrals_made ?? 0}</p>
            <Link href="/dashboard/referrals" className="mt-1 inline-block text-xs text-[#1B5E3B] underline">
              View program
            </Link>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Transfers</CardTitle>
            <div className="flex gap-2">
              <Link href="/dashboard/transfers/new">
                <Button size="sm"><Send className="h-4 w-4" /> New</Button>
              </Link>
              <Link href="/dashboard/transfers">
                <Button variant="ghost" size="sm">View all <ArrowRight className="h-4 w-4" /></Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {(summary?.transfers.recent.length ?? 0) === 0 ? (
              <p className="text-sm text-gray-500">No transfers yet. Create your first transfer to get started.</p>
            ) : (
              <div className="space-y-3">
                {summary?.transfers.recent.map((t) => (
                  <Link
                    key={t.id}
                    href={`/dashboard/transfers/${t.id}`}
                    className="flex items-center justify-between rounded-lg border p-3 transition hover:bg-gray-50"
                  >
                    <div>
                      <p className="font-medium">{t.reference}</p>
                      <p className="text-sm text-gray-500">{t.created_at ? formatDate(t.created_at) : "—"}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">{formatCurrency(t.total_amount_zar, "ZAR")}</p>
                      <StatusBadge status={t.status} />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Profile Completion</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-3 h-2 w-full rounded-full bg-gray-100">
                <div className="h-2 rounded-full bg-[#1B5E3B]" style={{ width: `${profilePct}%` }} />
              </div>
              {(summary?.profile_completion.missing.length ?? 0) > 0 ? (
                <p className="text-sm text-gray-500">
                  Missing: {summary?.profile_completion.missing.join(", ")}
                </p>
              ) : (
                <p className="text-sm text-green-600">Profile complete</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2 text-base"><FileCheck className="h-5 w-5" /> KYC Status</CardTitle></CardHeader>
            <CardContent>
              <p className="mb-2 text-sm">{summary?.kyc.status ?? "Draft"} — {summary?.kyc.documents_uploaded ?? 0} documents uploaded</p>
              {summary?.kyc.rejection_reason && (
                <p className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{summary.kyc.rejection_reason}</p>
              )}
              <Link href="/dashboard/kyc"><Button variant="outline" className="w-full">Manage KYC</Button></Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2 text-base"><Users className="h-5 w-5" /> Beneficiaries</CardTitle></CardHeader>
            <CardContent>
              {(summary?.beneficiaries.items.length ?? 0) === 0 ? (
                <p className="mb-3 text-sm text-gray-500">Add recipients to start sending.</p>
              ) : (
                <ul className="mb-3 space-y-1 text-sm">
                  {summary?.beneficiaries.items.slice(0, 3).map((b) => (
                    <li key={b.id}>{b.full_name} · {b.country}</li>
                  ))}
                </ul>
              )}
              <Link href="/dashboard/beneficiaries"><Button variant="outline" className="w-full">Manage Beneficiaries</Button></Link>
            </CardContent>
          </Card>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Transaction History</CardTitle>
          <Link href="/dashboard/transfers"><Button variant="ghost" size="sm">All transfers</Button></Link>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          {(summary?.transaction_history.length ?? 0) === 0 ? (
            <p className="text-sm text-gray-500">No transaction history yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="p-2">Reference</th>
                  <th className="p-2">Amount</th>
                  <th className="p-2">Fee</th>
                  <th className="p-2">Rate</th>
                  <th className="p-2">Status</th>
                  <th className="p-2">Date</th>
                </tr>
              </thead>
              <tbody>
                {summary?.transaction_history.slice(0, 10).map((t) => (
                  <tr key={t.id} className="border-b">
                    <td className="p-2">
                      <Link href={`/dashboard/transfers/${t.id}`} className="text-[#1B5E3B] underline">
                        {t.reference}
                      </Link>
                    </td>
                    <td className="p-2">{formatCurrency(t.send_amount_zar, "ZAR")}</td>
                    <td className="p-2">{formatCurrency(t.fee_zar, "ZAR")}</td>
                    <td className="p-2">{t.exchange_rate}</td>
                    <td className="p-2"><StatusBadge status={t.status} /></td>
                    <td className="p-2">{t.created_at ? formatDate(t.created_at) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
