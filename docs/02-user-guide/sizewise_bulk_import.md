---
Document ID: "USER-023"
Title: "Sizewise Item Master — Bulk Import (Paste from Excel)"
Owner: "Operations Team"
Audience: "End User"
Module: "Core"
Version: "1.1.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: "Barcode Studio"
Last Updated: "2026-06-30"
Last Reviewed: "2026-06-30"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# Sizewise Item Master — Bulk Import (Paste from Excel)

The Sizewise Item Master page (`/sizewise_item`) supports two modes:

1. **Manual Style Creator** — fill in article, color, sizes one-by-one
2. **Paste Size Matrix** — copy rows directly from Excel and bulk-import

This guide covers the Paste mode, including the **Pre-Import Verification** system.

---

## How to Paste from Excel

> **Navigation (v2.4.2+):** Sizewise Item Master is now located under **Barcode Studio** in the sidebar (previously under Masters). Direct URL: `/sizewise_item`

1. Open your Excel / Google Sheets file
2. Select rows including the **header row**
3. Copy (Ctrl+C)
4. Go to `Barcode Studio → Sizewise Item CRUD` (or navigate directly to `/sizewise_item`) → click **"Paste Size Matrix (Excel)"** tab
5. Click anywhere in the paste zone → Paste (Ctrl+V)

### Required Column Headers

| Excel Column | Maps To | Required? |
|---|---|---|
| `ARTICLE` or `STYLE CODE` | Article No | ✅ Yes |
| `COLOR` or `COLOUR` | Color | ✅ Yes |
| `CATOGARY` or `CATEGORY` | Item Group | ✅ Yes |
| `SUB - CATO` or `DESCRIPTION` | Sub-Category | Optional |
| `MRP` or `PLANNED MRP` or `RATE` or `PRICE` or `SELLING PRICE` | MRP | ✅ Yes |
| `TTL QTY` or `TOTAL QTY` | Total Qty (display only) | Optional |
| `36`, `37`, `38` ... `42` or `S`, `M`, `L` | Size columns | ✅ At least 1 |

> ⚠️ **MRP must be > 0** for a row to be valid. If MRP is blank or zero, that row will be skipped.

---

## Pre-Import Verification (Auto-runs after paste)

After pasting, the system **automatically checks** all category, color, and sub-category values against the database **before** allowing import.

### What it checks

| Value | Checked Against |
|---|---|
| Category (CATOGARY column) | ERPNext Item Groups |
| Color | Color Item Attribute values |
| Sub-Category | SMRITI Sub Category master |

### Verification Panel States

| Indicator | Meaning | Action |
|---|---|---|
| 🟡 Amber dot | Value does not exist in DB | Will be **auto-created** on import |
| 🔵 Purple dot | Value corrected by user | Will use the corrected value |
| 🟢 Green dot | Value exists in DB | No action needed |

### Correcting Values

- **Type** in the correction input to fix a spelling mistake
- **Click a suggestion chip** to use an existing DB value instead
- Leave as-is to auto-create the new value during import

### Confirming

Click **"Confirm & Enable Import"** to:
1. Apply all corrections to every row in memory
2. Unlock the Import button

---

## Import Behaviour

- Each valid row creates one **Style Template** (if not exists) + one **Size Variant** per active size column
- Auto-generates **EAN-13 barcodes** for new variants
- Creates **Standard Selling** and **MRP** price list entries at the given MRP
- New Item Groups, Colors, Sub-Categories are **created on-the-fly** if they don't exist

### Error Handling

If any row fails during backend processing:
- The error is shown **inline** in the progress panel (article number + reason)
- Successful rows are still committed
- Full traceback is logged to Frappe Error Log (`/app/error-log`)

---

## Troubleshooting

**Q: Some items show "No MRP" in the status column**  
A: The MRP column header must exactly match one of: `MRP`, `PLANNED MRP`, `SELLING PRICE`, `RATE`, `PRICE`. Column `WMP` or `WSP` will NOT be detected.

**Q: Import button stays disabled after paste**  
A: The verification panel must be confirmed first. Scroll down to the amber "Pre-Import Verification" panel and click "Confirm & Enable Import".

**Q: "18 errors" shown after import**  
A: Click the down-arrow in the progress panel to expand per-row error details. Also check `/app/error-log` for full tracebacks.

**Q: Color not auto-created**  
A: Ensure the `Color` Item Attribute exists in ERPNext (`/app/item-attribute/Color`). The system will add new values to it automatically.

**Q: I previously got import errors due to missing colors or categories. Do I need to clean up the database before re-importing?**  
A: No. Failed rows are not partially imported, so there is no corrupt data to clean up. To resolve:
1. Refresh the `/sizewise_item` page.
2. Re-paste the exact same Excel data.
3. Use the new **Pre-Import Verification** panel to confirm/correct the missing attributes.
4. Click **Confirm & Enable Import** and then click **Import All Styles & Variants**. The import will now succeed.

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |
| 1.1.0 | 2026-06-30 | Jawahar R. Mallah | Updated navigation reference — Sizewise Item CRUD now under Barcode Studio (moved from Masters) |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL