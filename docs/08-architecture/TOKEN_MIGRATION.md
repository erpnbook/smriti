---
Document ID: "SMRITI-ARCH-007"
Title: "SMRITI UI Midnight Token Migration Blueprint"
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

# SMRITI Token Migration — Phase 1 (Repair)

Status: **Phase 1 complete.** Phase 2 (Consolidate) and Phase 3 (Enforce)
not yet started — see roadmap at the end of this document.

## Why this document exists

A static audit of `public/css/*.css` found that the project's own
"single source of truth" token file (`smriti_tokens.css`) was silently
broken, and that 17+ CSS custom properties were referenced via `var()`
somewhere in the app but defined nowhere. This document is the permanent
record of what was wrong, what changed, and what is still pending — so
the next person (human or agent) editing these files doesn't have to
rediscover any of this from scratch.

**Rule going forward:** when in doubt about what a token's canonical
name should be, grep the repo for actual usage first. Do not invent a
"better" name and assume it's canonical — verify it against every call
site. (We got this wrong once during this exact repair — see
"Self-correction" below — and only caught it by running the validator
against the fix instead of trusting the first draft.)

---

## What was actually broken

### 1. Duplicate `:root` content in `smriti_tokens.css`
The file contained 30 CSS custom properties declared **twice** at the
same nesting level, with different values each time (e.g.
`--smriti-color-bg-page` was `#e8ecf2` at line 48 and `#f8fafc` at line
163). Per the CSS spec, the second declaration silently wins — so every
property in the first, fully-commented "Neumorphic Hybrid" block was
dead code that no page ever actually rendered with.

### 2. Corrupted Z-Index section
Mid-file, the comment header for the Z-Index token section was mangled
into invalid Unicode bytes, and the `--smriti-z-index-*` declarations
that should have followed it were missing entirely — likely lost during
a botched edit that was never caught before commit.

### 3. 17 orphaned `var()` references (no fallback)
Confirmed via static cross-reference of every `var(--smriti-*)` usage
against every `--smriti-*` definition across all 20 files in
`public/css/`. Each of these silently drops the declaration it's used
in (the browser treats an undefined-custom-property-with-no-fallback
as invalid and ignores the whole rule):

