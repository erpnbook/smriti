---
Document ID: "ARCH-028"
Title: "SMRITI UI Configuration Engine V1"
Owner: "Architecture Team"
Audience: "Architect"
Module: "PSV"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI UI Configuration Engine V1

**Status:** FROZEN  
**Version:** 1.0  
**Effective:** 2026-06-18  
**Authority:** AITDL / PrathamOne  
**Repo Path:** `docs/architecture/ui/SMRITI_UI_CONFIGURATION_ENGINE_V1.md`  
**Modification Policy:** Any change to this document requires Architecture Change Proposal (ACP) approval. No silent reinterpretation during implementation.  
**Lifecycle:** DRAFT → REVIEW → LOCKED → FROZEN. FROZEN means implementation may begin; no functional changes permitted; only typo/clarity corrections allowed without ACP.

---

## 1. Purpose and Scope

This document defines the UI Configuration Engine for SMRITI Retail OS — the centralized system that resolves visual appearance, experience profiles, and brand identity for every UI surface in the application.

The engine governs:
- How UI tokens (colors, spacing, typography, radius, shadow, z-index) are resolved
- The precedence hierarchy when multiple configuration sources conflict
- The boundary between resolver internals and component-visible contracts
- Phase 1 implementation scope and enforcement strategy

This engine does NOT govern:
- Business logic
- Data access patterns
- Routing (governed by AITDL.md § Routing Governance)
- Licensing enforcement logic (governed by SMRITI_LICENSE_ARCHITECTURE_V1.md)

---

## 2. Stack Constraints (LOCKED)

SMRITI Retail OS operates on:

```
Backend:   Frappe Framework + Python
Frontend:  Vanilla JavaScript (ES6+)
Markup:    HTML (Frappe www/ pages)
Styling:   Vanilla CSS (CSS Custom Properties / Variables)
```

The following are FORBIDDEN in this engine:

```
TypeScript
React
Vue
Angular
Any npm build pipeline
Context Providers
Hooks (useUIConfiguration, useTheme, etc.)
src/core/* directory structures
```

All engine files must fit the existing Frappe public asset structure:

```
public/js/*.js
public/css/*.css
```

---

## 3. Resolver Hierarchy

The UI Configuration Engine applies a **deterministic 7-level resolver hierarchy**.
Higher levels override lower levels. The resolver evaluates all levels on every call
and returns a single merged token map.

```
Level 1 (Highest)  Terminal Policy
                   ↓ overrides all below
Level 2            System Module Policy
                   ↓
Level 3            User Module Override
                   ↓
Level 4            User Theme Preference
                   ↓
Level 5            Role Default
                   ↓
Level 6            Store Default
                   ↓
Level 7 (Lowest)   System Default
```

### Level Definitions

| Level | Source | Example |
|---|---|---|
| Terminal Policy | Hardcoded per terminal type (POS, kiosk, mobile) | POS always dark, cannot be overridden |
| System Module Policy | Module-level forced overrides (e.g., billing forces dark mode) | `/billing` always uses `theme-pos-dark` |
| User Module Override | User's saved preference for a specific module | User set inventory to light |
| User Theme Preference | User's global theme preference | User selected Hybrid |
| Role Default | Default theme for a role (e.g., Cashier → compact) | SMRITI Cashier → compact experience |
| Store Default | Store-level configuration set in Config Portal | Store chose minimalist |
| System Default | Base fallback — Hybrid Neumorphic, full experience | Installed default |

### Hierarchy Rule

```
If Level 1 returns a value for token X → use it. Stop.
If Level 2 returns a value for token X → use it. Stop.
...
If no level returns a value for token X → use System Default.
```

The hierarchy is evaluated independently per token. A terminal policy can override
`--smriti-color-bg-primary` while leaving `--smriti-spacing-padding-y` resolved
from the Store Default.

**The hierarchy order is frozen. It cannot be modified without ACP.**

---

