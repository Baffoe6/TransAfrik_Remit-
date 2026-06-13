"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";

type Dashboard = {
  summary: {
    failed_logins_24h: number;
    active_sessions: number;
    staff_mfa_enabled: number;
    staff_total: number;
    unresolved_alerts: number;
    locked_accounts: number;
    admin_mfa_required: boolean;
    ip_allowlist_enabled: boolean;
    lockout_max_attempts: number;
    password_max_age_days: number;
  };
  secrets_checklist: { key: string; label: string; ok: boolean }[];
};

type FailedLogin = { id: number; user_id: number | null; ip_address: string | null; details: string | null; created_at: string };
type Session = { id: number; user_id: number; ip_address: string | null; user_agent: string | null; created_at: string; last_used_at: string | null; expires_at: string };
type MfaStaff = { user_id: number; email: string | null; role: string; mfa_enabled: boolean; mfa_enabled_at: string | null };
type Alert = { id: number; alert_type: string; severity: string; user_id: number | null; ip_address: string | null; title: string; details: string | null; is_resolved: boolean; created_at: string };
type RiskEvent = { id: number; user_id: number | null; event_type: string; ip_address: string | null; details: string | null; created_at: string };
type AllowlistEntry = { id: number; user_id: number | null; ip_cidr: string; label: string | null; is_active: boolean; created_at: string };

