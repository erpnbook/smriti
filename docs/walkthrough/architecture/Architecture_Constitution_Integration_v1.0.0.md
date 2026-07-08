# Architecture — Independent Product Constitution Integration v1.0.0

## 1. Purpose

Perform a governance-compliant integration of the proposed "SMRITI Retail OS — Independent Product Architecture Constitution" document into the existing governance stack, avoiding SPC-002 (duplication) and SPC-008 (new document without consolidation) violations while preserving the three genuinely new elements the proposal introduced.

## 2. Scope

| File | Action |
|---|---|
| `SMRITI_PRODUCT_CONSTITUTION.md` | Modified — added SPC-C-012 and SPC-C-013 as Candidate Articles + amendment log entry |
| `SMRITI_EXPERIENCE_CONSTITUTION.md` | Modified — added Document Experience Constitution section (Rules DOC-E1 through DOC-E5) |
| `SMRITI_UI_ARCHITECTURE.md` | Created — new companion document filling the gap referenced in `SMRITI_EXPERIENCE_CONSTITUTION.md` §Purpose line 6 |

## 3. Files Created

| File | Purpose |
|---|---|
| `SMRITI_UI_ARCHITECTURE.md` | Companion document: Component Inventory, Document Format Matrix, current directory layout, module UI ownership, naming conventions, future-state layout (explicitly labelled as not-current) |

## 4. Files Modified

### `SMRITI_PRODUCT_CONSTITUTION.md`

Two Candidate Articles added to the Candidate Articles table:

- **SPC-C-012 — SMRITI Component Library Standard:** Formalises the goal of extracting inline component patterns into a shared reusable library. Blocker: library not yet built. Interim baseline is `products.html` (A2 reference).
- **SPC-C-013 — SMRITI Document Format Standard:** Formalises the five-format requirement (Screen, Print, PDF, Email, Mobile) for every business document. Blocker: Print Studio must be formally scoped and implemented.

Amendment log updated: v1.1.0 entry added.

### `SMRITI_EXPERIENCE_CONSTITUTION.md`

New section: **Document Experience Constitution** inserted before the Compliance section.

Rules added:
- **DOC-E1:** Five-format requirement per document (Screen / Print / PDF / Email / Mobile)
- **DOC-E2:** SMRITI branding on all printed/emailed documents
- **DOC-E3:** Business language on document field labels (vocabulary table)
- **DOC-E4:** Print View must be chrome-free
- **DOC-E5:** All documents registered in Print Studio

Scope table: 13 business documents enumerated across Purchase, Billing, Inventory, Logistics, and Reports modules.

## 5. Architecture Decisions

### Decision 1 — Integrate, Do Not Create a Competing Document

The proposed "Independent Product Architecture Constitution" was reviewed against the existing governance stack and found to:
- Substantially duplicate `SMRITI_PLATFORM_VISION.md`, `SMRITI_PRODUCT_CONSTITUTION.md`, and `ARCHITECTURE.md`
- Propose a directory layout (`modules/purchase/`) conflicting with the actual codebase (`purchase_studio/` + `www/`)
- Propose per-module HTML co-location conflicting with Frappe `www/` routing convention

**Decision:** The three genuinely new elements were extracted and integrated into the appropriate existing documents rather than creating a fourth competing constitution.

### Decision 2 — SMRITI_UI_ARCHITECTURE.md as the Companion Document

`SMRITI_EXPERIENCE_CONSTITUTION.md` §Purpose explicitly lists `SMRITI_UI_ARCHITECTURE.md` as a companion document that did not previously exist. This gap was the correct home for the Component Inventory and Document Format Matrix. The new file is set to **DRAFT** status (not LOCKED) pending authority review.

### Decision 3 — Future-State Layout Explicitly Labelled

The per-module HTML co-location pattern from the original proposal is preserved in `SMRITI_UI_ARCHITECTURE.md` §8 (Future-State Layout) but is explicitly marked: *"This is NOT the current standard. Do not create these directories now."* This prevents agent misinterpretation while keeping the architectural aspiration on record for future ADR consideration.

## 6. Design Rationale

