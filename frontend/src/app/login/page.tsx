"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth, getHomeForRole } from "@/lib/auth";
import { ApiError } from "@/lib/api";
import { getDeviceId, getDeviceLabel } from "@/lib/device";

type LoginMode = "password" | "otp" | "step_up";

export default function LoginPage() {
  const { login, loginWithOtp, sendOtp, completeStepUp } = useAuth();
  const router = useRouter();
  const [mode, setMode] = useState<LoginMode>("password");
  const [identifier, setIdentifier] = useState("");
  const [mobile, setMobile] = useState("");
  const [password, setPassword] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpChannel, setOtpChannel] = useState<"sms" | "whatsapp">("sms");
  const [mfaCode, setMfaCode] = useState("");
  const [mfaStep, setMfaStep] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [devCode, setDevCode] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const finishLogin = (user: { role: string } | null) => {
    if (user) router.push(getHomeForRole(user.role));
  };

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await login(identifier, password, mfaStep ? mfaCode : undefined);
      if (result.mfaRequired) {
        setMfaStep(true);
        return;
      }
      if (result.stepUpRequired) {
        setMode("step_up");
        setMobile(result.stepUpMobile || "");
        setOtpSent(true);
        setError("Additional verification required. Enter the code sent to your mobile.");
        return;
      }
      finishLogin(result.user);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSendOtp = async () => {
    setError("");
    setLoading(true);
    try {
      const res = await sendOtp(mobile, otpChannel, mode === "step_up" ? "step_up" : "login");
      setOtpSent(true);
      if (res.dev_code) setDevCode(res.dev_code);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to send code");
    } finally {
      setLoading(false);
    }
  };

  const handleOtpLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = mode === "step_up"
        ? await completeStepUp(mobile, otpCode)
        : await loginWithOtp(mobile, otpCode);
      finishLogin(result.user);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">
            {mfaStep ? "Two-factor authentication" : mode === "step_up" ? "Verify your device" : "Welcome back"}
          </CardTitle>
          <CardDescription>
            {mode === "otp" ? "Sign in with a one-time code" : "Sign in with mobile, email, or OTP"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!mfaStep && mode !== "step_up" && (
            <div className="mb-4 flex rounded-lg border p-1">
              <button
                type="button"
                className={`flex-1 rounded-md py-2 text-sm font-medium ${mode === "password" ? "bg-[#1B5E3B] text-white" : "text-gray-600"}`}
                onClick={() => { setMode("password"); setOtpSent(false); setError(""); }}
              >
                Password
              </button>
              <button
                type="button"
                className={`flex-1 rounded-md py-2 text-sm font-medium ${mode === "otp" ? "bg-[#1B5E3B] text-white" : "text-gray-600"}`}
                onClick={() => { setMode("otp"); setOtpSent(false); setError(""); }}
              >
                OTP Login
              </button>
            </div>
          )}

          {error && <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          {mode === "password" && !mfaStep && (
            <form onSubmit={handlePasswordLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="identifier">Mobile Number or Email</Label>
                <Input
                  id="identifier"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="+27... or you@email.com"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Signing in..." : "Sign In"}
              </Button>
            </form>
          )}

          {mfaStep && (
            <form onSubmit={handlePasswordLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="mfa">Authenticator code</Label>
                <Input id="mfa" inputMode="numeric" value={mfaCode} onChange={(e) => setMfaCode(e.target.value)} required maxLength={6} />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>Verify</Button>
              <Button type="button" variant="ghost" className="w-full" onClick={() => setMfaStep(false)}>Back</Button>
            </form>
          )}

          {(mode === "otp" || mode === "step_up") && !mfaStep && (
            <form onSubmit={handleOtpLogin} className="space-y-4">
              {mode === "otp" && (
                <div className="space-y-2">
                  <Label htmlFor="mobile">Mobile Number</Label>
                  <Input
                    id="mobile"
                    type="tel"
                    value={mobile}
                    onChange={(e) => setMobile(e.target.value)}
                    placeholder="+27721234567"
                    required
                    disabled={otpSent}
                  />
                </div>
              )}
              {mode === "step_up" && (
                <p className="text-sm text-gray-600">Enter the verification code sent to your registered mobile number.</p>
              )}
              {!otpSent && mode === "otp" && (
                <div className="space-y-2">
                  <Label>Delivery channel</Label>
                  <div className="flex gap-2">
                    <Button type="button" variant={otpChannel === "sms" ? "default" : "outline"} size="sm" onClick={() => setOtpChannel("sms")}>SMS</Button>
                    <Button type="button" variant={otpChannel === "whatsapp" ? "default" : "outline"} size="sm" onClick={() => setOtpChannel("whatsapp")}>WhatsApp</Button>
                  </div>
                  <Button type="button" className="w-full" onClick={handleSendOtp} disabled={loading || !mobile}>
                    Send Code
                  </Button>
                </div>
              )}
              {otpSent && (
                <>
                  {devCode && <p className="rounded bg-amber-50 p-2 text-xs text-amber-800">Dev code: {devCode}</p>}
                  <div className="space-y-2">
                    <Label htmlFor="otp">Verification Code</Label>
                    <Input id="otp" inputMode="numeric" value={otpCode} onChange={(e) => setOtpCode(e.target.value)} required maxLength={6} />
                  </div>
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? "Verifying..." : "Verify & Sign In"}
                  </Button>
                  {mode === "otp" && (
                    <Button type="button" variant="ghost" className="w-full" onClick={() => { setOtpSent(false); setDevCode(null); }}>
                      Resend code
                    </Button>
                  )}
                </>
              )}
            </form>
          )}

          <p className="mt-4 text-center text-sm text-gray-500">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="font-medium text-[#1B5E3B] hover:underline">Register</Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
