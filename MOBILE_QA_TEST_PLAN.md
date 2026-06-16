# Mobile QA Test Plan — Production Candidate v2.0

See also: [ANDROID_PREVIEW_TEST_PLAN.md](ANDROID_PREVIEW_TEST_PLAN.md)

## Critical journeys

### 1. New customer registration
- [ ] Register with valid SA mobile (+27...)
- [ ] Password min 8 characters accepted
- [ ] Duplicate mobile shows API error
- [ ] POPIA/AML/terms toggles required
- [ ] Invite code works when pilot mode on
- [ ] Redirected to OTP verification after register

### 2. Mobile verification
- [ ] OTP send shows success (no code in UI)
- [ ] Resend cooldown works (60s)
- [ ] Valid OTP marks phone verified
- [ ] App unlocks main tabs after verify

### 3. KYC
- [ ] Upload passport/ID (`id_passport`)
- [ ] Upload proof of address
- [ ] Upload selfie
- [ ] Document preview shown
- [ ] Rejection reason displayed if rejected

### 4. Beneficiary
- [ ] Create Ghana MTN mobile money recipient
- [ ] Invalid Ghana number rejected
- [ ] Edit and delete beneficiary
- [ ] Favorite and quick send

### 5. Transfer + payment
- [ ] Blocked without KYC approval
- [ ] Blocked without phone verify
- [ ] Live quote on amount change
- [ ] Pay@ voucher: reference + QR shown
- [ ] Flutterwave: secure URL opens, status poll works

### 6. Post-payment
- [ ] Tracking timeline updates
- [ ] Receipt QR + share works
- [ ] Support ticket with category

---

**Pass criteria:** All critical journeys complete without crash on physical Android device.
