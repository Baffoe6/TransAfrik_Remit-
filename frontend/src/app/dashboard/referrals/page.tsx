"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

interface ReferralDashboard {
  referral_code: string;
  program_name: string;
  total_points: number;
  voucher_threshold: number;
  referrals_made: number;
  referrals: { id: number; referred_user_id: number | null; converted: boolean; created_at: string }[];
  vouchers: { code: string; discount_zar: string; status: string }[];
}

export default function CustomerReferralsPage() {
  const [data, setData] = useState<ReferralDashboard | null>(null);

  useEffect(() => {
    api<ReferralDashboard>("/referrals/dashboard").then(setData).catch(() => {});
  }, []);

  if (!data) return <p className="text-gray-500">Loading referral program...</p>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-[#1B5E3B]">My Referrals</h1>
        <p className="text-gray-600">{data.program_name}</p>
      </div>
      <Card>
        <CardHeader><CardTitle>Your Referral Code</CardTitle></CardHeader>
        <CardContent>
          <p className="text-3xl font-bold tracking-wider text-[#1B5E3B]">{data.referral_code}</p>
          <p className="mt-2 text-sm text-gray-500">Share this code with friends to earn rewards</p>
        </CardContent>
      </Card>
      <div className="grid gap-4 sm:grid-cols-3">
        <Card><CardHeader><CardTitle className="text-sm">Reward Points</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.total_points}</p><p className="text-xs text-gray-500">/{data.voucher_threshold} for voucher</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Referrals Made</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.referrals_made}</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Vouchers</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{data.vouchers.length}</p></CardContent></Card>
      </div>
      {data.vouchers.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Discount Vouchers</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {data.vouchers.map((v) => (
              <div key={v.code} className="flex justify-between rounded border p-2 text-sm">
                <span className="font-mono">{v.code}</span>
                <div className="flex gap-2">
                  <span>{formatCurrency(v.discount_zar, "ZAR")} off</span>
                  <Badge>{v.status}</Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
