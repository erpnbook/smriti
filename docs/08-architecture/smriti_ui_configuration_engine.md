---
Document ID: "ARCH-027"
Title: "SMRITI UI Configuration Engine — Governance Document v1.4"
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

# SMRITI UI Configuration Engine — Governance Document v1.4
**Date**: 2026-06-24
**Audit Execution**: AITDL
**Audit Owner**: Jawahar R. Mallah, Founder & Chief Architect, AITDL
**Final Approval Authority**: Founder Review Required

---

> [!IMPORTANT]
> **THEME GOVERNANCE STATUS**
>
> `SMRITI_THEME_ARCHITECTURE_VERSION = 1.4`
> `SMRITI_THEME_GOVERNANCE_ACTIVE = TRUE`
> `SMRITI_THEME_CHANGE_FREEZE = TRUE`
>
> **Theme Sprint Status:**
> - THEME-001 Governance Foundation — COMPLETE
> - THEME-002 Theme Preview Framework — COMPLETE
> - THEME-003 Density Token Adoption — COMPLETE
> - THEME-004 Theme Switching Framework — COMPLETE
> - THEME-005 Global Default Theme Migration — COMPLETE
>
> **Phase 2 Roadmap (Founder Decision — 2026-06-24):**
> - THEME-006 Theme Analytics — ⏸️ DEFERRED
> - THEME-007 Accessibility Audit — ✅ KEEP
> - THEME-008 Minimalist Completion — ❌ CANCELLED (no validated business use case)
> - THEME-009 Store-Level Theme Defaults — 🟡 POST-PILOT
>
> **Modification Policy:**
> Any changes to theme architecture, resolver hierarchy, token governance, or default theme behavior require:
> 1. Architecture Impact Assessment
> 2. Theme Compliance Scan
> 3. Founder Approval

---

> [!NOTE]
> **SMRITI Architecture Principle #01 — Business Value Before Visual Variety**
>
> *Retail customer does not buy themes.*
> *Retail customer buys speed, accuracy, inventory visibility,*
> *billing efficiency, profitability, and business intelligence.*
>
> UI investments must demonstrate measurable business value
> before introducing new visual customization.
>
> — Jawahar R. Mallah, Founder & Chief Architect, AITDL

---

> [!NOTE]
> **SMRITI Architecture Principle #02 — Revenue Before Refinement**
>
> When choosing between a business capability and a visual enhancement,
> priority shall be given to the business capability unless the visual
> enhancement demonstrates measurable impact on:
> - Revenue
> - Conversion
> - Productivity
> - Compliance
> - User Error Reduction
>
> Visual polish is valuable. Business outcomes take precedence.
>
> — Jawahar R. Mallah, Founder & Chief Architect, AITDL

---

## Engine Overview

The SMRITI UI Configuration Engine is a **deterministic 7-level token resolver** built as a self-contained JavaScript IIFE. It resolves all UI configuration tokens (colors, spacing, density, typography) at runtime through a priority hierarchy and injects them into `:root` CSS variables.

### Files

| File | Purpose | Version |
|------|---------|---------|
| [`smriti_ui_resolver.js`](../../apps/smriti_retail_os/smriti_retail_os/public/js/smriti_ui_resolver.js) | 7-Level resolver engine | v1.4.0 |
| [`smriti_theme_manager.js`](../../apps/smriti_retail_os/smriti_retail_os/public/js/smriti_theme_manager.js) | Public switching API | v1.1.0 |
| [`smriti_sidebar.js`](../../apps/smriti_retail_os/smriti_retail_os/public/js/smriti_sidebar.js) | SPA sidebar pills | v1.9.2 |
| [`smriti_sidebar_standalone.js`](../../apps/smriti_retail_os/smriti_retail_os/public/js/smriti_sidebar_standalone.js) | Standalone sidebar pills | v1.9.2 |
| [`smriti_tokens.css`](../../apps/smriti_retail_os/smriti_retail_os/public/css/smriti_tokens.css) | CSS token declarations | v1.3 |

---

## 7-Level Resolution Hierarchy

Tokens are resolved lowest → highest priority. Higher levels override lower levels.

```
Level 7 (lowest)  SYSTEM_DEFAULT_TOKENS      Platform-neutral base values
Level 6           _readStoreDefault()         Store-wide theme (window.SMRITI_SITE_CONFIG)
Level 5           _readRoleDefault()          Role-based overrides (window.SMRITI_USER_ROLES)
Level 4           _readUserThemePreference()  User's stored theme (localStorage)
Level 3           _readUserModuleOverride()   Per-page user pref [Phase 2, reserved]
Level 2           _readSessionOverride()      URL ?theme= param (session only)
Level 1 (highest) _readAccessibilityLayer()   WCAG: high-contrast, motion-reduce
```

