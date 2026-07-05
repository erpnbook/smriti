---
Document ID: "SMRITI-ARCH-004"
Title: "SMRITI Design System"
Owner: "UI/UX Team"
Audience: "Frontend Developer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-07-04"
Last Reviewed: "2026-07-04"
AI Generated: "No"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Design System

> **Status: draft.** Phase 1 (token repair) is complete and validated.
> Phases 2–3 (consolidation, enforcement) are not yet done — see
> `TOKEN_MIGRATION.md`. This document describes the system as it is
> intended to work once those phases land; where the live code doesn't
> yet match, that's called out explicitly rather than glossed over.

This document has one job: explain **how to use** the existing token
vocabulary, and **what the brand means**, without redefining either.
The token names are fixed by `smriti_tokens.css` (the only source of
truth). This file does not introduce new tokens.

---

## The four layers

```
Layer 4 — Brand Philosophy     "Enterprise Intelligence with Retail Simplicity"
              ↓
Layer 3 — Design Rules         Navy builds trust. Blue guides decisions.
                                Green signals positive outcomes.
                                Warning/Danger are operational, not brand.
              ↓
Layer 2 — Semantic Tokens      --smriti-color-brand-primary
                                --smriti-color-status-success
                                --smriti-spacing-lg, --smriti-radius-md, ...
              ↓
Layer 1 — Raw Values           #6941c6, 16px, 14px, ...
```

Philosophy lives at the top. Engineering lives at the bottom. **They
are not mixed**: nobody should ever need to introduce a new CSS custom
property to express a brand idea. If the existing token vocabulary
can't say what you mean, that's a Layer 2 gap to raise — not a license
to invent a Layer-4-flavored token name (`--smriti-foundation-navy`,
etc.). That mistake is exactly how the project ended up with three
overlapping naming generations before this repair.

---

## Brand semantics vs. UI semantics

These are two different systems, and conflating them was the original
mistake in an earlier draft of this design philosophy. They coexist at
different levels:

**Brand semantics** (marketing-level — describe these in prose, not in
new variable names):
- Navy → Stability / Trust — used for large structural surfaces:
  sidebar, header, login, landing pages.
- Blue → Intelligence — used when the system is actively helping:
  insights, analytics, AI suggestions, forecasts. Not decorative.
- Green → Growth — reserved for genuinely positive business outcomes:
  profit, sales growth, recovered inventory, healthy stock, ROI.

**UI semantics** (interaction states — these are the actual tokens,
already defined, do not rename):
- `--smriti-color-status-success` (green) → a successful operation
- `--smriti-color-status-warning` (amber) → needs attention
- `--smriti-color-status-danger` (red) → an error or blocking state
- `--smriti-color-status-info` (blue) → general informational message

**The rule for resolving conflicts:** a transactional UI state (a
toast confirming a save, a validation error) always uses the UI
semantic token for that state, even when it happens to be the same hue
as a brand-semantic color elsewhere on the page. A success toast is
green because it succeeded, not because green means "growth" in that
context. Don't let the brand story override what a status color is
telling the cashier in the moment — operational clarity wins.

---

## How to use the token system (Layer 2 reference)

All values come from `smriti_tokens.css`. Component CSS must consume
`var(--smriti-*)` — never a hardcoded hex/rgb/rgba/hsl value, and never
a bare un-prefixed name in new code.

### Color
| Token | Use for |
|---|---|
| `--smriti-color-bg-page` | Page background |
| `--smriti-color-bg-primary` | Card / panel surface |
| `--smriti-color-bg-secondary` | Elevated secondary surface |
| `--smriti-color-bg-elevated` | Card-on-card / popover surface |
| `--smriti-color-bg-overlay` | Modal & sidebar backdrop tint |
| `--smriti-color-text-primary` / `-muted` / `-subtle` | Text emphasis tiers |
| `--smriti-color-brand-primary` / `-light` / `-dark` | Brand purple/navy family |
| `--smriti-color-brand-accent` | Secondary brand accent (POS highlight cards) |
| `--smriti-color-border-default` / `-strong` | Border weight tiers |
| `--smriti-color-status-{success,warning,danger,info}` (+ `-bg`, `-border`, `-rgb` variants) | UI semantic states — see above |

