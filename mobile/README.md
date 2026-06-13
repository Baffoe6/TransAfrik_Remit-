# TransAfrik Remit — Mobile App (v1.0 Preview)

Premium **React Native** fintech app built with **Expo SDK 52** and **TypeScript**. Connects to production API at `https://api.ipaygo.co.za`.

## Brand

Deep Green `#1B5E3B` · Gold `#C9A227` · Charcoal · White

## Stack

| Layer | Technology |
|-------|------------|
| Framework | React Native + Expo SDK 52 |
| Language | TypeScript (strict) |
| Data fetching | TanStack React Query |
| HTTP | Axios |
| State | Zustand |
| Secure storage | Expo Secure Store |
| Navigation | React Navigation (tabs + stack) |

## Architecture

```
mobile/src/
├── theme/           Design system (colors, typography, spacing)
├── components/      Premium UI kit
├── features/        auth, dashboard, transfers, beneficiaries, kyc, activity, profile, support
├── navigation/      5-tab bottom nav + stack
├── api/             Axios client + domain APIs (incl. payments, support)
├── store/           Zustand (auth, onboarding, send flow, settings)
├── services/        Secure Store, biometrics, offline cache
└── utils/           Currency, phone, validation
```

## Tabs

Home · Send · Beneficiaries · Activity · Profile

## Features

### Authentication
- Mobile number registration (required) + optional email
- Login with mobile or email + password
- Passwordless OTP login (SMS / WhatsApp)
- Password reset via SMS OTP
- Device trust + step-up verification (high-risk logins)
- Future: biometric / Face ID (`services/biometric.ts`)

### Customer
- Dashboard (profile %, KYC, wallet, transfers, referrals)
- Beneficiaries CRUD + search
- Transfers create / track / receipt
- KYC document upload + selfie capture
- Referral code + invite friends
- Dark mode support
- Offline cache for dashboard data

## Quick Start

```bash
cd mobile
cp .env.example .env
npm install
npx expo start
```

Scan the QR code with **Expo Go** (Android/iOS) or press `a` / `i` for emulator.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EXPO_PUBLIC_API_URL` | `https://api.ipaygo.co.za` | Backend API base URL |

## Builds

### Android — Internal testing (APK)
```bash
npm run eas:login    # one-time
npm run eas:init     # one-time — links project to Expo
npm run build:android:preview
```

See **[docs/ANDROID_PREVIEW_BUILD.md](docs/ANDROID_PREVIEW_BUILD.md)** for full internal testing guide.

### Android — Production (AAB for Play Store)
```bash
npm run build:android
# or: eas build --platform android --profile production
```

### iOS
```bash
npm run build:ios
# or: eas build --platform ios --profile production
```

See [docs/EAS_BUILD.md](docs/EAS_BUILD.md) and [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for full EAS setup.

## Testing

```bash
npm test
npm run lint
```

## Demo Account (local seed)

| Mobile | Password |
|--------|----------|
| +27821234567 | Customer@TransAfrik2024! |

> TransAfrik is operated by IPAYGO (Pty) Ltd — not a licensed bank or remittance operator.
