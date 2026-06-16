# TransAfrik Remit — Mobile Release Notes

## v2.0.0 Production Candidate (June 2026)

### Production readiness

- **Real customer registration** — mobile-first, POPIA/AML consents, invite codes, 8+ character passwords aligned with API
- **Mobile OTP verification** — required gate after registration; resend with cooldown
- **Login** — mobile or email + password; OTP alternative
- **KYC** — correct document types (`id_passport`), preview, workflow states
- **Transfer gates** — blocks send if phone unverified or KYC not approved
- **Flutterwave payment readiness** — secure browser flow, server-side session, status polling
- **Retail vouchers** — Pay@/EasyPay with QR, expiry, WhatsApp share
- **Support** — ticket categories, WhatsApp, FAQ
- **Compliance copy** — removed misleading demo/licensing language

### Backend additions

- `POST /payments/transfers/{id}/flutterwave/session`
- `GET /payments/transfers/{id}/payment-status`

### Tests

- 16 unit tests passing (validation, constants, stores, production rules)

---

## v1.0.0 Phase 16 (June 2026)

World-class fintech upgrade — live calculator, 6 corridors, templates, QR receipts, security center.

---

*TransAfrik Remit · IPAYGO (Pty) Ltd*
