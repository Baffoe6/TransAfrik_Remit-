"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

interface WalletProfile {
  total_sent_zar: string;
  total_fees_zar: string;
  transfer_count: number;
  completed_transfer_count: number;
  preferred_corridor: string;
  referral_code: string | null;
  last_transfer_at: string | null;
  disclaimer: string;
}

export default function WalletPage() {
  const [profile, setProfile] = useState<WalletProfile | null>(null);

  useEffect(() => {
    api<WalletProfile>("/wallet/profile").then(setProfile).catch(() => {});
  }, []);

  if (!profile) return <p className="text-gray-500">Loading wallet profile...</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Wallet Profile</h1>
      <p className="text-sm text-amber-800 bg-amber-50 rounded p-3">{profile.disclaimer}</p>
      <div className="grid gap-4 sm:grid-cols-2">
        <Card><CardHeader><CardTitle className="text-sm">Total Sent</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{formatCurrency(profile.total_sent_zar, "ZAR")}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Total Fees Paid</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{formatCurrency(profile.total_fees_zar, "ZAR")}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Transfers</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{profile.completed_transfer_count} / {profile.transfer_count}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Corridor</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{profile.preferred_corridor}</p></CardContent></Card>
      </div>
      {profile.referral_code && <p className="text-sm">Your referral code: <strong>{profile.referral_code}</strong></p>}
    </div>
  );
}
