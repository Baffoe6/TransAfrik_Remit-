# TransAfrik Remit — Mobile UI/UX Review

**Review date:** June 2026  
**Version:** 1.0.0-preview (Design System v2)  
**Benchmark:** Wise · Remitly · Sendwave · Revolut · Chipper Cash · Capitec

---

## Executive Summary

The mobile app has been redesigned from a functional MVP into a **premium African fintech experience**. The previous UI exhibited web-app patterns (emoji tab bar, green stack headers on tabs, bordered inputs, flat card stacks). The v2 design system introduces native navigation, a fintech component library, dark mode, and screen-specific UX improvements across all core flows.

**Readiness for store launch:** Design **85%** · Implementation **90%** · Polish **80%**

---

## 1. Before vs After

| Area | Before | After |
|------|--------|-------|
| Tab bar | Emoji icons, green headers | Ionicons, headerless tabs, pill active state |
| Home | Flat gradient + card stack | Hero header, quick actions, sectioned lists |
| Send flow | Basic bordered selects | Selectable cards, hero quote card, review summary |
| KYC | Plain progress bar | Hero progress card, per-doc status, camera/gallery CTAs |
| Beneficiaries | Plain list + star text | Avatar rows, favorites, empty state with CTA |
| Activity | Web-style search + list | Filter chips, card-wrapped rows, status pills |
| Tracking | Dot timeline | Icon header, amount card, native timeline component |
| Receipt | Basic table | Branded header, amount highlights, trust footer |
| Profile | Button list | Avatar hero, grouped menu, dark mode toggle |
| Loading | Static gray boxes | Animated skeleton shimmer |
| Empty states | Emoji | Ionicons in branded circles |

---

## 2. Screen-by-Screen Review

### Home ✅ Premium
- Personalized greeting in gradient hero
- Trust badges (Licensed partners, Encrypted, FICA)
- Quick action grid (Send, Recipients, Verify, Activity, Help)
- KYC status card with clear CTA
- Recent transfers + saved recipients with "See all"
- Refer & earn compact card

### Send Money ✅ Premium
- **Send tab:** Step explainer with icons before starting
- **Send flow:** 5-step wizard with labeled steps, hero quote card, review summary
- Gold primary CTA on send tab; green on flow continue

### KYC ✅ Premium
- Progress hero with status pill
- Per-document cards with completion state
- Clear hints for each document type
- Under-review state messaging

### Beneficiaries ✅ Premium
- Renamed "Recipients" in UI copy
- Search + add CTA above list
- Star favorites with Ionicons
- Avatar initials per recipient

### Activity & Receipts ✅ Premium
- Filter chips (All, Pending, Processing, Completed)
- Card-wrapped transfer rows
- Receipt with branded header and share/download actions

### Transfer Tracking ✅ Premium
- Status icon circle header
- Amount summary card
- Vertical timeline with completion states

### Profile ✅ Premium
- Large avatar + KYC pill
- Grouped settings menu (single card)
- Dark mode toggle
- Sign out with version footer

---

## 3. Design System Deliverables

| Deliverable | Location | Status |
|-------------|----------|--------|
| Design tokens | `src/theme/tokens.ts`, `colors.ts` | ✅ |
| Typography scale | `src/theme/typography.ts` | ✅ |
| Shadow system | `src/theme/shadows.ts` | ✅ |
| Component library | `src/components/fintech/` | ✅ |
| Fintech card system | `FintechCard` variants | ✅ |
| Loading skeletons | `Skeleton`, `SkeletonCard`, `SkeletonList` | ✅ |
| Empty states | `EmptyState` with icons | ✅ |
| Error states | `ErrorState` with retry | ✅ |
| Dark mode | `themeStore` + semantic colors | ✅ |
| Native interactions | Tab bar, list chevrons, active opacity | ✅ |

---

## 4. UI Architecture

See `MOBILE_DESIGN_SYSTEM.md` for full hierarchy.

**Navigation pattern:** Bottom tabs for primary destinations; stack pushes for transactional flows (send, KYC, tracking). Matches Wise/Remitly pattern.

**Information architecture:**
1. **Home** — hub + shortcuts
2. **Send** — intent + flow entry
3. **Recipients** — address book
4. **Activity** — history + receipts
5. **Profile** — account + settings

---

## 5. Remaining Recommendations (Post-v2)

| Priority | Item | Notes |
|----------|------|-------|
| P1 | Auth screens redesign | Login/register still v1 styling |
| P1 | Payment success screen | Add celebration animation |
| P2 | Haptic feedback | On send confirm, success |
| P2 | Bottom sheet for payment method | Remitly-style picker |
| P2 | Rate calculator widget on Home | Live FX from API |
| P3 | Lottie success animations | Store polish |
| P3 | Custom app icon refresh | Match v2 brand |

---

## 6. Store Launch Checklist (Design)

- [x] Native tab navigation (no emoji)
- [x] Dark mode support
- [x] Loading skeletons
- [x] Empty states with CTAs
- [x] Error states with retry
- [x] Premium card system
- [x] Send flow UX
- [x] KYC upload UX
- [x] Transfer tracking timeline
- [x] Receipt screen
- [ ] Auth/onboarding visual pass
- [ ] Splash screen animation
- [ ] App Store screenshots with v2 UI

---

## 7. Conclusion

TransAfrik Remit mobile v2 delivers a **credible premium fintech experience** suitable for pilot App Store and Google Play submission. The design removes web-app affordances and adopts patterns from leading remittance and African fintech apps while retaining the TransAfrik green-and-gold brand identity.

**Next step:** Run `npm run build:android:preview` with v2 UI and capture store screenshots.
