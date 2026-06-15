# Google Play Store Readiness — TransAfrik Remit

**Target:** Google Play · Internal testing → Production  
**Package:** `co.za.ipaygo.transafrik`  
**Version:** 1.0.0-preview

---

## Readiness Score: 80%

| Area | Status | Notes |
|------|--------|-------|
| UI/UX | ✅ Ready | Premium v2 redesign |
| Core flows | ✅ Ready | Send, KYC, tracking |
| API integration | ✅ Ready | `api.ipaygo.co.za` |
| Android build | ✅ In progress | EAS preview profile |
| Play Console | ⚠️ Verify | App listing created |
| Store listing | ❌ Pending | Screenshots, descriptions |
| Data safety | ⚠️ Pending | Play Data safety form |
| Service account | ⚠️ Pending | `google-service-account.json` |

---

## Pre-Submission Checklist

### Google Play Console
- [ ] Developer account active ($25 one-time)
- [ ] App created with package `co.za.ipaygo.transafrik`
- [ ] Internal testing track configured

### Build
- [x] EAS preview profile configured (`eas.json`)
- [ ] Preview APK tested on Android device
- [ ] Production AAB via `build:android` (app-bundle)
- [ ] `versionCode` auto-increment enabled (remote)

```bash
cd mobile
npm run build:android:preview   # APK for testing
npm run build:android           # AAB for Play Store
```

### Store Listing
- [ ] **App name:** TransAfrik Remit
- [ ] **Short description:** Send money from South Africa to Ghana — fast, secure, transparent.
- [ ] **Full description:** Include IPAYGO operator, partner processing, FICA compliance
- [ ] **Category:** Finance
- [ ] **Contact email:** support@transafrik.co.za (or production support email)
- [ ] **Privacy policy URL**

### Graphics
- [ ] Feature graphic: 1024 × 500
- [ ] App icon: 512 × 512 (from `assets/icon.png`)
- [ ] Phone screenshots: min 2, max 8 (1080 × 1920 or higher)
- [ ] 7-inch / 10-inch tablet (optional)

Reference mockups: `mobile/showcase/`

### Data Safety Form
- [ ] Personal info collected: Name, email, phone, ID documents
- [ ] Financial info: Transfer amounts, payment references
- [ ] Data encrypted in transit: Yes (HTTPS)
- [ ] Data deletion request supported: Yes
- [ ] Purpose: App functionality, fraud prevention, legal compliance

### Content Rating
- [ ] Complete IARC questionnaire
- [ ] Expected rating: Everyone or Teen (finance app)

### Permissions Justification
| Permission | Reason |
|------------|--------|
| CAMERA | KYC document capture |
| USE_BIOMETRIC | Optional login |
| INTERNET | API communication |

### Compliance (South Africa)
- [ ] FSCA remittance facilitation disclosure
- [ ] POPIA privacy compliance
- [ ] Not marketed as a bank or deposit-taking institution

---

## Submit to Play Store

1. Build production AAB: `npm run build:android`
2. Configure `google-service-account.json` in `eas.json`
3. Submit: `npx eas submit --platform android`
4. Promote from internal → closed → open → production

---

## EAS Build Status

Preview builds use profile `preview` with:
- `EXPO_PUBLIC_API_URL=https://api.ipaygo.co.za`
- `EXPO_PUBLIC_APP_ENV=preview`
- APK distribution for sideload / internal testing

---

## Known Gaps

1. Play Console store listing copy
2. Real device screenshots (capture from preview APK)
3. Google service account for automated submit
4. Auth screen visual polish
5. In-app review prompt (post-transfer)

---

## Timeline Estimate

| Phase | Duration |
|-------|----------|
| Preview APK QA | 3–5 days |
| Store listing + data safety | 2–3 days |
| Internal testing | 1 week |
| Google review | 1–7 days |

**Earliest production launch:** ~2 weeks from preview APK sign-off
