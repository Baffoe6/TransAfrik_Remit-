# TransAfrik Remit

Customer-facing remittance platform operated by **IPAYGO (Pty) Ltd**. Send money from South Africa (ZAR) to Africa via mobile money and partner corridors.

> **Disclaimer:** TransAfrik is a customer-facing remittance facilitation platform operated by IPAYGO (Pty) Ltd. Transfers are processed through approved third-party payment and remittance partners. TransAfrik is not licensed as a bank or remittance operator.

## Production (MVP v7.0.0)

| Service | URL |
|---------|-----|
| Frontend | https://app.ipaygo.co.za |
| API | https://api.ipaygo.co.za |
| Health | https://api.ipaygo.co.za/health |

**Production environment variables (Railway):**

```env
ENVIRONMENT=production
SEED_DEMO_DATA=false
ENABLE_DEV_ENDPOINTS=false
DOCS_ENABLED=false
CORS_ORIGINS=https://app.ipaygo.co.za
```

After deploy, run `alembic upgrade head` on the production database.

See also: [docs/API.md](docs/API.md) · [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) · [PROJECT_STATUS.md](PROJECT_STATUS.md)

### MVP Features

- **Waitlist** — public signup at `/waitlist`, admin management at `/admin/waitlist`
- **Customer dashboard** — profile completion, KYC, beneficiaries, transfers, history, referrals
- **KYC workflow** — document upload, admin review with notes
- **Transfer engine** — create/list/detail with MVP status labels
- **Corridors** — ZA→GH, ZW, ZM, KE, NG, UG (admin-managed)
- **Partner abstraction** — mock Flutterwave, Mukuru, Onafriq, Veengu providers
- **Compliance & operations dashboards** — metrics, CSV export, KYC queue
- **Launch readiness** — `/admin/launch-readiness` checklist with readiness %

### Production Staff Accounts

| Role | Email | Password (default seed) |
|------|-------|-------------------------|
| Admin | admin@transafrik.co.za | Admin@TransAfrik2024! |
| Founder | founder@transafrik.co.za | Founder@TransAfrik2024! |
| Compliance | compliance@transafrik.co.za | Compliance@TransAfrik2024! |
| Operations | operations@transafrik.co.za | Operations@TransAfrik2024! |

Demo customer, beneficiary, invite codes, and pilot stats are **not seeded** when `SEED_DEMO_DATA=false` (production default).

## Architecture

```
transafrik-remit/
├── frontend/          # Next.js 15+ (App Router), TypeScript, Tailwind, shadcn-style UI
├── backend/           # FastAPI, SQLAlchemy, Alembic, JWT auth
├── mobile/            # React Native (Expo) customer app — Phase 11
├── examples/          # Sample Mukuru batch CSV export
├── docker-compose.yml
└── README.md
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, TypeScript, Tailwind CSS, shadcn/ui components |
| Backend | FastAPI, Python 3.12, Pydantic |
| Database | PostgreSQL 16 |
| Auth | JWT access + refresh tokens, bcrypt password hashing |
| File Storage | Local or S3 (MinIO/AWS) via storage abstraction |
| Cache/Queue | Redis (rate limits, OTP, webhooks, session blacklist) |
| Deployment | Docker Compose (dev + staging with nginx) |

### User Roles

- **Customer** — register, KYC, beneficiaries, transfers, support
- **Admin** — full operations dashboard, batch exports, rate management
- **Compliance Officer** — same admin access for KYC/compliance review

## Quick Start (Docker)

```bash
# Clone and enter project
cd transafrik-remit

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Start all services
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

### Seed Accounts (local development)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@transafrik.co.za | Admin@TransAfrik2024! |
| Compliance | compliance@transafrik.co.za | Compliance@TransAfrik2024! |
| Founder | founder@transafrik.co.za | Founder@TransAfrik2024! |
| Operations | operations@transafrik.co.za | Operations@TransAfrik2024! |
| Agent | agent@transafrik.co.za | Agent@TransAfrik2024! |
| Demo Customer | customer@demo.co.za | Customer@TransAfrik2024! |

When `SEED_DEMO_DATA=true` (local default), the demo customer has approved KYC and an approved Ghana beneficiary ready for transfers.

Change these credentials in production via environment variables.

## Local Development (without Docker)

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Create database
createdb transafrik

