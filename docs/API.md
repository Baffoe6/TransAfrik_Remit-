# TransAfrik Remit API — MVP v7.0.0

Base URL: `https://api.ipaygo.co.za/api/v1`

## Public

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health (no auth) |
| GET | `/disclaimer` | Platform disclaimer |
| POST | `/waitlist/join` | Join pre-launch waitlist |

## Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register (mobile required, email optional) |
| POST | `/auth/login` | Login with mobile number or email + password |
| POST | `/auth/otp/send` | Send OTP via SMS or WhatsApp |
| POST | `/auth/login/otp` | Passwordless OTP login |
| POST | `/auth/login/step-up` | Complete step-up after high-risk password login |
| POST | `/auth/otp/verify-phone` | Verify mobile number (authenticated) |
| GET | `/auth/devices` | List trusted devices |
| POST | `/auth/devices/trust` | Trust or revoke a device |
| POST | `/auth/logout` | Logout |
| GET | `/auth/me` | Current user |

## Customer

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard/summary` | Unified dashboard data |
| GET/PATCH | `/profile` | Customer profile |
| GET/POST | `/kyc/documents` | KYC documents |
| POST | `/kyc/upload` | Upload KYC file |
| GET/POST/PATCH/DELETE | `/beneficiaries` | Beneficiary CRUD |
| POST | `/transfers/calculate` | Fee/FX quote |
| GET/POST | `/transfers` | List/create transfers |
| GET | `/transfers/{id}` | Transfer detail |

## Admin MVP

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/waitlist` | List waitlist leads |
| GET | `/admin/waitlist/export` | CSV export |
| GET | `/admin/compliance/dashboard` | Compliance metrics |
| GET | `/admin/compliance/export` | Compliance CSV |
| GET | `/admin/operations/dashboard` | Operations metrics |
| GET | `/admin/launch-readiness` | Launch checklist + % |
| GET | `/admin/partners` | Partner provider list |
| POST | `/admin/partners/{code}/quote` | Test mock quote |

Full OpenAPI docs available in development at `/docs`.
