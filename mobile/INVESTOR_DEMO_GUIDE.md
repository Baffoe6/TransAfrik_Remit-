# Investor Demo Guide — TransAfrik Remit Mobile

**Purpose:** Live or recorded demo for investors, partners, and pilot stakeholders  
**Duration:** 10–15 minutes  
**Platforms:** Android preview APK · iOS TestFlight (when available) · Web at app.ipaygo.co.za

---

## Demo Narrative (Story Arc)

> *"TransAfrik Remit is the mobile-first remittance product for South Africans sending money to Ghana — built with the UX quality of Wise and the trust standards of regulated African fintech."*

1. **Problem** — Expensive, opaque remittance to West Africa
2. **Solution** — Transparent fees, live tracking, mobile money delivery
3. **Traction** — Production API, pilot-ready platform, premium mobile v2
4. **Moat** — Compliance stack, partner rails, ZA→GH corridor focus
5. **Ask** — Pilot scale, store launch, corridor expansion

---

## Demo Flow (12 minutes)

### 1. Home Screen (2 min)
**Show:** Dashboard hub after login

**Talking points:**
- Personalized greeting, trust badges (Licensed partners, Encrypted, FICA)
- Quick Send — one tap to transfer
- KYC status visible — compliance-first onboarding
- Recent transfers — retention and repeat usage

**Screenshot:** `showcase/home-screen.png`

---

### 2. Send Money (3 min)
**Show:** Send tab → Start transfer → 5-step flow

**Steps to demo:**
1. Select Ghana corridor
2. Enter amount → **live quote** (fee + rate + recipient gets)
3. Pick beneficiary
4. Choose Pay@ / EFT payment method
5. Review and confirm → payment voucher

**Talking points:**
- Transparent pricing before payment (no hidden fees)
- Retail payment rails (Pay@, EasyPay) — no card required for pilot
- Partner-processed settlement (Mukuru / licensed partners)

**Screenshot:** `showcase/send-screen.png`

---

### 3. KYC Verification (2 min)
**Show:** Profile → KYC or Home KYC card

**Talking points:**
- FICA-required identity verification
- Document upload: SA ID, proof of address, selfie
- Compliance review within 24–48 hours
- Gates send capability — risk management

**Screenshot:** `showcase/kyc-screen.png`

---

### 4. Beneficiaries (1 min)
**Show:** Recipients tab

**Talking points:**
- Saved recipients with favorites
- Ghana mobile money and bank details
- Fast repeat sends for family support use case

**Screenshot:** `showcase/beneficiaries-screen.png`

---

### 5. Activity & Tracking (2 min)
**Show:** Activity tab → tap transfer → tracking timeline

**Talking points:**
- Full transfer history with filters
- Real-time status updates (15s polling)
- Delivery timeline: created → paid → compliance → partner → completed
- Official receipt for records

**Screenshots:** `showcase/activity-screen.png`, `showcase/receipt-screen.png`

---

### 6. Profile & Security (1 min)
**Show:** Profile tab

**Talking points:**
- Dark mode — modern fintech standard
- Biometric login option
- Security settings, support access
- Operator: IPAYGO (Pty) Ltd

**Screenshot:** `showcase/profile-screen.png`

---

### 7. Platform & Production (1 min)
**Show:** API health (optional browser)

```
https://api.ipaygo.co.za/health
```

**Talking points:**
- Production API on Railway, frontend on Vercel
- PostgreSQL + Redis, security center for admin
- Phase 12 production hardening complete
- Mobile v2 premium redesign — store-ready UX

---

## Demo Accounts

Use seeded pilot accounts (development) or create fresh pilot invite:

| Role | Purpose |
|------|---------|
| Customer | Full send flow demo |
| Admin | Show web ops dashboard (optional) |

**Production demo:** Use pilot invite codes only — do not use production with real funds without compliance sign-off.

---

## Backup Plan (If Live API Fails)

1. Show cached offline data on Activity screen
2. Walk through UI with showcase screenshots in `MOBILE_SHOWCASE.md`
3. Switch to web app at https://app.ipaygo.co.za
4. Show architecture docs: `MOBILE_DESIGN_SYSTEM.md`, `SECURITY_READINESS_REPORT.md`

---

## Key Metrics to Mention

| Metric | Value |
|--------|-------|
| Corridor | ZA → Ghana (GHS) |
| Payment methods | Pay@, EasyPay, EFT |
| API version | 7.0.0-mvp |
| Mobile version | 1.0.0-preview |
| Security readiness | 88% (Phase 12) |
| Design benchmark | Wise / Remitly / Revolut tier |

---

## FAQ Prep

**Q: Are you a bank?**  
A: No. TransAfrik Remit is a facilitation platform operated by IPAYGO (Pty) Ltd. Transfers are processed through licensed remittance partners.

**Q: How do you make money?**  
A: Transparent transfer fees (from R15) and FX spread on corridor rates.

**Q: When App Store / Play Store?**  
A: Preview builds available now; store submission targeted within 2 weeks of QA sign-off. See `APP_STORE_READINESS.md` and `PLAY_STORE_READINESS.md`.

**Q: What's next after Ghana?**  
A: Corridor expansion (Nigeria, Kenya), Flutterwave card payments, agent network.

---

## Materials Checklist

- [ ] Phone with preview APK installed
- [ ] Demo account logged in
- [ ] `MOBILE_SHOWCASE.md` open for visuals
- [ ] API health tab ready
- [ ] This guide printed or on second screen

---

## Contact

**Platform:** TransAfrik Remit  
**Operator:** IPAYGO (Pty) Ltd  
**Web:** https://app.ipaygo.co.za  
**API:** https://api.ipaygo.co.za