| Token | Used in | Effect when undefined |
|---|---|---|
| `--smriti-sidebar-width` | `smriti_sidebar.css` (5 call sites) | Sidebar collapse/expand does not resize the content area — visible gap/overlap on every toggle |
| `--smriti-sidebar-collapsed-width` | `smriti_sidebar.css` (3 call sites) | Same as above |
| `--smriti-color-bg-overlay` | `smriti_sidebar.css` (backdrop) | Modal/sidebar backdrop renders with zero darkening tint (blur still applies, tint doesn't) |
| `--smriti-t-base` | `smriti-backup.css`, `smriti-billing.css`, `smriti-inventory.css`, `smriti-purchase.css`, `smriti-reports.css`, `smriti-sizewise-item.css`, `smriti_sidebar_standalone.css` (30+ call sites total) | Transition duration silently absent → hover/interaction states snap instead of animating |
| `--smriti-ease` | same files as above | Transition easing curve silently absent |
| `--smriti-t-fast` | `smriti-backup.css`, `smriti-reports.css` | Same class of issue, fast-tier transitions |
| `--smriti-z-index-toast` | `smriti-backup.css` | Toast z-index declaration invalid; toast may render behind other fixed-position elements |
| `--smriti-shadow-pos-floating` | `smriti-sizewise-invoice.css` (×2) | POS card glow/floating shadow effect missing |

### 4. Un-prefixed tokens violating the file's own governance rule
`smriti_tokens.css` states: *"All tokens MUST use the approved
namespace: `--smriti-{category}-{name}`."* Yet `smriti_theme.css`
defined `--ease`, `--t-fast`, `--t-base`, `--t-slow`, `--radius-lg`,
etc. without the prefix — a different naming generation from before the
governance rule existed, never migrated.

### 5. Two independently-styled "billing" UIs (architectural, not just CSS — not resolved in Phase 1, see below)
`www/billing.html` (standalone web route) and `page/smriti_billing/`
(registered Frappe Desk Page, roles: `SMRITI Store Manager`, `SMRITI
Cashier`) load two different stylesheets built against two different
token generations (`public/css/smriti-billing.css` uses the new
namespaced tokens; `page/smriti_billing/smriti_billing.css` uses the
old short-name tokens and hardcoded pixel values). Both routes are live
and reachable by the same user roles.

---

## What changed in this pass

### `smriti_tokens.css` — fully rewritten
- Single `:root` block. No duplicate declarations (validated
  mechanically — see `validate_tokens.py`).
- All 17 previously-orphaned tokens now have a real definition.
- Z-Index tokens restored, matching the values already correctly
  defined (but never loaded by any page) in `smriti-ui-hardening.css`.
- Legacy compatibility aliases added for every old short-name token
  (`--smriti-bg`, `--radius-lg`, `--smriti-text`, etc.) so existing
  component CSS that references them keeps rendering unmodified during
  the migration window — same pattern already used correctly in
  `smriti-ui-hardening.css`, just never extended to this file.

### Self-correction made during this pass (kept here so it isn't repeated)
The first draft of this fix named the transition tokens
`--smriti-transition-ease` / `--smriti-transition-base` / etc.,
reasoning that this was the "proper" canonical form per the governance
naming pattern. Running the validator against that draft caught dozens
of remaining errors — because the actual call sites across 7 files all
use `var(--smriti-t-base)` / `var(--smriti-ease)` directly, not the
invented name. **Canonical names were corrected to match real usage**:
`--smriti-ease`, `--smriti-t-fast`, `--smriti-t-base`, `--smriti-t-slow`.
Lesson: a token's "canonical" name is whatever the majority of live
call sites already use, not whatever looks most consistent on paper.

### `validate_tokens.py` — new
A script (see file for full docstring) that mechanically catches the
exact three failure classes found above:
1. Duplicate `:root` blocks in one file
2. The same custom property declared twice in one block
3. `var(--token)` with no fallback where `--token` is undefined
   anywhere in the scanned files

Run it as: `python3 validate_tokens.py path/to/public/css`. Exit code 1
on any error — wire into CI per Phase 3 below.

It also emits (non-blocking) warnings for `var(--token, fallback)`
usages where `--token` is undefined but has a fallback — these are
often intentional white-label override hooks (confirmed several real
examples of this in `smriti_branding.css`), but worth a human glance
since a typo'd token name with a fallback fails *silently* in the same
way, just always taking the fallback path instead of erroring.

---

## What did NOT change in this pass (intentionally — see Phase 2/3 below)

- **No visual redesign.** All canonical values were preserved exactly
  as they were in the (correctly-resolving half of the) original file.
- **The billing duplication is not resolved.** This is an architecture
  decision (which UI is canonical: Desk Page or standalone route?), not
  a token-naming problem, and shouldn't be collapsed into a CSS-only
  fix. See Phase 2.
- **`smriti_theme.css`'s un-prefixed tokens were not removed**, only
  aliased. Removing them outright would be a breaking change for any
  component CSS still written against the old names — that's Phase 2/3
  work, done deliberately and with a deprecation window, not as a side
  effect of fixing the corrupted file.
- **`page/smriti_billing/smriti_billing.css`'s old token usage was not
  touched.** It still works (its tokens are independently defined in
  `smriti_theme.css`'s legacy block), it's just visually inconsistent
  with the standalone billing page. Fixing the inconsistency requires
  the architecture decision above first.

---

## Roadmap

### Phase 1 — Repair ✅ (this document)
- [x] Single canonical `:root` in `smriti_tokens.css`
- [x] Restore missing Z-Index and other orphaned tokens
- [x] Eliminate undefined no-fallback variables
- [x] Provide a mechanical validator

### Phase 2 — Consolidate (not started)
- [ ] **Decision needed:** is Billing primarily a Desk workflow or a
      standalone web workflow? Pick one as canonical; the other becomes
      a thin wrapper/redirect (see decision tree discussed when this
      issue was raised).
- [ ] Once decided, remove the non-canonical billing CSS file.
- [ ] Migrate `smriti_theme.css`'s remaining un-prefixed tokens
      (`--smriti-bg`, `--radius-lg`, etc.) so new code never has a
      reason to reach for the legacy alias.
- [ ] Audit `page/` directory more broadly for other Desk-page /
      standalone-page pairs with the same divergence pattern found in
      billing (sizewise invoice, inventory, purchase, reports, shift,
      etc. all have a `page/` AND a `public/css/` stylesheet — this
      audit only confirmed divergence for billing specifically; the
      others have not yet been diffed).

### Phase 3 — Enforce (not started)
- [ ] Wire `validate_tokens.py` into CI; block merges on exit code 1.
- [ ] Extend the validator (or add a second one) to catch the Jinja
      class of bug found separately in this audit — e.g.
      `frappe.user_roles` used in a template where a real list-typed
      context variable was assumed but a module/function object was
      actually exposed. This is a different language (Jinja/Python,
      not CSS) but the same root pathology: a value of one type
      silently mistaken for another, undetected until runtime. A
      lightweight route-smoke-test (load every `www/*.html` route under
      a couple of role contexts, assert no 500) would catch this class
      cheaply.
- [ ] Add a pre-commit hook (`tools/git-hooks/` already exists in this
      repo) that runs the validator on changed `.css` files only, for
      fast local feedback before CI.

### Phase 4 — Document (not started until Phase 1–3 are stable)
- [ ] `DESIGN_SYSTEM.md` (draft included alongside this file — but
      treat it as a draft pending Phase 2/3 completion, since
      documenting an unenforced system just adds a confident-sounding
      claim that isn't backed by anything yet).
