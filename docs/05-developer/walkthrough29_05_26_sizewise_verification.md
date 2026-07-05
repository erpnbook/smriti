---
Document ID: "DEV-065"
Title: "Walkthrough: Sizewise Item Master — Pre-Import Verification & On-the-Fly Insert"
Owner: "Development Team"
Audience: "Developer"
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

# Walkthrough: Sizewise Item Master — Pre-Import Verification & On-the-Fly Insert

**Date:** 2026-05-31  
**Author:** Jawahar R Mallah / SMRITI Development Team  
**Commit:** `f9243f4`  
**Branch:** `main` → `erpnbook/smriti.git`  
**Files Changed:**
- `smriti_retail_os/item_master_api.py`
- `smriti_retail_os/www/sizewise_item.html`

---

## 🎯 Problem Statement

When pasting a multi-row Excel size matrix into the **Sizewise Item Master CRUD** (`/sizewise_item`), the bulk import was silently failing for rows where:

1. **Category values** (e.g. `SANDAL`, `CHAPPAL`) did not exist as ERPNext **Item Groups**
2. **Color values** (e.g. `PISTA`, `CREAM`) did not exist as **Color attribute values**
3. **Sub-Category values** (e.g. `LASTIC PATTA`, `MUEL`) did not exist in SMRITI Sub Category master

The errors were caught by the backend `try/except` block but only stored as `str(e)` — no traceback, no article reference, and no visible error in the UI. The user only saw `Import errors: Array(18)` in the browser console.

Additionally, the `MRP` column (confirmed as exactly `MRP` in the Excel header) was being correctly detected — the root cause of failures was missing master values, not column detection.

---

## ✅ Solution Implemented

### 1. Pre-Import Verification Step (Frontend + Backend)

A full **pre-import verification panel** was added between the paste preview grid and the import toolbar. It:

- **Auto-runs immediately after paste** — no manual trigger needed
- Calls the new `validate_pivot_values` backend API
- Shows each new/missing value with a **status dot**, **correction input**, and **existing-value suggestion chips**
- **Blocks the Import button** until the user clicks "Confirm & Enable Import"
- Applies spelling corrections to all `parsedStyles` before the import payload is built

### 2. New Backend API: `validate_pivot_values`

**File:** [`item_master_api.py`](../../apps/smriti_retail_os/smriti_retail_os/item_master_api.py)

```python
@frappe.whitelist()
def validate_pivot_values(styles_json):
```

Checks three categories of values:

| Value Type | Checked Against | ERPNext DocType |
|---|---|---|
| `item_group` (Category) | All existing Item Groups | `Item Group` |
| `color` | Color attribute values | `Item Attribute Value` (parent=Color) |
| `sub_category` | SMRITI Sub Category master | `SMRITI Sub Category` (if exists) |

Returns:
```json
{
  "new_categories":    [{ "value": "SANDAL",      "suggestions": ["Footwear", "Products"] }],
  "new_colors":        [{ "value": "PISTA",        "suggestions": ["BLACK", "BEIGE", "CREAM"] }],
  "new_sub_cats":      [{ "value": "LASTIC PATTA", "suggestions": ["BURMY", "MUEL"] }],
  "existing_categories": ["Footwear", "Products", ...],
  "existing_colors":     ["BLACK", "BEIGE", ...],
  "existing_sub_cats":   [...],
  "has_issues": true
}
```

### 3. Improved Import Error Logging

```python
except Exception as e:
    import traceback
    errors.append({
        "row_idx": idx + 1,
        "article_no": ...,
        "error": str(e),
        "detail": traceback.format_exc()   # ← NEW: full traceback
    })
    frappe.log_error(title=f"SMRITI Pivot Import — Row {idx+1}: {article_no}", ...)
```

And on the frontend, failed rows are now shown **inline** below the progress bar with article number + error message — not just in the console.

---

## 🖥️ User Flow (After Fix)

