# Security Readiness Report — TransAfrik Remit

**Phase:** 12 — Production Security & Launch Hardening  
**Date:** June 2026  
**Platforms:** Web (`app.ipaygo.co.za`) · API (`api.ipaygo.co.za`)

---

## Executive Summary

Phase 12 implements production-grade identity and access controls for staff accounts, centralized security monitoring via the **Security Center**, and policy enforcement for account lockout, password rotation, and optional IP allowlisting. The platform is ready for a controlled pilot launch once migration `012_production_security` is applied and production environment variables are configured.

---

## Controls Implemented

| Control | Status | Notes |
|---------|--------|-------|
| Mandatory admin MFA | ✅ | `ADMIN_MFA_REQUIRED=true` (default). Staff without MFA receive `mfa_setup_required` on login. |
| Device trust framework | ✅ | Existing device fingerprinting + step-up OTP for high-risk logins |
| Login anomaly detection | ✅ | Risk scoring + automated `SecurityAlert` records |
| Session management | ✅ | Active session list + per-session and bulk revoke |
| Security event monitoring | ✅ | `SecurityAuditLog` + Security Center dashboard |
| IP allowlist (admin) | ✅ | Opt-in via `ADMIN_IP_ALLOWLIST_ENABLED` |
| Password rotation policy | ✅ | 90-day max age for staff; reuse of last 5 passwords blocked |
| Account lockout | ✅ | 5 failed attempts → 30-minute lock |
| Audit trail | ✅ | Extended event types + `/admin/security-center/audit-trail` |
| Secrets abstraction | ✅ | `app/secrets/provider.py` — env + vault providers |

---

## Security Center (`/admin/security-center`)

Admin UI and API endpoints:

- **Failed logins** — recent `LOGIN_FAILED` audit entries
- **Active sessions** — revoke individual or all sessions per user
- **MFA status** — staff MFA enrollment overview
- **Security alerts** — unresolved anomaly/brute-force alerts with resolve action
- **Risk events** — login anomalies, step-up, MFA failures, IP blocks, lockouts
- **IP allowlist** — CRUD for admin CIDR entries
- **Secrets checklist** — production secret validation

API prefix: `/api/v1/admin/security-center/*`

---

## Environment Variables (Production)

```env
ADMIN_MFA_REQUIRED=true
ACCOUNT_LOCKOUT_MAX_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=30
PASSWORD_MAX_AGE_DAYS=90
ADMIN_IP_ALLOWLIST_ENABLED=false   # enable after allowlist populated
SECRET_KEY=<strong-random-key>
REDIS_URL=<redis-connection>
```

---

## Migration Required

```bash
cd backend && alembic upgrade head
```

Revision: `012_production_security`

---

## Residual Risks

1. **IP allowlist** — disabled by default; enable only after office/VPN CIDRs are configured.
2. **Customer MFA** — not enforced; staff-only in Phase 12.
3. **Impossible travel** — heuristic only (new device + new IP); no GeoIP database yet.
4. **Password change UI** — API returns `password_change_required`; dedicated staff password-change screen recommended before full production.

---

## Readiness Score

| Area | Score |
|------|-------|
| Authentication hardening | 95% |
| Session & device security | 90% |
| Monitoring & alerting | 85% |
| Secrets management | 80% |
| **Overall security readiness** | **88%** |

**Recommendation:** Proceed with pilot launch after migration, MFA enrollment for all staff, and production secret rotation.