- **No new standalone constitution:** Prevents SPC-002 (Single Source of Truth) and SPC-008 (Standing Governance Principle) violations
- **Candidate Article status for SPC-C-012/013:** Correctly reflects that neither the component library nor the Print Studio are yet implemented — they carry no blocking authority until adopted via formal amendment
- **Document Format Matrix as a live tracker:** The `⬜/✅` completion table in `SMRITI_UI_ARCHITECTURE.md` §5.2 gives teams a concrete, maintainable record of print/email coverage across all 13 documents
- **Future-state section in UI Architecture doc:** Preserves the architectural aspiration of per-module HTML without misleading agents into creating conflicting directory structures today

## 7. Implementation Summary

Three changes, executed in sequence:

1. `SMRITI_PRODUCT_CONSTITUTION.md` — Candidate articles table and amendment log updated
2. `SMRITI_EXPERIENCE_CONSTITUTION.md` — Document Experience Constitution section appended before Compliance section
3. `SMRITI_UI_ARCHITECTURE.md` — New file created at repo root

## 8. Tests Executed

No automated tests exist for governance document changes. The following manual verifications were performed:

- `git diff SMRITI_PRODUCT_CONSTITUTION.md` — diff confirmed
- `git diff SMRITI_EXPERIENCE_CONSTITUTION.md` — diff confirmed
- `git add -N SMRITI_UI_ARCHITECTURE.md` then `git diff SMRITI_UI_ARCHITECTURE.md` — full content confirmed

## 9. Verification Results

**Evidence:**

```
git diff SMRITI_PRODUCT_CONSTITUTION.md

+| SPC-C-012 | SMRITI Component Library Standard | UI Components | ...
+| SPC-C-013 | SMRITI Document Format Standard | Business Documents | ...
+| v1.1.0 | 2026-07-08 | Added Candidate Articles SPC-C-012 and SPC-C-013 ...
```

```
git diff SMRITI_EXPERIENCE_CONSTITUTION.md

+## Document Experience Constitution
+### Rule DOC-E1 — Every Business Document Has Five Format Definitions
+### Rule DOC-E2 — Documents Use SMRITI Branding
+### Rule DOC-E3 — Document Language is Business Language
+### Rule DOC-E4 — Print View Is Chrome-Free
+### Rule DOC-E5 — Documents Are Registered
```

```
git diff SMRITI_UI_ARCHITECTURE.md  (new file, 300+ lines)
Confirmed: §1 Precedence, §2 Current File Layout, §3 Module UI Ownership,
§4 Component Inventory, §5 Document Format Matrix, §6 Design System,
§7 Platform Boundary, §8 Future-State Layout, §9 Naming Conventions
```

**Interpretation:** All three files changed as intended. No existing content was removed or modified beyond the two targeted additions to existing files.

**Recommendation:** Jawahar R. Mallah to review `SMRITI_UI_ARCHITECTURE.md` and promote from DRAFT to LOCKED when satisfied, following the same amendment process used for `SMRITI_PLATFORM_VISION.md` v2.0.0.

## 10. Known Limitations

- `SMRITI_UI_ARCHITECTURE.md` is DRAFT — no blocking authority until LOCKED by the architect
- SPC-C-012 and SPC-C-013 are Candidate Articles — no blocking authority until promoted via formal amendment
- The Document Format Completion Tracker (§5.2) reflects the state as of 2026-07-08; it must be updated as Print Studio work progresses
- `SMRITI_EXPERIENCE_CONSTITUTION.md` is listed as LOCKED v1.0.0 — the addition of the Document Experience section constitutes a material amendment and should be formally versioned to v1.1.0 by the architect

## 11. Future Work

- Architect to review and version-bump `SMRITI_EXPERIENCE_CONSTITUTION.md` to v1.1.0
- Architect to review and LOCK `SMRITI_UI_ARCHITECTURE.md`
- Scope and implement Print Studio (prerequisite for SPC-C-013 adoption)
- Scope SMRITI Component Library (prerequisite for SPC-C-012 adoption)
- File ADR if per-module HTML co-location (§8 Future-State Layout) is to be pursued
- Update Document Format Completion Tracker as Print/PDF/Email formats are built per document

## 12. Related ADRs

None currently. An ADR is required before proceeding with the per-module HTML co-location layout described in `SMRITI_UI_ARCHITECTURE.md` §8.

## 13. Related RFCs

None.

---

*Area: Architecture / Governance*
*Version: v1.0.0*
*Date: 2026-07-08*
*Author: AI Architecture Agent*