export default function SecurityCenterPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [failedLogins, setFailedLogins] = useState<FailedLogin[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [mfaStaff, setMfaStaff] = useState<MfaStaff[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [riskEvents, setRiskEvents] = useState<RiskEvent[]>([]);
  const [allowlist, setAllowlist] = useState<AllowlistEntry[]>([]);
  const [newIp, setNewIp] = useState("");
  const [newIpLabel, setNewIpLabel] = useState("");
  const [message, setMessage] = useState("");

  const load = useCallback(() => {
    api<Dashboard>("/admin/security-center/dashboard").then(setDashboard).catch(() => {});
    api<FailedLogin[]>("/admin/security-center/failed-logins").then(setFailedLogins).catch(() => {});
    api<Session[]>("/admin/security-center/sessions").then(setSessions).catch(() => {});
    api<{ staff: MfaStaff[] }>("/admin/security-center/mfa-status").then((r) => setMfaStaff(r.staff)).catch(() => {});
    api<Alert[]>("/admin/security-center/alerts?resolved=false").then(setAlerts).catch(() => {});
    api<RiskEvent[]>("/admin/security-center/risk-events").then(setRiskEvents).catch(() => {});
    api<AllowlistEntry[]>("/admin/security-center/ip-allowlist").then(setAllowlist).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);

  const revokeSession = async (sessionId: number) => {
    await api(`/admin/security-center/sessions/${sessionId}/revoke`, { method: "POST" });
    setMessage(`Session ${sessionId} revoked`);
    load();
  };

  const resolveAlert = async (alertId: number) => {
    await api(`/admin/security-center/alerts/${alertId}`, {
      method: "PATCH",
      body: JSON.stringify({ resolved: true }),
    });
    load();
  };

  const addAllowlist = async (e: React.FormEvent) => {
    e.preventDefault();
    await api("/admin/security-center/ip-allowlist", {
      method: "POST",
      body: JSON.stringify({ ip_cidr: newIp, label: newIpLabel || null }),
    });
    setNewIp("");
    setNewIpLabel("");
    setMessage("IP allowlist entry added");
    load();
  };

  const severityColor = (s: string) =>
    s === "critical" ? "text-red-700" : s === "high" ? "text-orange-600" : s === "medium" ? "text-amber-600" : "text-gray-600";

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-[#1B5E3B]">Security Center</h1>
        <p className="text-gray-500">Production security monitoring, sessions, MFA, and alerts</p>
      </div>

      {message && <p className="text-sm text-green-700">{message}</p>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-gray-500">Failed Logins (24h)</CardTitle></CardHeader>
          <CardContent><p className="text-3xl font-bold text-red-600">{dashboard?.summary.failed_logins_24h ?? "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-gray-500">Active Sessions</CardTitle></CardHeader>
          <CardContent><p className="text-3xl font-bold text-[#1B5E3B]">{dashboard?.summary.active_sessions ?? "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-gray-500">Staff MFA</CardTitle></CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{dashboard ? `${dashboard.summary.staff_mfa_enabled}/${dashboard.summary.staff_total}` : "—"}</p>
            {dashboard?.summary.admin_mfa_required && <p className="text-xs text-amber-600 mt-1">MFA enforced</p>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-gray-500">Open Alerts</CardTitle></CardHeader>
          <CardContent><p className="text-3xl font-bold text-orange-600">{dashboard?.summary.unresolved_alerts ?? "—"}</p></CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Failed Logins</CardTitle></CardHeader>
          <CardContent>
            {failedLogins.length === 0 ? (
              <p className="text-sm text-gray-500">No recent failed logins.</p>
            ) : (
              <ul className="max-h-64 space-y-2 overflow-y-auto text-sm">
                {failedLogins.map((f) => (
                  <li key={f.id} className="rounded border p-2">
                    <div className="flex justify-between">
                      <span>{f.details || "Failed login"}</span>
                      <span className="text-gray-400">{f.ip_address || "—"}</span>
                    </div>
                    <span className="text-xs text-gray-400">{new Date(f.created_at).toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Active Sessions</CardTitle></CardHeader>
          <CardContent>
            {sessions.length === 0 ? (
              <p className="text-sm text-gray-500">No active sessions.</p>
            ) : (
              <ul className="max-h-64 space-y-2 overflow-y-auto text-sm">
                {sessions.map((s) => (
                  <li key={s.id} className="flex items-center justify-between rounded border p-2">
                    <div>
                      <p>User #{s.user_id} · {s.ip_address || "unknown IP"}</p>
                      <p className="text-xs text-gray-400">{new Date(s.created_at).toLocaleString()}</p>
                    </div>
                    <Button size="sm" variant="outline" onClick={() => revokeSession(s.id)}>Revoke</Button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>MFA Status (Staff)</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {mfaStaff.map((s) => (
                <li key={s.user_id} className="flex justify-between rounded border p-2">
                  <span>{s.email || `User #${s.user_id}`} · {s.role}</span>
                  <span className={s.mfa_enabled ? "text-green-600" : "text-red-600"}>
                    {s.mfa_enabled ? "Enabled" : "Not enabled"}
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Security Alerts</CardTitle></CardHeader>
          <CardContent>
            {alerts.length === 0 ? (
              <p className="text-sm text-gray-500">No open alerts.</p>
            ) : (
              <ul className="max-h-64 space-y-2 overflow-y-auto text-sm">
                {alerts.map((a) => (
                  <li key={a.id} className="rounded border p-2">
                    <div className="flex justify-between">
                      <span className="font-medium">{a.title}</span>
                      <span className={severityColor(a.severity)}>{a.severity}</span>
                    </div>
                    <p className="text-xs text-gray-500">{a.details}</p>
                    <Button size="sm" variant="ghost" className="mt-1" onClick={() => resolveAlert(a.id)}>Resolve</Button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Risk Events</CardTitle></CardHeader>
          <CardContent>
            {riskEvents.length === 0 ? (
              <p className="text-sm text-gray-500">No risk events recorded.</p>
            ) : (
              <ul className="max-h-48 space-y-2 overflow-y-auto text-sm">
                {riskEvents.map((r) => (
                  <li key={r.id} className="flex justify-between rounded border p-2">
                    <span>{r.event_type.replace(/_/g, " ")} · User #{r.user_id ?? "—"}</span>
                    <span className="text-gray-400">{new Date(r.created_at).toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Admin IP Allowlist</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-gray-600">
            {dashboard?.summary.ip_allowlist_enabled
              ? "IP allowlist enforcement is ON — only listed IPs can access admin accounts."
              : "IP allowlist enforcement is OFF — enable ADMIN_IP_ALLOWLIST_ENABLED in production when ready."}
          </p>
          <form onSubmit={addAllowlist} className="flex flex-wrap gap-3">
            <div className="space-y-1">
              <Label>IP / CIDR</Label>
              <Input value={newIp} onChange={(e) => setNewIp(e.target.value)} placeholder="203.0.113.0/24" required />
            </div>
            <div className="space-y-1">
              <Label>Label</Label>
              <Input value={newIpLabel} onChange={(e) => setNewIpLabel(e.target.value)} placeholder="Office VPN" />
            </div>
            <Button type="submit" className="self-end">Add</Button>
          </form>
          <ul className="space-y-1 text-sm">
            {allowlist.filter((e) => e.is_active).map((e) => (
              <li key={e.id} className="rounded border px-3 py-2">{e.ip_cidr} {e.label && `· ${e.label}`}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {dashboard?.secrets_checklist && (
        <Card>
          <CardHeader><CardTitle>Secrets Readiness</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {dashboard.secrets_checklist.map((c) => (
                <li key={c.key} className="flex justify-between">
                  <span>{c.label}</span>
                  <span className={c.ok ? "text-green-600" : "text-red-600"}>{c.ok ? "OK" : "Missing"}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Security Policies</CardTitle></CardHeader>
        <CardContent className="grid gap-2 text-sm sm:grid-cols-3">
          <p>Lockout: {dashboard?.summary.lockout_max_attempts ?? 5} attempts</p>
          <p>Password rotation: {dashboard?.summary.password_max_age_days ?? 90} days</p>
          <p>Locked accounts: {dashboard?.summary.locked_accounts ?? 0}</p>
        </CardContent>
      </Card>
    </div>
  );
}
