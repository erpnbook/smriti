---
Document ID: "ARCH-018"
Title: "Phase 2A — UI Governance Audit Report"
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

# Phase 2A — UI Governance Audit Report
**SMRITI UI Configuration Engine — Legacy Style & Token Audit**
**Status:** ANALYSIS COMPLETE 🟢
**Date:** 2026-06-18
**Authority:** SMRITI Architecture Committee

---

## 1. Executive Summary

As SMRITI moves into **Phase 2 (UI Governance Cleanup)**, a comprehensive codebase audit was conducted to identify all remaining legacy style declarations, hardcoded colors, spacing, font sizes, border-radii, box-shadows, and inline style attributes.

The goal is to establish a clear roadmap for refactoring these hardcoded values to consume the SMRITI Token Namespace (`--smriti-*`) resolved dynamically by the UI Configuration Engine.

### Core Metrics Summary

| Category | HTML Files (`www/`) | CSS Files (`public/css/`) | JS Files (`public/js/`) | Grand Total |
|---|---|---|---|---|
| **Inline Style Attrs (`style=`)** | 2,179 | 0 | 0 | **2,179** |
| **Hex Colors (`#fff`)** | 1,040 | 270 | 21 | **1,331** |
| **rgb/rgba/hsl Literals** | 1,132 | 369 | 8 | **1,509** |
| **Hardcoded Font Sizes** | 1,688 | 309 | 1 | **1,998** |
| **Hardcoded Border Radii** | 280 | 77 | 0 | **357** |
| **Hardcoded Box Shadows** | 205 | 99 | 1 | **305** |
| **Hardcoded Spacing (px/rem)** | 2,843 | 577 | 6 | **3,426** |
| **Total Violations** | **9,367** | **1,701** | **37** | **11,105** |

---

## 2. File-by-File Violation Counts

### HTML Files Audit (Sorted by Total Violations)

| File | Inline Style Attrs | Hex Colors | rgb/rgba/hsl | Font Size | Border Radius | Box Shadows | Spacing | Total |
|---|---|---|---|---|---|---|---|---|
| `barcode.html` | 275 | 70 | 55 | 151 | 12 | 8 | 230 | **801** |
| `purchase.html` | 136 | 40 | 50 | 81 | 9 | 13 | 141 | **470** |
| `billing.html` | 134 | 25 | 38 | 88 | 13 | 15 | 143 | **456** |
| `platform_center.html` | 113 | 58 | 44 | 67 | 9 | 15 | 112 | **418** |
| `security.html` | 159 | 16 | 39 | 62 | 13 | 3 | 125 | **417** |
| `psv-dashboard.html` | 96 | 17 | 53 | 78 | 11 | 8 | 104 | **367** |
| `reports.html` | 52 | 32 | 39 | 60 | 8 | 1 | 102 | **294** |
| `sales_return.html` | 120 | 16 | 25 | 47 | 2 | 5 | 74 | **289** |
| `sizewise_invoice.html` | 127 | 17 | 4 | 44 | 2 | 0 | 78 | **272** |
| `smriti-help.html` | 54 | 29 | 18 | 46 | 18 | 5 | 80 | **250** |
| `backup.html` | 73 | 18 | 21 | 51 | 2 | 3 | 80 | **248** |
| `suppliers.html` | 68 | 17 | 14 | 46 | 2 | 3 | 87 | **237** |
| `configure.html` | 63 | 29 | 0 | 42 | 10 | 2 | 90 | **236** |
| `item_master.html` | 5 | 33 | 52 | 32 | 18 | 9 | 61 | **210** |
| `supplier_returns.html` | 78 | 16 | 18 | 34 | 2 | 3 | 55 | **206** |
| `sales_invoices.html` | 58 | 20 | 17 | 30 | 2 | 2 | 49 | **178** |
| `sales_orders.html` | 17 | 17 | 24 | 43 | 4 | 5 | 68 | **178** |
| `payments.html` | 30 | 17 | 21 | 43 | 5 | 3 | 51 | **170** |
| `eway_bill.html` | 43 | 16 | 17 | 28 | 4 | 2 | 52 | **162** |
| `smriti-home.html` | 6 | 18 | 31 | 32 | 8 | 4 | 56 | **155** |
| `smriti-license.html` | 25 | 21 | 26 | 38 | 4 | 1 | 39 | **154** |
| `inventory.html` | 34 | 17 | 20 | 30 | 2 | 4 | 43 | **150** |
| `shift.html` | 31 | 18 | 16 | 23 | 4 | 4 | 52 | **148** |
| `setup_wizard.html` | 11 | 19 | 34 | 23 | 7 | 8 | 45 | **147** |
| `psa.html` | 31 | 17 | 17 | 27 | 2 | 3 | 49 | **146** |
| `customers.html` | 31 | 17 | 13 | 25 | 1 | 3 | 51 | **141** |
| `smriti-security-log.html` | 10 | 19 | 13 | 33 | 9 | 5 | 52 | **141** |
| `analytics.html` | 21 | 19 | 18 | 24 | 10 | 1 | 47 | **140** |
| `stock-audit.html` | 24 | 17 | 20 | 19 | 4 | 3 | 40 | **127** |
| `print_templates.html` | 23 | 17 | 19 | 23 | 2 | 3 | 38 | **125** |
| `scheme_creator.html` | 24 | 15 | 22 | 17 | 6 | 3 | 34 | **121** |
| `smriti-go-live.html` | 11 | 13 | 30 | 24 | 13 | 0 | 28 | **119** |
| `purchase_invoice.html` | 23 | 16 | 17 | 20 | 2 | 2 | 35 | **115** |
| `delivery_challan.html` | 20 | 16 | 16 | 20 | 2 | 2 | 35 | **111** |
| `purchase_receipt.html` | 20 | 16 | 16 | 20 | 2 | 2 | 35 | **111** |
| `psv-opening-balance.html` | 19 | 16 | 16 | 17 | 1 | 4 | 36 | **109** |
| `sales-upload.html` | 15 | 17 | 17 | 21 | 2 | 3 | 33 | **108** |
| `category_master.html` | 15 | 15 | 19 | 15 | 5 | 3 | 32 | **104** |
| `psv_reconciliation.html` | 22 | 17 | 14 | 18 | 1 | 2 | 29 | **103** |
| `products.html` | 18 | 17 | 14 | 17 | 2 | 3 | 31 | **102** |
| `psv_exception_analysis.html` | 12 | 16 | 19 | 17 | 2 | 1 | 26 | **93** |
| `brand_master.html` | 12 | 15 | 15 | 14 | 4 | 3 | 28 | **91** |
| `login.html` | 0 | 19 | 29 | 7 | 7 | 7 | 14 | **83** |
| `smriti_support.html` | 6 | 16 | 13 | 16 | 0 | 2 | 30 | **83** |
| `offline.html` | 0 | 16 | 19 | 10 | 9 | 5 | 22 | **81** |
| `smriti-login.html` | 0 | 16 | 28 | 10 | 4 | 5 | 18 | **81** |
| `smriti-coming-soon.html` | 1 | 22 | 1 | 9 | 6 | 1 | 17 | **57** |
| `release_notes.html` | 0 | 14 | 10 | 10 | 2 | 1 | 19 | **56** |
| `403.html` | 0 | 8 | 10 | 7 | 2 | 3 | 9 | **39** |
| `404.html` | 0 | 8 | 10 | 7 | 2 | 3 | 9 | **39** |
| `smriti-403.html` | 0 | 8 | 10 | 7 | 2 | 3 | 9 | **39** |
| `smriti-404.html` | 0 | 8 | 10 | 7 | 2 | 3 | 9 | **39** |
| `smriti-safe.html` | 1 | 14 | 0 | 4 | 3 | 0 | 8 | **30** |
| `sizewise_item.html` | 12 | 0 | 1 | 4 | 0 | 0 | 3 | **20** |