# Run migrations and seed
alembic upgrade head
python -m app.seed

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Phase 1 — Multi-Channel Payment Collection

TransAfrik supports banked and unbanked customers in South Africa through multiple payment rails:

| Method | Code | Description |
|--------|------|-------------|
| Pay@ Voucher | `pay_at` | Cash at Shoprite, Checkers, Pick n Pay, Boxer, Usave |
| EasyPay Voucher | `easy_pay` | Cash at EasyPay partner outlets |
| EFT Bank Transfer | `eft` | EFT or cash deposit + proof upload |
| Instant EFT (Stitch) | `stitch` | Future-ready stub |
| Instant EFT (Ozow) | `ozow` | Future-ready stub |
| Card (Peach / PayFast) | `peach_payments`, `payfast` | Future-ready stubs |

### Customer Transfer Flow

1. Register and complete KYC
2. Add beneficiary (MTN, Telecel Cash, AirtelTigo Money)
3. Create transfer and select payment method
4. System generates payment reference / voucher / banking instructions
5. Customer pays (cash at retailer, EFT, or future instant methods)
6. Admin verifies payment (EFT) or system records retailer payment
7. Compliance review if AML flags triggered
8. Admin exports Mukuru batch → manual processing → completed

### Transfer Statuses

`draft` → `awaiting_payment` → `payment_pending_verification` → `payment_verified` → `compliance_review` → `ready_for_processing` → `submitted_to_mukuru` → `processing` → `completed`

Also: `failed`, `refunded`, `expired`

### Admin Batch Export

1. Go to **Admin → Transfers**
2. Select transfers under review
3. Click **Export Mukuru Batch**
4. Download CSV for manual upload to Mukuru Enterprise

See `examples/mukuru_batch_sample.csv` for the export format.

## Provider Abstraction

### Payment Collection (`PaymentProvider`)

Located in `backend/app/payment_providers/`. Stubs implemented for:

- `PayAtProvider`, `EasyPayProvider`, `EftProvider`
- `StitchProvider`, `OzowProvider`, `PeachPaymentsProvider`, `PayFastProvider`

Methods: `generate_reference()`, `check_payment_status()`, `process_webhook()`, `initiate_payment()`

### Remittance Disbursement (`RemittanceProvider`)

Located in `backend/app/providers/`. Methods:

- `create_transfer()`, `get_transfer_status()`, `cancel_transfer()`
- `export_batch()`, `export_excel()`, `generate_batch()`
- `reconcile_transfer()`, `reconcile_transactions()`
- `mark_as_submitted()`, `mark_as_completed()`

**Current implementation:** `ManualMukuruProvider` — CSV/Excel batches for Mukuru Enterprise. Stubs: `MukuruProvider`, `VeenguProvider`, `OnafriqProvider`, `FlutterwaveProvider`.

## Security

- bcrypt password hashing
- JWT access (30 min) + refresh (7 day) tokens
- Role-based access control (customer, admin, compliance_officer)
- Pydantic input validation on all endpoints
- File upload validation (type, size limits)
- Audit logging for all admin actions
- Basic AML flags: repeated transfers, high-value, multiple beneficiaries, name mismatch

## API Documentation

Interactive docs at `/docs` (Swagger) and `/redoc` when the backend is running.

Base path: `/api/v1`

Key endpoints:
- `POST /api/v1/auth/register` — customer registration
- `POST /api/v1/auth/login` — login
- `POST /api/v1/transfers/calculate` — fee/FX calculator
- `POST /api/v1/transfers` — create transfer
- `GET /api/v1/admin/dashboard` — admin stats
- `POST /api/v1/admin/transfers/export-batch` — Mukuru CSV export

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (use `openssl rand -hex 32`) |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `UPLOAD_DIR` | Local file upload directory |
| `SEED_ADMIN_EMAIL` | Initial admin email |
| `SEED_ADMIN_PASSWORD` | Initial admin password |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL |

## Phase 2 — Production Modules (v2.0.0)

### Notification Service
- SMS and email provider abstractions (`backend/app/notifications/`)
- Database-backed templates with lifecycle events (created, payment received/verified, completed, failed, compliance review)
- Automatic notifications on transfer status changes

### Exchange Rate Engine
- Admin-managed rates with **effective dates** and **rate history**
- Customer calculator uses active rate for the selected date
- API: `POST /api/v1/admin/exchange-rates/v2`, `GET /api/v1/admin/exchange-rates/history`

