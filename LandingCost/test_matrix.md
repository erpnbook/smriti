# SMRITI Landed Cost Allocation — Test Matrix
**Companion to:** SMRITI_Landed_Cost_Spec_v1.md (Revision D) + validation_spec.md
**Purpose:** Each locked rule maps to at least one test case. No rule should ship untested.

| # | Rule (Spec Ref) | Test Case | Expected Result |
|---|---|---|---|
| 1 | Draft/Cancelled Purchase Receipt blocked (3.1) | Create allocation referencing a Draft PR | ValidationError, save blocked |
| 2 | Cross-Company receipts blocked (3.1) | Select 2 receipts from different Companies | ValidationError on save |
| 3 | Cross-Currency receipts blocked (3.1) | Select receipts in INR and USD | ValidationError on save |
| 4 | Draft/Cancelled Purchase Invoice blocked (Rev C) | source_type=Same Vendor Bill, invoice in Draft | ValidationError on save |
| 5 | Same Vendor Bill amount > invoice total | Cost Line amount = ₹10,000, invoice total = ₹8,000 | ValidationError on save |
| 6 | Third Party Bill independence | Submit allocation with Third Party Bill source; later cancel that bill's payment | Allocation document unaffected; no cascade |
| 7 | Manual/No Bill — no payable | source_type=Manual/No Bill, submit allocation | No Purchase Invoice/Payment Entry created anywhere |
| 8 | Weight/Volume not selectable (Rev A/B) | Inspect allocation_basis Select options in UI | Only Value/Qty/Manual present |
| 9 | valuation_basis locked to Purchase Only (Rev A) | Attempt to set valuation_basis = "Landed Inclusive" | Field is read-only; not settable via UI or API in Phase 1 |
| 10 | Stock Ledger untouched (Section 1.1) | Submit allocation, inspect Item valuation_rate before/after | valuation_rate unchanged |
| 11 | Landed Cost % zero-guard (Rev C) | All receipt items rate = 0 (free sample) | landed_cost_percent = 0, no exception raised |
| 12 | Value-basis zero-guard (Rev C) | base_purchase_value = 0, allocation_basis = Value | ValidationError raised, Qty/Manual suggested |
| 13 | Manual allocation — negative row blocked (Rev C) | Enter -50 for one row's manual allocation | ValidationError on submit |
| 14 | Manual allocation — sum mismatch blocked (Rev C) | Manual rows sum to ₹1,980 vs Cost Line amount ₹2,000 (>tolerance) | ValidationError on submit |
| 15 | Manual allocation — sum within tolerance passes | Manual rows sum to ₹2,000.005 vs ₹2,000.00 (tolerance 0.01) | Submit succeeds |
| 16 | Audit Snapshot grain correctness (Rev B) | Allocation with 2 cost components (different bases) across 3 receipt rows for same SKU | 6 distinct snapshot rows (3 rows × 2 components), each with correct allocation_method_used |
| 17 | Audit Snapshot row name stability (Rev D) | Submit allocation; later reorder unrelated rows on the source Purchase Receipt | purchase_receipt_row values in snapshot remain valid references (unaffected by reorder) |
| 18 | Snapshot immutability on Cancel (Rev A/C) | Cancel a submitted allocation | audit_snapshot rows unchanged, not deleted |
| 19 | No re-allocation on Debit Note (Section 1.3) | Create a Debit Note against a receipt that has an existing landed cost allocation | Existing allocation document and its snapshot are completely untouched; no new allocation auto-triggered |
| 20 | Cost Component deletion blocked when referenced (Rev C) | Attempt to delete a Cost Component used in a submitted allocation | ValidationError; deactivate succeeds instead |
| 21 | Cost Component deletion allowed when unreferenced | Delete a Cost Component never used in any submitted allocation | Deletion succeeds |
| 22 | Report default — Inventory Valuation (5.2) | Open Inventory Valuation report, no manual toggle | Shows PURCHASE basis by default |
| 23 | Report default — Margin Analysis (5.2) | Open Margin Analysis report, no manual toggle | Shows LANDED basis by default |
| 24 | BOTH mode delta correctness (5.3) | SKU with Purchase=500, Landed=530 | Delta column shows +30 |
| 25 | get_inventory_cost() contract (Service Freeze) | Call with mode="purchase" and mode="landed" for same item | Returns valuation_rate and estimated_landed_cost_last respectively, no duplicate calc logic elsewhere |
| 26 | Same SKU across multiple receipts in one allocation (Rev B) | Allocate freight across 2 receipts both containing SKU "SHIRT-BLACK-M" at different rates | 2 separate snapshot rows for that SKU, each tied to its own purchase_receipt + row, not blended |

## UAT-Specific (requires real Tattly data — Section 7 checklist items 2, 3, 4)

| # | Scenario | Depends On |
|---|---|---|
| U1 | Real fabric-mill invoice with bundled freight (Same Vendor Bill path) | Checklist #3 — confirm this is Tattly's actual pattern |
| U2 | Real transporter/courier invoice as separate bill (Third Party Bill path) | Checklist #3 |
| U3 | Multiple Tattly users switching Cost Basis Selector in the same session | Checklist #4 — confirms session-only storage is sufficient |
| U4 | Company setup with valuation_basis locked before first live receipt | Checklist #2 |