## 4. Accessibility Override Precedence

Accessibility overrides sit **above the full resolver hierarchy** — they are applied
as a post-resolution layer, not as a resolver level.

```
Resolver Output (Levels 1–7)
         ↓
Accessibility Override Layer   ← applied last, cannot be suppressed
         ↓
Final Token Map → Component
```

### Accessibility Override Rules

| Trigger | Effect |
|---|---|
| `prefers-contrast: more` (OS/browser) | Force high-contrast border and text tokens |
| `prefers-reduced-motion: reduce` | Set all transition/animation tokens to `0ms` or `none` |
| `prefers-color-scheme: dark` (OS) | Apply dark mode tokens unless Terminal Policy explicitly blocks |
| User-set `smriti-a11y-high-contrast: true` in Frappe User Preferences | Force `--smriti-color-border` ≥ 3:1 contrast ratio |
| User-set `smriti-a11y-reduced-motion: true` | Same as `prefers-reduced-motion` |

### Rule

Accessibility overrides may never be suppressed by any resolver level, including Terminal Policy.
A terminal policy may specify `theme-pos-dark`, but the accessibility layer still applies
reduced-motion and high-contrast rules on top of it.

---

## 5. License Validation Gate

The UI Configuration Engine checks license state before applying non-default profiles.

```
SMRITI.getResolvedUIConfig()
         ↓
License Gate Check
         ↓
license_status == Active OR Grace Period (feature: UI_THEMES not BLOCKED)
    → Full resolver runs (Levels 1–7)
license_status == Unregistered / Expired / Suspended / Tampered
    → System Default tokens only
    → Theme profile: smriti-default
    → Experience profile: standard
    → Brand profile: smriti
    → No user/role/store overrides applied
```

The license gate does NOT block the UI from rendering. It blocks non-default profile
resolution only. A user with an expired license still sees a functional interface —
but on the System Default theme, with no customization.

License state is read from `frappe.boot.smriti_license` (injected by boot.py).
The resolver never makes a direct API call to check license state — it reads
the boot-time snapshot only.

---

## 6. Token Namespace (FROZEN)

All CSS Custom Properties created by the SMRITI UI Configuration Engine MUST use
the following namespace prefixes. No other prefix is permitted for engine-managed tokens.

```
--smriti-color-*        Color tokens
--smriti-spacing-*      Spacing tokens (padding, margin, gap)
--smriti-radius-*       Border radius tokens
--smriti-shadow-*       Box shadow tokens
--smriti-font-size-*    Typography size tokens
--smriti-font-weight-*  Typography weight tokens
--smriti-z-index-*      Z-index layer tokens
--smriti-dimension-*    Layout dimension tokens (widths, heights, min/max bounds)
```

### Token Registry (Reference)

The canonical token definitions are in:
```
docs/architecture/ui/ui_token_registry.md
```

### Naming Convention Within Namespaces

