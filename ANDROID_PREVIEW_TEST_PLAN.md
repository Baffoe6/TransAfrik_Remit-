# TransAfrik Remit — Android Preview Test Plan

**Build:** EAS `preview` profile  
**Version:** `1.0.0-preview` (build `1`)  
**Commit:** `a32874e` — Phase 16 world-class fintech upgrade  
**APK:** [Direct download](https://expo.dev/artifacts/eas/e1UC1L7cZ6_s7kKDut9p8xQlYbd8DifPTQwa7TTD23Q.apk)  
**Install (QR):** [EAS build page](https://expo.dev/accounts/baffoe6/projects/transafrik-remit/builds/f1697bb3-a1b4-4161-81e9-e575cbabd2ae)  
**API:** https://api.ipaygo.co.za  
**Date:** June 2026

---

## Pre-test setup

- [ ] Install APK on physical Android device (Android 10+ recommended)
- [ ] Enable **Install from unknown sources** if sideloading APK directly
- [ ] Confirm device has internet (Wi‑Fi or mobile data)
- [ ] Confirm API health: `GET https://api.ipaygo.co.za/health` returns `healthy`
- [ ] Use a test mobile number registered in staging/production (or register fresh)
- [ ] Have a Ghana test beneficiary ready (mobile money or bank)

**Tester:** _______________  
**Device model / OS:** _______________  
**Test date:** _______________

---

## 1. Login

| # | Step | Expected | Pass |
|---|------|----------|------|
| 1.1 | Open app after install | Splash → onboarding or login screen | ☐ |
| 1.2 | Login with mobile + PIN | Authenticates, lands on Home tab | ☐ |
| 1.3 | Login with email + password (if account has email) | Successful login | ☐ |
| 1.4 | OTP login (SMS/WhatsApp) | OTP received and accepted | ☐ |
| 1.5 | Invalid credentials | Clear error message, no crash | ☐ |
| 1.6 | Session persists after app restart | Still logged in | ☐ |

**Notes:**

---

## 2. Register

| # | Step | Expected | Pass |
|---|------|----------|------|
| 2.1 | Tap Register from auth screen | Registration form loads | ☐ |
| 2.2 | Complete registration (name, mobile, PIN) | Account created, logged in | ☐ |
| 2.3 | Duplicate mobile number | Validation error shown | ☐ |
| 2.4 | Weak / invalid PIN | Validation error shown | ☐ |
| 2.5 | Onboarding slides (if shown) | Can skip or complete all slides | ☐ |

**Notes:**

---

## 3. KYC

| # | Step | Expected | Pass |
|---|------|----------|------|
| 3.1 | Navigate to KYC from Home or Profile | KYC screen with workflow states | ☐ |
| 3.2 | View progress bar | Shows % complete | ☐ |
| 3.3 | Scan ID (OCR) / Take photo | Camera opens, upload succeeds | ☐ |
| 3.4 | Upload proof of address (gallery) | Document uploaded, status updates | ☐ |
| 3.5 | Selfie verification | Camera capture and upload works | ☐ |
| 3.6 | Document preview | Preview image shown after capture | ☐ |
| 3.7 | Workflow status pill | Draft → Submitted → Reviewing states visible | ☐ |
| 3.8 | Home KYC card reflects status | Status matches profile/dashboard | ☐ |

**Notes:**

---

## 4. Beneficiaries

| # | Step | Expected | Pass |
|---|------|----------|------|
| 4.1 | Open Recipients tab | List loads (or empty state) | ☐ |
| 4.2 | Add new recipient (mobile money) | Saved and appears in list | ☐ |
| 4.3 | Add bank account recipient | Saved with correct type | ☐ |
| 4.4 | Category filter (Mobile Money / Bank / Cash Pickup) | List filters correctly | ☐ |
| 4.5 | Search by name | Results filter live | ☐ |
| 4.6 | Favorite a recipient (star) | Star toggles, favorites sort first | ☐ |
| 4.7 | Network logo badge (MTN etc.) | Shown for mobile money providers | ☐ |
| 4.8 | Quick send from recipient card | Opens send flow with recipient pre-selected | ☐ |
| 4.9 | Verification status pill | Displayed per recipient | ☐ |

**Notes:**

---

## 5. Send money flow

| # | Step | Expected | Pass |
|---|------|----------|------|
| 5.1 | Home live calculator | Enter amount → fee, rate, receive amount update | ☐ |
| 5.2 | Corridor selector (6 routes) | Switching corridor updates calculator | ☐ |
| 5.3 | Tap Send now → Send flow | Step 1 corridor pre-filled | ☐ |
| 5.4 | Step 2 — live quote | Amount changes recalculate quote (debounced) | ☐ |
| 5.5 | Step 3 — select recipient | Recipient selection required to continue | ☐ |
| 5.6 | Step 4 — payment method | Pay@ / EFT methods listed | ☐ |
| 5.7 | Step 5 — review summary | Fees, rate, partner badge, delivery ETA shown | ☐ |
| 5.8 | Save as template | Template saved, appears on Send tab | ☐ |
| 5.9 | Confirm & pay | Transfer created without error | ☐ |
| 5.10 | Send tab recent templates | Tapping template resumes flow | ☐ |

**Notes:**

---

## 6. Voucher generation

| # | Step | Expected | Pass |
|---|------|----------|------|
| 6.1 | After confirm & pay | Payment success screen loads | ☐ |
| 6.2 | Payment reference / voucher number | Displayed clearly | ☐ |
| 6.3 | Barcode or QR payment data (if applicable) | Renders correctly | ☐ |
| 6.4 | Copy / share reference (if available) | Reference accessible for Pay@ payment | ☐ |
| 6.5 | Instructions for completing payment | Clear next steps shown | ☐ |

**Notes:**

---

## 7. Transfer tracking

| # | Step | Expected | Pass |
|---|------|----------|------|
| 7.1 | Home active transfer widget | Shows in-progress transfer with progress bar | ☐ |
| 7.2 | Tap widget → tracking screen | Opens Transfer Tracking | ☐ |
| 7.3 | Delivery timeline | Steps render with dates | ☐ |
| 7.4 | Status pill updates | Matches API status | ☐ |
| 7.5 | Polling refresh (~15s) | Status updates without manual refresh | ☐ |
| 7.6 | Activity tab timeline + progress | Per-transfer progress visible | ☐ |

**Notes:**

---

## 8. Receipts

| # | Step | Expected | Pass |
|---|------|----------|------|
| 8.1 | Open receipt from Activity or Tracking | Receipt screen loads | ☐ |
| 8.2 | QR verification code | QR renders, scannable | ☐ |
| 8.3 | Amount, fee, rate, total | Values match transfer | ☐ |
| 8.4 | Recipient details section | Name, country, payout method shown | ☐ |
| 8.5 | Transaction timeline on receipt | Events listed chronologically | ☐ |
| 8.6 | Share via WhatsApp | Opens WhatsApp with receipt text | ☐ |
| 8.7 | Share via Email | Opens email client with receipt | ☐ |
| 8.8 | Download / share receipt | System share sheet works | ☐ |

**Notes:**

---

## 9. Notifications

| # | Step | Expected | Pass |
|---|------|----------|------|
| 9.1 | Open Notifications from Home bell icon | Inbox loads | ☐ |
| 9.2 | Seeded / demo notifications visible | Rate alert, promo items shown | ☐ |
| 9.3 | Tap notification | Marks as read, unread dot clears | ☐ |
| 9.4 | Mark all read | All items marked read | ☐ |
| 9.5 | Notification type icons | Transfer, KYC, rate, promo icons correct | ☐ |

**Notes:**

---

## 10. Profile & security

| # | Step | Expected | Pass |
|---|------|----------|------|
| 10.1 | Profile tab loads | Avatar, name, tier badge, KYC status | ☐ |
| 10.2 | Transfer limits card | Tier limit displayed (e.g. R25,000/mo) | ☐ |
| 10.3 | Account & compliance status | Status pills accurate | ☐ |
| 10.4 | Referral program card | Navigates to Referral screen | ☐ |
| 10.5 | Security center | Trusted devices, sessions, login history | ☐ |
| 10.6 | Biometrics screen | Configure biometrics flow opens | ☐ |
| 10.7 | Dark mode toggle | Theme switches correctly | ☐ |
| 10.8 | Sign out | Returns to login, session cleared | ☐ |
| 10.9 | Support (WhatsApp, FAQ, tickets) | All tabs functional | ☐ |

**Notes:**

---

## Regression / non-functional

| # | Check | Expected | Pass |
|---|-------|----------|------|
| R.1 | App launch time | < 5s on mid-range device | ☐ |
| R.2 | No crashes during full send journey | Zero crashes | ☐ |
| R.3 | Offline banner (airplane mode on Home) | Offline indicator shown, cached data visible | ☐ |
| R.4 | Haptic feedback on key actions | Light haptic on send/corridor select | ☐ |
| R.5 | Accessibility — text contrast | Readable in light and dark mode | ☐ |

---

## Sign-off

| Role | Name | Date | Result |
|------|------|------|--------|
| QA tester | | | ☐ Pass / ☐ Fail |
| Product owner | | | ☐ Approved / ☐ Blocked |

**Blocking issues:**

1. 
2. 
3. 

---

*TransAfrik Remit · IPAYGO (Pty) Ltd · Android Preview `1.0.0-preview` (build 1)*
