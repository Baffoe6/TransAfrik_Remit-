# Pilot Launch Checklist — TransAfrik Remit

Use this checklist before enabling real customer traffic on the pilot corridor.

---

## Infrastructure

- [ ] Railway API deployed with latest `main` (Phase 12)
- [ ] Vercel frontend deployed with `/admin/security-center`
- [ ] `alembic upgrade head` run on production DB (revision `012_production_security`)
- [ ] Redis connected (`REDIS_URL` set; health check green)
- [ ] PostgreSQL backups configured
- [ ] HTTPS enforced (`REQUIRE_HTTPS=true`)

---

## Security (Phase 12)

- [ ] `SECRET_KEY` rotated from default
- [ ] All admin/compliance/founder accounts have MFA enabled
- [ ] Security Center reviewed — no critical unresolved alerts
- [ ] Account lockout policy verified (5 attempts / 30 min)
- [ ] Staff password ages within 90-day policy
- [ ] IP allowlist populated (if `ADMIN_IP_ALLOWLIST_ENABLED=true`)
- [ ] OTP dev code exposure disabled (`OTP_DEV_EXPOSE_CODE=false`)
- [ ] API docs disabled in production (`DOCS_ENABLED=false`)

---

## Operations

- [ ] Health endpoint returns 200 (`/health`)
- [ ] Demo seed data disabled or isolated (`SEED_DEMO_DATA=false` in prod)
- [ ] Pilot mode configured (`PILOT_MODE_ENABLED` as intended)
- [ ] Mukuru / payment provider sandbox → production cutover plan documented
- [ ] Support team has runbook access (`/admin/runbook`)
- [ ] Launch readiness dashboard ≥ 80% (`/admin/launch-readiness`)

---

## Compliance & Legal

- [ ] KYC workflow tested end-to-end
- [ ] Sanctions screening active on transfers
- [ ] Terms of service and privacy policy published
- [ ] FICA / AML documentation current

---

## Mobile (Phase 11)

- [ ] Expo preview build tested on Android
- [ ] Mobile auth + send flow verified against production API
- [ ] EAS credentials configured for store submission (when ready)

---

## Go / No-Go

| Gate | Owner | Sign-off |
|------|-------|----------|
| Security Center green | Admin | |
| API health green | DevOps | |
| Compliance sign-off | Compliance Officer | |
| Founder approval | Founder | |

**Pilot launch approved:** _______________  **Date:** _______________
