# TransAfrik Remit — Project Status (MVP v7.0.0)

**Release:** Production Remittance Facilitation MVP  
**Date:** June 2026  
**Domains:** [app.ipaygo.co.za](https://app.ipaygo.co.za) · [api.ipaygo.co.za](https://api.ipaygo.co.za)

---

## Executive Summary

TransAfrik Remit has been upgraded from a pilot/demo platform to a **production-ready remittance facilitation MVP**. The system supports customer onboarding (web + mobile), KYC, beneficiary management, transfer requests, admin operations, compliance review, and partner abstraction — with **mock partner integrations** (no live money movement).

---

## Completed Work by Phase

### Phase 1 — Cleanup & Production Hardening
- [x] Demo seed data gated behind `SEED_DEMO_DATA` (off in production)
- [x] System admin accounts migrated to `@transafrik.co.za` (+ operations@)
- [x] Swagger/docs disabled when `ENVIRONMENT=production` + `DOCS_ENABLED=false`
- [x] Dev endpoints hidden via `ENABLE_DEV_ENDPOINTS=false`
- [x] Production CORS for `app.ipaygo.co.za`
- [x] Demo UI links hidden in production frontend nav

### Phase 2 — Waitlist System
- [x] `waitlist_leads` table (migration 009)
- [x] `POST /api/v1/waitlist/join`
- [x] Admin: list, search, export CSV
- [x] Frontend: `/waitlist`, `/admin/waitlist`

### Phase 3 — Real Customer Dashboard
- [x] `GET /api/v1/dashboard/summary` — profile completion, KYC, beneficiaries, transfers, history, referrals
- [x] Frontend `/dashboard` wired to summary API (all 6 sections)
- [x] Beneficiary soft-delete (`DELETE /beneficiaries/{id}`)
- [x] Existing CRUD preserved

### Phase 4 — KYC Module
- [x] Document upload (ID/passport, POA, selfie)
- [x] Admin review with approve/reject + `review_notes`
- [x] Storage abstraction (local + S3)

### Phase 5 — Transfer Engine
- [x] Transfer lifecycle (existing 12 states mapped to MVP labels)
- [x] `POST/GET /transfers`, `GET /transfers/{id}`
- [x] MVP status mapper service

### Phase 6 — Corridors
- [x] 6 corridors seeded: ZA→GH/ZW/ZM/KE/NG/UG
- [x] Admin corridor management UI (`/admin/corridors`)

### Phase 7 — Partner Abstraction
- [x] `PartnerProvider` interface: `quote()`, `create_transfer()`, `get_status()`
- [x] Mock: Flutterwave, Mukuru, Onafriq, Veengu
- [x] Admin quote test endpoint

### Phase 8 — Compliance Dashboard
- [x] `GET /api/v1/admin/compliance/dashboard`
- [x] CSV export for high-risk transactions
- [x] Frontend `/admin/compliance` — metrics + KYC queue + transfer review

### Phase 9 — Operations Dashboard
- [x] `GET /api/v1/admin/operations/dashboard`
- [x] Metrics: customers, KYC queue, transfers, volumes, waitlist count
- [x] Frontend `/admin/operations` — MVP metrics + infrastructure health

### Phase 10 — Launch Readiness
- [x] `GET /api/v1/admin/launch-readiness`
- [x] Readiness percentage + checklist
- [x] Frontend: `/admin/launch-readiness`

---

## Architecture

| Layer | Pattern |
|-------|---------|
| Backend | FastAPI + SQLAlchemy + Alembic |
| Services | Business logic (`app/services/`) |
| Repositories | Data access (`app/repositories/`) |
| Providers | Partner abstraction (`app/providers/partners/`) |
| Frontend | Next.js App Router + TypeScript strict |
| Storage | Local / S3 abstraction |
| Cache | Redis (OTP, sessions, rate limits) |
| Mobile | React Native + Expo (Phase 11) |

---

## Migrations

Latest revision: **011_otp_device_trust**

```bash
cd backend && alembic upgrade head
```

### Phase 0 — Mobile-First Identity (v7.1)
- [x] `users.mobile_number` primary identifier (renamed from `phone`)
- [x] `users.email` nullable; `first_name`/`last_name`/`status` on users
- [x] Phone utilities: `normalize_phone_number`, `validate_phone_number`, `format_phone_number`
- [x] Login: mobile or email + password (`identifier` field)
- [x] Register: mobile required, email optional
- [x] Waitlist: mobile mandatory, email optional
- [x] Beneficiary mobile wallet E.164 validation
- [x] Admin customer search by mobile, email, name, ID
- [x] Dashboard mobile identity + verification status
- [x] SMS OTP verification (`POST /auth/otp/send`, `POST /auth/otp/verify-phone`)
- [x] WhatsApp OTP verification (channel=whatsapp)
- [x] Passwordless OTP login (`POST /auth/login/otp`)
- [x] Device trust + risk scoring (step-up on high-risk password login)
- [x] Password reset via OTP (`POST /auth/password/forgot`, `POST /auth/password/reset`)

### Phase 11 — Mobile Application (Expo)
- [x] React Native + Expo SDK 52 + TypeScript in `/mobile`
- [x] Shared API client (Axios) → `https://api.ipaygo.co.za`
- [x] Auth: register, login, OTP login, forgot/reset password
- [x] Dashboard, beneficiaries CRUD + search, transfers create/track/receipt
- [x] KYC upload (ID, passport, POA, selfie capture)
- [x] Referrals, wallet, profile, dark mode
- [x] Offline cache (dashboard), push notification stub, biometric service
- [x] Future-ready partner registry (Flutterwave, Mukuru, Onafriq, Veengu)
- [x] EAS build config (`eas.json`), deployment guide, env template
- [x] Jest test suite (`npm test` — 3 passed)
- [ ] EAS production builds (Android APK/AAB, iOS IPA) — run via `eas build`
- [ ] Push token registration with backend
- [ ] Biometric login wired to auth UI

---

## Production Accounts (seeded)

| Role | Email |
|------|-------|
| Admin | admin@transafrik.co.za |
| Founder | founder@transafrik.co.za |
| Compliance | compliance@transafrik.co.za |
| Operations | operations@transafrik.co.za |

Set `SEED_DEMO_DATA=false` and `ENVIRONMENT=production` on Railway.

---

## Remaining for Live Money Movement

- Live Flutterwave / Mukuru / Onafriq / Veengu API certification
- FIC licensing and legal sign-off
- Production S3 bucket configuration
- Email/SMS provider credentials for OTP
- End-to-end settlement reconciliation with partners

---

## Test Coverage

```bash
cd backend && pytest tests/ -v    # 72 passed
cd frontend && npm test           # 8 passed
cd mobile && npm test             # 3 passed
```

Key suites: `test_mvp.py`, `test_phase61_*.py`, `test_smoke.py`, `utils.test.ts`, `waitlist.test.ts`, `mobile/__tests__/*.test.ts`

---

*Operated by IPAYGO (Pty) Ltd — TransAfrik Remit facilitation platform.*
