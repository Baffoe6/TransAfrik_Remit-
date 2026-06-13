# TransAfrik Mobile — Deployment Guide

## Prerequisites

- Node.js 20+
- Expo account ([expo.dev](https://expo.dev))
- EAS CLI: `npm install -g eas-cli`
- Apple Developer account (iOS)
- Google Play Console account (Android)

## 1. Configure EAS

```bash
cd mobile
eas login
eas init
```

Update `eas.json` with your Apple ID and ASC App ID for iOS submission.

## 2. Environment Variables

Set in Expo dashboard (Project → Secrets) or `eas.json` build profiles:

```
EXPO_PUBLIC_API_URL=https://api.ipaygo.co.za
EXPO_PUBLIC_APP_ENV=production
```

For staging:
```
EXPO_PUBLIC_API_URL=https://api-staging.ipaygo.co.za
```

## 3. Android Build

### Internal testing (APK)
```bash
eas build --platform android --profile preview
```

### Production (AAB for Play Store)
```bash
eas build --platform android --profile production
eas submit --platform android --profile production
```

**Package name:** `co.za.ipaygo.transafrik`

## 4. iOS Build

### Simulator
```bash
eas build --platform ios --profile preview
```

### App Store
```bash
eas build --platform ios --profile production
eas submit --platform ios --profile production
```

**Bundle ID:** `co.za.ipaygo.transafrik`

## 5. Push Notifications

1. Configure Expo push credentials in EAS
2. Register device token server-side (future endpoint)
3. `notificationService.registerForPush()` runs on app launch (extend in `App.tsx`)

## 6. OTA Updates (optional)

```bash
eas update --branch production --message "Bug fix"
```

## 7. Local Native Builds

```bash
npx expo prebuild
npx expo run:android
npx expo run:ios
```

## 8. CI/CD Example (GitHub Actions)

```yaml
- run: cd mobile && npm ci && npm test
- run: cd mobile && eas build --platform all --profile production --non-interactive
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| API 401 errors | Check `EXPO_PUBLIC_API_URL` includes no `/api/v1` suffix |
| KYC upload fails | Ensure camera/photo permissions in `app.json` |
| OTP not received | Configure `SMS_PROVIDER` on Railway backend |
| Biometric unavailable | Device must have Face ID / fingerprint enrolled |

## Partner Integrations (Future)

Backend mock providers ready: Flutterwave, Mukuru, Onafriq, Veengu. Mobile `features/partners.ts` lists providers for future native SDK integration.
