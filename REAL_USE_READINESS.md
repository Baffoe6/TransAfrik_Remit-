# TransAfrik Remit — Real Use Readiness

**Version:** 2.0.0 Production Candidate  
**API:** https://api.ipaygo.co.za  
**Web:** https://app.ipaygo.co.za

---

## Production-ready flows

| Flow | Status | Notes |
|------|--------|-------|
| Registration (mobile-first) | ✅ | Mobile + 4-digit PIN, POPIA/terms consents, optional email/referral/invite |
| Mobile OTP verification | ✅ | Post-register gate; resend with cooldown |
| Login (mobile + PIN) | ✅ | Primary; email/password secondary; OTP for new devices |
| KYC upload | ✅ | `id_passport`, proof of address, selfie — backend-aligned |
| Beneficiaries | ✅ | MM/bank/cash pickup, Ghana validation |
| Transfer creation | ✅ | Real API records; KYC/phone gates |
| Pay@ / EasyPay vouchers | ✅ | QR, reference, retail instructions |
| Flutterwave card readiness | ✅ | Server session endpoint; mobile secure browser flow |
| Transfer tracking | ✅ | 15s polling, production status labels |
| Receipts | ✅ | QR, share, compliance disclaimer |
| Support tickets | ✅ | Categories, WhatsApp, FAQ |
| Security center | ✅ | Devices API mapping fixed |

---

## Removed demo assumptions

- No hardcoded demo customer login
- No fake balance cards
- No "FICA compliant" / misleading licensing copy
- Accurate partner-powered messaging throughout

---

## Customer onboarding path

1. Register (mobile + PIN) → accept POPIA & terms
2. Verify mobile (OTP)
3. Complete KYC documents
4. Add beneficiary
5. Send money → pay via Flutterwave or retail voucher
6. Track → receipt

---

## Backend dependencies

- `SEED_DEMO_DATA=false` on production (correct)
- Flutterwave secrets **server-side only**
- SMS/WhatsApp OTP provider configuration on Railway
- R2 storage for KYC documents (via backend abstraction)

---

*IPAYGO (Pty) Ltd — TransAfrik Remit*
