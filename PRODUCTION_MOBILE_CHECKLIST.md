# Production Mobile Checklist

## Pre-launch

- [x] Real registration with production API
- [x] Mobile OTP verification gate
- [x] KYC document types aligned with backend
- [x] Transfer eligibility gates (KYC + phone)
- [x] Flutterwave session endpoint (backend)
- [x] Flutterwave mobile payment screen
- [x] Demo language removed
- [x] TypeScript strict + tests pass
- [ ] SMS/WhatsApp OTP provider live on Railway
- [ ] Flutterwave live API keys on Railway
- [ ] R2 storage configured for KYC
- [ ] Physical device QA sign-off
- [ ] Play Store internal testing track

## Deploy

- [ ] `eas build --profile preview` (Android APK)
- [ ] Push to `main`
- [ ] Verify `GET /health` returns healthy
- [ ] Verify https://app.ipaygo.co.za loads

## Post-launch monitoring

- [ ] Monitor transfer creation errors
- [ ] Monitor KYC upload failures
- [ ] Monitor payment session creation
- [ ] Review support tickets daily during pilot