### CSS Files Audit (Sorted by Total Violations)

| File | Hex Colors | rgb/rgba/hsl | Font Size | Border Radius | Box Shadows | Spacing | Total |
|---|---|---|---|---|---|---|---|
| `smriti-sizewise-item.css` | 24 | 75 | 64 | 21 | 15 | 120 | **319** |
| `smriti-sizewise-invoice.css` | 55 | 61 | 63 | 14 | 7 | 100 | **300** |
| `smriti_theme.css` | 65 | 48 | 5 | 0 | 13 | 5 | **136** |
| `smriti_sidebar.css` | 41 | 15 | 17 | 12 | 3 | 42 | **130** |
| `smriti-shift.css` | 10 | 27 | 26 | 1 | 9 | 56 | **129** |
| `smriti-billing.css` | 3 | 29 | 18 | 2 | 11 | 35 | **98** |
| `smriti_sidebar_standalone.css` | 7 | 13 | 16 | 7 | 2 | 38 | **83** |
| `smriti-barcode.css` | 8 | 21 | 15 | 1 | 6 | 29 | **80** |
| `smriti-purchase.css` | 2 | 21 | 15 | 2 | 7 | 31 | **78** |
| `smriti-inventory.css` | 2 | 20 | 14 | 1 | 6 | 28 | **71** |
| `smriti-desk.css` | 0 | 2 | 20 | 0 | 2 | 36 | **60** |
| `smriti_sales_invoice.css` | 25 | 9 | 3 | 7 | 6 | 5 | **55** |
| `smriti-backup.css` | 1 | 12 | 12 | 2 | 7 | 17 | **51** |
| `smriti-reports.css` | 0 | 6 | 12 | 0 | 3 | 25 | **46** |
| `smriti-ui-hardening.css` | 11 | 9 | 3 | 5 | 2 | 4 | **34** |
| `smriti_branding.css` | 9 | 1 | 6 | 2 | 0 | 6 | **24** |
| `smriti_desk_override.css` | 7 | 0 | 0 | 0 | 0 | 0 | **7** |

### JS Files Audit (Sorted by Total Violations)

