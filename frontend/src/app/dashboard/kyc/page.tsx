"use client";

import { useEffect, useState } from "react";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { KycStatusBadge } from "@/components/transfers/status-badge";
import { api, apiUpload } from "@/lib/api";
import type { KycDocument, Profile } from "@/types";
import { formatDate } from "@/lib/utils";

const DOC_TYPES = [
  { value: "id_passport", label: "ID / Passport" },
  { value: "proof_of_address", label: "Proof of Address" },
  { value: "selfie", label: "Selfie (Placeholder)" },
];

export default function KycPage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [documents, setDocuments] = useState<KycDocument[]>([]);
  const [docType, setDocType] = useState("id_passport");
  const [uploading, setUploading] = useState(false);

  const load = () => {
    api<Profile>("/profile").then(setProfile).catch(() => {});
    api<KycDocument[]>("/kyc/documents").then(setDocuments).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append("document_type", docType);
    form.append("file", file);
    try {
      await apiUpload("/kyc/upload", form);
      load();
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1B5E3B]">KYC Verification</h1>
        {profile && <KycStatusBadge status={profile.kyc_status} />}
      </div>

      {profile?.kyc_rejection_reason && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          Rejection reason: {profile.kyc_rejection_reason}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Upload Documents</CardTitle>
          <CardDescription>Upload clear copies of your identification documents for verification.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Document Type</Label>
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="flex h-10 w-full rounded-md border border-gray-300 px-3 text-sm"
            >
              {DOC_TYPES.map((d) => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="flex cursor-pointer items-center justify-center gap-2 rounded-lg border-2 border-dashed border-[#1B5E3B]/30 p-8 hover:border-[#1B5E3B]">
              <Upload className="h-6 w-6 text-[#1B5E3B]" />
              <span className="text-sm font-medium">{uploading ? "Uploading..." : "Choose file to upload"}</span>
              <input type="file" className="hidden" accept=".pdf,.jpg,.jpeg,.png,.webp" onChange={handleUpload} disabled={uploading} />
            </label>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Uploaded Documents</CardTitle></CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <p className="text-sm text-gray-500">No documents uploaded yet.</p>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <p className="font-medium">{doc.document_type.replace(/_/g, " ")}</p>
                    <p className="text-sm text-gray-500">{doc.original_filename} — {formatDate(doc.created_at)}</p>
                  </div>
                  <KycStatusBadge status={doc.status} />
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