### Fee Engine
- Tiered fees with **country-specific**, **payment-method**, and **provider** rules plus priority ordering
- Admin UI at `/admin/rates` (v2 fee endpoints)
- API: `POST /api/v1/admin/fee-rules/v2`, `GET /api/v1/admin/fee-rules/v2`

### Compliance Module
- Customer risk profiles, AML flags, sanctions screening placeholder, EDD case queue
- Integrated into transfer creation via `compliance_engine`
- Admin EDD queue at `/admin/compliance/edd`

### Analytics Dashboard
- Daily/monthly volume and revenue, transfers by country and payment method
- Admin UI at `/admin/analytics`

### Production Security
- **MFA (TOTP)** for admin/compliance staff — setup at `/admin/security`
- **Rate limiting** via SlowAPI (auth endpoints throttled)
- **Session management** — refresh tokens tracked in `user_sessions`
- **Security audit logs** — login, logout, MFA events

### API Readiness
- `MukuruProvider`, `PayAtProvider`, `EasyPayProvider` API-ready interfaces (stubs with manual fallback)
- Webhook framework: `POST /api/v1/webhooks/{provider_code}`
- Provider configuration UI at `/admin/providers`

### Migration

```bash
cd backend && alembic upgrade head
python -m app.seed
```

## Phase 3 — Operations & Mobile (v3.0.0)

### Mukuru Operations Module
- `MukuruBatch`, `MukuruBatchItem`, `MukuruSettlement` models
- Batch approval workflow: create → approve → submit → reconcile
- Admin UI: `/admin/mukuru` (export history, reconciliation dashboard)

### Payment Collection Integration Layer
- Complete Pay@ and EasyPay provider architecture with voucher/barcode generation
- Webhook handlers update payment references and transfer status
- Settlement reconciliation per provider

### Treasury Dashboard
- `/admin/treasury` — funds collected, pending, paid out, liabilities, revenue

### Settlement Dashboard
- `/admin/settlement` — Pay@, EasyPay, EFT collections, Mukuru payouts, variance reporting

### WhatsApp Notifications
- Provider abstraction (`ConsoleWhatsAppProvider`, `TwilioWhatsAppProvider` placeholder)
- WhatsApp templates for transfer lifecycle events
- Delivery logs via existing `notification_logs`

### React Native Mobile App (Phase 11)
- Production Expo app in `mobile/` — auth, dashboard, KYC, beneficiaries, transfers, referrals, wallet
- Stack: React Native, Expo SDK 52, TypeScript, React Query, Axios, Zustand, Secure Store
- Builds: `npm run build:android` / `npm run build:ios` (EAS)
- See [mobile/README.md](mobile/README.md) and [mobile/docs/DEPLOYMENT.md](mobile/docs/DEPLOYMENT.md)

### Operations Audit Trail
- `operations_audit_logs` — batch, settlement, treasury, provider actions
- Admin UI: `/admin/operations-audit`

### Migration

```bash
cd backend && alembic upgrade head
python -m app.seed
```

## Phase 4 — Partner-Ready Platform (v4.0.0)

### Real-Time Transfer Tracking
- `TransferTrackingEvent` model + live tracking API
- `GET /transfers/{id}/tracking` and SSE stream at `/tracking/stream`
- Frontend `LiveTransferTracking` component with 4s polling

### Customer Wallet Profile (No Stored Funds)
- Activity summary only — `GET /api/v1/wallet/profile`
- UI: `/dashboard/wallet`

### FX Engine
- Rate source abstraction (`ManualRateSource`, `ApiRateSource` placeholder)
- Markup rules via `FxMarkupRule` — integrated into `calculate_transfer_amounts`
- Admin: `GET/POST /admin/fx/sources`, `GET/POST /admin/fx/markup`

### Retail Payment Network Layer
- Unified `RetailPaymentNetwork` for Pay@, EasyPay, Kazang, Flash, Shoprite, Pick n Pay
- Wired into payment provider registry

### Mukuru Connector Architecture
- `MukuruProvider` interface, `MockMukuruProvider`, `LiveMukuruProvider`

### Expanded Beneficiaries
- Types: mobile money (MTN/Telecel/AirtelTigo Ghana), bank account, cash pickup
- Validation per type in `BeneficiaryCreate` schema