```
--smriti-color-bg-primary          Background: primary surface
--smriti-color-bg-secondary        Background: secondary / elevated surface
--smriti-color-bg-page             Background: full page / canvas
--smriti-color-text-primary        Text: primary (high emphasis)
--smriti-color-text-muted          Text: secondary (medium emphasis)
--smriti-color-text-subtle         Text: tertiary (low emphasis)
--smriti-color-brand-primary       Brand: primary accent
--smriti-color-brand-light         Brand: lighter accent
--smriti-color-brand-dark          Brand: darker accent
--smriti-color-status-success      Status: success
--smriti-color-status-danger       Status: danger / error
--smriti-color-status-warning      Status: warning
--smriti-color-status-info         Status: informational
--smriti-color-border-default      Border: default
--smriti-color-border-strong       Border: high emphasis

--smriti-spacing-xs                4px
--smriti-spacing-sm                8px
--smriti-spacing-md                12px
--smriti-spacing-lg                16px
--smriti-spacing-xl                24px
--smriti-spacing-2xl               32px
--smriti-spacing-padding-y         Component vertical padding
--smriti-spacing-padding-x         Component horizontal padding
--smriti-spacing-gap               Component gap (flex/grid)

--smriti-radius-xs                 4px
--smriti-radius-sm                 6px
--smriti-radius-md                 10px
--smriti-radius-lg                 14px
--smriti-radius-xl                 18px
--smriti-radius-2xl                24px
--smriti-radius-full               9999px

--smriti-shadow-xs                 Minimal elevation
--smriti-shadow-sm                 Low elevation
--smriti-shadow-md                 Medium elevation
--smriti-shadow-lg                 High elevation
--smriti-shadow-xl                 Maximum elevation
--smriti-shadow-neu-float          Neumorphic: element floats out
--smriti-shadow-neu-pressed        Neumorphic: element pressed in

--smriti-font-size-xs              0.72rem
--smriti-font-size-sm              0.82rem
--smriti-font-size-base            0.95rem
--smriti-font-size-md              1rem
--smriti-font-size-lg              1.15rem
--smriti-font-size-xl              1.35rem
--smriti-font-size-2xl             1.6rem

--smriti-font-weight-regular       400
--smriti-font-weight-medium        500
--smriti-font-weight-semibold      600
--smriti-font-weight-bold          700
--smriti-font-weight-extrabold     800

--smriti-z-index-base              0
--smriti-z-index-dropdown          100
--smriti-z-index-sticky            200
--smriti-z-index-overlay           500
--smriti-z-index-modal             1000
--smriti-z-index-sidebar           1041
--smriti-z-index-toast             1100
--smriti-z-index-tooltip           1200

--smriti-dimension-sidebar-width             260px
--smriti-dimension-sidebar-collapsed-width   68px
```

### Backward Compatibility — Existing `--smriti-*` Tokens

Existing tokens in `smriti_theme.css` using the short `--smriti-bg`, `--smriti-primary`
pattern are NOT removed in Phase 1. The engine writes new `--smriti-color-*` tokens
alongside them. Existing pages consuming the old tokens continue to work.

Migration from old to new tokens is a Phase 2 activity.

### Color Exceptions

The CSS named color keywords `white` and `transparent` are permitted for static light-surface elements, text on high-contrast brand backgrounds (e.g., active tabs, brand primary buttons, and badges), and overlay backgrounds across all theme profiles. All other color overrides must use namespaced SMRITI tokens.

---

## 7. Token/Profile Boundary (FROZEN)

This is the most important governance boundary in the UI Configuration Engine.

### Rule

```
Resolver Layer   → knows and uses profiles internally
Component Layer  → knows and uses tokens ONLY
```

### What Components May Access

```javascript
const ui = SMRITI.getResolvedUIConfig();

// ✅ CORRECT — components access resolved tokens only
ui.tokens["--smriti-color-bg-primary"]
ui.tokens["--smriti-color-text-primary"]
ui.tokens["--smriti-spacing-padding-y"]
ui.tokens["--smriti-radius-md"]
ui.tokens["--smriti-shadow-sm"]
```

### What Components May NEVER Access

```javascript
// ❌ FORBIDDEN — resolver internals, never exposed to components
ui.themeProfile
ui.experienceProfile
ui.brandProfile
```

These three profile names are resolver inputs. They are used inside
`SMRITI.getResolvedUIConfig()` to determine which token values to return.
They are NOT part of the public contract.

### Why This Boundary Exists

If a component checks `ui.themeProfile === "minimalist"` and branches its behavior,
it becomes tightly coupled to the resolver's internal classification.
When the resolver's profile names change, every component that checked profile names
must be updated.

When components only consume tokens, the resolver can change its internal profiles,
add new ones, rename them, or merge them — and components are unaffected.

---

## 8. Vanilla JS Runtime Contract (FROZEN)

### `SMRITI.getResolvedUIConfig()`

Returns the fully resolved UI configuration for the current context.

