# CHANGELOG — SMRITI Retail OS (erpnbook/smriti)

All notable changes to the Frappe app are documented here.
Format follows Keep a Changelog. Versioning follows Semantic Versioning.

---

## [2.0.0] — 2026-07-02

### Added

#### Purchase Studio (F-01)
- feat(purchase-studio): SSDL Layers 0-8 backend complete [1e71655]
- feat(purchase-studio): Layer 7-02 smriti-purchase.html UI complete [9dfaa22]
- feat(purchase-studio): add mandatory name field to custom field fixtures [1524811]
- feat(purchase-studio): move DocTypes to canonical module path, fix module name [bce28c7]
- docs: SSDL v1.0 — AITDL Engineering Standard AES-002 [ab98acb]

#### Purchase Analytics Studio (F-02)
- feat(sas): Purchase Analytics Studio — 6 purchase reports, filters, navigation, fixtures [a8285cd]
  - purchase_order_summary, grn_register, purchase_invoice_register
  - supplier_purchase_summary, item_wise_purchase, purchase_return_register
  - Filter engine enhancements: company, date, warehouse, status, project
  - 6 SAS_REPORT_DEFAULTS entries
  - fixtures/smriti_report_template.json
  - patches/seed_purchase_report_templates.py

#### UIE — Universal Integration Engine (F-03)
- feat: implement SMRITI TallyPrime Integration module, console UI, and automated unit tests [8fef0ac]
- feat: implement customer ledger auto-creation on sync [3667d68]
- feat: auto-create mapped settings ledgers (Sales, Cash, Bank, Duties) [a98c0e2]
- feat: implement Purchase, Debit/Credit Notes, and Payment Entry sync workflows [faf682f]
- feat: skip zero-value vouchers gracefully [e2a0402]
- feat: add explicit VOUCHERTYPENAME mapping, Narration attribution, force repost [856558a]
- feat: add reference mapping (supplier bill_no) and dynamic Audit comparison [bfccd5f]
- feat(scf): implement BaseAdapter, TallyAdapter, SyncCoordinator [c93c1cd]
- feat(uie): implement UIE Sprint 1 core foundation, REST adapter, payload builder [1ee8134]
- feat(uie): implement SMRITI UIE Integration Center console [9891b38]
- feat(uie): add legacy /smriti-tally compatibility redirect [299bad9]
- feat(uie, theme): harden UIE with indexing, dispatcher optimizations, tests [9ac3d1e]
- perf(uie): decouple payload builder from full document requirements [513fbd8]
- test(uie): add E2E integration test covering complete enqueue-to-dispatch flow [041be70]

#### Navigation Manager (F-04)
- feat(nav): implement database-driven SMRITI Navigation Manager (SNM) [927e54a]
- feat(nav): create dedicated Barcode Studio navigation group [3355e12]
- feat: implement Step 1 Navigation Reconciliation and fix branding tests [fc5da72]

#### Negative Stock Engine (F-05)
- feat(snsm): implement negative stock management engine and css theme reconciliation [30c9b3f]

#### Analytics Studio Foundation (F-06)
- feat: SMRITI Analytics Studio (SAS) v1.0 [c8b1a2f]
- chore(sas): add static report catalog fixture [b84742d]
- feat(nav-governance): implement Navigation Governance Framework v1.0 [cbb5efa]

#### DocType File-Backed Migrations
- feat: migrate SMRITI Barcode Settings DocType to standard file-backed schema [88fcb92]
- feat: migrate SMRITI Telemetry Event Definition DocType to standard file-backed schema [1a50909]

#### Other Features
- feat: add returns registers, GSTR-1 9B and credit note deadline alerts [47096f2]
- feat(pwa): Advanced PWA v2 — offline support, IndexedDB, background sync [692b693]
- feat(nav): unify navigation and implement dynamic collapsible sidebar [cd4ab0b]
- feat(print): SMRITI Print Modal — P3 debranding complete [c9a8395]
- feat(barcode): SMRITI Label Studio v2.1 RC — QZ Tray USB routing [8eac38a]
- feat(barcode): live autocomplete with keyboard navigation, debounce [dde2b2e]
- feat: migrate SMRITI Print Template to file-based DocType [3e1569d]

### Changed

#### Theme / UI
- UI Theme System Hardening and Dark Mode Consolidation [26f817f]
- Consolidate duplicate token declarations from smriti_theme.css to smriti_tokens.css [ad0b4ec]
- Map branding stylesheet text variables to canonical token fallbacks [bdf89bf]
- Align sidebar background token and sync body data-theme attribute [52a31f7]
- Commit validate_tokens.py to app tools folder [8ecaf20]
- fix(theme): align all theme_manager.js fallback defaults to sleek-compact [7cf3410]
- fix(css): replace disconnected c1 tokens with canonical theme tokens [1384833]
- fix(theme): map --smriti-primary to brand token [c869997]
- fix(theme): resolve unicode comment corruption and define missing tokens [58b652]
- fix(assets): remove hardcoded version strings, add favicon via token_loader [9c85f6]

#### Navigation
- fix(nav): resolve release-blocker 404 routes in Purchase sidebar [c50c374]
- fix(theme,nav): ensure initUIEngine runs reliably via token_loader [4ce00cd]
- fix(route): smriti-home.html — eliminate /app/smriti-* route dependency [8a37cc5]
- feat: implement Step 1 Navigation Reconciliation [fc5da72]

### Fixed
- fix(spc-rule6): remediate frappe.client calls in legacy purchase pages [01aa3fe]
- fix(tests): correct whitelist check for Frappe v16 [0b27667]
- fix(SAS): dataset_engine schema — correct POS Invoice column mapping [17f4d5b]
- fix(debranding): P1+P2 ERPNext/Frappe frontend exposure eliminated [b0ce720]
- fix(debranding): payments.html print — wrap PDF download in SmritiPrint modal [a39b2f1]
- fix(sidebar): 4 concrete bugs from audit [d73a00c]
- fix(barcode): correct style resolution priority (4-step) [efcd7e5]
- fix(barcode): extract .prn string from generate_prn() dict response [3782848]
- fix(barcode): replace str.format with safe substitute [fbaba46]
- fix(barcode): correct DocType query (Item Attribute → Item Variant Attribute) [6940a3]
- fix(backup): resolve deprecated with_files param, seed root Item Group [bc0e603]
- fix(branding): replace Frappe logo with SMRITI bag icon [26bf8d0]
- fix(csrf): defensive csrf_token resolution across all www page controllers [a9b8d6e]
- fix(csrf): handle stale csrf tokens in sw.js [df71bfc]
- fix(api): validate HTTP response status in fetch API helper [91c249a]
- fix(theme): add defensive dark theme fallbacks to setup wizard [331ed47]

### Performance
- perf(uie): decouple payload builder — N+1 eliminated [513fbd8]

---

## [1.8.6] — Previous Release

See git tag v1.8.6 for prior changes.

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
