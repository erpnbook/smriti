---
Document ID: "SMRITI-ARCH-006"
Title: "Sprint 005 Architecture Proposal"
Owner: "Product Team"
Audience: "Architect"
Module: "Core"
Version: "1.0.0"
Status: "Draft"
Primary Document: "No"
Depends On: ""
Related Modules: ""
Last Updated: "2026-07-04"
Last Reviewed: "2026-07-04"
AI Generated: "No"
Reviewed By: "Jawahar R. Mallah"
---

# Sprint SDC-005: Knowledge Governance & Support Intelligence
## Architectural Blueprint & Proposal

* **Author**: Jawahar R. Mallah
* **Designation**: Founder & Chief Architect
* **Organization**: AITDL – AI Technology & Development Lab
* **Date**: 2026-06-25
* **Version**: 1.0.0
* **Status**: Proposed

> "Always decision-ready."
> 
> — Jawahar R. Mallah
> Founder & Chief Architect, AITDL

---

## 1. Architectural Foundation & Separation of Concerns

Enforcing the constitution **AI-GOV-01** and the architectural verdict:
* **SDC (Compiler Layer)**: Performs static repository analysis and generates deterministic IR inventories.
* **SKE (Retrieval Layer)**: Acts as the single source of truth and executes graph traverses/lookups.
* **AI Context Builder (Orchestrator)**: Constructs high-density, safety-guarded Markdown context packs.
* **LLM (Narration Layer)**: Formats the response, never generating facts or credentials independent of the SKE Ground Truth.

---

## 2. Proposed Modules for Sprint SDC-005

```
     Repository Code Shift
              │
              ▼
    Knowledge Diff Engine (Static Scan) ──► Mark Stale Context Packs
              │
              ▼
   Knowledge Coverage Dashboard ─────────► Measure Completeness %
              │
              ▼
     Support Intelligence ───────────────► Ticket Matcher & SOP Suggester
```

### A. Module 1: Knowledge Coverage Dashboard
Measure completeness of repository metadata and documentation per module (Item Master, Barcode, Billing, PSV, etc.).

#### 1. Completeness Formula
The completeness score for any module $M$ is defined as:
$$Coverage(M) = \frac{W_f \cdot F_{doc} + W_a \cdot A_{doc} + W_g \cdot G_{linked} + W_t \cdot T_{attached}}{W_f + W_a + W_g + W_t}$$

Where:
* $F_{doc}$: % of custom fields containing `business_description` and validation rules.
* $A_{doc}$: % of whitelisted APIs containing documentation, worked examples, and DB references.
* $G_{linked}$: % of glossary terms mapped to code dependencies.
* $T_{attached}$: % of error codes and screens having troubleshooting SOPs.
* $W$: Weight metrics (e.g. fields: 30%, APIs: 20%, glossary: 20%, troubleshooting: 30%).

#### 2. Coverage Targets
* **Item Master**: Target 100%
* **Barcode Studio**: Target 100%
* **Billing / Purchase / Inventory**: Target 80%+
* **PSV / CGE / PDT**: Target 80%+

---

### B. Module 2: Knowledge Diff Engine (Staleness Checks)
Detects drift between the static code/schema and the compiled SKE IR files. If a DocType schema or python controller undergoes modification:
* Computes file checksums during commit/build.
* Flags corresponding manuals, FAQs, and AI context cache entries as `STALE`.
* Restricts AI Chat Drawer from serving stale context packs until SDC compiler re-scans the repository.

---

### C. Module 3: Support Intelligence
Bridges real-world support ticket queries with the SKE knowledge base to auto-suggest resolution SOPs.

#### 1. Support Mapping Flow
1. Incident ticket received (e.g., `ERR-PRN-029: Print terminal timeout`).
2. SKE maps the error code or query terms to the Barcode Studio reprint queue schema (`print_job_id`, `warehouse_id`).
3. SKE retrieves the matching Troubleshooting SOP (e.g., printer routing steps, driver checks).
4. AI Chat drawer renders the suggested SOP alongside the exact SKE Ground Truth Evidence Badge.

---

## 3. Draft Schema Definitions

### A. Coverage Inventory Schema (`sdc/schemas/knowledge_coverage.schema.json`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SMRITI Knowledge Coverage Schema",
  "type": "object",
  "properties": {
    "module_id": { "type": "string" },
    "module_name": { "type": "string" },
    "coverage_percentage": { "type": "number", "minimum": 0, "maximum": 100 },
    "metrics": {
      "type": "object",
      "properties": {
        "fields_documented": { "type": "integer" },
        "fields_total": { "type": "integer" },
        "apis_documented": { "type": "integer" },
        "apis_total": { "type": "integer" },
        "troubleshooting_sops": { "type": "integer" }
      },
      "required": ["fields_documented", "fields_total", "apis_documented", "apis_total"]
    }
  },
  "required": ["module_id", "module_name", "coverage_percentage", "metrics"]
}
```

---

## 4. Next Steps
* Create task lists and define milestones for SDC-005.
* Implement static coverage computation in `sdc/discovery.py`.
* Implement Whitelisted Coverage dashboard UI in SMRITI.
