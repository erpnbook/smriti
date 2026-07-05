---
Document ID: "ARCH-007"
Title: "BRD-01: Branding, Attribution & Documentation Governance Standard"
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

# BRD-01: Branding, Attribution & Documentation Governance Standard

**Status:** LOCKED (Frozen for SMRITI v1.0)  
**Version:** 1.0  
**Effective:** 2026-06-21  
**Applies To:** All Developers, Technical Writers, AI Agents, and Partner Integrators.  

---

## 1. Purpose & Scope

This standard establishes the permanent rules governing the product identity, trademark compliance, domain names, content standards, AI generation guidelines, and open-source licensing attributions of **SMRITI Retail OS™**. The goal is to enforce consistency, ensure legal compliance, and present SMRITI as a premium, enterprise-grade Retail Intelligence Platform.

---

## 2. Product Identity & Attribution

1. **Official Product Name**:
   ```text
   SMRITI Retail OS™
   ```
2. **Developer Entity**:
   ```text
   AITDL – AI Technology & Development Lab
   ```
3. **Primary Tech Attribution**:
   The following reference must be displayed on all primary public interfaces (e.g., login screens, help centers, about pages):
   > **SMRITI Retail OS™**  
   > Developed by AITDL  
   > Powered by ERPNext® & Frappe® Framework

---

## 3. Trademark & Domain Policy

1. **Trademark Protection**: Compound brands or product names that imply ERPNext is co-branded or owned by SMRITI/AITDL are strictly prohibited to prevent consumer confusion.
   * *Allowed*: "SMRITI Retail OS™ powered by ERPNext®"
   * *Forbidden*: "SMRITI ERPNext", "ERPNext by SMRITI", "ERPNext Retail OS"
2. **Domain Registration Policy**: No official, reseller, or partner website domains registered for SMRITI distribution shall contain the strings "erpnext" or "frappe".
   * *Allowed*: `erpnbook.com`, `smriti.aitdl.com`, `yourdomain.com`
   * *Forbidden*: `erpnext-retail.com`, `smriti-erpnext.com`, `erpnext-smriti.com`

---

## 4. Knowledge Center Content Policy

1. **Audience Segmentation**:
   * *Target Audience*: Store operators, cashiers, supervisors, auditors, managers, and business owners.
   * *Non-Target*: Developers, software architects, and founders (their context must be isolated).
2. **Language Matrix**:
   * **Official User Manuals**: Must be written in professional, simple, task-oriented, and example-driven Business English.
   * **Universal Explain Modal & Business Dictionary**: Explicitly supports and preserves Hinglish definitions (under the `hinglish_definition` database fields) to maintain local accessibility for ground-level store staff.
3. **Consolidation of Author Profiles**: Personal author biographies, credentials, and documentation philosophy must be consolidated into a standalone "About SMRITI" section. They must not appear at the top or bottom of standard user manuals.

---

## 5. Documentation Style & Chapter Schema

Every chapter in the SMRITI User Manuals must follow this structure:
1. **Purpose**: Clear, 1-sentence statement of what the module does.
2. **Business Problem**: Why this module is needed (e.g., locked capital, stock shrinkage).
3. **When To Use**: Specific retail triggers (e.g., daily close, monthly audit).
4. **Step-By-Step Guide**: Sequential, clean instructions for the operator.
5. **Real Example**: A practical worked case study with numbers.
6. **Common Mistakes**: Frequent cashier/operator errors and how to avoid them.
7. **FAQ**: Standard questions answered in simple language.
8. **Related Formulas**: Links to registered math formulas (e.g., WOC, Sales Velocity).
9. **Related KPIs**: Impacted dashboard indicators.
10. **Key Takeaways**: Concise summary bullet points.

---

## 6. Open Source Attribution Policy

1. **Attribution Preservation**: SMRITI Retail OS incorporates and extends open-source technologies. Attribution to ERPNext® and Frappe® shall be preserved where legally required.
2. **No Alterations**: No developer, partner, or reseller may remove required open-source notices or licenses from source distributions or public website footers.

---

## 7. AI Agent Compliance Policy

Any AI assistant or automated development tool generating documentation, in-app explanations, or code assets for SMRITI must adhere to the following directives:
1. **No Inventing Claims**: AI agents shall not invent licensing claims, features, or warranties.
2. **No Deleting Attribution**: AI agents shall not delete open-source attributions, company credits, or standard copyright notices.
3. **No Unauthorized Branding**: AI agents must adhere to the official SMRITI Retail OS™ typography and branding rules, avoiding unauthorized styles or logo variations.
4. **No Internal Leakage**: AI agents shall not expose internal database schemas, technical variables, or architectural notes in end-user manuals.
5. **Aesthetics Requirement**: Web layouts generated by AI must use the SMRITI design system (Navy `#1A2B5C` + Blue `#2563EB` + Arial) with modern, dynamic, and premium layouts.