### Spacing, radius, shadow, type
Use the existing `--smriti-spacing-*`, `--smriti-radius-*`,
`--smriti-shadow-*`, `--smriti-font-*` scales as defined. Don't
introduce a one-off pixel value in component CSS where a scale step
already exists — that's how `page/smriti_billing/smriti_billing.css`
ended up with hardcoded `20px`/`15px`/`12px` instead of
`var(--smriti-spacing-xl)`/`var(--smriti-spacing-lg)`/`var(--smriti-spacing-md)`,
diverging visually from the standalone billing page that uses the
scale correctly.

### Transitions
`--smriti-ease`, `--smriti-t-fast` (0.12s), `--smriti-t-base` (0.20s),
`--smriti-t-slow` (0.35s). Note these are **not** namespaced as
`--smriti-transition-*` despite the general `--smriti-{category}-{name}`
convention — see `TOKEN_MIGRATION.md`'s "Self-correction" note for why:
30+ existing call sites already use this exact form, and matching real
usage took priority over naming purity.

### Z-Index
Use the named tier, never a raw number: `--smriti-z-index-content` (1)
→ `-card` (10) → `-sticky` (100) → `-topbar` (200) → `-dropdown` (5000)
→ `-modal` (10000) → `-notification` / `-toast` (15000) →
`-devtools` (99999). These tiers are deliberately spaced widely apart
so a future addition can slot between existing tiers without a
renumbering cascade.

---

## Glassmorphism / neumorphism — use with intent, not by default

The codebase contains both a glassmorphic treatment
(`backdrop-filter: blur()`, frosted borders) and a neumorphic shadow
system (`--smriti-shadow-neu-float`, `--smriti-shadow-neu-pressed`).
These are visually striking but have real costs:

- **Performance**: `backdrop-filter: blur()` is expensive to composite
  and can visibly lag on lower-end POS terminal hardware — exactly the
  device class this product runs on at the register.
- **Contrast risk**: text over a blurred, semi-transparent surface can
  fail contrast checks that the same text over a flat surface would
  pass. No contrast audit has been done on the glass surfaces yet.

**Guidance until that audit happens:** prefer flat `--smriti-color-bg-*`
surfaces for anything on the critical path of a transaction (billing
cart, payment confirmation, manager PIN entry). Reserve glass/neu
treatments for lower-stakes, lower-frequency screens (dashboards,
settings, marketing-facing pages like pricing/ROI calculator) where a
dropped frame or a contrast edge case is a cosmetic issue, not a
checkout-blocking one.

---

## Governance

```
✓ One canonical token file (smriti_tokens.css)
✓ No duplicate :root blocks
✓ No undefined CSS variables (no var() without either a real
  definition or an intentional fallback)
✓ No hardcoded colors in component CSS
✓ No duplicate component CSS for the same feature (billing currently
  violates this — tracked in TOKEN_MIGRATION.md Phase 2)
✓ No page-local token definitions
✓ Theme/token validation in CI (validate_tokens.py — not yet wired in,
  tracked in TOKEN_MIGRATION.md Phase 3)
```

**The technical debt was never the color choices.** It was the absence
of enforcement — nothing stopped a duplicate `:root` block or an
orphaned variable from shipping, because nothing checked. These rules
exist to make that structurally harder, not to relitigate which blue is
the right blue.

---

## The API Stability Rule

Once a canonical token name is published, it is considered part of the public UI API.

Existing token names may be aliased, deprecated, or removed according to the migration policy, but should not be renamed casually.

Brand evolution should occur through documentation and theme profiles, not through renaming canonical tokens.
