# Android Preview APK — Internal Testing Guide

Build a shareable **Android APK** for internal QA using **Expo EAS** (`preview` profile).

**Output:** Signed APK installable on any Android device (no Play Store required).

---

## Prerequisites

| Item | Command / link |
|------|----------------|
| Node.js 20+ | `node -v` |
| Expo account | [expo.dev/signup](https://expo.dev/signup) |
| EAS CLI | Included in project — use `npm run eas:login` (or `npx eas`) |
| Git repo | Project at `mobile/` |

---

## Step 1 — One-time EAS setup

```bash
cd mobile
npm install
npm run eas:login
npm run eas:init
```

> **Windows note:** If your prompt is already `...\mobile>`, do **not** run `cd mobile` again.
> **EAS CLI:** Installed locally — always use `npm run eas:login` or `npx eas`, not bare `eas`.

`eas init` will:
- Link the project to your Expo account
- Add `extra.eas.projectId` to `app.json`
- Create the project on [expo.dev](https://expo.dev)

When prompted:
- **Platform:** Android (and iOS if you plan iOS later)
- **Slug:** `transafrik-remit` (already set in `app.json`)

---

## Step 2 — Verify configuration

### `eas.json` — preview profile (APK)

```json
"preview": {
  "distribution": "internal",
  "channel": "preview",
  "env": {
    "EXPO_PUBLIC_API_URL": "https://api.ipaygo.co.za",
    "EXPO_PUBLIC_APP_ENV": "preview"
  },
  "android": {
    "buildType": "apk"
  }
}
```

| Setting | Value |
|---------|-------|
| Build type | `apk` (not AAB) |
| Distribution | `internal` (share via Expo dashboard link) |
| Package | `co.za.ipaygo.transafrik` |
| API URL | `https://api.ipaygo.co.za` |

### Pre-build checks

```bash
npm test
npm run lint
```

Ensure `mobile/assets/icon.png` and `mobile/assets/adaptive-icon.png` exist.

---

## Step 3 — Build the preview APK

```bash
cd mobile
npm run build:android:preview
```

Equivalent:

```bash
eas build --platform android --profile preview
```

EAS will:
1. Upload your project to Expo cloud builders
2. Generate an Android signing keystore (first build only — stored by EAS)
3. Produce a signed `.apk` file

**First build:** ~10–20 minutes. Subsequent builds are faster.

### Non-interactive (CI)

```bash
eas build --platform android --profile preview --non-interactive
```

Requires `EXPO_TOKEN` environment variable ([create token](https://expo.dev/settings/access-tokens)).

---

## Step 4 — Download and distribute

1. Open the build URL printed in the terminal, or go to [expo.dev](https://expo.dev) → **Projects** → **TransAfrik Remit** → **Builds**
2. Wait for status **Finished**
3. Click **Download** to get the `.apk`
4. Share the APK or the Expo build page link with testers

### Install on a test device

**Option A — Direct APK**
1. Transfer APK to the phone (email, Drive, USB)
2. Open the file → **Install**
3. Enable **Install unknown apps** if prompted (Settings → Security)

**Option B — QR code from Expo dashboard**
1. Open the finished build page on the phone
2. Scan or tap the install link

---

## Step 5 — Test credentials

The preview APK connects to **production API** (`https://api.ipaygo.co.za`).

| Login | Password | Notes |
|-------|----------|-------|
| `admin@transafrik.co.za` | `Admin@TransAfrik2024!` | Staff account (always seeded) |
| `+27821234567` | `Customer@TransAfrik2024!` | Demo customer — **local seed only** |

For full customer testing with demo data, point a custom build at your local API:

```bash
eas build --platform android --profile preview \
  --env EXPO_PUBLIC_API_URL=http://YOUR_LAN_IP:8000
```

---

## Build profiles reference

| Profile | Command | Output | Use case |
|---------|---------|--------|----------|
| `preview` | `npm run build:android:preview` | APK | **Internal QA** |
| `preview-apk` | `npm run build:android:apk` | APK | Alias of preview |
| `development` | `eas build -p android --profile development` | APK + dev client | Hot reload debugging |
| `production` | `npm run build:android` | AAB | Google Play Store |

---

## Signing credentials

EAS manages Android signing automatically on first build.

To view or download credentials:

```bash
eas credentials --platform android
```

To use your own keystore:

```bash
eas credentials --platform android
# Choose "Set up a new keystore" or "Upload existing keystore"
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `EAS project not configured` | Run `npm run eas:init` in `mobile/` |
| `'eas' is not recognized` | Run `npm install` then use `npm run eas:login` or `npx eas` |
| `Cannot find path ...\mobile\mobile` | You're already in `mobile/` — skip the extra `cd mobile` |
| Build fails — missing assets | Verify `mobile/assets/icon.png` exists |
| `expo-asset` error | Run `npx expo install expo-asset` |
| APK won't install | Uninstall older version with same package name |
| API 401 / network error | Confirm `EXPO_PUBLIC_API_URL` has no `/api/v1` suffix |
| OTP not received | Configure `SMS_PROVIDER` on Railway backend |
| Build queued long | Free tier queue — upgrade or wait |

---

## Quick command summary

```bash
# One-time setup (from repo root)
cd mobile
npm install
npm run eas:login
npm run eas:init

# Build internal testing APK
npm run build:android:preview

# Check build status
npx eas build:list --platform android --limit 5

# View signing credentials
eas credentials --platform android
```

---

## Next steps after internal testing

1. Collect QA feedback from testers
2. Fix issues and rebuild with `npm run build:android:preview`
3. When ready for Play Store, switch to production AAB:

```bash
npm run build:android
# Output: .aab for Google Play internal track
```

---

*See also: [EAS_BUILD.md](./EAS_BUILD.md) · [DEPLOYMENT.md](./DEPLOYMENT.md) · [README.md](../README.md)*