```javascript
/**
 * Returns the resolved UI configuration for the current page context.
 * Evaluates all 7 resolver levels + accessibility overrides + license gate.
 *
 * @returns {Object} resolved configuration
 * @returns {Object} .tokens  - Map of CSS variable name → resolved value
 *                             Components may ONLY consume .tokens
 * @returns {string} .mode    - "light" | "dark" (for non-token consumers, e.g. SVG icons)
 * @returns {boolean} .reducedMotion - true if reduced motion is active
 */
SMRITI.getResolvedUIConfig = function() { ... };
```

Return shape:

```javascript
{
  tokens: {
    "--smriti-color-bg-primary":    "#ffffff",
    "--smriti-color-text-primary":  "#0f172a",
    "--smriti-spacing-padding-y":   "10px",
    "--smriti-radius-md":           "10px",
    "--smriti-shadow-sm":           "0 1px 3px rgba(15,23,42,.08)",
    // ... all tokens
  },
  mode: "light",              // "light" | "dark"
  reducedMotion: false        // true if accessibility override active
}
```

**What is NOT in the return object:**

```javascript
// These must NEVER appear in the public return contract:
themeProfile        // resolver internal
experienceProfile   // resolver internal
brandProfile        // resolver internal
resolverTrace       // debug only, stripped in production
```

---

### `SMRITI.applyUIConfig(config)`

Writes the resolved token map to the document root as CSS Custom Properties.

```javascript
/**
 * Applies a resolved UI config to the document root (:root).
 * Writes all token values as CSS Custom Properties.
 * Idempotent — safe to call multiple times.
 *
 * @param {Object} config - Output of SMRITI.getResolvedUIConfig()
 */
SMRITI.applyUIConfig = function(config) { ... };
```

Usage:

```javascript
// Standard pattern — resolve and apply
const ui = SMRITI.getResolvedUIConfig();
SMRITI.applyUIConfig(ui);

// After apply, CSS variables are live on :root
// All components that consume var(--smriti-color-bg-primary) update automatically
```

### What Calls These Functions

```
Page initialization  → SMRITI.applyUIConfig(SMRITI.getResolvedUIConfig())
Theme toggle event   → SMRITI.applyUIConfig(SMRITI.getResolvedUIConfig())
Route change         → SMRITI.applyUIConfig(SMRITI.getResolvedUIConfig())
License state change → SMRITI.applyUIConfig(SMRITI.getResolvedUIConfig())
```

### What Does NOT Call These Functions

```
Individual components   → components consume var(--smriti-*) via CSS, not JS
Business logic          → no UI config calls in service/API layers
Backend/Python          → these are client-side functions only
```

---

## 9. Phase 1 Implementation Scope (FROZEN)

### Included in Phase 1

```
docs/architecture/ui/
  SMRITI_UI_CONFIGURATION_ENGINE_V1.md    ← this document
  ui_token_registry.md                    ← full token definitions
  ui_profile_registry.md                  ← approved profile definitions
  ui_governance_checklist.md              ← per-PR governance checklist

public/js/
  smriti_ui_resolver.js                   ← resolver hierarchy + license gate
  smriti_theme_manager.js                 ← SMRITI.getResolvedUIConfig() + applyUIConfig()

public/css/
  smriti_tokens.css                       ← System Default token values (:root)

Scope of CSS migration:
  Billing module inline CSS               ← migrate hardcoded values to token variables
  Shared smriti_theme.css                 ← READ ONLY in Phase 1, do not modify
```

### Excluded from Phase 1

```
inventory.html
purchase.html
barcode.html
reports.html
security.html
configure.html
psv-dashboard.html
All other www/*.html pages (except billing.html)
smriti_theme.css modification
smriti_sidebar.css modification
```

### Phase 1 Governance Rule

**`smriti_theme.css` is READ ONLY in Phase 1.**  
The engine writes new `--smriti-color-*` tokens via `smriti_tokens.css`.  
The existing `--smriti-bg`, `--smriti-primary` tokens remain untouched.  
No existing page is broken by Phase 1 delivery.