> [!NOTE]
> `SYSTEM_DEFAULT_TOKENS` is intentionally **not the place to change the theme default**.
> The theme default is controlled via `DEFAULT_THEME_PROFILE` (Level 4 fallback).

---

## DEFAULT_THEME_PROFILE

```javascript
var DEFAULT_THEME_PROFILE = "sleek-compact";   /* THEME-005 — Founder Approved 2026-06-24 */
```

**Location**: `smriti_ui_resolver.js`, immediately after `global.SMRITI = global.SMRITI || {};`

**Purpose**: Controls the out-of-box theme for new users (no `localStorage` preference stored).

**Single Source of Truth**: Exposed via `SMRITI.getDefaultTheme()` so all consumers read the same value.

| Scenario | Behaviour |
|----------|-----------|
| New user (no localStorage) | Receives `DEFAULT_THEME_PROFILE` = `sleek-compact` |
| Existing user with stored pref | localStorage value wins — default is **never reached** |
| Rollback | Change value to `"hybrid-light"`, redeploy assets (no bench restart) |

---

## Public API

```javascript
// Get the platform default theme key
SMRITI.getDefaultTheme()                    // → "sleek-compact"

// Get the currently active theme for the current user
SMRITI.getCurrentTheme()                    // → "sleek-compact" | "hybrid-light" | ...

// Switch theme in real-time (no page reload)
SMRITI.switchTheme("sleek-compact")        // persists to localStorage + re-runs resolver

// Get full resolved token map for current user
SMRITI.getResolvedUIConfig()               // → { "--smriti-table-row-height": "32px", ... }

// Apply a token config to :root
SMRITI.applyUIConfig(config)               // injects into #smriti-ui-engine-tokens style tag
```

---

## Theme Profiles

All 4 profiles are **permanent**. No profile may be removed without Founder approval.

| Profile Key | Row Height | Padding-Y | Toolbar | Bg Page | Status |
|-------------|-----------|-----------|---------|---------|--------|
| `hybrid-light` | 44px | 10px | 56px | `#e8ecf2` | 🟡 Legacy / Fallback — preserved |
| `hybrid-dark` | 44px | 10px | 56px | `#0f0f13` | ✅ Active — preserved |
| `sleek-compact` | **32px** | **6px** | **40px** | `#f1f4f8` | ✅ **Default** — Active |
| `minimalist` | 36px | 8px | 44px | `#ffffff` | ❌ Retained in code — THEME-008 CANCELLED |

---

## Theme Roadmap

| ID | Name | Status | Founder Decision |
|----|------|--------|------------------|
| THEME-001 | Governance Foundation | ✅ COMPLETE | — |
| THEME-002 | Theme Preview Framework | ✅ COMPLETE | — |
| THEME-003 | Density Token Adoption | ✅ COMPLETE | — |
| THEME-004 | Theme Switching Framework | ✅ COMPLETE | — |
| THEME-005 | Global Default → `sleek-compact` | ✅ COMPLETE | 2026-06-24 |
| THEME-006 | Theme Analytics | ⏸️ DEFERRED | No immediate business value |
| THEME-007 | Accessibility Audit (WCAG) | ✅ KEEP | Compliance requirement |
| THEME-008 | Minimalist Profile Completion | ❌ CANCELLED | No validated business use case |
| THEME-009 | Store-Level Theme Defaults | 🟡 POST-PILOT | Activate after field validation |

---

## Product Priority Direction (Founder — 2026-06-24)

```
NEW_THEME_DEVELOPMENT       = OFF
BUSINESS_CAPABILITY_DEVELOPMENT = ON

Priority 1 → PSV Commercialization
Priority 2 → PDT
Priority 3 → CGE
Priority 4 → Sales Force Management

Themes     → Maintenance Only
```

> Theme system is stable, governed, documented, and default-selected.
> All future engineering bandwidth goes to revenue-generating capabilities.

---

## Architecture Principles (Frozen)

**Principle #01 — Business Value Before Visual Variety**
> Retail customer does not buy themes. Retail customer buys speed, accuracy, inventory visibility, billing efficiency, profitability, and business intelligence. UI investments must demonstrate measurable business value before introducing new visual customization.

