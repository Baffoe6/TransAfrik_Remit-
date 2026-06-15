# App Store (iOS) Readiness — TransAfrik Remit

**Target:** Apple App Store · TestFlight → Production  
**Bundle ID:** `co.za.ipaygo.transafrik`  
**Version:** 1.0.0-preview

---

## Readiness Score: 75%

| Area | Status | Notes |
|------|--------|-------|
| UI/UX | ✅ Ready | Premium v2 redesign complete |
| Core flows | ✅ Ready | Send, KYC, tracking, receipts |
| API integration | ✅ Ready | Production API configured |
| Dark mode | ✅ Ready | Light/dark/system |
| Auth screens | ⚠️ Partial | Login/register still v1 styling |
| App Store assets | ❌ Pending | Screenshots, preview video |
| Apple Developer | ⚠️ Verify | Account + ASC app record |
| Privacy manifest | ⚠️ Pending | App Privacy labels |
| TestFlight | ⚠️ Pending | First iOS EAS build |

---

## Pre-Submission Checklist

### Apple Developer Account
- [ ] Enrolled in Apple Developer Program ($99/year)
- [ ] App created in App Store Connect
- [ ] Bundle ID `co.za.ipaygo.transafrik` registered

### Build
- [ ] Run `npm run build:ios` (EAS production profile)
- [ ] TestFlight internal testing (min 1 build)
- [ ] Test on physical iPhone (iOS 16+)

### App Store Connect Metadata
- [ ] App name: **TransAfrik Remit**
- [ ] Subtitle: Send money to Ghana
- [ ] Category: Finance
- [ ] Age rating: 4+ (or 12+ if required for finance)
- [ ] Privacy Policy URL (hosted on app.ipaygo.co.za)
- [ ] Support URL

### Screenshots (Required sizes)
- [ ] 6.7" (iPhone 15 Pro Max) — 1290 × 2796
- [ ] 6.5" (iPhone 11 Pro Max) — 1242 × 2688
- [ ] 5.5" (optional legacy) — 1242 × 2208

Use screens from `mobile/showcase/` as reference; capture from TestFlight build for submission.

### App Privacy
- [ ] Declare: Contact Info, Financial Info, Identifiers
- [ ] KYC document collection disclosed
- [ ] Data linked to user: Yes (account, transfers)
- [ ] Tracking: No (unless analytics added)

### Review Notes
- [ ] Demo account credentials for Apple reviewer
- [ ] Explain remittance facilitation model (not a bank)
- [ ] KYC required before send — provide test path

### Compliance
- [ ] FICA / AML compliance statement in app
- [ ] Terms of Service and Privacy Policy accessible in-app
- [ ] IPAYGO (Pty) Ltd operator disclosure

---

## Build Commands

```bash
cd mobile
npx eas login
npm run build:ios
npx eas submit --platform ios
```

Update `eas.json` → `submit.production.ios` with real Apple ID and ASC App ID.

---

## Known Gaps Before Submission

1. Auth/onboarding visual pass (P1)
2. Real device screenshots from TestFlight
3. App Store preview video (recommended)
4. Push notification entitlement review
5. Camera permission usage string in Info.plist (expo-camera plugin)

---

## Timeline Estimate

| Phase | Duration |
|-------|----------|
| TestFlight build + QA | 1 week |
| App Store assets | 2–3 days |
| Review submission | 1–2 days |
| Apple review | 1–7 days |

**Earliest production launch:** ~2 weeks from TestFlight build
