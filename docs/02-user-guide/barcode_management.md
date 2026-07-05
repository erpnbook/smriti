---
Document ID: "USER-001"
Title: "Barcode & Label Print Management Guide"
Owner: "Operations Team"
Audience: "End User"
Module: "Core"
Version: "2.1.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: "Barcode Studio, Label Studio, Print Templates"
Last Updated: "2026-06-30"
Last Reviewed: "2026-06-30"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# Barcode & Label Print Management Guide

This guide covers **barcode setup**, **label print templates**, **token mapping**, **printer configuration**, and **troubleshooting** for the SMRITI Label Studio (`/barcode`) under the dedicated **Barcode Studio** menu.

---

## 1. Primary vs. Secondary Barcodes

SMRITI Retail OS supports multi-barcode setups to accommodate multi-channel operations:
- **Primary Barcode**: The default barcode scanned at billing terminals and printed on retail price tags. Exactly one primary barcode is enforced per size-variant.
- **Secondary Barcodes**: Vendor-supplied barcodes, global GTINs, or marketplace codes. Scanning any secondary barcode will correctly resolve the same item.

---

## 2. Importing Barcodes from Excel

The **Sizewise Item Master Bulk Importer** supports loading both primary and secondary barcodes.

### Column Mapping

| Excel Column Header | Type | Purpose |
|---|---|---|
| `BARCODE NO` | Primary | The main retail barcode (auto-generated if left blank). |
| `SECONDARY BARCODES` | Secondary | Comma-separated list of additional barcodes (e.g. `VND123, GTIN8890`). |

### Import Preservation Rules
- Updating a style variant or re-running an import **will not delete** your existing secondary barcodes.
- The importer automatically detects duplicate secondary barcodes and prevents them from being registered if they conflict with other items in the system.

---

## 3. Manual Barcode Constraints

When typing barcodes manually in the Size Config matrix:
1. **Allowed Characters**: Letters (`A-Z`, `a-z`), numbers (`0-9`), hyphens (`-`), and underscores (`_`).
2. **Disallowed Characters**: Spaces, punctuation, and symbols (e.g., `#`, `@`, `*`, `$`).
3. **Length**: Must be between **3 and 30 characters**.
4. **Collision Prevention**: The system checks if the manual barcode collides with any existing barcode or `Item Code` in the database.

---

## 4. Barcode Resolution & Printing Fallback

When printing tags via `/barcode` or resolving items at the POS:
1. The system checks for a **Primary Barcode** (`custom_is_primary = 1`).
2. If no barcode is marked primary, it falls back to the **first created barcode**.
3. If no barcodes exist at all, it uses the **Item Code** as the barcode value.

---

## 5. Print Templates — Overview

The **SMRITI Print Template** system (`/print-templates`) allows custom label layouts using raw ZPL or TSPL commands with dynamic `{token}` placeholders.

### How It Works

```
Item selected in Label Studio
        ↓
get_item_print_details() resolves all token values
        ↓
generate_prn() replaces {tokens} in ZPL/TSPL template
        ↓
PRN string sent to printer via QZ Tray (USB) or LAN socket
```

---

## 6. Print Template Fields

When creating or editing a template at `/print-templates`:

| Field | Required | Description |
|---|---|---|
| **Template Title** | Yes | Display name shown in dropdown (e.g. `Footwear 50x25 Zebra`) |
| **Label Size** | Yes | Physical label dimensions: `50x25`, `50x30`, `75x50`, `100x50` |
| **Printer Language** | Yes | `ZPL` (Zebra) or `TSPL` (TSC/Honeywell) |
| **Printer Family** | Yes | `ZPL` or `TSPL` — determines command syntax |
| **Template Version** | No | Semantic version for template change tracking |
| **Active** | Yes | If unchecked, template will not appear in print dropdown |
| **Is Default for Size** | No | Auto-selects this template when label size matches |
| **Raw PRN Template** | Yes | Full ZPL/TSPL command string with `{token}` placeholders |
| **Field Mappings JSON** | No | Custom token to ERPNext field overrides (see Section 8) |

---

## 7. Standard Token Reference

These tokens can be used directly in the Raw PRN Template. They are always available without any JSON mapping:

| Token | Value Source | Example Output |
|---|---|---|
| `{item_code}` | Full SKU code | `BBM-0001-6` |
| `{item_name}` | Item name field | `Blue Mesh Runner` |
| `{brand}` | Brand field | `BlueBird` |
| `{barcode}` | Primary barcode (auto-resolved) | `8901234567890` |
| `{mrp}` | custom_mrp then MRP price list then Standard Selling | `1299.00` |
| `{size}` | Size attribute (SIZE / SHOE SIZE / FOOTWEAR SIZE) | `8` |
| `{color}` | Color attribute (Color / Colour / Shade) | `Blue` |
| `{style}` | 4-step resolution — see Section 7.1 | `BBM-0001` |
| `{style_code}` | Stored custom_style_code or style_no field only | `BBM-0001` |
| `{variant_template}` | variant_of — direct ERP parent template ID | `BBM-0001` |
| `{pkd_date}` | Current packing month/year | `06/26` |
| `{pack_size}` | custom_pack_size or custom_carton_size | `12` |
| `{gender}` | custom_gender field | `Mens` |
| `{heel_type}` | custom_heel_type field | `Flat` |
| `{outsole}` | custom_outsole field | `Rubber` |
| `{upper_material}` | custom_upper_material field | `Mesh` |
| `{merchandise_category}` | custom_merchandise_category field | `Sports` |
| `{sub_category}` | custom_sub_category field | `Running` |
| `{purchase_class}` | custom_purchase_class field | `A` |

