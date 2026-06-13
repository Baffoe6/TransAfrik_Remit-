# TransAfrik Remit — Mobile Status (Phase 11)

**Release:** TransAfrik Remit Mobile v1.0 Preview  
**Date:** June 2026  
**API:** [api.ipaygo.co.za](https://api.ipaygo.co.za)

---

## Executive Summary

Premium **fintech-grade** React Native app (Expo SDK 52 + TypeScript) for African migrant customers. Full design system, 5-step send flow, payment vouchers, KYC tracker, activity/receipts, support, and production API integration.

---

## Architecture (v1.0 Preview)

```
mobile/src/
├── theme/          Design tokens (green, gold, charcoal)
├── components/     Premium UI kit
├── features/       auth, dashboard, transfers, beneficiaries, kyc, activity, profile, support, referrals, notifications
├── navigation/     5-tab + stack navigators
├── api/            auth, transfers, payments, support, kyc, dashboard
├── store/          auth, onboarding, settings, send flow
├── services/       secure storage, biometrics, offline cache
└── utils/          currency, phone, validation, constants
```

---

## Feature Matrix

### Authentication
- [x] Mobile + 4-digit PIN login (primary)
- [x] Email + password login (secondary)
- [x] OTP login (SMS / WhatsApp)
- [x] Password/PIN reset via OTP
- [x] Onboarding flow (3 slides)
- [x] Biometric enable screen
- [ ] Biometric auto-unlock on launch (placeholder)

### Customer
- [x] Premium home dashboard with trust indicators
- [x] 5-step send flow with payment voucher generation
- [x] Transfer tracking with live polling (15s)
- [x] Professional receipt screen
- [x] Activity tab with filter/search
- [x] Beneficiaries with favorites + search
- [x] KYC progress tracker (0–100%) + camera/gallery upload
- [x] Referrals with WhatsApp/SMS share
- [x] Support FAQ + tickets + WhatsApp button
- [x] Notifications center (push placeholder)
- [x] Profile + security settings
- [x] Offline cache (dashboard, beneficiaries, transfers)

### Notifications
- [x] Push notification service stub
- [ ] Server-side push token registration
- [ ] SMS / WhatsApp notification delivery (backend future)

### Future-Ready
- [x] Partner registry: Flutterwave, Mukuru, Onafriq, Veengu
- [x] Biometric service (`expo-local-authentication`)
- [x] Device fingerprinting for trust scoring

---

## Verification Results

| Check | Result | Notes |
|-------|--------|-------|
| `npm test` | **Pass** | 3/3 tests |
| `npm run lint` | **Pass** | TypeScript strict |
| API health `GET /health` | **200** | DB + Redis healthy |
| Auth login `POST /auth/login` | **401** | Invalid credentials rejected (endpoint live) |
| API base URL in client | **OK** | Defaults to `https://api.ipaygo.co.za` |
| `npx expo start` | **Pass** | After `expo-asset` dependency added |

---

## Architecture

See [mobile/docs/ARCHITECTURE.md](mobile/docs/ARCHITECTURE.md) for the full diagram.

```
App.tsx
  ├── AuthNavigator (unauthenticated)
  │     Login, Register, OTP Login, Forgot Password
  └── MainNavigator (authenticated)
        ├── Tabs: Dashboard, Transfers, Beneficiaries, Profile
        └── Stack: KYC, Wallet, Referral, Transfer Detail, Beneficiary Form
```

**Data flow:** Screens → React Query / Zustand → Axios `apiClient` → `https://api.ipaygo.co.za/api/v1`

---

## Build & Deploy Readiness

| Item | Status |
|------|--------|
| EAS config (`eas.json`) | Ready |
| Android package `co.za.ipaygo.transafrik` | Configured |
| iOS bundle `co.za.ipaygo.transafrik` | Configured |
| Production env `EXPO_PUBLIC_API_URL` | Set in EAS production profile |
| EAS production build executed | **Pending** — run `eas build` |
| App Store / Play Store submission | **Pending** — credentials required |
| Push notification credentials | **Pending** — configure in Expo dashboard |

See [mobile/docs/EAS_BUILD.md](mobile/docs/EAS_BUILD.md) for step-by-step build instructions.

---

## Remaining Before Store Launch

1. Run EAS production builds (`eas build --platform all --profile production`)
2. Configure Apple Developer + Google Play service accounts
3. Wire biometric login to auth screens
4. Register push tokens with backend
5. Configure live SMS provider on Railway for OTP delivery
6. End-to-end QA on physical devices (Android + iOS)

---

## Quick Start

```bash
cd mobile
cp .env.example .env
npm install
npx expo start
```

---

*Operated by IPAYGO (Pty) Ltd — TransAfrik Remit mobile customer application.*