1. **Theme selection layer controls defaults** — never `SYSTEM_DEFAULT_TOKENS`
2. **`DEFAULT_THEME_PROFILE` is the single source of truth** — read via `SMRITI.getDefaultTheme()`
3. **User preferences are always honoured** — `localStorage` wins over every default
4. **All retained profiles are permanent** — `hybrid-light`, `hybrid-dark`, `sleek-compact` preserved; `minimalist` retained in code but not developed further
5. **Resolver is decoupled from `frappe.boot`** — works on all standalone www pages
6. **CSS injection only via `#smriti-ui-engine-tokens`** — no direct style mutations
7. **Public API is the contract** — components use `SMRITI.*` methods, not resolver internals

---

## Rollback Procedure

```bash
# 1. Edit smriti_ui_resolver.js — change one line:
#    var DEFAULT_THEME_PROFILE = "hybrid-light";

# 2. Deploy to assets (no bench restart needed)
docker cp smriti_ui_resolver.js smriti_retail-backend-1:/home/frappe/frappe-bench/sites/assets/smriti_retail_os/js/smriti_ui_resolver.js

# 3. Clear website cache
docker exec smriti_retail-backend-1 bench --site smriti_retail clear-website-cache

# 4. Bump version in HTML files (force browser cache refresh)
#    smriti_ui_resolver.js?v=X.X.X → bump patch version
```

> [!NOTE]
> No DB migration. No localStorage migration. No DocType changes. Existing user preferences survive rollback unchanged.

---

## Verification Commands

```javascript
// Verify default for new users
localStorage.removeItem('smriti-theme-style');
SMRITI.getCurrentTheme();   // → "sleek-compact"

// Verify existing user pref preserved
localStorage.setItem('smriti-theme-style', 'hybrid-dark');
SMRITI.getCurrentTheme();   // → "hybrid-dark" (default not applied)

// Verify getDefaultTheme API
SMRITI.getDefaultTheme();   // → "sleek-compact"
```

---

## Phase 2 Placeholders (Reserved)

- **Level 3** (`_readUserModuleOverride`): Per-page theme override for individual modules (e.g., POS always uses `hybrid-light` regardless of user preference)
- **`window.SMRITI_SITE_CONFIG`**: Server-injected store defaults (replaces frappe.boot at Level 6)
- **`window.SMRITI_USER_ROLES`**: Server-injected role list (replaces frappe.user_roles at Level 5)

---

## SMRITI_DOCUMENT_GOVERNANCE_RULE_001

> [!WARNING]
> **Platform-Wide Document Governance Rule**
> `Rule ID: SMRITI_DOCUMENT_GOVERNANCE_RULE_001`
> `Effective: 2026-06-24`
> `Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL`
>
> **0-byte documentation files are treated as missing artifacts.**
>
> Placeholder files may exist during active development.
> Before any readiness review gate — commercialization, pilot, architecture, or release:
>
> ```
> File exists + 0 bytes  = FAIL (same as file not existing)
> File exists + content  = eligible for review
> ```
>
> Applies to all SMRITI modules without exception:
> PSV, CGE, PDT, SFM, Inventory, Billing, Themes, and all future modules.
>
> Rationale: A 0-byte file appears as existing in audit inventory scans,
> creating false confidence that documentation is complete when it is not.
> This rule prevents silent gaps from passing governance gates.
>
> Enforcement: Any audit script or readiness checklist must verify
> file size greater than 0, not just file existence.

---

## SMRITI_DOCUMENT_GOVERNANCE_RULE_002

> [!WARNING]
> **Platform-Wide Module Lifecycle Rule**
> `Rule ID: SMRITI_GOVERNANCE_RULE_002`
> `Effective: 2026-06-24`
> `Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL`

**No module may enter unlimited documentation expansion.**

Every SMRITI module follows one lifecycle — in order, without skipping:

```
BUILD
  → AUDIT
    → COMMERCIALIZATION
      → PILOT
        → REALITY
```

**After `PILOT_EXECUTION_MODE = ON`:**

New documentation for that module requires evidence of pilot need.

```
ALLOWED after pilot starts:
  Fix: documentation gap discovered during pilot execution
  Add: content specifically requested by pilot customer
  Update: content contradicted by real pilot data

NOT ALLOWED after pilot starts:
  New documents not connected to active pilot needs
  Speculative improvements to existing documentation
  Features not yet tested by a real user
```

**Rationale**: This session demonstrated the risk.
A theme audit evolved into 12 commercialization documents — correctly.
Without this rule, 12 documents could evolve into 30 — incorrectly.
The rule prevents the "build more" instinct from overriding the "observe reality" imperative.

**Applies to**: PSV (active), CGE, PDT, SFM, and all future SMRITI modules.

**Exception process**: Founder approval required to add documentation
after `PILOT_EXECUTION_MODE = ON` for any module.

---

*Governance Approved: Jawahar R. Mallah — Founder & Chief Architect, AITDL*
*"Always decision-ready."*




## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |