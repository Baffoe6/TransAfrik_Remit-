"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/lib/auth";
import { ApiError } from "@/lib/api";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    mobile_number: "",
    email: "",
    pin: "",
    confirm_pin: "",
    first_name: "",
    last_name: "",
    invite_code: "",
    referral_code: "",
  });
  const [acceptPopia, setAcceptPopia] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.pin !== form.confirm_pin) {
      setError("PINs do not match");
      return;
    }
    if (!/^\d{4,6}$/.test(form.pin)) {
      setError("PIN must be 4–6 digits");
      return;
    }
    if (!acceptPopia || !acceptTerms) {
      setError("Please accept POPIA and Terms & Conditions");
      return;
    }
    setLoading(true);
    try {
      await register({
        mobile_number: form.mobile_number,
        email: form.email || undefined,
        pin: form.pin,
        first_name: form.first_name,
        last_name: form.last_name,
        invite_code: form.invite_code || undefined,
        referral_code: form.referral_code || undefined,
        accept_popia: acceptPopia,
        accept_terms: acceptTerms,
      });
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Create your account</CardTitle>
          <CardDescription>Mobile number + 4-digit PIN — email optional</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="first_name">First Name</Label>
                <Input id="first_name" value={form.first_name} onChange={update("first_name")} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">Last Name</Label>
                <Input id="last_name" value={form.last_name} onChange={update("last_name")} required />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="mobile_number">Mobile Number</Label>
              <Input
                id="mobile_number"
                type="tel"
                inputMode="tel"
                autoComplete="tel"
                value={form.mobile_number}
                onChange={update("mobile_number")}
                placeholder="+27721234567"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email (optional)</Label>
              <Input id="email" type="email" value={form.email} onChange={update("email")} placeholder="you@email.com" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="pin">4-digit PIN</Label>
                <Input id="pin" type="password" inputMode="numeric" maxLength={6} value={form.pin} onChange={update("pin")} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm_pin">Confirm PIN</Label>
                <Input id="confirm_pin" type="password" inputMode="numeric" maxLength={6} value={form.confirm_pin} onChange={update("confirm_pin")} required />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="referral_code">Referral code (optional)</Label>
              <Input id="referral_code" value={form.referral_code} onChange={update("referral_code")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="invite_code">Invite code (optional)</Label>
              <Input id="invite_code" value={form.invite_code} onChange={update("invite_code")} placeholder="Required only during pilot" />
            </div>
            <label className="flex items-start gap-2 text-sm">
              <input type="checkbox" checked={acceptPopia} onChange={(e) => setAcceptPopia(e.target.checked)} className="mt-1" />
              <span>I consent to processing of my personal information in accordance with POPIA.</span>
            </label>
            <label className="flex items-start gap-2 text-sm">
              <input type="checkbox" checked={acceptTerms} onChange={(e) => setAcceptTerms(e.target.checked)} className="mt-1" />
              <span>I accept the Terms of Service and Privacy Policy.</span>
            </label>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creating account..." : "Create Account"}
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-gray-500">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-[#1B5E3B] hover:underline">Sign in</Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
