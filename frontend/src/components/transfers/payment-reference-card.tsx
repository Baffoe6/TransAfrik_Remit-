"use client";

import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { isDevMode } from "@/lib/api";
import type { PaymentReferenceBrief } from "@/types";

interface Props {
  transferReference: string;
  transferId: number;
  transferStatus: string;
  paymentRef: PaymentReferenceBrief;
  onMarkPaid?: () => void;
  onDownloadVoucher: () => void;
}

export function PaymentReferenceCard({
  transferReference,
  transferId,
  transferStatus,
  paymentRef,
  onMarkPaid,
  onDownloadVoucher,
}: Props) {
  const isVoucher = !!paymentRef.voucher_number;
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(paymentRef.qr_data || paymentRef.reference_number)}`;

  return (
    <Card className="border-[#C9A227]/30">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Payment Instructions</CardTitle>
        {isVoucher && (
          <Button size="sm" variant="secondary" onClick={onDownloadVoucher}>
            <Download className="h-4 w-4" /> Download Voucher PDF
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">Payment Reference</span>
          <span className="font-mono font-semibold">{paymentRef.reference_number}</span>
        </div>
        {paymentRef.voucher_number && (
          <div className="flex justify-between">
            <span className="text-gray-500">Voucher Number</span>
            <span className="font-mono">{paymentRef.voucher_number}</span>
          </div>
        )}
        {paymentRef.expiry_date && (
          <div className="flex justify-between">
            <span className="text-gray-500">Expires</span>
            <span>{paymentRef.expiry_date}</span>
          </div>
        )}
        {paymentRef.barcode_data && (
          <div className="rounded bg-gray-100 p-3 font-mono text-xs text-center tracking-widest">
            {paymentRef.barcode_data}
          </div>
        )}
        <div className="flex justify-center py-2">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={qrUrl} alt="Payment QR Code" width={150} height={150} className="rounded border" />
        </div>
        {paymentRef.banking_instructions && (
          <div className="rounded-lg bg-[#1B5E3B]/5 p-4 space-y-1">
            <p className="font-medium text-[#1B5E3B]">Banking Details</p>
            {Object.entries(paymentRef.banking_instructions).map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <span className="capitalize text-gray-500">{k.replace(/_/g, " ")}</span>
                <span className="font-medium">{v}</span>
              </div>
            ))}
          </div>
        )}
        {isVoucher && transferStatus === "awaiting_payment" && isDevMode() && onMarkPaid && (
          <Button variant="outline" size="sm" onClick={onMarkPaid} className="w-full">
            Simulate Retailer Payment (Dev Only)
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
