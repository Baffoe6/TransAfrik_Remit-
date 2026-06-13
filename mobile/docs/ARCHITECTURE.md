# TransAfrik Mobile — Architecture

## System Context

```mermaid
flowchart TB
    subgraph clients [Client Applications]
        WEB[Next.js Web App<br/>app.ipaygo.co.za]
        MOB[React Native App<br/>Expo SDK 52]
    end

    subgraph api [Backend API]
        FAST[FastAPI<br/>api.ipaygo.co.za]
        AUTH[Auth Service<br/>JWT + OTP + Device Trust]
        KYC[KYC Service]
        TXN[Transfer Engine]
        PART[Partner Abstraction<br/>Flutterwave · Mukuru · Onafriq · Veengu]
    end

    subgraph infra [Infrastructure]
        PG[(PostgreSQL)]
        REDIS[(Redis)]
        S3[Object Storage]
    end

    WEB --> FAST
    MOB --> FAST
    FAST --> AUTH
    FAST --> KYC
    FAST --> TXN
    TXN --> PART
    FAST --> PG
    AUTH --> REDIS
    KYC --> S3
```

---

## Mobile App Layers

```mermaid
flowchart TB
    subgraph presentation [Presentation Layer]
        SCREENS[Screens<br/>auth · dashboard · beneficiaries · transfers · kyc · profile]
        NAV[Navigation<br/>AuthNavigator · MainNavigator]
        UI[Components<br/>ui.tsx]
    end

    subgraph state [State Layer]
        ZS[Zustand Stores<br/>authStore · themeStore]
        RQ[React Query<br/>server cache + staleTime]
        OFF[Offline Cache<br/>AsyncStorage dashboard]
    end

    subgraph data [Data Layer]
        API[API Modules<br/>auth · dashboard · beneficiaries · transfers · wallet]
        CLIENT[Axios Client<br/>JWT interceptors + refresh]
    end

    subgraph platform [Platform Services]
        SEC[Expo Secure Store<br/>tokens]
        DEV[Device Service<br/>fingerprint + trust payload]
        BIO[Biometric Service<br/>Face ID / fingerprint]
        PUSH[Notification Service<br/>push stub]
    end

    subgraph external [External]
        BE[https://api.ipaygo.co.za/api/v1]
    end

    SCREENS --> NAV
    SCREENS --> UI
    SCREENS --> ZS
    SCREENS --> RQ
    RQ --> API
    ZS --> API
    API --> CLIENT
    CLIENT --> SEC
    CLIENT --> DEV
    CLIENT --> BE
    SCREENS --> OFF
    SCREENS --> BIO
    SCREENS --> PUSH
```

---

## Navigation Structure

```mermaid
flowchart LR
    APP[App.tsx] --> AUTH{Authenticated?}
    AUTH -->|No| AN[AuthNavigator]
    AUTH -->|Yes| MN[MainNavigator]

    AN --> LOGIN[LoginScreen]
    AN --> REG[RegisterScreen]
    AN --> OTP[OtpLoginScreen]
    AN --> FP[ForgotPasswordScreen]

    MN --> TABS[Bottom Tabs]
    MN --> STACK[Stack Screens]

    TABS --> DASH[Dashboard]
    TABS --> TXLIST[Transfers]
    TABS --> BEN[Beneficiaries]
    TABS --> PROF[Profile]

    STACK --> KYC[KycScreen]
    STACK --> WAL[WalletScreen]
    STACK --> REF[ReferralScreen]
    STACK --> TXD[TransferDetail]
    STACK --> TXC[CreateTransfer]
    STACK --> BENF[BeneficiaryForm]
```

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant S as Mobile Screen
    participant ST as authStore
    participant C as apiClient
    participant B as Backend API

    U->>S: Enter credentials
    S->>C: POST /auth/login + device payload
    C->>B: Authenticate
    alt Success
        B-->>C: access_token + refresh_token
        C-->>ST: Store tokens (Secure Store)
        ST-->>S: Navigate to MainNavigator
    else Step-up required
        B-->>C: step_up_required + mobile
        S->>C: POST /auth/login/step-up
        C->>B: Verify OTP
        B-->>C: tokens
    else MFA required
        B-->>C: mfa_required
        S->>U: Prompt for MFA code
    end

    Note over C,B: 401 responses trigger automatic token refresh via /auth/refresh
```

---

## Directory Structure

```
mobile/
├── app.json              # Expo config (icons, permissions, bundle IDs)
├── eas.json              # EAS build profiles
├── index.ts              # Entry point
├── src/
│   ├── App.tsx           # Root: QueryClient, auth bootstrap, navigation
│   ├── api/
│   │   ├── client.ts     # Axios instance + JWT refresh interceptor
│   │   ├── auth.ts       # Login, register, OTP, password reset
│   │   ├── dashboard.ts  # GET /dashboard/summary
│   │   ├── beneficiaries.ts
│   │   ├── transfers.ts
│   │   └── wallet.ts
│   ├── components/ui.tsx # Button, Input, Card, Screen, etc.
│   ├── features/partners.ts  # Future partner SDK registry
│   ├── navigation/
│   │   ├── AuthNavigator.tsx
│   │   └── MainNavigator.tsx
│   ├── screens/          # Feature screens by domain
│   ├── services/
│   │   ├── secureStorage.ts
│   │   ├── device.ts
│   │   ├── offlineCache.ts
│   │   ├── biometric.ts
│   │   └── notifications.ts
│   ├── store/
│   │   ├── authStore.ts
│   │   └── themeStore.ts
│   └── types/index.ts    # User, Beneficiary, Transfer, KYC, Corridor
└── __tests__/            # Jest unit tests
```

---

## Shared TypeScript Models

| Model | Backend alignment | Mobile usage |
|-------|-------------------|--------------|
| `User` | `users` table | Auth, profile |
| `Beneficiary` | `beneficiaries` | CRUD screens |
| `Transfer` | `transfers` | Create, list, detail |
| `TransferDetail` | Transfer + timeline | Receipt screen |
| `KycDocument` | `kyc_documents` | Upload screen |
| `DashboardSummary` | `/dashboard/summary` | Home screen |
| `Corridor` | `corridors` | Transfer creation |
| `TokenResponse` | Auth responses | Login flows |

---

## API Endpoints Used

| Module | Endpoints |
|--------|-----------|
| Auth | `/auth/register`, `/auth/login`, `/auth/login/otp`, `/auth/otp/send`, `/auth/login/step-up`, `/auth/password/forgot`, `/auth/password/reset`, `/auth/me`, `/auth/logout` |
| Dashboard | `/dashboard/summary` |
| Beneficiaries | `/beneficiaries` CRUD |
| Transfers | `/transfers`, `/transfers/calculate`, `/transfers/{id}`, `/transfers/{id}/timeline` |
| KYC | `/kyc/documents`, `/kyc/upload` |
| Wallet | `/wallet/profile` |
| Referrals | `/referrals/dashboard` |

Base URL: `EXPO_PUBLIC_API_URL` → `https://api.ipaygo.co.za` (appends `/api/v1` in client).

---

## Security

- **Tokens:** Stored in Expo Secure Store (encrypted on-device)
- **Device trust:** Fingerprint hash sent with login requests
- **Token refresh:** Automatic via Axios interceptor on 401
- **Biometrics:** Local auth service ready; not yet primary login method
- **Permissions:** Camera (KYC selfie), photo library (document upload)

---

*See also: [README.md](../README.md) · [EAS_BUILD.md](./EAS_BUILD.md) · [DEPLOYMENT.md](./DEPLOYMENT.md)*
