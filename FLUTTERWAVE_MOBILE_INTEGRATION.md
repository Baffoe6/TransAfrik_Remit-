# Flutterwave Mobile Integration

**Status:** Integration-ready (Phase 24)  
**Secrets:** Backend only — never in mobile bundle

---

## Flow

```
Customer confirms transfer
        ↓
POST /api/v1/transfers (create transfer record)
        ↓
POST /api/v1/payments/transfers/{id}/flutterwave/session
        ↓
Mobile receives { payment_url, session_ref }
        ↓
Customer opens secure URL (external browser)
        ↓
Flutterwave webhook → backend marks payment received
        ↓
GET /api/v1/payments/transfers/{id}/payment-status (poll)
        ↓
Transfer tracking updates
```

---

## Mobile implementation

| Component | Path |
|-----------|------|
| Payment method detection | `FLUTTERWAVE_METHOD_CODES` in `utils/compliance.ts` |
| API client | `paymentsApi.flutterwaveSession()` |
| Payment screen | `features/transfers/FlutterwavePaymentScreen.tsx` |
| Send flow routing | `SendFlowScreen.tsx` — routes card methods to Flutterwave |

---

## Backend endpoint

```
POST /api/v1/payments/transfers/{transfer_id}/flutterwave/session
Authorization: Bearer <customer token>

Response:
{
  "payment_url": "https://...",
  "session_ref": "flw_...",
  "provider": "flutterwave",
  "status": "pending",
  "expires_at": "..."
}
```

When Flutterwave API keys are configured on Railway, replace URL generation in `payments.py` with live Flutterwave API call.

---

## Security checklist

- [x] No `FLUTTERWAVE_SECRET_KEY` in mobile
- [x] Mobile only opens public `payment_url`
- [x] Payment confirmation via backend webhook + status poll
- [ ] Configure Flutterwave webhook URL on Railway
- [ ] Add `flutterwave` payment method to seed/production DB

---

*TransAfrik Remit v2.0*
