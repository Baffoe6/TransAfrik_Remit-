# TransAfrik Remit — Mobile Status (Phase 16)

**Release:** TransAfrik Remit Mobile v1.0 Phase 16  
**Date:** June 2026  
**API:** [api.ipaygo.co.za](https://api.ipaygo.co.za)

---

## Executive Summary

**World-class fintech remittance** React Native app (Expo SDK 52 + TypeScript) comparable to Wise, Revolut, and Remitly. Live exchange-rate calculator, six African corridors, transfer templates, QR receipts, security center, notification inbox, and premium design system v2.

See [PHASE16_WORLD_CLASS_UPGRADE.md](PHASE16_WORLD_CLASS_UPGRADE.md) for full feature breakdown.

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

## EAS Android Preview Build (Phase 16)

| Field | Value |
|-------|-------|
| **Status** | **FINISHED** |
| **Profile** | `preview` |
| **Platform** | Android APK |
| **App version** | `1.0.0-preview` |
| **Build number** | `1` |
| **Git commit** | `a32874e` — feat(mobile): world-class fintech remittance experience upgrade |
| **Build ID** | `f1697bb3-a1b4-4161-81e9-e575cbabd2ae` |
| **Completed** | 2026-06-15 22:35 UTC |
| **APK download** | [Direct APK](https://expo.dev/artifacts/eas/e1UC1L7cZ6_s7kKDut9p8xQlYbd8DifPTQwa7TTD23Q.apk) |
| **Install page (QR)** | [EAS build page](https://expo.dev/accounts/baffoe6/projects/transafrik-remit/builds/f1697bb3-a1b4-4161-81e9-e575cbabd2ae) |
| **API target** | `https://api.ipaygo.co.za` |
| **Channel** | `preview` |

**Install:** Open the EAS build page on an Android device and scan the QR code, or download the APK directly.

**QA checklist:** [ANDROID_PREVIEW_TEST_PLAN.md](ANDROID_PREVIEW_TEST_PLAN.md)

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
