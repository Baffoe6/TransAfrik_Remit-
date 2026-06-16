# Mobile PIN Authentication — Migration Plan

## Overview

TransAfrik moves to **mobile number + 4-digit PIN** as the primary customer identity. Email/password remains for legacy staff and migrated accounts only.

## Database (migration `013_pin_authentication`)

| Column | Change |
|--------|--------|
| `users.pin_hash` | Added (bcrypt, same as passwords) |
| `users.password_hash` | Now nullable (PIN-only customers) |
| `users.email` | Already nullable |
| `users.mobile_number` | Required for new customers (unique) |

Run on deploy:

```bash
cd backend && alembic upgrade head
```

## API Changes

### Registration — `POST /api/v1/auth/register`

**Required:** `mobile_number`, `first_name`, `last_name`, `pin` (4–6 digits), `accept_popia`, `accept_terms`  
**Optional:** `email`, `invite_code`, `referral_code`

PIN is stored as `pin_hash` only — never plain text.

### Primary login — `POST /api/v1/auth/login/pin`

```json
{ "mobile_number": "+27821234567", "pin": "1234" }
```

### Legacy login — `POST /api/v1/auth/login`

Email + password for staff and existing email accounts (`identifier` + `password`).

### PIN reset

- `POST /api/v1/auth/pin/forgot` — sends OTP (`pin_reset` purpose)
- `POST /api/v1/auth/pin/reset` — `{ mobile_number, code, new_pin }`

### Optional PIN for legacy users — `POST /api/v1/auth/pin/set`

Authenticated users with password but no PIN can set one (requires `current_password` if password exists).

## OTP (Twilio Verify)

Set environment variables:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_VERIFY_SERVICE_SID`
- `OTP_PROVIDER=twilio_verify`

Phase 1: SMS. Phase 2: WhatsApp (`channel: whatsapp`).

OTP purposes: `verify_phone`, `pin_reset`, `step_up`, `login`, `beneficiary_change`, `high_value_transfer`, `kyc_update`.

Development: `OTP_PROVIDER=console` (default) with `OTP_DEV_EXPOSE_CODE=true` returns `dev_code` in responses.

## Existing User Migration

| User type | Action |
|-----------|--------|
| Email/password customer | Continue `/auth/login`; optionally `POST /auth/pin/set` |
| New customer | Register with mobile + PIN; verify phone OTP; complete KYC (email optional) |
| Staff/admin | Unchanged — password + MFA |

### Demo seed (local only)

- Mobile: `+27821234567`
- PIN: `1234`
- Legacy password still works for email login

## Mobile App

- **Login:** Mobile + PIN default; “Sign in with email” secondary link
- **Register:** PIN + confirm PIN; email/referral/invite optional
- **Forgot PIN:** OTP reset flow

## Security (unchanged infrastructure)

- Failed login lockout (`failed_login_attempts`, `locked_until`)
- Device trust + step-up OTP on new/high-risk devices
- Rate limits on auth endpoints

## Rollout Checklist

1. Deploy backend + run migration `013`
2. Set Twilio Verify env vars on Railway
3. Ship mobile build with PIN UI
4. Communicate PIN setup to existing email customers
5. Monitor `login_failed` / `account_locked` security events
