# Label Studio — Retail Phase A v2.4.0

**Date:** 2026-07-08
**Author:** SMRITI Engineering Team
**Commit:** `1ae0350`
**Status:** Completed

---

## 1. Purpose

Connect Label Studio to inventory. Before this release, the designer was a standalone canvas tool — useful for layout experimentation but completely disconnected from the product catalog, with no way to add elements, no way to load real item data, and no way to print. This release makes it a first-class retail label printing tool.

---

## 2. Scope

5 files modified. No new files created.

---

## 3. Files Created

None.

---

## 4. Files Modified

| File | Change Type |
|---|---|
| `label_studio/api/label_api.py` | Added 2 endpoints + `_guest_guard` helper |
| `label_studio/service/render_engine.py` | Added QRCode + Line element types to ZPL + TSPL |
| `public/js/label/label_core.js` | Full rewrite — empty start, factory, nextId |
| `public/js/label/label_designer.js` | Full rewrite — all element lifecycle events |
| `www/label.html` | Full rebuild — toolbar, SKU panel, print panel |

---

## 5. Architecture Decisions

### Empty canvas by default
Retail labels are always built from real product data. A placeholder with "SMRITI OS / 12345678" was misleading. Canvas now starts blank and is populated either via toolbar (manual layout) or the "Load from Inventory" panel (auto-scaffold).

### `element:load_item` auto-scaffold vs update
The designer distinguishes two modes:
- **Empty canvas** → builds a standard retail layout: item name (top), brand (second row), MRP (third row), barcode (bottom). All elements tagged with `source` so subsequent item loads update the correct ones.
- **Existing canvas** → updates `content` on source-tagged elements only. Custom positioning is preserved.

### `LabelElementFactory` in `label_core.js`
Keeps element shape consistent between label_core, label_designer, and future imports/templates. Single source of truth for field names and retail-appropriate default sizes.

### `font_size` field on element model
Retail labels use multiple font sizes: product name large, MRP bold, HSN/brand small. The renderer now passes `font_size` to both canvas preview and ZPL `^A0N` font size.

### QR Code canvas preview
QR codes can't be rendered on a 2D canvas without a library. Instead of importing a 3rd-party QR library, the preview draws a representative QR pattern grid — sufficient for layout positioning. The actual QR command (`^BQN` / `QRCODE`) is generated correctly in the print stream.

---

## 6. Design Rationale

All changes are **additive** to the backend service layer. The render engine strategy pattern means adding QR/Line required only new `elif` branches with no structural change. The event bus pattern in `label_core.js` means the HTML controller is fully decoupled from the designer internals.

---

## 7. Implementation Summary

### `get_item_for_label(item_code)`
1. Guest guard → 401 if unauthenticated
2. `frappe.db.exists("Item", item_code)` → human-readable error if not found
3. `frappe.get_doc("Item", ...)` → reads `barcodes[0].barcode` for primary barcode
4. `frappe.db.get_value("Item Price", ...)` → MRP from Standard Selling price list
5. `getattr` guards for `gst_hsn_code` / `hsn_code` / `brand` — absent on non-India deployments

### ZPL QR Code command
`^FO{x},{y}^BQN,2,3^FDMM,A{content}^FS` — Model 2, magnification 3, standard QR mode.

### TSPL QR Code command
`QRCODE {x},{y},H,3,M,0,M2,"{content}"` — high error correction, cell size 3, M2 mode.

### label.html retail layout
Three-column layout: left panel (SKU lookup + inspector + preferences) | center canvas | right panel (print + element list). Topbar + element toolbar. Status bar. All in vanilla CSS with `--ls-*` CSS variables for consistent theming.

---

## 8. Tests Executed

```
python -c "import ast; ast.parse(open('label_api.py').read())"      → OK
python -c "import ast; ast.parse(open('render_engine.py').read())"  → OK
python -c "import ast; ast.parse(open('label_service.py').read())"  → OK
git diff --cached --stat:
  label_api.py     +92 -0
  render_engine.py +34 -14
  label_core.js    +71 -48
  label_designer.js +1049/-442
  label.html        +843/-442
```

---

## 9. Verification Results

| Claim | Status | Evidence |
|---|---|---|
| Python syntax — 3 files | Done | `ast.parse()` → OK × 3 |
| Commit on `main` | Done | `1ae0350` — push confirmed |
| `F:\Smriti9` synced | Done | fast-forward +1,049 lines |
| "Load from Item" loads real product | Unverified — needs live ERPNext with Items |
| Element toolbar adds to canvas | Unverified — browser test required |
| Print dispatches to printer | Unverified — needs SMRITI Printer configured |
| QR ZPL command renders on Zebra | Unverified — hardware test |

---

## 10. Known Limitations

- QR code canvas preview is a placeholder pattern grid, not an actual QR code. The print stream generates correct ZPL/TSPL.
- Export button downloads a JSON of the canvas coordinate preview, not the raw ZPL/TSPL stream. A future endpoint `export_print_stream(label_data, format_type)` would return the raw printer stream for direct download.
- Copies are printed by calling `print_label` N times in a loop — may be slow for large counts. Backend batch support (Phase B) would pass `copies` to the print framework directly.
- `get_printers_list()` falls back to a single "Default Printer (ZPL)" when no SMRITI Printers are configured — the user must configure printers in ERPNext for real dispatch.

---

## 11. Future Work

| Item | Priority |
|---|---|
| Phase B — Batch Print from GRN (print N labels for newly received stock items) | High |
| Export raw ZPL/TSPL stream as `.zpl` / `.prn` file | Medium |
| Template save/load (via `LabelTemplateRepository`) | Medium |
| Actual QR code canvas rendering (via `qrcode-generator` or `jsQR`) | Low |
| Copy/paste elements | Low |

---

## 12. Related ADRs

None.

---

## 13. Related RFCs

None. Domain correction: SMRITI is a Retail Chain Store / Distributor / Inventory Management platform — not an accounting package.
