# ADR-001: Purchase Invoice Creation Policy — Configurable (Option C)

**Status:** ACCEPTED  
**Date:** 2026-07-01  
**Decider:** Jawahar R. Mallah, Founder & Chief Architect, AITDL  
**SSDL Phase:** 2 — Capability Ownership Map (SPC-011 Conflict Escalation)  
**Related Standard:** AES-002 SSDL v1.0.0 | SPC-009 | SPC-011

---

## Context

During Phase 2 (Capability Ownership Map) of SMRITI Purchase Studio, three technically
valid implementations were identified for Purchase Invoice creation. Per SPC-011, the
agent stopped and escalated to the human architect for resolution.

**Conflict:** Should Purchase Invoice creation in SMRITI be:
- Option A — Only from GRN (strict retail chain: PO → GRN → PI → Payment)
- Option B — Standalone only (direct supplier invoice, no PO/GRN required)
- Option C — Configurable per company (business-driven policy)

## Decision

**Option C — Configurable per Company** is adopted.

Default configuration: **Both** (GRN-linked and Standalone are both permitted).

## Business Rationale

SMRITI Retail OS serves multiple business types, each with a different purchase workflow:

| Business Type | Workflow | PI Creation Mode |
|---|---|---|
| Fashion / Footwear Retail | PO → GRN → PI → Payment | GRN Only |
| Small Retailer | Supplier Invoice → PI → Stock → Payment | Standalone |
| Distributor | PO → Multiple GRNs → Single PI → Payment | GRN Only |
| General Retail | Mixed (both modes active) | Both (Default) |

No single mode is correct for all SMRITI customers. The policy must be a business
decision made per company, not a framework assumption.

## Implementation Specification

A new DocType or Single document shall be created:

```
SMRITI Purchase Settings
  purchase_invoice_policy: Select
    Options:
      - grn_only    (label: "GRN Only — Invoice must reference a GRN")
      - standalone  (label: "Standalone — Invoice created independently")
      - both        (label: "Both — GRN-linked and Standalone permitted")
    Default: both
```

The `purchase_service.py` `create_invoice()` method shall read this setting at runtime
and enforce the policy:
- If `grn_only` and no GRN reference → raise validation error
- If `standalone` and GRN reference provided → raise validation error (optional, TBD)
- If `both` → accept either mode

## Consequences

**Positive:**
- SMRITI can serve retail, distribution, and hybrid businesses from a single codebase
- Policy is explicit and auditable — no implicit framework defaults
- Changing the policy requires zero code changes

**Negative:**
- Adds one configuration step per company during onboarding
- `purchase_service.py` must check policy on every invoice creation call

## SPC-011 Resolution

This decision resolves the ownership conflict identified in Phase 2.
The conflict is now closed. Phase 3 (Business Workflow) may proceed.

## Revision History

| Date | Change | Author |
|---|---|---|
| 2026-07-01 | Initial decision | Jawahar R. Mallah |
