---
Document ID: "ARCH-030"
Title: "SMRITI UI Profile Registry"
Owner: "Architecture Team"
Audience: "Architect"
Module: "Core"
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

# SMRITI UI Profile Registry

**Status:** FROZEN  
**Version:** 1.0  
**Effective:** 2026-06-18  
**Authority:** AITDL / PrathamOne  
**Repo Path:** `docs/architecture/ui/ui_profile_registry.md`  
**Parent Spec:** `docs/architecture/ui/SMRITI_UI_CONFIGURATION_ENGINE_V1.md`  
**Modification Policy:** Any addition, removal, or rename of a profile identifier requires Architecture Change Proposal (ACP) approval. No silent reinterpretation.  
**Lifecycle:** FROZEN — implementation may begin; profile names may not change without ACP.

---

## Registry Authority

This document is the single source of truth for all profile identifiers used
in the SMRITI UI Configuration Engine.

Governance rule:

```
Conversation ≠ Specification
Repository Document = Specification
```

Profile names implemented in `smriti_ui_resolver.js` MUST exactly match the identifiers
listed in this document. Any deviation is a governance violation requiring ACP.

---

## Theme Profile Registry

Theme profiles control the visual appearance of color surfaces, shadows, and depth.

| Identifier | Description | Status |
|---|---|---|
| `hybrid` | Default — Neumorphic clay light mode. System Default theme. | ✅ ACTIVE |
| `minimalist` | Flat minimal light mode. Reduced shadows, cleaner borders. | ✅ ACTIVE |
| `dark` | Full dark mode. Deep backgrounds, light text. | ✅ ACTIVE |
| `pos-dark` | POS terminal forced dark. Compact spacing, no neumorphic shadows. | ✅ ACTIVE |

### Usage Notes

- `hybrid` is the system fallback. If no preference is stored, `hybrid` resolves.
- `hybrid` and `minimalist` are user-selectable via `localStorage["smriti-theme-style"]`.
- `dark` is applied when `body[data-theme="dark"]` or `body.dark-mode` is detected.
- `pos-dark` is applied by System Module Policy (Level 2) when `pathname === "/billing"`.
- `pos-dark` is also applied by Terminal Policy (Level 1) when `terminal_type === "pos"`.

### localStorage Values

The existing live key for user theme preference is:

```
Key:   smriti-theme-style
Values: "hybrid" | "minimalist"
```

These values map directly to Theme Profile identifiers. No alias translation occurs.

---

## Experience Profile Registry

Experience profiles control spacing density and typography scale.

| Identifier | Description | Status |
|---|---|---|
| `standard` | Default spacing and typography. No token overrides. | ✅ ACTIVE |
| `compact` | Reduced padding, smaller font sizes. Applied to Cashier role by default. | ✅ ACTIVE |
| `comfortable` | Increased padding and font sizes. For accessibility or large-display use. | ✅ ACTIVE |

### Usage Notes

- `standard` is the system fallback experience profile.
- `compact` is applied automatically by Role Default (Level 5) for `SMRITI Cashier` role.
- `comfortable` is available for Store Default (Level 6) and future user override (Level 3, Phase 2).

---

## Brand Profile Registry

Brand profiles control brand-specific color overrides for white-label deployments.

| Identifier | Description | Status |
|---|---|---|
| `smriti` | Default SMRITI brand. No token overrides — inherits system defaults. | ✅ ACTIVE |
| `whitelabel` | White-label override. Populated from `frappe.boot.smriti_site_config.brand_overrides`. | ✅ ACTIVE |

### Usage Notes

- `smriti` is the system default brand profile. All standard deployments use this.
- `whitelabel` is reserved for future OEM/partner deployments. Token values are
  injected at boot time from site configuration. In Phase 1, `whitelabel` has no
  overrides and behaves identically to `smriti`.

---

## Profile Identity Governance

### Naming Convention (FROZEN)

Profile identifiers are lowercase, hyphen-separated, no underscores, no camelCase:

```
✅ hybrid
✅ pos-dark
✅ whitelabel
❌ posDAark
❌ pos_dark
❌ RetailStandard
```

### Forbidden Operations (Without ACP)

The following operations on this registry require ACP before implementation:

```
Adding a new profile identifier
Removing an existing profile identifier
Renaming an existing profile identifier
Changing the default fallback of any profile type
```

### Resolver Conformance Rule

The keys in `smriti_ui_resolver.js` must exactly match this registry:

```javascript
// REQUIRED — resolver must use exactly these keys:
var _THEME_PROFILES      = { "hybrid": {...}, "minimalist": {...}, "dark": {...}, "pos-dark": {...} };
var _EXPERIENCE_PROFILES = { "standard": {...}, "compact": {...}, "comfortable": {...} };
var _BRAND_PROFILES      = { "smriti": {...}, "whitelabel": {...} };
```

Any key present in the resolver but absent from this document is a registry violation.
Any key present in this document but absent from the resolver is an implementation gap.

---

## Conformance Verification (Phase 1A)

Verified against `smriti_ui_resolver.js` commit `e824aad`:

| Registry | Document | Resolver | Match |
|---|---|---|---|
| Theme: `hybrid` | ✅ | ✅ | ✅ MATCH |
| Theme: `minimalist` | ✅ | ✅ | ✅ MATCH |
| Theme: `dark` | ✅ | ✅ | ✅ MATCH |
| Theme: `pos-dark` | ✅ | ✅ | ✅ MATCH |
| Experience: `standard` | ✅ | ✅ | ✅ MATCH |
| Experience: `compact` | ✅ | ✅ | ✅ MATCH |
| Experience: `comfortable` | ✅ | ✅ | ✅ MATCH |
| Brand: `smriti` | ✅ | ✅ | ✅ MATCH |
| Brand: `whitelabel` | ✅ | ✅ | ✅ MATCH |

**Conformance Status: 9/9 PASS**

---

## Why These Names Were Chosen

Profile names were frozen from the existing live system, not from discussion artifacts.

The SMRITI live deployment already uses:

```
localStorage["smriti-theme-style"] = "hybrid" | "minimalist"
```

These are deployed values on production-equivalent systems. Changing them would require:
- Migration code
- Alias mapping
- localStorage compatibility layer
- Testing of existing user preferences

With zero functional benefit in Phase 1.

Names like `retail-standard`, `retail-dark`, `executive`, `warehouse`, `touch`
appeared in architecture discussion history but were **never committed to the repository**.
Per SMRITI governance:

```
Conversation ≠ Specification
Repository Document = Specification
```

Those names were therefore not implemented and are not part of this registry.

---

## Sign-off

| Item | Status |
|---|---|
| Theme profiles (4) | ✅ FROZEN |
| Experience profiles (3) | ✅ FROZEN |
| Brand profiles (2) | ✅ FROZEN |
| Naming convention | ✅ FROZEN |
| Resolver conformance verified | ✅ 9/9 PASS |
| ACP requirement stated | ✅ |
| localStorage compatibility confirmed | ✅ |
| Discussion-only names excluded | ✅ |

```
ui_profile_registry.md

Registry Status  : FROZEN
Governance Gate  : PASSED
Phase 1A         : COMPLETE
Implementation Gate (Phase 1B) : OPEN
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