### 7.1 — `{style}` Token — 4-Step Resolution Priority

For variant items (e.g. `BBM-0001-6`), `{style}` resolves in this order:

```
Step 1: variant_of              → BBM-0001   (ERP parent template — most accurate)
Step 2: custom_style_code field → BBM-0001   (explicit stored style code)
Step 3: style_no field          → BBM-0001   (alternate style field)
Step 4: SKU hyphen split        → BBM         (last resort — item_code.split("-")[0])
```

> **Note:** `{style_code}` always returns the stored field value only (Steps 2 or 3). It does not fall back to `variant_of` or SKU split. Use `{style}` for the most complete resolution chain.

### 7.2 — Token vs. Token Comparison

| Token | Variant Item `BBM-0001-6` | Non-Variant Item `ITEM-9988` |
|---|---|---|
| `{item_code}` | `BBM-0001-6` | `ITEM-9988` |
| `{style}` | `BBM-0001` (via variant_of) | `ITEM` (via SKU split) |
| `{style_code}` | `BBM-0001` (if custom_style_code set) | `` (blank if field empty) |
| `{variant_template}` | `BBM-0001` | `` (blank — not a variant) |

---

## 8. Field Mappings JSON — Custom Token Overrides

The **Field Mappings JSON** section on each template allows you to remap any `{token}` to a specific ERPNext field. This overrides the standard resolution for that token.

### Format
```json
[
  { "token": "style",       "source_field": "variant_of"        },
  { "token": "style_code",  "source_field": "custom_style_code" },
  { "token": "item_name",   "source_field": "item_name"         },
  { "token": "mrp",         "source_field": "custom_mrp"        },
  { "token": "color",       "source_field": "attribute:Color"   },
  { "token": "size",        "source_field": "attribute:SIZE"    }
]
```

### Supported `source_field` Values

| Format | Example | Reads From |
|---|---|---|
| Standard field | `"item_name"` | item_doc.item_name |
| Custom field | `"custom_style_code"` | item_doc.custom_style_code |
| ERPNext field | `"variant_of"` | item_doc.variant_of |
| Attribute | `"attribute:Color"` | Item Attributes child table |

> **Important:** When Field Mappings JSON is present on a template, **only mapped tokens are resolved**. Any token not listed in the JSON will print as blank. Always add every token used in the ZPL/TSPL code to the JSON mapping grid.

---

## 9. Print Profiles — Saving Printer Configurations

A **Print Profile** saves a named combination of: Template, Printer IP + Port, DPI, Copies per label, and Label size.

**To create a profile:**
1. Open `/barcode` and click **Configure** (gear icon)
2. Fill in Printer IP, select Template, set DPI and copies
3. Click **Save Profile**
4. Mark as **Default** to auto-load on every session

Saved profiles persist in SMRITI Company Settings and are shared across all users on the same site.

---

## 10. Printer Connection Methods

### Method A — LAN Network Print (Recommended)
- Printer connected to the store network via Ethernet or WiFi
- SMRITI sends ZPL/TSPL directly via TCP socket to `printer_ip:printer_port`
- No driver or QZ Tray required on the client PC
- Recommended for warehouse and back-office printing

### Method B — USB Local Print via QZ Tray
- QZ Tray desktop application must be running on the cashier/store PC
- SMRITI connects to QZ Tray via WebSocket (`wss://localhost:8181`)
- QZ Tray routes the raw ZPL/TSPL string to the selected USB printer
- Required when the printer is connected directly via USB cable

> **If USB print fails:** Ensure QZ Tray is running and the correct printer is selected. If you see a browser console error `data[i].data.search is not a function`, update to the latest SMRITI version — this was a payload extraction bug fixed in commit `efcd7e5`.

---

## 11. Identifying Items Missing Barcodes

To scan your inventory for active products without barcodes:
- Store managers can query the active missing barcodes list from the backend to identify items needing print runs or vendor barcode linking.
- The **Transaction Load** feature in Label Studio shows a checklist of items in any Purchase Receipt or Stock Entry. Items missing barcodes are highlighted with a red **Missing Barcode** badge.

---

## 12. Common Print Issues & Quick Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| `{style}` prints full SKU like `BBM-0001-6` | Old code using SKU split only | Update SMRITI — 4-step resolution active from v1.x |
| `{style_code}` prints blank | Token not in Field Mappings JSON | Add `{"token":"style_code","source_field":"custom_style_code"}` to JSON |
| `{variant_template}` prints blank | Token not in Field Mappings JSON | Add `{"token":"variant_template","source_field":"variant_of"}` to JSON |
| USB print crashes with JS error | Old code — prnContent was dict not string | Update SMRITI — `.prn` extraction applied in all 3 flows |
| All fields print blank on custom template | Field Mappings JSON present but incomplete | Add all `{tokens}` used in ZPL to the JSON mapping grid |
| Fallback template warning toast appears | Custom template had a ZPL render error | Check ZPL syntax and verify token names match exactly |
| Barcode prints as item_code not barcode value | No barcode registered for this item | Import or manually add a barcode in Item Master |

---

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Initial guide — barcodes and import |
| 2.0.0 | 2026-06-30 | Jawahar R. Mallah | Full rewrite — added Print Templates, Token Reference, Field Mappings JSON, 4-step style resolution, QZ Tray flows, Print Profiles, Quick Fix table |
| 2.1.0 | 2026-06-30 | Jawahar R. Mallah | Updated navigation references to Label Studio and the new Barcode Studio menu group |

---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."
> — Jawahar R. Mallah
> Founder & Chief Architect, AITDL