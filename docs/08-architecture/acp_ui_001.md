---
Document ID: "ARCH-004"
Title: "Architecture Change Proposal (ACP-UI-001)"
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

# Architecture Change Proposal (ACP-UI-001)

**Title:** Dimension Namespace Extension for UI Configuration Engine  
**Proposal ID:** ACP-UI-001  
**Status:** APPROVED ✅  
**Date:** 2026-06-18  
**Author:** Jawahar R. Mallah (Founder & Chief Architect, AITDL)
**Maintainer:** AITDL
**Implementation Assistance:** Automated AI development tools
**Authority:** SMRITI Architecture Committee / PrathamOne  

---

## 1. Context and Problem Statement

The [SMRITI UI Configuration Engine V1](./smriti_ui_configuration_engine_v1.md) (§6) defines a frozen set of approved token namespaces:
- `--smriti-color-*`
- `--smriti-spacing-*` (padding, margin, gap)
- `--smriti-radius-*`
- `--smriti-shadow-*`
- `--smriti-font-size-*`
- `--smriti-font-weight-*`
- `--smriti-z-index-*`

During the Wave 1 cleanup, component-specific dimensions (specifically the sidebar widths of `260px` and `68px`) were refactored using custom properties. While these dimensions were temporarily placed under `--smriti-sidebar-*`, this prefix is outside the approved frozen namespaces. 

Mapping layout dimensions (widths, heights, etc.) to `--smriti-spacing-*` violates the design system semantics, as "spacing" strictly represents margins, paddings, and flex/grid gaps.

---

## 2. Proposed Changes

We propose extending the token namespace by introducing a dedicated layout dimensions prefix:

```css
--smriti-dimension-*      Layout dimension tokens (widths, heights, min/max constraints)
```

The dimension namespace is reserved for structural layout dimensions (width, height, min/max constraints) and must not be used for spacing, padding, margin, or gap values.

### 1. Update to SMRITI_UI_CONFIGURATION_ENGINE_V1.md

Extend section §6 ("Token Namespace") to include:

```markdown
--smriti-dimension-*    Layout dimension tokens
```

And define the initial layout tokens in the registry:
- `--smriti-dimension-sidebar-width`: The standard expanded width of the responsive left sidebar (Default: `260px`).
- `--smriti-dimension-sidebar-collapsed-width`: The collapsed icon-only width of the responsive left sidebar (Default: `68px`).

---

## 3. Impact Analysis

- **Backward Compatibility:** 100% compatible. It adds a new namespace without affecting existing color, spacing, typography, or shadow tokens.
- **Stylelint/Scanner Compliance:** The custom python scanner (`scripts/smriti_style_governance_scan.py`) will be updated (if necessary) to allow `--smriti-dimension-*` without flagging it.
- **Engine Logic:** No runtime JS changes are required in `smriti_ui_resolver.js`, as it dynamically applies all namespaced `--smriti-*` properties written to `:root`.
- **HTML/JS Files:** 0 impact on page rendering or business logic.

---

## 4. Proposed Token Definitions (Registry)

```css
:root {
  --smriti-dimension-sidebar-width: 260px;
  --smriti-dimension-sidebar-collapsed-width: 68px;
}
```
These will be declared at Level 7 default level inside `smriti_tokens.css`.


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