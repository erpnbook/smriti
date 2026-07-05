---
Document ID: "DEV-SAS-001"
Title: "SMRITI Analytics Studio (SAS) — Developer Guide v1.0"
Owner: "Development Team"
Audience: "Developer"
Module: "SAS"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: "ARCH-SAS-001"
Related Modules: "Purchase Studio, Inventory, Sales"
Last Updated: "2026-07-02"
Last Reviewed: "2026-07-02"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Analytics Studio (SAS) — Developer Guide

**Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
**Version:** 1.0.0 | **Release:** v2.0.0 | **Date:** 2026-07-02

---

## Architecture Overview

```
SAS Frontend (smriti-analytics-studio.html)
        ↓  frappe.call("run_report", {report_key, filters})
reports_api.py → _run_sql_report(report_key, filters)
        ↓
REPORT_QUERIES[report_key]   ← SQL with filter injection
        ↓
sas_service.py → SAS_REPORT_DEFAULTS[report_key]  ← Metadata
        ↓
Response: {data, columns, chart, kpis}
```

---

## Key Files

| File | Responsibility |
|---|---|
| `smriti_retail_os/reports_api.py` | SQL queries, filter engine, report dispatch |
| `smriti_retail_os/analytics_studio/sas_service.py` | Report metadata, KPI definitions, defaults |
| `smriti_retail_os/fixtures/smriti_report_template.json` | DocType fixture for SMRITI Report Template |
| `smriti_retail_os/patches/seed_purchase_report_templates.py` | Idempotent DB seed patch |

---

## How to Add a New Report — Step-by-Step

### Step 1 — Write the SQL Query

In `reports_api.py`, add to the `REPORT_QUERIES` dict:

```python
REPORT_QUERIES = {
    # ... existing entries ...
    "my_new_report": """
        SELECT
            t.name        AS doc_name,
            t.supplier    AS supplier,
            t.grand_total AS grand_total
        FROM `tabPurchase Order` t
        WHERE
            t.docstatus = 1
            {company_filter}
            {date_filter}
            {supplier_filter}
        ORDER BY t.creation DESC
    """,
}
```

**Filter placeholders available:**

| Placeholder | Injected When |
|---|---|
| `{company_filter}` | `company` param present |
| `{date_filter}` | `from_date`/`to_date` present |
| `{supplier_filter}` | `supplier` param present |
| `{warehouse_filter}` | `warehouse` param present |
| `{status_filter}` | `status` param present |
| `{item_group_filter}` | `item_group` param present |
| `{brand_filter}` | `brand` param present |

> **SQL safety:** Filter values are parameterized via `frappe.db.sql(query, values)`. Never interpolate user input directly.

### Step 2 — Define Columns

In `reports_api.py`, add to `REPORT_COLUMNS`:

```python
REPORT_COLUMNS = {
    "my_new_report": [
        {"label": "Document", "fieldname": "doc_name", "fieldtype": "Data", "width": 140},
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Data", "width": 160},
        {"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
    ],
}
```

### Step 3 — Add SAS Metadata

In `sas_service.py`, add to `SAS_REPORT_DEFAULTS`:

```python
SAS_REPORT_DEFAULTS = {
    # ... existing entries ...
    "my_new_report": {
        "report_name": "SMRITI My New Report",
        "category": "Purchase",   # Must match an existing category key
        "has_chart": True,
        "chart_type": "bar",
        "chart_x_field": "supplier",
        "chart_y_fields": ["grand_total"],
        "has_kpi": True,
        "kpi_fields": [
            {"label": "Total Value", "fieldname": "grand_total",
             "aggregate": "sum", "fieldtype": "Currency"},
        ],
        "conditional_rules": [],
        "explain_enabled": True,
    },
}
```

**Category values:** `"Purchase"`, `"Sales"`, `"Inventory Analytics"`, `"Cash"`, `"Accounting"`, `"Audit"`

### Step 4 — Add Fixture Record

In `fixtures/smriti_report_template.json`, add a new entry:

```json
{
  "doctype": "SMRITI Report Template",
  "name": "SMRITI My New Report",
  "report_key": "my_new_report",
  "category": "Purchase",
  "is_active": 1,
  "columns_json": "[...]",
  "filters_json": "[...]"
}
```

### Step 5 — Seed the Template

```bash
bench --site smriti_retail execute \
  smriti_retail_os.patches.seed_purchase_report_templates.execute
```

Or add it to the seed script for auto-execution during `bench migrate`.

### Step 6 — Write a Test

```python
# In tests/test_purchase_studio.py
def test_my_new_report(self):
    result = frappe.call(
        "smriti_retail_os.reports_api.run_report",
        report_key="my_new_report",
        from_date="2026-01-01",
        to_date="2026-12-31"
    )
    self.assertIn("data", result)
    self.assertIn("columns", result)
    self.assertIn("kpis", result)
```

---

## Filter Engine Internals

The filter engine in `_run_sql_report()` works as follows:

```python
def _run_sql_report(report_key, filters):
    query_template = REPORT_QUERIES[report_key]
    conditions = {}

    if filters.get("company"):
        conditions["company_filter"] = "AND t.company = %(company)s"
    else:
        conditions["company_filter"] = ""

    if filters.get("from_date") and filters.get("to_date"):
        conditions["date_filter"] = "AND t.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    else:
        conditions["date_filter"] = ""

    # ... etc for each filter

    final_query = query_template.format(**conditions)
    data = frappe.db.sql(final_query, filters, as_dict=True)
    return data
```

---

## Conditional Formatting

To highlight cells based on value:

```python
"conditional_rules": [
    {
        "field": "overdue_days",
        "condition": "gt",       # gt, lt, eq, ne, gte, lte
        "value": 0,
        "style": "color: red; font-weight: bold;"
    }
]
```

The SAS frontend applies these rules when rendering the data table.

---

## Report Categories

Categories are defined in `sas_service.py → get_srs_report_list_for_sas()`. To add a new category:

```python
REPORT_CATEGORIES = ["Purchase", "Sales", "Inventory Analytics", "Cash", "Accounting", "Audit", "MyNewCategory"]
```

Then assign `"category": "MyNewCategory"` in the report's `SAS_REPORT_DEFAULTS` entry.

---

*Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL*