### Agent Portal
- Role: `agent` — dashboard, commissions, referrals
- UI: `/agent` | Seed: `agent@transafrik.co.za`

### Founder Executive Dashboard
- Aggregates collections, transfers, revenue, compliance, treasury, agents
- UI: `/admin/founder` | Seed: `founder@ipaygo.co.za`

### Migration

```bash
cd backend && alembic upgrade head
python -m app.seed
```

All v3.0.0 `/api/v1` endpoints remain backward compatible.

## Phase 5 — Multi-Corridor Fintech Platform (v5.0.0)

### Provider Orchestration Layer
- `app/services/provider_router.py` — configuration-driven routing by corridor, cost, priority
- Unified `OrchestrationProvider` interface: `quote()`, `create_transfer()`, `get_status()`, `cancel_transfer()`, `reconcile()`
- Supports Mukuru, Flutterwave, Veengu, Onafriq, EasyPay, PayAt

### Multi-Corridor Engine
- `Corridor` model with provider assignment, fee/FX rules
- Seeded corridors: ZA → GH, ZW, ZM, KE, NG, UG
- Admin UI: `/admin/corridors`

### Live FX Feed Engine
- Feed providers: ExchangeRate-API, CurrencyLayer, OpenExchangeRates
- Hourly sync, fallback logic, historical snapshots (`FxRateSnapshot`, `FxSyncRun`)
- Admin UI: `/admin/fx-sources`

### Customer Referral Program
- Referral codes, reward points, discount vouchers
- Customer UI: `/dashboard/referrals` | API: `GET /api/v1/referrals/dashboard`

### WhatsApp Self-Service Bot
- Menu: track transfer, voucher, beneficiary status, payment instructions, support
- Transports: Twilio, Meta Cloud API, Infobip (console fallback)
- Webhook: `POST /api/v1/whatsapp/webhook/{transport}`

### Document & Compliance Center
- Categories: FICA, KYC, CIPC, Tax, Bank Confirmation, Partner/Mukuru/Flutterwave docs
- Upload, versioning, expiry, audit trail
- Admin UI: `/admin/documents`

### White-Label Multi-Tenant Foundation
- `Tenant` model — brand, domain, theme colors
- API: `GET /api/v1/tenant/brand`

### Board & Investor Dashboard
- Monthly volume, revenue, customers, agents, compliance, corridors, providers, referral growth
- Admin UI: `/admin/board`

### API Hardening
- API key management, provider secrets vault, request signing, security monitoring
- Admin: `GET/POST /admin/api-keys`, `POST /admin/provider-secrets`

### Production Operations Center
- Provider health, queue status, webhook/FX/settlement failures
- Admin UI: `/admin/operations`

### Migration

```bash
cd backend && alembic upgrade head
python -m app.seed
```

All v4.0.0 `/api/v1` endpoints remain backward compatible. Mobile app uses the same `/api/v1` base URL.

## Phase 6 — Pilot Launch Readiness (v6.0.0)

### Pilot Mode
- Invite-only registration with `invite_code` on `/auth/register`
- Pilot customer approval workflow, transfer/daily/monthly/corridor limits
- Admin: `/admin/pilot` | Customer: `/dashboard/pilot`
- Demo invite: `PILOTDEMO2026` (seed)

### Production Deployment Readiness
- `validate_production_config()` — secrets, CORS, HTTPS, docs, dev endpoints
- `HttpsEnforcementMiddleware` for production
- Scripts: `backend/scripts/backup_db.ps1`, `restore_db.ps1`, `migration_safety.py`

### Compliance Pack Generator
- PDF packs: KYC summary, transfer audit, payment proof, AML review, Mukuru batch, partner onboarding
- `POST /api/v1/admin/compliance-packs/generate`

### Live Provider Credential Setup
- Validate credentials, health checks, webhook/signature testing on `/admin/providers`
- Supports Mukuru, Flutterwave, Pay@, EasyPay, Veengu, Onafriq

### Operations Runbook
- Admin UI: `/admin/runbook` — transfer processing, payment verify, compliance, Mukuru batch, settlement, failures

### Demo Mode
- Safe investor/partner demos with no-real-money warnings
- Admin: `/admin/demo` — customer, admin, agent, founder journeys

