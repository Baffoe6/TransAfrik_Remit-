"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, getApiBaseUrl } from "@/lib/api";

interface DocumentItem {
  id: number;
  category: string;
  title: string;
  version: number;
  expires_at: string | null;
  created_at: string;
}

const CATEGORIES = ["fica", "kyc", "cipc_documents", "tax_documents", "bank_confirmation", "partner_agreements", "mukuru_documents", "flutterwave_documents"];

export default function AdminDocumentsPage() {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [category, setCategory] = useState("fica");
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const load = () => api<DocumentItem[]>("/admin/documents").then(setDocs).catch(() => {});
  useEffect(() => { load(); }, []);

  const upload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    form.append("category", category);
    form.append("title", title);
    const token = localStorage.getItem("access_token");
    await fetch(`${getApiBaseUrl()}/api/v1/admin/documents`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
    });
    setTitle("");
    setFile(null);
    load();
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Document & Compliance Center</h1>
      <Card>
        <CardHeader><CardTitle>Upload Document</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={upload} className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Category</Label>
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="flex h-10 w-full rounded-md border px-3 text-sm">
                {CATEGORIES.map((c) => <option key={c} value={c}>{c.replace(/_/g, " ")}</option>)}
              </select>
            </div>
            <div className="space-y-2"><Label>Title</Label><Input value={title} onChange={(e) => setTitle(e.target.value)} required /></div>
            <div className="space-y-2 sm:col-span-2"><Label>File</Label><Input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} required /></div>
            <Button type="submit" className="sm:col-span-2">Upload</Button>
          </form>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Documents</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {docs.map((d) => (
            <div key={d.id} className="flex justify-between rounded border p-2 text-sm">
              <span>{d.title} <span className="text-gray-400">v{d.version} · {d.category}</span></span>
              <a href={`${getApiBaseUrl()}/api/v1/admin/documents/${d.id}/download`} className="text-[#1B5E3B] hover:underline" target="_blank" rel="noreferrer">Download</a>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