```
1. User copies rows from Excel (ARTICLE, COLOR, CATOGARY, SUB-CATO, 36..42, TTL QTY, MRP)
2. User clicks the Paste Zone → pastes (Ctrl+V)
3. System parses TSV, renders column map + stats bar + preview grid
4. ──────────────────────────────────────────────────────────────
   ⚡ Pre-Import Verification panel appears automatically
   🔄 Spinner: "Checking categories, colors and sub-categories against database..."
   ──────────────────────────────────────────────────────────────
5. Panel renders results:
   📁 Item Categories (2 new)
      🟠 SANDAL   [input: SANDAL  ] [Footwear] [Products]
      🟠 CHAPPAL  [input: CHAPPAL ] [Footwear] [Products]
   🎨 Colors (1 new)
      🟠 PISTA    [input: PISTA   ] [BLACK] [BEIGE] [CREAM]

6. User can:
   a) Leave as-is → new value will be auto-created on import
   b) Type a correction → dot turns 🔵 purple, shows "✏️ Will use: Footwear"
   c) Click a suggestion chip → instantly applies the existing value

7. User clicks [✓ Confirm & Enable Import]
   → Corrections applied to all parsedStyles in memory
   → Import button unlocks

8. User clicks [🚀 Import All Styles & Variants]
   → Backend creates/updates items with corrected values
```

---

## 🎨 Verification Panel — Visual States

| Dot Color | Meaning |
|---|---|
| 🟡 Amber | New value — will be **auto-created** in the database |
| 🔵 Purple | **Corrected** — will use the typed or chip-selected value |
| 🟢 Green | Exists in DB — no action needed |

If **all values already exist**, the panel shows a green banner:  
`✅ All categories, colors and sub-categories exist in the database. Ready to import!`  
…and the Import button unlocks immediately without requiring confirmation.

If the verification **API fails** (network error, etc.), the panel shows a warning and unlocks import anyway — verification is a helper, not a hard blocker.

---

## 📌 Column Alias Reference (MRP Detection)

The MRP column is detected using these exact header aliases (case-insensitive):

```js
mrp: ['MRP', 'PLANNED MRP', 'SELLING PRICE', 'RATE', 'PRICE']
```

> ✅ Confirmed: The Excel sheet uses `MRP` as the header — correctly detected.  
> Any column named differently (e.g. `WMP`, `WSP`) will **not** be mapped to MRP and will cause `mrp = 0` → row marked invalid → not sent to backend.

---

## 🔧 Technical Reference

### Frontend JS Functions Added

| Function | Description |
|---|---|
| `runVerification()` | Async — calls `validate_pivot_values` API, shows spinner, then renders panel |
| `renderVerificationPanel(res)` | Builds HTML for all new-value sections |
| `_buildVerifySection(icon, title, items, prefix, existing)` | Renders one section (category/color/sub) |
| `onVerifyInput(key, value)` | Handles live typing — updates dot color + status label |
| `applyVerifySuggestion(key, value)` | Applies a suggestion chip click |
| `confirmAndApplyVerification()` | Collects all corrections → patches `parsedStyles` → unlocks import |
| `_unlockImport()` | Enables the import button if valid styles exist |

### State Variables

```js
let verificationCorrections = {};  
// e.g. { 'cat:SANDAL': 'Footwear', 'clr:PISTA': 'PISTA', 'sub:MUEL': 'MUEL' }

let verificationPassed = false;
// Set to true after confirmAndApplyVerification() or if has_issues=false
```

### Backend API Location

```
smriti_retail_os/item_master_api.py
→ validate_pivot_values(styles_json)       ← NEW (line ~772)
→ import_pivot_item_master(styles_json)    ← Updated error logging
```

---

## 🚫 Known Limitations

- Sub-category verification only runs if the `SMRITI Sub Category` DocType exists on the site. It is silently skipped otherwise.
- Correction is applied **in-memory only** — if the user clears and re-pastes, corrections reset.
- Color corrections are uppercased automatically (ERPNext convention).

---

## 📦 Git Commit Summary

```
feat(sizewise): pre-import verification with on-the-fly insert & spell correction

- Added validate_pivot_values() API in item_master_api.py
- Added Pre-Import Verification Panel in sizewise_item.html
- Improved import error logging with full traceback
- Improved frontend error display: per-row article + error in UI

Commit: f9243f4
Files:  2 changed, +492 insertions
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