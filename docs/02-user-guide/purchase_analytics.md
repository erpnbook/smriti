---
Document ID: "USER-034"
Title: "SMRITI Purchase Analytics — User Guide v1.0"
Owner: "Operations Team"
Audience: "End User"
Module: "SAS"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: "USER-033"
Related Modules: "Purchase Studio"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Purchase Analytics — User Guide

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Date:** 2026-07-02

---

## Overview

SMRITI Analytics Studio (SAS) includes 6 purchase reports covering the complete procurement lifecycle. Access them via:

- **Sidebar → Reports → Purchase Reports**, or
- **Analytics Studio → Purchase** category

---

## Report 1 — Purchase Order Summary

**What it shows:** One row per Purchase Order with balance tracking.

| Column | Description |
|---|---|
| PO Number | ERPNext PO document name |
| Supplier | Supplier name |
| PO Date | Order creation date |
| Grand Total | Total PO value |
| Advance Paid | Amount paid in advance |
| Balance Amount | Grand Total minus Advance Paid |
| Status | Current PO status |

**Key insight:** Use Balance Amount to understand outstanding commitment to suppliers.

**Filters:** From/To Date, Supplier, Status, Project, Company

---

## Report 2 — GRN Register

**What it shows:** All goods received (returns excluded automatically).

| Column | Description |
|---|---|
| GRN Number | Purchase Receipt name |
| Supplier | Receiving from |
| Receiving Date | Date goods arrived |
| Warehouse | Destination warehouse |
| Grand Total | Total received value |
| Status | Completed / Draft |

**Key insight:** Cross-reference with PO Summary to identify undelivered orders.

**Filters:** From/To Date, Supplier, Warehouse, Status, Company

---

## Report 3 — Purchase Invoice Register

**What it shows:** All supplier invoices with payment status and overdue tracking.

| Column | Description |
|---|---|
| Invoice No | SMRITI invoice reference |
| Supplier Bill No | Supplier's own invoice number |
| Supplier | |
| Invoice Date | |
| Due Date | Payment deadline |
| Grand Total | |
| Outstanding | Amount yet to be paid |
| Overdue Days | Days past due date (0 if not overdue) |

**🔴 Overdue Days > 0 are highlighted in red.** Use this to prioritize payments.

**Filters:** From/To Date, Supplier, Status (Unpaid/Overdue/Paid), Company

---

## Report 4 — Supplier Purchase Summary

**What it shows:** Aggregated purchase history per supplier.

| Column | Description |
|---|---|
| Supplier | |
| Invoice Count | Total number of invoices |
| Total Value | Cumulative purchase value |
| Paid Amount | Total paid |
| Outstanding | Total remaining |
| Average Invoice | Mean invoice value |

**📊 Drill-down:** Click any supplier row to open their Invoice Register.

**Use case:** Compare supplier spend, identify top vendors, negotiate terms.

**Filters:** From/To Date, Company

---

## Report 5 — Item-wise Purchase Analysis

**What it shows:** Item-level purchase data with cost analysis.

| Column | Description |
|---|---|
| Item Code | |
| Item Name | |
| Item Group | Category |
| Brand | |
| Total Qty | Total quantity purchased |
| Total Value | Total purchase value |
| Weighted Avg Rate | `Total Value ÷ Total Qty` — true average cost |

> **Why Weighted Average Rate?** A simple average of rates distorts cost when quantities vary. SMRITI uses `SUM(amount) / SUM(qty)` for accurate cost intelligence.

**Filters:** From/To Date, Supplier, Item Group, Brand, Warehouse, Company

---

## Report 6 — Purchase Return Register

**What it shows:** All debit notes / purchase returns with GST breakdown.

| Column | Description |
|---|---|
| Return No | Purchase Receipt (return) name |
| Supplier | |
| Return Date | |
| Taxable Value | Base return value before tax |
| CGST | Central GST amount |
| SGST | State GST amount |
| IGST | Integrated GST (inter-state) |
| Grand Total | Full return value |

**Use case:** Reconcile returns against supplier credit notes. Match IGST/CGST/SGST for GST return filing.

**Filters:** From/To Date

---

## Using Filters

All purchase reports share a common filter panel:

1. Click **🔍 Filters** at the top of the report
2. Set any applicable filters
3. Click **Run Report**

**Date Range:** Leave empty to see all-time data.
**Status:** Leave empty to see all statuses.

---

## Exporting Reports

Every report supports:
- **Excel Export** — Click the Excel icon at the top right
- **Print** — Click the Print icon (opens SMRITI Print Modal)

---

## Interpreting KPIs

Each purchase report shows summary KPIs at the top:

| Report | KPIs Shown |
|---|---|
| PO Summary | Total PO Value, Total Balance, Total Qty |
| Invoice Register | Grand Total, Paid Amount, Outstanding |
| Supplier Summary | Total Value, Outstanding |
| Item Analysis | Total Qty, Total Value |
| Return Register | Total Returns Value |

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
