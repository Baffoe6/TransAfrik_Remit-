"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { SecurityAuditEntry, UserSessionItem } from "@/types";

export default function SecurityPage() {
  const [auditLogs, setAuditLogs] = useState<SecurityAuditEntry[]>([]);
  const [sessions, setSessions] = useState<UserSessionItem[]>([]);
  const [mfaUri, setMfaUri] = useState<string | null>(null);
  const [mfaCode, setMfaCode] = useState("");
  const [message, setMessage] = useState("");

  const load = () => {
    api<SecurityAuditEntry[]>("/admin/security/audit").then(setAuditLogs).catch(() => {});
    api<UserSessionItem[]>("/admin/security/sessions").then(setSessions).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const setupMfa = async () => {
    const res = await api<{ provisioning_uri: string }>("/admin/security/mfa/setup", { method: "POST" });
    setMfaUri(res.provisioning_uri);
    setMessage("Scan the URI in your authenticator app (or paste as otpauth URL), then enter a code below.");
  };

  const enableMfa = async (e: React.FormEvent) => {
    e.preventDefault();
    await api("/admin/security/mfa/enable", { method: "POST", body: JSON.stringify({ code: mfaCode }) });
    setMessage("MFA enabled successfully. You will need a code on next login.");
    setMfaUri(null);
    setMfaCode("");
    load();
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Security</h1>

      <Card>
        <CardHeader>
          <CardTitle>Admin MFA (TOTP)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-gray-600">Enable two-factor authentication for admin and compliance officer accounts.</p>
          <Button onClick={setupMfa}>Set up MFA</Button>
          {mfaUri && (
            <div className="rounded bg-gray-50 p-3 text-xs break-all">{mfaUri}</div>
          )}
          {message && <p className="text-sm text-green-700">{message}</p>}
          <form onSubmit={enableMfa} className="flex gap-2 max-w-sm">
            <div className="flex-1 space-y-2">
              <Label>Verification code</Label>
              <Input value={mfaCode} onChange={(e) => setMfaCode(e.target.value)} maxLength={6} />
            </div>
            <Button type="submit" className="mt-8">Enable</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Active Sessions</CardTitle>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <p className="text-sm text-gray-500">No active sessions.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {sessions.map((s) => (
                <li key={s.id} className="flex justify-between rounded border p-2">
                  <span>User #{s.user_id} · {s.ip_address || "unknown IP"}</span>
                  <span className="text-gray-500">{new Date(s.created_at).toLocaleString()}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Security Audit Log</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm max-h-96 overflow-y-auto">
            {auditLogs.map((log) => (
              <li key={log.id} className="rounded border p-2">
                <div className="flex justify-between">
                  <span className="font-medium">{log.event_type}</span>
                  <span className="text-gray-500">{new Date(log.created_at).toLocaleString()}</span>
                </div>
                {log.details && <p className="text-gray-600">{log.details}</p>}
                {log.ip_address && <p className="text-xs text-gray-400">IP: {log.ip_address}</p>}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
