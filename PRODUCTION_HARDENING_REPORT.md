# Production Hardening Report — Phase 12

**Project:** TransAfrik Remit  
**Operator:** IPAYGO (Pty) Ltd  
**Report date:** June 2026

---

## 1. Scope

Phase 12 adds defense-in-depth controls for staff authentication, session lifecycle, anomaly detection, and operational security visibility ahead of pilot launch.

---

## 2. Backend Changes

### Database (Migration `012_production_security`)

**Users table extensions:**
- `failed_login_attempts` — lockout counter
- `locked_until` — temporary lock expiry
- `password_changed_at` — rotation tracking
- `must_change_password` — forced reset flag

**New tables:**
- `admin_ip_allowlist` — per-user or global CIDR rules
- `security_alerts` — operational security alerts
- `password_history` — last 5 password hashes (reuse prevention)

### Services

| Module | Purpose |
|--------|---------|
| `account_security_service.py` | Lockout, password expiry, history |
| `anomaly_detection_service.py` | Login risk alerts, failed login queries |
| `ip_allowlist_service.py` | Admin IP enforcement |
| `secrets/provider.py` | Unified secrets access (env / vault) |

### Auth Router Updates

- Account lock check before login (HTTP 423)
- Failed login increments counter; auto-lock at threshold
- Admin IP allowlist enforcement (when enabled)
- Mandatory MFA for staff (`mfa_setup_required` / `mfa_required` responses)
- Login anomaly analysis on every successful auth
- Password reuse check on reset
- `TOKEN_REFRESH` audit events

### New API Router

`security_center_admin.py` — `/api/v1/admin/security-center/`

Endpoints: `dashboard`, `failed-logins`, `sessions`, `sessions/{id}/revoke`, `mfa-status`, `alerts`, `risk-events`, `audit-trail`, `ip-allowlist`

---

## 3. Frontend Changes

- **New page:** `/admin/security-center` — unified security operations dashboard
- **Redirect:** `/admin/security` → `/admin/security-center`
- **Navigation:** Security link added to admin header

---

## 4. Configuration Defaults

| Setting | Default | Production recommendation |
|---------|---------|---------------------------|
| `ADMIN_MFA_REQUIRED` | `true` | Keep enabled |
| `ACCOUNT_LOCKOUT_MAX_ATTEMPTS` | `5` | Keep or tighten to 3 |
| `ACCOUNT_LOCKOUT_MINUTES` | `30` | 30–60 |
| `PASSWORD_MAX_AGE_DAYS` | `90` | 90 |
| `ADMIN_IP_ALLOWLIST_ENABLED` | `false` | Enable after CIDRs configured |

---

## 5. Testing

New test suite: `backend/tests/test_phase12_security.py`

Covers: staff role detection, lockout, password expiry, IP allowlist, secrets provider, security center auth gate.

Run:

```bash
cd backend && pytest tests/test_phase12_security.py -v
```

---

## 6. Deployment Steps

1. Merge Phase 12 to `main`
2. Deploy API (Railway) and frontend (Vercel)
3. Run migration: `alembic upgrade head`
4. Set production env vars (see `SECURITY_READINESS_REPORT.md`)
5. Enroll all staff in MFA via Security Center
6. Review Security Center dashboard before pilot traffic

---

## 7. Files Added / Modified

**New:**
- `backend/alembic/versions/012_production_security.py`
- `backend/app/models/security_hardening.py`
- `backend/app/services/account_security_service.py`
- `backend/app/services/anomaly_detection_service.py`
- `backend/app/services/ip_allowlist_service.py`
- `backend/app/secrets/provider.py`
- `backend/app/routers/security_center_admin.py`
- `backend/tests/test_phase12_security.py`
- `frontend/src/app/admin/security-center/page.tsx`
- `SECURITY_READINESS_REPORT.md`
- `PILOT_LAUNCH_CHECKLIST.md`
- `PRODUCTION_HARDENING_REPORT.md`

**Modified:**
- `backend/app/config.py`
- `backend/app/models/user.py`, `enums.py`, `__init__.py`
- `backend/app/services/security_service.py`
- `backend/app/routers/auth.py`
- `backend/app/schemas/auth.py`
- `backend/app/main.py`
- `frontend/src/components/layout/header.tsx`
- `frontend/src/app/admin/security/page.tsx` (redirect)

---

## 8. Sign-Off

Phase 12 production hardening is **complete pending deployment and migration**. No breaking changes to customer auth flows; staff accounts receive additional enforcement on next login.
