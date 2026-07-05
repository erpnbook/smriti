---
Document ID: "ARCH-SAS-001"
Title: "SMRITI Analytics Studio (SAS) — Architecture Document v1.0"
Owner: "Architecture Team"
Audience: "Architect"
Module: "SAS"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: "Purchase Studio, Inventory, Sales"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Analytics Studio (SAS) — Architecture Document

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Release:** v2.0.0 | **Date:** 2026-07-02

---

## Purpose

The SMRITI Analytics Studio (SAS) is a unified report execution engine that:
1. Provides a single `/run_report` API surface for all SMRITI reports
2. Separates SQL logic (REPORT_QUERIES) from metadata (SAS_REPORT_DEFAULTS)
3. Delivers structured responses to the SAS frontend (data + columns + chart + KPIs)
4. Enforces explainability (ⓘ button) per Rule 10 (DOC-01)

SAS is **read-only**. It never mutates any business data.

---

## Architecture Diagram

```
SMRITI Analytics Studio Frontend
smriti-analytics-studio.html
        │
        │  frappe.call("reports_api.run_report", {report_key, filters})
        ▼
reports_api.py
  ├── REPORT_QUERIES dict       ← SQL templates (with filter placeholders)
  ├── REPORT_COLUMNS dict       ← Column definitions
  ├── _run_sql_report()         ← Filter injection + frappe.db.sql()
  └── _run_custom_report()      ← For non-SQL / dataset-based reports
        │
        │  (dispatches to)
        ▼
sas_service.py
  ├── SAS_REPORT_DEFAULTS dict  ← Metadata: chart type, KPI fields, conditional rules
  ├── get_srs_report_list_for_sas()  ← Returns catalog for sidebar
  └── get_report_explain()      ← Returns transparency documentation
        │
        ▼
Response: { data, columns, chart, kpis, total_rows }
```

---

## Component Responsibilities

### reports_api.py

- **REPORT_QUERIES** — Dict of `report_key → SQL template string`. Uses `{filter_name}` placeholders.
- **REPORT_COLUMNS** — Dict of `report_key → list of column dicts` (label, fieldname, fieldtype, width).
- **_run_sql_report()** — Injects filters, calls `frappe.db.sql()`, applies pagination.
- **run_report()** — Public whitelisted entry point. Routes to `_run_sql_report()` or `_run_custom_report()`.

### sas_service.py

- **SAS_REPORT_DEFAULTS** — Dict of `report_key → metadata`. Contains: chart_type, kpi_fields, conditional_rules, explain_enabled, category.
- **get_srs_report_list_for_sas()** — Aggregates all enabled reports grouped by category. Used by the SAS sidebar.
- **get_report_explain()** — Returns the transparency metadata for the ⓘ explain modal.

### Fixtures

- **smriti_report_template.json** — DocType fixture for SMRITI Report Template. Contains columns_json and filters_json per template.
- **seed_purchase_report_templates.py** — Idempotent seed patch. Uses `frappe.get_doc().save()` with upsert pattern.

---

## Filter Injection Design

The filter engine avoids dynamic SQL injection by using positional placeholders:

```python
# Template
query = """
    SELECT ... FROM tabPurchase Order t
    WHERE t.docstatus = 1
    {company_filter}
    {date_filter}
"""

# Injection
if filters.get("company"):
    company_filter = "AND t.company = %(company)s"
    values["company"] = filters["company"]
else:
    company_filter = ""

final_query = query.format(company_filter=company_filter, ...)
frappe.db.sql(final_query, values)  # ← parameterized, not interpolated
```

User-supplied values are **always** passed as parameters to `frappe.db.sql()`, never as string format arguments.

---

## Report Catalog Architecture

The SAS sidebar catalog is built at runtime by `get_srs_report_list_for_sas()`:

1. Reads all enabled `SMRITI Report Template` records from DB
2. Merges with `SAS_REPORT_DEFAULTS` metadata
3. Groups by category
4. Returns sorted dict: `{"Purchase": [...], "Sales": [...], ...}`

This means adding a new report requires:
- Entry in `REPORT_QUERIES`
- Entry in `SAS_REPORT_DEFAULTS`
- A `SMRITI Report Template` DB record (via fixture or seed patch)

---

## v2.0.0 SAS Inventory

| Category | Reports | Total |
|---|---|---|
| Purchase | PO Summary, GRN Register, Invoice Register, Supplier Summary, Item Analysis, Return Register | 6 |
| Sales | Item-wise Sales, Daily Summary | 2 |
| Inventory Analytics | Stock Position, Style Stock, Size Stock, SKU Productivity, PSV Reorder | 5 |
| Cash | Cash Reconciliation, Z-Report, Payment Mode Summary | 3 |
| Accounting | Customer Outstanding, Supplier Outstanding, Payment Register, Receipt Register, Cash Book, Day Book | 6 |
| Audit | Security Audit Log, Address Change Log | 2 |
| **Total** | | **24** |

---

## Governance Compliance

| Rule | Compliance |
|---|---|
| Rule 10 (DOC-01) — Explainability | `explain_enabled` flag per report; ⓘ modal renders transparency docs |
| Rule 11 (DOC-02) — Formula Registry | KPI formulas registered in `kgf_formula_registry.md` |
| SMRITI Architecture Rule 2 (Service-First) | Frontend → `run_report` API → `_run_sql_report` → DB |
| SMRITI Architecture Rule 3 (Inventory-First) | All stock-related reports read from ERPNext Stock Ledger |
| SMRITI Architecture Rule 5 (Single Source of Truth) | Each report key maps to exactly one query + one metadata entry |

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
*"Always decision-ready."*
