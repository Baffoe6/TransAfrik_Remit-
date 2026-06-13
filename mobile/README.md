# TransAfrik Remit — Mobile App (Phase 11)

Production-ready **React Native** customer app built with **Expo** and **TypeScript**. Uses the same backend APIs as the web app.

**API:** `https://api.ipaygo.co.za`

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
├── api/           # Shared API client (Axios)
├── components/    # UI primitives
├── features/      # Domain modules (partners, etc.)
├── navigation/    # Auth + main navigators
├── screens/       # Customer screens
├── services/      # Device, biometrics, notifications, offline cache
├── store/         # Zustand (auth, theme)
└── types/         # Shared models
```

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
