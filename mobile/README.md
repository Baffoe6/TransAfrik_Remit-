# TransAfrik Remit — Flutter Mobile App

Customer mobile scaffold for TransAfrik Remit (API v3.0.0).

## Features

- Authentication (JWT)
- Customer profile
- KYC document status
- Beneficiaries list
- Transfers list and detail
- Payment voucher display (QR + barcode data)
- Transfer tracking timeline

## Setup

```bash
cd mobile
flutter pub get
flutter run --dart-define=API_URL=http://localhost:8000/api/v1
```

For Android emulator, default API URL is `http://10.0.2.2:8000/api/v1`.

## Demo Account

| Email | Password |
|-------|----------|
| customer@demo.co.za | Customer@TransAfrik2024! |

> TransAfrik is a facilitation platform operated by IPAYGO (Pty) Ltd — not a licensed bank or remittance operator.
