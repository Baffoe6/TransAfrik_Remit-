# TransAfrik Remit — Mobile Status (v2.0 Production Candidate)

**Release:** TransAfrik Remit Mobile v2.0.0  
**Date:** June 2026  
**API:** [api.ipaygo.co.za](https://api.ipaygo.co.za)

---

## Executive Summary

**Production-ready customer app** — real registration, OTP verification, KYC, beneficiaries, transfers, Flutterwave payment readiness, and retail vouchers. No demo customer assumptions.

See [REAL_USE_READINESS.md](REAL_USE_READINESS.md) · [FLUTTERWAVE_MOBILE_INTEGRATION.md](FLUTTERWAVE_MOBILE_INTEGRATION.md)

---

## Architecture (Phase 16)

```
mobile/src/
├── theme/              Design tokens (green, gold, charcoal)
├── components/
│   ├── fintech/        Design system v2 components
│   └── worldclass/     Phase 16 calculators, widgets, glass cards
├── features/           auth, dashboard, transfers, beneficiaries, kyc, activity, profile, support, notifications
├── navigation/         5-tab + stack navigators (React Navigation)
├── api/                auth, transfers, payments, support, kyc, dashboard, notifications
├── store/              auth, calculator, templates, rate alerts, notification inbox, send flow
├── hooks/              useLiveQuote, useDebounce
├── services/           haptics, secure storage, biometrics, offline cache
└── utils/              currency, phone, validation, constants (6 corridors)
```

---

## Feature Matrix (Phase 16)

### Home
- [x] Live exchange rate card (replaces balance)
- [x] Real-time send calculator
- [x] Active transfer widget + progress
- [x] Favorite recipients carousel
- [x] Rate alert widget
- [x] Referral / promo card
- [x] 6-corridor selector (ZA→GH, ZW, ZM, KE, NG, UG)

### Send
- [x] Wise-style live calculator with debounced quotes
- [x] Payout partner badges
- [x] Transfer summary + save as template
- [x] Recent templates on Send tab

### Beneficiaries
- [x] Category filters (mobile money, bank, cash pickup)
- [x] Network logos, favorites, quick send
- [x] Verification status pills

### Activity & Receipts
- [x] Timeline view + progress bars
- [x] Time filters (today/week/month) + status filters incl. refunded
- [x] QR receipt, WhatsApp/email share, export

### KYC & Profile
- [x] OCR scan placeholder, selfie, workflow states, document preview
- [x] Tier badge, transfer limits, compliance status
- [x] Security center (devices, sessions, MFA, biometrics, PIN)

### Support & Notifications
- [x] WhatsApp, FAQ, tickets, live chat placeholder
- [x] Notification inbox with typed alerts

---

## Verification Results

| Check | Result | Notes |
|-------|--------|-------|
| `npm test` | **Pass** | Unit + store + navigation tests |
| `npm run lint` | **Pass** | TypeScript strict |
| `npx expo export --platform android` | **Pass** | JS bundle |
| API health | **200** | Production API |
| GitHub `origin/main` | **Pass** | Commit `a32874e` pushed |
| Vercel web app | **Live** | [app.ipaygo.co.za](https://app.ipaygo.co.za) |

---

## EAS Android Preview Build (v2.0)

| Field | Value |
|-------|-------|
| **Status** | **FINISHED** |
| **Profile** | `preview` |
| **App version** | `2.0.0` |
| **Build number** | `1` |
| **Git commit** | `d7d699e` — production-ready remittance app |
| **Build ID** | `38d52673-14f6-4dc8-8a01-fc4be597f9c1` |
| **APK download** | [Direct APK](https://expo.dev/artifacts/eas/bkAGtGP7kf7w1NAkOm3OTZ5Ny3VupMCAyNrPL12_fNM.apk) |
| **QR install** | [EAS build page](https://expo.dev/accounts/baffoe6/projects/transafrik-remit/builds/38d52673-14f6-4dc8-8a01-fc4be597f9c1) |

**QA:** [MOBILE_QA_TEST_PLAN.md](MOBILE_QA_TEST_PLAN.md) · [PILOT_CUSTOMER_TEST_GUIDE.md](PILOT_CUSTOMER_TEST_GUIDE.md)

---

## Dependencies Added (Phase 16)

- `expo-haptics` — tactile feedback
- `react-native-reanimated` — animation plugin
- `react-native-qrcode-svg` + `react-native-svg` — receipt QR codes

---

## Remaining Before Store Launch

1. ~~EAS preview build~~ ✅ (see above)
2. EAS production builds (Play Store AAB)
3. Backend multi-corridor pricing parity
4. True PDF receipt generation
5. OCR backend pipeline
6. Push token registration with backend
7. Physical device QA (use ANDROID_PREVIEW_TEST_PLAN.md)

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