| File | Hex Colors | rgb/rgba/hsl | Font Size | Border Radius | Box Shadows | Spacing | Total |
|---|---|---|---|---|---|---|---|
| `smriti_sizewise_invoice.js` | 5 | 0 | 1 | 0 | 1 | 1 | **8** |
| `customer.js` | 2 | 4 | 0 | 0 | 0 | 0 | **6** |
| `purchase_order.js` | 6 | 0 | 0 | 0 | 0 | 0 | **6** |
| `supplier.js` | 2 | 4 | 0 | 0 | 0 | 0 | **6** |
| `main.js` | 0 | 0 | 0 | 0 | 0 | 4 | **4** |
| `smriti_billing.js` | 2 | 0 | 0 | 0 | 0 | 0 | **2** |
| `smriti_pwa.js` | 2 | 0 | 0 | 0 | 0 | 0 | **2** |
| `smriti_shift.js` | 2 | 0 | 0 | 0 | 0 | 0 | **2** |
| `smriti_sidebar_standalone.js` | 0 | 0 | 0 | 0 | 0 | 1 | **1** |

---

## 3. Severity Classification

We classify legacy styles under four risk and governance priority levels:

### 1. 🔴 Critical Priority (Must-Fix in Phase 2B / 2C)
*   **Violations:** Raw hex colors (`#6366f1`, `#ef4444`) and `rgb`/`rgba` literals in CSS sheets and HTML `<style>` blocks.
*   **Reason:** Raw color literals completely bypass the theme resolver. A user switching to `pos-dark` or `minimalist` modes will still see hardcoded light-mode background colors, breaking the core feature of the UI Configuration Engine.
*   **Volumetric Count:** ~2,840 instances.

### 2. 🟠 High Priority (Design Alignment)
*   **Violations:** Hardcoded pixel spacing, paddings, margins, border-radii, and font-sizes (e.g. `font-size: 14px`, `margin-top: 15px`).
*   **Reason:** These create visual misalignment across components and conflict with the responsiveness rules. They must be remapped to `--smriti-spacing-*`, `--smriti-radius-*`, and `--smriti-font-size-*` variables.
*   **Volumetric Count:** ~5,781 instances.

### 3. 🟡 Medium Priority (Visual Polish)
*   **Violations:** Hardcoded box shadows (`box-shadow: 0 4px ...`).
*   **Reason:** Shadow effects look poor in dark modes if they aren't resolved dynamically. They should point to `--smriti-shadow-*`.
*   **Volumetric Count:** ~305 instances.

### 4. 🟢 Low Priority (Deferred structural cleanup)
*   **Violations:** HTML tag-level `style="..."` inline attributes.
*   **Reason:** Structural HTML modification is risky and tedious. Remapping hex colors inside these inline attributes is quick and low-risk, but removing the style tags altogether and refactoring to CSS classes should be deferred to long-term maintenance.
*   **Volumetric Count:** ~2,179 instances.

---

## 4. Recommended Execution Order & Migration Plan

To maintain stability and prevent regressions on key transaction pages, cleanup will occur in the following chronological sequence:

### Phase 2B — Low-Risk CSS Cleanup (Pre-approved)
Focus exclusively on shared stylesheets to standardize default visual rules.
1.  **Refactor core stylesheets:**
    *   `smriti_sidebar.css` (130 violations)
    *   `smriti-backup.css` (51 violations)
    *   `smriti-inventory.css` (71 violations)
    *   `smriti-purchase.css` (78 violations)
    *   `smriti-reports.css` (46 violations)
2.  **Remap to SMRITI tokens:** Replace hex colors, font-sizes, and spacing with token variables. Keep structural CSS classes intact.

### Phase 2C — POS Billing Terminal Finalization
Finish the outstanding hardcoded values in Billing UI files.
1.  **Refactor `smriti-billing.css`:** Remap remaining shadows and margins to spacing/shadow tokens.
2.  **Billing HTML Cleanup:** Remap inline `<style>` blocks in `billing.html` to tokens.
3.  **Governance Gate:** Under no circumstances should checkout (`checkout()`) or payment calculation (`updateTotals()`) JavaScript code be modified.

### Phase 2D — Legacy Module Migration (Staged roll-out)
Clean up remaining standalone modules in descending order of transaction priority.
*   **Stage 1:** `purchase.html` (470 violations) & `inventory.html` (150 violations)
*   **Stage 2:** `barcode.html` (801 violations) & `reports.html` (294 violations)
*   **Stage 3:** `platform_center.html` (418 violations) & `security.html` (417 violations)

---

## 5. Migration Effort & Resources Estimate

| Step | Work Items | Complexity | Estimated Time |
|---|---|---|---|
| **Phase 2B** | Remap 5 core CSS files to `--smriti-*` | Low | 1–2 days |
| **Phase 2C** | Clean up `smriti-billing.css` + `billing.html` style block | Medium | 1 day |
| **Phase 2D** | Remap other HTML files (`purchase.html`, `barcode.html`, etc.) | High | 3–5 days |

---

## 6. Audit Verdict

**Governance Check:** **PASS**
*   Legacy scanner successfully parsed all HTML, CSS, and JS styles.
*   Legacy token violations are quantified and grouped.
*   No codebase changes or refactorings were performed.

**Recommendation:** Open **Phase 2B (Low-Risk CSS Cleanup)** immediately.


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