# TransAfrik Remit Mobile — Release Notes v1.0 Preview

**Release:** v1.0.0-preview  
**Date:** June 2026  
**Platform:** Android & iOS (Expo SDK 52)  
**API:** https://api.ipaygo.co.za

---

## Overview

TransAfrik Remit Mobile v1.0 Preview is a premium fintech-grade remittance app designed for African migrant customers sending money from South Africa. This release transforms the Phase 11 MVP into a polished, mobile-first experience comparable to leading remittance apps — optimized for simplicity, trust, and speed.

---

## What's New

### Premium Design System
- Brand palette: Deep Green `#1B5E3B`, Gold `#C9A227`, Charcoal, White
- Typography scale, spacing tokens, elevated cards
- Loading skeletons, empty states, error states, offline banner
- Error boundary for graceful crash recovery

### Navigation
- **5-tab bottom navigation:** Home · Send · Beneficiaries · Activity · Profile
- Stack screens for send flow, KYC, receipts, support, security

### Onboarding
- 3-slide welcome flow (send money, pay at retail, track transfers)
- Skip option; shown once per device

### Authentication (Mobile-First)
- **Primary:** Mobile number + 4-digit PIN
- **Secondary:** Email + password
- OTP login via SMS / WhatsApp
- PIN reset via SMS OTP
- Biometric enable screen (Face ID / fingerprint)
- Secure token storage via Expo Secure Store

### Home Dashboard
- Personalized greeting
- KYC status card with completion %
- Quick Send CTA
- Exchange rate card
- Recent transfers
- Saved beneficiaries preview
- Referral and support cards
- Trust indicators: Secure transfer · Partner processed · Compliance checked

### Send Money Flow (5 Steps)
1. Select destination country (GH, ZW, ZM, KE, NG, UG)
2. Enter amount in ZAR with live quote
3. Select beneficiary
4. Choose payment method (Pay@, EasyPay, EFT, etc.)
5. Review and confirm

### Payment Reference Flow
- Generates payment reference via production API
- Displays voucher number, QR/barcode data
- Retail payment instructions
- Share voucher via system share sheet

### Transfer Tracking
- Live status timeline with 15-second polling
- Status badges and reference display
- Recipient and amount summary

### Activity & Receipts
- Full transfer history with status filters
- Search by reference number
- Professional branded receipt screen
- Share receipt placeholder

### Beneficiary Management
- Mobile money (MTN, Telecel, AirtelTigo), bank account, cash pickup
- Add, edit, delete beneficiaries
- Favorite beneficiaries (local storage)
- Search beneficiaries

### KYC Upload Flow
- Progress tracker (0%, 25%, 50%, 75%, 100%)
- Upload ID/passport, proof of address, selfie
- Camera capture + gallery picker (Expo Camera / Image Picker)
- Rejection reason display and resubmission

### Referrals
- Referral code display
- Share via WhatsApp and SMS
- Earnings and friends invited summary

### Support
- FAQ section
- Create support ticket (production API)
- View ticket status
- WhatsApp support button

### Profile & Security
- Personal details and KYC status
- Edit profile (address)
- Security settings
- Biometric configuration
- Sign out

### Offline Experience
- Cached dashboard, beneficiaries, and transfer history
- Offline banner when using cached data
- React Query retry on reconnect

---

## API Integration

| Module | Endpoints |
|--------|-----------|
| Auth | `/auth/login`, `/register`, `/login/otp`, `/password/forgot`, `/password/reset` |
| Dashboard | `/dashboard/summary` |
| Transfers | `/transfers`, `/calculate`, `/{id}`, `/{id}/timeline` |
| Payments | `/payments/methods`, `/payments/transfers/{id}/generate` |
| Beneficiaries | `/beneficiaries` CRUD |
| KYC | `/kyc/documents`, `/kyc/upload` |
| Referrals | `/referrals/dashboard` |
| Support | `/support/tickets` |

---

## Build & Deploy

### Local Development
```bash
cd mobile
npm install
npx expo start
```

### Android Preview APK
```bash
npm run eas:login
npm run build:android:preview
```

### Configuration
- `app.json` version: `1.0.0-preview`
- EAS project linked
- Expo Camera plugin enabled for KYC selfie capture
- Production API URL: `https://api.ipaygo.co.za`

---

## Known Limitations (Preview)

| Item | Status |
|------|--------|
| Push notification inbox | UI ready; backend token API pending |
| PDF receipt download | Placeholder button |
| Flutterwave card payment | Coming soon label in send flow |
| Biometric auto-unlock on launch | Enable screen only |
| Public corridors API | Static corridor list used |
| Device trust / active sessions | Placeholder screens |

---

## Tech Stack

- React Native 0.76 + Expo SDK 52
- TypeScript (strict)
- TanStack React Query
- Zustand
- Axios
- React Navigation
- Expo Secure Store, Camera, Image Picker, Local Authentication, Notifications

---

## Upgrade Path from Phase 11

- Legacy `screens/` replaced with `features/` module structure
- New design system in `theme/` and `components/`
- Added `payments`, `support`, `notifications` API clients
- Navigation expanded from 4 to 5 tabs (Activity added)
- Send flow replaced single-screen transfer with 5-step wizard

---

*Operated by IPAYGO (Pty) Ltd — TransAfrik Remit facilitation platform.*
