"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";

const DESTINATIONS = [
  { code: "GH", label: "Ghana" },
  { code: "ZW", label: "Zimbabwe" },
  { code: "ZM", label: "Zambia" },
  { code: "KE", label: "Kenya" },
  { code: "NG", label: "Nigeria" },
  { code: "UG", label: "Uganda" },
];

const VOLUMES = ["Under R5,000", "R5,000 – R20,000", "R20,000 – R50,000", "Over R50,000"];

export default function WaitlistPage() {
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    mobile: "",
    country_to: "GH",
    estimated_monthly_volume: VOLUMES[0],
  });
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api("/waitlist/join", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          country_from: "ZA",
          email: form.email || undefined,
        }),
      });
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to join waitlist");
    }
  }

  if (done) {
    return (
      <div className="mx-auto max-w-lg px-4 py-16 text-center">
        <Card>
          <CardHeader>
            <CardTitle className="text-[#1B5E3B]">You&apos;re on the list</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">Thank you for your interest in TransAfrik Remit. We&apos;ll notify you when your corridor opens.</p>
            <Link href="/"><Button variant="outline">Back to home</Button></Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-12">
      <Card>
        <CardHeader>
          <CardTitle className="text-[#1B5E3B]">Join the Waitlist</CardTitle>
          <p className="text-sm text-gray-500">Be first to send money when we launch your corridor.</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={submit} className="space-y-4">
            {error && <p className="rounded bg-red-50 p-2 text-sm text-red-700">{error}</p>}
            <div className="grid gap-4 sm:grid-cols-2">
              <div><Label>First name</Label><Input required value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /></div>
              <div><Label>Last name</Label><Input required value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></div>
            </div>
            <div><Label>Mobile Number</Label><Input type="tel" required value={form.mobile} onChange={(e) => setForm({ ...form, mobile: e.target.value })} placeholder="+27721234567" /></div>
            <div><Label>Email (optional)</Label><Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></div>
            <div>
              <Label>Destination country</Label>
              <select className="w-full rounded-md border px-3 py-2" value={form.country_to} onChange={(e) => setForm({ ...form, country_to: e.target.value })}>
                {DESTINATIONS.map((d) => <option key={d.code} value={d.code}>{d.label}</option>)}
              </select>
            </div>
            <div>
              <Label>Estimated monthly transfer volume</Label>
              <select className="w-full rounded-md border px-3 py-2" value={form.estimated_monthly_volume} onChange={(e) => setForm({ ...form, estimated_monthly_volume: e.target.value })}>
                {VOLUMES.map((v) => <option key={v} value={v}>{v}</option>)}
              </select>
            </div>
            <Button type="submit" className="w-full">Join Waitlist</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
