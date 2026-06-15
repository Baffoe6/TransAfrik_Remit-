# TransAfrik Remit — Mobile Release Notes

## v1.0.0 Phase 16 — World-Class Fintech Upgrade (June 2026)

### Highlights

This release transforms TransAfrik Remit from a premium MVP into a world-class remittance experience aligned with Wise, Revolut, Remitly, and Chipper Cash.

### New Features

**Home**
- Live exchange rate card with real-time calculator (You Send, Fee, Rate, Recipient Receives)
- Six corridor selector: South Africa to Ghana, Zimbabwe, Zambia, Kenya, Nigeria, Uganda
- Active transfer widget with progress tracking
- Favorite recipients carousel and rate alert widget
- Referral and promotions card

**Send Money**
- Wise-style calculator with live recalculation on amount changes
- Payout partner badges (Mukuru, Flutterwave, Onafriq)
- Save transfers as templates; quick-load recent templates

**Recipients**
- Filter by Mobile Money, Bank Account, or Cash Pickup
- Network logos, favorites, quick send, verification status

**Activity**
- Per-transfer timeline and progress bars
- Filters: Today / Week / Month and Pending / Processing / Completed / Failed / Refunded
- One-tap export to receipt

**Receipts**
- QR verification code
- Share via WhatsApp, Email, or system share
- Recipient details and transaction timeline

**KYC**
- OCR ID scan (camera), selfie verification, document preview
- Workflow states: Draft → Submitted → Reviewing → Approved → Rejected

**Profile & Security**
- Tier badges and monthly transfer limits
- Full security center: trusted devices, sessions, login history, MFA, biometrics, PIN

**Support & Notifications**
- WhatsApp support, expandable FAQ, ticket management, live chat placeholder
- Notification inbox for rate, transfer, KYC, and promo alerts

### Technical

- New `worldclass` component library
- Zustand stores: calculator, templates, rate alerts, notification inbox
- `useLiveQuote` hook with 500ms debounce
- Haptic feedback via `expo-haptics`
- Expanded test coverage

### Previous Releases

**v1.0.0 Preview (Phase 14)** — Premium fintech redesign, design system v2, headerless tabs, dark mode

**v1.0.0 Preview (Phase 11)** — Initial production MVP with 5-step send flow, KYC, activity, support

---

*TransAfrik Remit · IPAYGO (Pty) Ltd*