### Legal Pages
- `/legal/terms`, `/privacy`, `/popia`, `/aml-fica`, `/refund`, `/complaints`, `/partner-disclaimer`
- API: `GET /api/v1/legal/pages/{slug}`

### Support Operations (Enhanced)
- SLA tracking, priority levels, transfer-linked tickets, escalation queue, WhatsApp handoff
- Admin: `/admin/support/escalations`, `/admin/support/sla-breaches`

### Launch Checklist
- `/admin/launch-checklist` — provider creds, legal docs, compliance, pilot customers, payments, backup, security

### Migration

```bash
cd backend && alembic upgrade head
python -m app.seed
```

All prior `/api/v1` endpoints remain backward compatible.

## Phase 6.1 — Production Integration Infrastructure (v6.1.0)

### Provider Credential Vault
- Fernet-encrypted credentials in `provider_secrets` (reversible, keyed by `SECRET_KEY`)
- Sandbox/production switching via `ProviderConfig.is_sandbox` + `ApiEnvironment`
- Admin vault API: `GET/POST /api/v1/admin/vault/credentials`, `POST /api/v1/admin/vault/validate/{provider}`

### Live Webhook Security
- HMAC-SHA256 verification with `X-Signature` header
- Replay protection via `X-Webhook-Timestamp` + `X-Webhook-Nonce` (Redis)
- Idempotency on `external_id` (Redis + DB dedup)
- Optional webhook queue in Redis

### S3 Storage Layer
- `STORAGE_BACKEND=local|s3` — KYC, payment proofs, compliance packs, document center
- MinIO included in `docker-compose.staging.yml`

### Redis Layer
- Rate limiting, OTP storage, webhook queues, JWT session blacklist on logout
- In-memory fallback when `REDIS_URL` is unset (dev/tests)

### Notification Providers
- Email: SMTP, SendGrid, AWS SES
- SMS: Console, Africa's Talking, Twilio
- WhatsApp: Console, Twilio (configure via env vars)

### Integration Test Harness
- `backend/tests/harness/` — provider, webhook, settlement simulators
- `backend/tests/test_phase61_*.py`

### Staging Deployment

```bash
docker compose -f docker-compose.staging.yml up --build
```

- Services: PostgreSQL, Redis, MinIO (S3), backend, frontend, nginx reverse proxy
- Health: `GET /health` reports database, Redis, and storage status
- SSL: see `deploy/nginx/ssl/README.md` and `deploy/nginx/nginx-ssl.conf.example`

### Migration

```bash
cd backend && alembic upgrade head
```

## TODO — Future Integrations

### Payment Collection APIs

- [ ] **Pay@** — live voucher generation and payment confirmation webhooks
- [ ] **EasyPay** — live reference API and retailer settlement
- [ ] **Stitch** — instant EFT payment initiation and callbacks
- [ ] **Ozow** — instant EFT integration
- [ ] **Peach Payments / PayFast** — card payment gateway

### Remittance Provider APIs

- [ ] **Mukuru API** — replace manual batch with OAuth and real-time submission
- [ ] **Veengu** — mobile money aggregation
- [ ] **Onafriq** — cross-border payment rails
- [ ] **Flutterwave** — disbursement integration

### Infrastructure

- [x] S3-compatible file storage abstraction (MinIO/AWS S3) — Phase 6.1
- [x] Real email providers (SendGrid/SES/SMTP) — Phase 6.1
- [x] SMS providers (Africa's Talking / Twilio) — Phase 6.1
- [x] Webhook security (HMAC, replay, idempotency) — Phase 6.1
- [x] Redis for token blacklisting, OTP, rate limiting, webhook queue — Phase 6.1
- [x] CI/CD pipeline (GitHub Actions)
- [x] Staging deployment (Docker + nginx) — Phase 6.1
- [ ] POPIA consent management and data export/deletion endpoints
- [ ] Enhanced AML rules engine with configurable thresholds
- [x] Real-time FX rate feeds (Phase 5 — placeholder adapters, configure API keys)
- [x] Multi-corridor support beyond ZAR→GHS (Phase 5)

### Compliance

- [ ] FIC reporting integration
- [ ] Sanctions screening (OFAC/UN lists)
- [ ] Transaction monitoring dashboard for compliance officers
- [ ] Automated SAR (Suspicious Activity Report) generation

## License

Proprietary — IPAYGO (Pty) Ltd. All rights reserved.