---

## 10. Enforcement Strategy

### Layer 1 — Stylelint (CSS files)

Scope: `public/css/*.css`  
Blocks: hex colors, rgb/rgba/hsl literals, hardcoded px spacing, hardcoded radius values  
Trigger: pre-commit hook  
Config: `.stylelintrc` in project root

### Layer 2 — ESLint Custom Rules (JS files)

Scope: `public/js/*.js`  
Blocks: string literals matching hex color pattern (`/#[0-9a-fA-F]{3,6}/`)  
Blocks: hardcoded px values in JS style assignments  
Trigger: pre-commit hook  
Config: `.eslintrc` custom rule `no-hardcoded-style-values`

### Layer 3 — Python Governance Scanner (HTML inline styles)

Scope: `www/*.html` inline `<style>` blocks and `style=""` attributes  
Blocks: hex colors, rgb/rgba/hsl, hardcoded px values not using `var(--smriti-*)`  
Trigger: pre-commit hook (Python script)  
Script: `scripts/smriti_style_governance_scan.py`  
Output: violation count per file, file path, line number

### Enforcement Activation

All three layers activate via a single `pre-commit` configuration.  
No CI pipeline required — enforcement runs locally before every commit.  
The Python scanner is also runnable standalone:

```bash
python scripts/smriti_style_governance_scan.py --scope billing
```

---

## 11. Routing Authority

Per the Architecture Clarification (2026-06-18):

```
SMRITI_ROUTING_ARCHITECTURE.md (dedicated file) does not yet exist.

Temporary Authoritative Routing Architecture:
AITDL.md → Section: Routing Governance

Status: ACTIVE
Until:  docs/architecture/routing/SMRITI_ROUTING_ARCHITECTURE.md is created
        and supersedes the AITDL section.
```

All UI engine route references must comply with AITDL.md Routing Governance.

---

## 12. Files This Engine MUST NOT Touch

The following files are outside the scope of the UI Configuration Engine forever,
unless explicitly approved via ACP:

```
smriti_retail_os/hooks.py
smriti_retail_os/boot.py
Any Python service layer
Any API layer (*.py)
ERPNext DocTypes
Frappe configuration
```

The engine is a pure frontend concern.

---

## 13. Sign-off

| Item | Status |
|---|---|
| Resolver hierarchy (7 levels) | ✅ FROZEN |
| Accessibility override precedence | ✅ FROZEN |
| License validation gate | ✅ FROZEN |
| Token namespace (`--smriti-color-*` etc.) | ✅ FROZEN |
| Token/profile boundary | ✅ FROZEN |
| Vanilla JS runtime contract | ✅ FROZEN |
| Phase 1 scope (Billing + shared tokens) | ✅ FROZEN |
| Enforcement strategy (3-layer) | ✅ FROZEN |
| TypeScript/React forbidden | ✅ FROZEN |
| Routing authority (AITDL.md) | ✅ RESOLVED |
| Backward compatibility (`--smriti-*` tokens) | ✅ FROZEN |

```
SMRITI UI Configuration Engine V1

Architecture Status : FROZEN
Governance Status   : PASSED
Implementation Gate : OPEN (Phase 1)

Ready For:
  ✓ docs/architecture/ui/ document creation
  ✓ public/js/smriti_ui_resolver.js
  ✓ public/js/smriti_theme_manager.js
  ✓ public/css/smriti_tokens.css
  ✓ Billing module CSS token migration
  ✓ 3-layer enforcement setup
```

Governance directive for any AI assistant or automated development tool touching UI configuration code:

```
UI configuration development MUST comply with
docs/architecture/ui/SMRITI_UI_CONFIGURATION_ENGINE_V1.md.

Any deviation requires explicit Architecture Change Proposal (ACP),
not silent reinterpretation during implementation.
```


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL