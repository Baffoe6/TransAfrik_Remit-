# TransAfrik Mobile — Expo EAS Build Instructions

Step-by-step guide to build and distribute the TransAfrik Remit mobile app via **Expo Application Services (EAS)**.

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Node.js | 20+ |
| Expo account | [expo.dev/signup](https://expo.dev/signup) |
| EAS CLI | `npm install -g eas-cli` |
| Apple Developer | Required for iOS App Store ($99/year) |
| Google Play Console | Required for Android Play Store ($25 one-time) |

---

## 1. Initial Setup

```bash
cd mobile
npm install
eas login
eas init
```

`eas init` links the project to your Expo account and sets `EAS_PROJECT_ID` in `app.json`.

---

## 2. Environment Variables

### Local development

```bash
cp .env.example .env
```

```env
EXPO_PUBLIC_API_URL=https://api.ipaygo.co.za
EXPO_PUBLIC_APP_ENV=development
```

### EAS builds

Production URL is already set in `eas.json`:

```json
"production": {
  "env": {
    "EXPO_PUBLIC_API_URL": "https://api.ipaygo.co.za"
  }
}
```

For secrets (future API keys), use Expo dashboard → **Project → Secrets** or:

```bash
eas secret:create --name EXPO_PUBLIC_API_URL --value https://api.ipaygo.co.za --scope project
```

> **Important:** Do not include `/api/v1` in `EXPO_PUBLIC_API_URL`. The Axios client appends it automatically.

---

## 3. Build Profiles

Defined in `eas.json`:

| Profile | Purpose | Output |
|---------|---------|--------|
| `development` | Dev client with hot reload | Internal |
| `preview` | QA / internal testing | Android APK, iOS Simulator |
| `preview-apk` | Same as preview (APK alias) | Android APK |
| `production` | Store release | Android AAB, iOS IPA |

---

## 4. Android Builds

> **Internal testing APK:** See [ANDROID_PREVIEW_BUILD.md](./ANDROID_PREVIEW_BUILD.md) for the complete step-by-step guide.

### Internal testing (APK — share via link)

```bash
npm run build:android:preview
# or: eas build --platform android --profile preview
```

Download the APK from the Expo dashboard link and install on test devices.

### Production (AAB for Google Play)

```bash
eas build --platform android --profile production
```

**Package name:** `co.za.ipaygo.transafrik`

### Submit to Google Play

1. Create a service account in Google Cloud Console
2. Download JSON key → save as `mobile/google-service-account.json` (gitignored)
3. Update `eas.json` submit profile if path differs
4. Run:

```bash
eas submit --platform android --profile production
```

---

## 5. iOS Builds

### Simulator build (no Apple device needed)

```bash
eas build --platform ios --profile preview
```

### Production (App Store)

```bash
eas build --platform ios --profile production
```

**Bundle ID:** `co.za.ipaygo.transafrik`

### Submit to App Store

Update `eas.json` submit section:

```json
"ios": {
  "appleId": "your-apple-id@example.com",
  "ascAppId": "YOUR_ASC_APP_ID"
}
```

Then:

```bash
eas submit --platform ios --profile production
```

---

## 6. Build Both Platforms

```bash
eas build --platform all --profile production
```

Non-interactive (CI):

```bash
eas build --platform all --profile production --non-interactive
```

---

## 7. OTA Updates (Optional)

Push JavaScript-only updates without a full store rebuild:

```bash
eas update --branch production --message "Fix transfer receipt display"
```

Configure `runtimeVersion` in `app.json` before using OTA in production.

---

## 8. Local Native Builds

For debugging native modules without EAS cloud:

```bash
npx expo prebuild
npx expo run:android    # requires Android Studio
npx expo run:ios        # requires Xcode (macOS only)
```

---

## 9. CI/CD (GitHub Actions)

```yaml
name: Mobile CI

on:
  push:
    paths: ['mobile/**']
  pull_request:
    paths: ['mobile/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: mobile/package-lock.json
      - run: cd mobile && npm ci && npm test && npm run lint

  build:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm install -g eas-cli
      - run: cd mobile && npm ci
      - run: cd mobile && eas build --platform all --profile production --non-interactive
        env:
          EXPO_TOKEN: ${{ secrets.EXPO_TOKEN }}
```

Generate `EXPO_TOKEN` at [expo.dev/settings/access-tokens](https://expo.dev/settings/access-tokens).

---

## 10. Pre-Build Checklist

- [ ] `npm test` passes
- [ ] `npm run lint` passes
- [ ] `mobile/assets/icon.png` and `adaptive-icon.png` present
- [ ] `EXPO_PUBLIC_API_URL` points to production API
- [ ] Backend migration `011_otp_device_trust` applied on Railway
- [ ] `SMS_PROVIDER` configured on backend for OTP delivery
- [ ] Camera/photo permissions verified in `app.json`
- [ ] App tested on physical Android + iOS device via Expo Go or preview APK

---

## 11. Troubleshooting

| Issue | Solution |
|-------|----------|
| `expo-asset` not found | Run `npx expo install expo-asset` |
| API returns 401 | Check token storage; verify `EXPO_PUBLIC_API_URL` has no `/api/v1` suffix |
| Build fails on credentials | Run `eas credentials` to configure signing |
| KYC camera blank | Grant camera permission; test on physical device |
| OTP not received | Set `SMS_PROVIDER=africas_talking` or `twilio` on Railway |
| iOS build requires Mac | Use EAS cloud build — no Mac needed for `eas build` |

---

## App Identifiers

| Platform | Identifier |
|----------|------------|
| Android package | `co.za.ipaygo.transafrik` |
| iOS bundle ID | `co.za.ipaygo.transafrik` |
| Expo slug | `transafrik-remit` |
| App name | TransAfrik Remit |

---

*See also: [DEPLOYMENT.md](./DEPLOYMENT.md) · [ARCHITECTURE.md](./ARCHITECTURE.md) · [MOBILE_STATUS.md](../../MOBILE_STATUS.md)*