---

## 8. Founder Attribution Standard

1. **Authorized Locations**: Founder and Chief Architect attribution (Jawahar R. Mallah, AITDL) shall appear only in:
   * "About SMRITI" or "About the Author" pages.
   * Internal Governance Documents (such as KGF or BRD).
   * Technical Architecture Documents.
   * Official Whitepapers & Investor Materials.
2. **Operational Manuals Excluded**: Founder attribution, biographies, and personal notes shall not be displayed inside operational store user manuals or daily cashier handbooks.

---

## 9. Product Positioning

SMRITI Retail OS™ must never be positioned or marketed as "another generic ERP". Instead, it must be positioned as:
> **Retail Intelligence Platform**  
> Built on ERPNext®  
> Enhanced by the SMRITI Intelligence Layer (CGE, PDT, PSV, Formula Registry, and Explain Engine).

---

## 10. Dynamic Footer Standard

Every SMRITI custom web page template (`/smriti-*`, `/billing`, `/inventory`, etc.) must render a footer at the bottom containing:
```html
<div class="smriti-footer">
    <p><strong>SMRITI Retail OS™</strong></p>
    <p>Developed by AITDL | Powered by ERPNext® & Frappe® Framework</p>
    <p>&copy; AITDL. All Rights Reserved.</p>
</div>
```
The footer must not contain a hardcoded calendar year to ensure the system remains evergreen.

---

## 11. URI Scheme Standard (Universal Asset URIs)

To ensure consistency and compatibility across the SMRITI Knowledge Governance Platform, all cross-referenced assets within manuals, dictionary cards, training workbooks, or dashboards must be linked using the SMRITI Asset URI standard.

### Standard Format:
`[Asset Name](asset_type:ASSET_CODE)`

### Registered Schemes:
- **`formula:`**: Direct link to the SMRITI Formula Registry (e.g. `[Weeks of Cover](formula:INV-002)`).
- **`dictionary:`**: Direct link to the SMRITI Business Dictionary (e.g. `[Party Stock Account](dictionary:PSA)`).
- **`training:`**: Direct link to SMRITI Training workbook modules or exercises (e.g. `[Distributor Onboarding](training:MOD-001)`).
- **`report:`**: Direct link to SMRITI-specific custom reports (e.g. `[Broken Size Report](report:RPT-001)`).

### Technical Implementation (Active Schemes)

#### `formula:` Scheme
- **Click handler**: Intercepts in `smriti-help.html` → dispatches `smriti:formula-open` CustomEvent.
- **Event bus listener**: `window.addEventListener('smriti:formula-open', ...)` → calls `openFormulaInDrawer()`.
- **Dynamic fetch**: On cache miss, calls `smriti_retail_os.api.formula_api.get_formula_detail`.
- **Governance gateway**: `FORMULA_INDEX` set in `formula_service.py` — only registered formula IDs reachable.
- **Role security**: System Manager sees Draft/Inactive; Cashier/Store Manager sees Approved+Active only.

#### `dictionary:` Scheme (DOC-GOV-03 — Active from Sprint B)
- **Hover tooltip**: On `mouseover` of `dictionary:` anchor, shows floating card with term name + 1-line definition. No network call — served from `allTerms` cache.
- **Click handler**: Intercepts in `smriti-help.html` → dispatches `smriti:term-open` CustomEvent.
- **Event bus listener**: `window.addEventListener('smriti:term-open', ...)` → calls `openTermInDrawer()`.
- **Dynamic fetch**: On cache miss, calls `smriti_retail_os.api.dictionary_api.get_term_detail`.
- **Governance gateway**: `TERM_INDEX` set in `dictionary_service.py` — only registered term IDs reachable.
- **Normalization**: `openTermInDrawer()` normalizes FAQ keys `{q, a}` or `{question, answer}` and mistakes keys `{mistake, a}` or plain string.
- **Deep link**: `?term=TERM_ID` URL param opens term drawer directly on page load.

#### `training:` and `report:` Schemes
- Registered but not yet active in the current release. Reserved for future sprint implementation.

### Governance Rule

Even if only specific schemes are active in the current release, all new manuals, tools, and documentation links must strictly conform to these URI schemes, avoiding fuzzy text matching or direct database routing.

To add a new term to the dictionary: scheme:
1. Insert the `term_id` into `TERM_INDEX` in `dictionary_service.py`.
2. Create the `SMRITI Business Term` DocType record with `status=Approved, is_active=1`.
3. Run `seed_default_terms.py` patch if the term is a standard KGF term.



## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |