# TransAfrik Remit — Mobile Design System v2

Premium fintech design language aligned with Wise, Remitly, Revolut, and modern African fintech apps.

---

## 1. Brand Principles

| Principle | Expression |
|-----------|------------|
| **Trust** | Green palette, shield icons, compliance badges, partner disclaimers |
| **Simplicity** | One primary action per screen, progressive send flow |
| **Speed** | Quick actions, skeleton loaders, offline cache |
| **Mobile-first** | Native tab bar, bottom sheets pattern, thumb-zone CTAs |
| **Premium** | Elevated cards, gradient heroes, refined typography |

---

## 2. Color Tokens

### Brand palette (`theme/colors.ts`)

| Token | Light | Usage |
|-------|-------|-------|
| `primary` | `#1B5E3B` | CTAs, active states, icons |
| `primaryDark` | `#0A2E1C` | Hero gradients |
| `accent` | `#C9A227` | Gold CTAs, highlights |
| `bg` | `#F7FAF8` | Screen background |
| `surface` | `#FFFFFF` | Cards, inputs |
| `text` | `#111827` | Headings, amounts |
| `textSecondary` | `#6B7280` | Subtitles, metadata |

### Dark mode

| Token | Dark | Notes |
|-------|------|-------|
| `bg` | `#060E0A` | Deep green-black |
| `surface` | `#122018` | Elevated cards |
| `primary` | `#3DB87A` | Brighter for contrast |

### Semantic colors

- `success` / `successBg` — completed transfers, KYC approved
- `warning` / `warningBg` — pending, offline banner
- `error` / `errorBg` — failures, rejections
- `info` / `infoBg` — in-progress states

---

## 3. Typography (`theme/typography.ts`)

| Style | Size | Weight | Use |
|-------|------|--------|-----|
| `display` | 34 | 800 | Hero amounts |
| `displaySm` | 28 | 800 | Screen titles (hero) |
| `h1` | 26 | 700 | Screen titles |
| `h2` | 20 | 700 | Section headers |
| `h3` | 17 | 600 | Card titles |
| `body` | 16 | 400 | Body copy |
| `caption` | 13 | 400 | Metadata |
| `label` | 12 | 600 | Uppercase labels |
| `amount` | 40 | 800 | Money displays |
| `tab` | 11 | 600 | Tab bar labels |

---

## 4. Spacing & Radius (`theme/spacing.ts`)

**Spacing:** `xs(4)` · `sm(8)` · `md(12)` · `lg(16)` · `xl(24)` · `xxl(32)` · `xxxl(48)`

**Radius:** `sm(8)` · `md(12)` · `lg(16)` · `xl(24)` · `full(999)`

---

## 5. Shadows (`theme/shadows.ts`)

| Level | Use |
|-------|-----|
| `sm` | Chips, small elements |
| `md` | Cards, list items |
| `lg` | Hero cards, modals |
| `xl` | Floating actions |

---

## 6. Component Library (`components/fintech/`)

| Component | Purpose |
|-----------|---------|
| `FintechCard` | Elevated/muted/hero card variants |
| `HeroHeader` | Gradient header with greeting |
| `AmountDisplay` | Large money typography |
| `Avatar` | Initials / flag avatars |
| `ListItem` | Native list row with chevron |
| `QuickActionGrid` | Horizontal action shortcuts |
| `SearchBar` | Filled search input |
| `FilterChips` | Activity filters |
| `Timeline` | Transfer tracking steps |
| `ProgressBar` | KYC progress |
| `StatusPill` | Status badges |
| `TrustBadge` | Hero trust indicators |
| `SectionHeader` | Section title + action |

### Feedback components (`components/Feedback.tsx`)

- `Skeleton` / `SkeletonCard` / `SkeletonList` — animated shimmer
- `EmptyState` — icon + CTA (no emoji clutter)
- `ErrorState` — retry pattern
- `OfflineBanner` — cached data indicator

---

## 7. UI Architecture

```
App.tsx
├── AuthNavigator (unauthenticated)
│   ├── Onboarding
│   ├── Login / Register / OTP
│   └── Forgot Password
└── MainNavigator (authenticated)
    ├── Tabs (headerless)
    │   ├── Home — dashboard + quick actions
    │   ├── Send — corridor intro
    │   ├── Beneficiaries — recipients
    │   ├── Activity — transfer history
    │   └── Profile — settings hub
    └── Stack (modal flows)
        ├── SendFlow (5 steps)
        ├── PaymentSuccess
        ├── TransferTracking
        ├── Receipt
        ├── Kyc
        └── Profile sub-screens
```

---

## 8. Screen Hierarchy

```
Home
├── Quick Send → SendFlow
├── KYC → Kyc
├── Activity → Tabs/Activity
├── Transfer detail → TransferTracking
└── Recipients → Tabs/Beneficiaries

Send (tab)
└── SendFlow → PaymentSuccess → TransferTracking

Activity (tab)
├── TransferTracking
└── Receipt

Profile (tab)
├── EditProfile
├── Security / Biometrics
├── Kyc / Referral / Notifications / Support
└── Dark mode toggle
```

---

## 9. Dark Mode

Controlled via `themeStore` (`light` | `dark` | `system`). Profile screen includes toggle. All components use `useAppTheme()` — no hardcoded `#fff` backgrounds on screens.

---

## 10. File Map

```
mobile/src/
├── theme/
│   ├── colors.ts      # Semantic themes
│   ├── typography.ts  # Type scale
│   ├── spacing.ts     # Layout tokens
│   ├── shadows.ts     # Elevation
│   ├── tokens.ts      # Brand constants
│   └── index.ts       # useAppTheme()
├── components/
│   ├── fintech/       # Premium component library
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Feedback.tsx
│   └── Screen.tsx
└── features/          # Screen implementations
```

---

## 11. Do / Don't

**Do**
- Use `FintechCard` for grouped content
- Use `AmountDisplay` for money
- Use `ListItem` for tappable rows
- Use `HeroHeader` for tab home screens
- Show skeletons while loading

**Don't**
- Use emoji as tab icons
- Use bordered web-style full-width inputs without fill
- Stack multiple primary buttons
- Hardcode `#F8FAF9` — use `theme.bg`
- Use green header bars on tab screens (headerless tabs)
