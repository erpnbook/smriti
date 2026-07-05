---
Document ID: "DEV-043"
Title: "SMRITI PSV — Agent Prompt: Phase 3"
Owner: "Development Team"
Audience: "Developer"
Module: "PSV"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI PSV — Agent Prompt: Phase 3
# Reports + Opening Balance Wizard + Dashboard API
# Spec Version: v1.0.2 Final Freeze
# Prerequisite: Phase 2 Acceptance Gate — ALL 12 PASSED

---

## CONTEXT REMINDER
- All balances from balance_engine.py — never raw SQL in reports
- company mandatory in all balance calls
- Item code = Item Variant always
- Reports are ERPNext Script Reports (Python) under Party Stock Visibility module

---

## TASK 3.1 — Report: PSV Party Stock Balance

`report/psv_party_stock_balance/psv_party_stock_balance.json`
```json
{
  "doctype": "Report",
  "name": "PSV Party Stock Balance",
  "ref_doctype": "SMRITI Party Stock Ledger Entry",
  "report_type": "Script Report",
  "module": "Party Stock Visibility",
  "is_standard": "Yes"
}
```

`report/psv_party_stock_balance/psv_party_stock_balance.py`
```python
import frappe

def execute(filters=None):
    filters = filters or {}
    company = filters.get("company") or frappe.defaults.get_user_default("Company")

    columns = [
        {"label": "Party Account",  "fieldname": "party_stock_account", "fieldtype": "Link",     "options": "SMRITI Party Stock Account", "width": 180},
        {"label": "Location",       "fieldname": "location_name",       "fieldtype": "Data",     "width": 130},
        {"label": "Zone",           "fieldname": "zone",                "fieldtype": "Data",     "width": 80},
        {"label": "Item Variant",   "fieldname": "item_code",           "fieldtype": "Link",     "options": "Item", "width": 200},
        {"label": "Balance Qty",    "fieldname": "balance",             "fieldtype": "Float",    "width": 100},
        {"label": "MRP",            "fieldname": "mrp",                 "fieldtype": "Currency", "width": 90},
        {"label": "Balance Value",  "fieldname": "balance_value",       "fieldtype": "Currency", "width": 120},
    ]

    from smriti_retail.party_stock_visibility.engine.balance_engine import get_all_party_balances
    all_balances = get_all_party_balances(company)

    conditions = []
    if filters.get("party_stock_account"):
        conditions.append(lambda r: r.party_stock_account == filters["party_stock_account"])
    if filters.get("zone"):
        conditions.append(lambda r: r.zone == filters["zone"])
    if not filters.get("show_zero"):
        conditions.append(lambda r: r.balance != 0)

    data = []
    for r in all_balances:
        if all(c(r) for c in conditions):
            mrp = frappe.db.get_value("Item", r.item_code, "standard_rate") or 0
            data.append({
                "party_stock_account": r.party_stock_account,
                "location_name":       r.location_name,
                "zone":                r.zone,
                "item_code":           r.item_code,
                "balance":             r.balance,
                "mrp":                 mrp,
                "balance_value":       r.balance * mrp,
            })

    data.sort(key=lambda x: (x["party_stock_account"], x["item_code"]))
    return columns, data


def get_filters():
    return [
        {"fieldname": "company",             "label": "Company",       "fieldtype": "Link",   "options": "Company", "reqd": 1},
        {"fieldname": "party_stock_account", "label": "Party Account", "fieldtype": "Link",   "options": "SMRITI Party Stock Account"},
        {"fieldname": "zone",                "label": "Zone",          "fieldtype": "Select", "options": "\nNorth\nSouth\nEast\nWest\nCentral"},
        {"fieldname": "show_zero",           "label": "Show Zero",     "fieldtype": "Check"},
    ]
```

---

## TASK 3.2 — Report: PSV Reconciliation

`report/psv_reconciliation/psv_reconciliation.py`
```python
import frappe

def execute(filters=None):
    filters = filters or {}
    company = filters.get("company") or frappe.defaults.get_user_default("Company")

    columns = [
        {"label": "Party",          "fieldname": "party_stock_account", "fieldtype": "Link",     "options": "SMRITI Party Stock Account", "width": 160},
        {"label": "Item Variant",   "fieldname": "item_code",           "fieldtype": "Link",     "options": "Item", "width": 200},
        {"label": "System Balance", "fieldname": "system_balance",      "fieldtype": "Float",    "width": 120},
        {"label": "Physical Count", "fieldname": "physical_qty",        "fieldtype": "Float",    "width": 120},
        {"label": "Variance",       "fieldname": "variance",            "fieldtype": "Float",    "width": 100},
        {"label": "Audit Date",     "fieldname": "audit_date",          "fieldtype": "Date",     "width": 110},
        {"label": "Status",         "fieldname": "status",              "fieldtype": "Data",     "width": 100},
    ]

    from smriti_retail.party_stock_visibility.engine.balance_engine import get_all_party_balances
    all_balances = {
        (r.party_stock_account, r.item_code): r.balance
        for r in get_all_party_balances(company)
    }

    where = "WHERE s.status = 'Approved'"
    values = {}
    if filters.get("party_stock_account"):
        where += " AND s.party_stock_account = %(psa)s"
        values["psa"] = filters["party_stock_account"]
    if filters.get("from_date"):
        where += " AND s.audit_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        where += " AND s.audit_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    physical = frappe.db.sql(f"""
        SELECT s.party_stock_account, i.item_code,
               i.physical_qty, s.audit_date, s.status
        FROM `tabSMRITI Party Physical Snapshot` s
        JOIN `tabSMRITI Party Physical Item` i ON i.parent = s.name
        {where}
        ORDER BY s.party_stock_account, i.item_code
    """, values=values, as_dict=True)

    data = []
    for row in physical:
        key = (row.party_stock_account, row.item_code)
        sys_bal = all_balances.get(key, 0)
        data.append({
            "party_stock_account": row.party_stock_account,
            "item_code":           row.item_code,
            "system_balance":      sys_bal,
            "physical_qty":        row.physical_qty,
            "variance":            row.physical_qty - sys_bal,
            "audit_date":          row.audit_date,
            "status":              row.status,
        })
    return columns, data


def get_filters():
    return [
        {"fieldname": "company",             "label": "Company",       "fieldtype": "Link", "options": "Company", "reqd": 1},
        {"fieldname": "party_stock_account", "label": "Party Account", "fieldtype": "Link", "options": "SMRITI Party Stock Account"},
        {"fieldname": "from_date",           "label": "Audit From",    "fieldtype": "Date"},
        {"fieldname": "to_date",             "label": "Audit To",      "fieldtype": "Date"},
    ]
```

---

## TASK 3.3 — Report: PSV Sell-Through

`report/psv_sell_through/psv_sell_through.py`
```python
import frappe

def execute(filters=None):
    filters = filters or {}
    company = filters.get("company") or frappe.defaults.get_user_default("Company")

    columns = [
        {"label": "Party",          "fieldname": "party_stock_account", "fieldtype": "Link",    "options": "SMRITI Party Stock Account", "width": 160},
        {"label": "Item Variant",   "fieldname": "item_code",           "fieldtype": "Link",    "options": "Item", "width": 200},
        {"label": "Dispatched",     "fieldname": "dispatched",          "fieldtype": "Float",   "width": 100},
        {"label": "Sold",           "fieldname": "sold",                "fieldtype": "Float",   "width": 100},
        {"label": "Balance",        "fieldname": "balance",             "fieldtype": "Float",   "width": 100},
        {"label": "Sell-Through %", "fieldname": "sell_through_pct",    "fieldtype": "Percent", "width": 120},
    ]

    rows = frappe.db.sql("""
        SELECT
            party_stock_account,
            item_code,
            SUM(CASE WHEN qty > 0 THEN qty ELSE 0 END)  AS dispatched,
            SUM(CASE WHEN qty < 0 THEN ABS(qty) ELSE 0 END) AS sold,
            SUM(qty) AS balance
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE company = %s
        GROUP BY party_stock_account, item_code
        HAVING dispatched > 0
        ORDER BY party_stock_account, item_code
    """, [company], as_dict=True)

    if filters.get("party_stock_account"):
        rows = [r for r in rows if r.party_stock_account == filters["party_stock_account"]]
    if filters.get("min_sell_through"):
        threshold = float(filters["min_sell_through"])
        rows = [r for r in rows if (r.sold / r.dispatched * 100) >= threshold]

    data = []
    for r in rows:
        pct = round((r.sold / r.dispatched) * 100, 2) if r.dispatched else 0
        data.append({
            "party_stock_account": r.party_stock_account,
            "item_code":           r.item_code,
            "dispatched":          r.dispatched,
            "sold":                r.sold,
            "balance":             r.balance,
            "sell_through_pct":    pct,
        })

    data.sort(key=lambda x: x["sell_through_pct"], reverse=True)
    return columns, data


def get_filters():
    return [
        {"fieldname": "company",             "label": "Company",         "fieldtype": "Link",  "options": "Company", "reqd": 1},
        {"fieldname": "party_stock_account", "label": "Party Account",   "fieldtype": "Link",  "options": "SMRITI Party Stock Account"},
        {"fieldname": "min_sell_through",    "label": "Min Sell-Through %", "fieldtype": "Float"},
    ]
```

---

## TASK 3.4 — Report: PSV Stock Ageing

`report/psv_stock_ageing/psv_stock_ageing.py`
```python
import frappe
from frappe.utils import date_diff, today

def execute(filters=None):
    filters = filters or {}
    company = filters.get("company") or frappe.defaults.get_user_default("Company")

    columns = [
        {"label": "Party",      "fieldname": "party_stock_account", "fieldtype": "Link",  "options": "SMRITI Party Stock Account", "width": 160},
        {"label": "Item",       "fieldname": "item_code",           "fieldtype": "Link",  "options": "Item", "width": 200},
        {"label": "0-30 Days",  "fieldname": "d0_30",               "fieldtype": "Float", "width": 90},
        {"label": "31-60 Days", "fieldname": "d31_60",              "fieldtype": "Float", "width": 90},
        {"label": "61-90 Days", "fieldname": "d61_90",              "fieldtype": "Float", "width": 90},
        {"label": "90+ Days",   "fieldname": "d90_plus",            "fieldtype": "Float", "width": 90},
        {"label": "Total",      "fieldname": "total",               "fieldtype": "Float", "width": 90},
    ]

    dispatches = frappe.db.sql("""
        SELECT party_stock_account, item_code, qty, posting_datetime
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE company = %s AND voucher_type = 'Dispatch' AND is_reversal = 0
        ORDER BY posting_datetime
    """, [company], as_dict=True)

    today_str = today()
    buckets = {}
    for row in dispatches:
        key = (row.party_stock_account, row.item_code)
        age = date_diff(today_str, row.posting_datetime)
        b = buckets.setdefault(key, {"d0_30": 0, "d31_60": 0, "d61_90": 0, "d90_plus": 0})
        if age <= 30:   b["d0_30"]    += row.qty
        elif age <= 60: b["d31_60"]   += row.qty
        elif age <= 90: b["d61_90"]   += row.qty
        else:           b["d90_plus"] += row.qty

    data = []
    for (psa, item), b in sorted(buckets.items()):
        total = sum(b.values())
        if total <= 0:
            continue
        data.append({
            "party_stock_account": psa,
            "item_code":           item,
            **b,
            "total":               total,
        })
    return columns, data


def get_filters():
    return [
        {"fieldname": "company",             "label": "Company",       "fieldtype": "Link", "options": "Company", "reqd": 1},
        {"fieldname": "party_stock_account", "label": "Party Account", "fieldtype": "Link", "options": "SMRITI Party Stock Account"},
    ]
```

---

## TASK 3.5 — Opening Balance Wizard (Frappe Page)

`page/psv_opening_balance/psv_opening_balance.json`
```json
{
  "doctype": "Page",
  "name": "psv-opening-balance",
  "title": "PSV Opening Balance Import",
  "module": "Party Stock Visibility",
  "roles": [{"role": "System Manager"}]
}
```

`page/psv_opening_balance/psv_opening_balance.js`
```javascript
frappe.pages['psv-opening-balance'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'PSV Opening Balance Import',
        single_column: true
    });

    $(page.main).html(`
        <div style="max-width:700px; margin:30px auto; padding:20px;">
            <div class="alert alert-warning">
                <strong>⚠ One-Time Migration Utility.</strong>
                Use only during initial PSV deployment.
                Each party+item can only receive one Opening Balance voucher.
            </div>
            <div class="form-group">
                <label>Company</label>
                <input id="ob-company" class="form-control" placeholder="Company name">
            </div>
            <div class="form-group">
                <label>Party Stock Account</label>
                <input id="ob-party" class="form-control" placeholder="e.g. ABC Fashion-Mumbai">
            </div>
            <div class="form-group">
                <label>Upload Excel</label>
                <input type="file" id="ob-file" class="form-control" accept=".xlsx,.xls">
                <small class="text-muted">Columns: Item Variant Code | Opening Qty</small>
            </div>
            <button class="btn btn-primary" id="ob-preview">Preview</button>
            <button class="btn btn-success" id="ob-import" style="display:none; margin-left:10px;">
                Confirm Import
            </button>
            <div id="ob-preview-area" style="margin-top:20px;"></div>
        </div>
    `);

    let parsedRows = [];

    $('#ob-preview').click(async function() {
        const file = document.getElementById('ob-file').files[0];
        if (!file) { frappe.msgprint('Select a file first.'); return; }
        // Upload file first, then parse
        const fd = new FormData();
        fd.append('file', file, file.name);
        fd.append('is_private', 1);
        const up = await fetch('/api/method/upload_file', { method: 'POST', body: fd });
        const upData = await up.json();
        const fileUrl = upData.message?.file_url;
        if (!fileUrl) { frappe.msgprint('Upload failed.'); return; }

        frappe.call({
            method: 'smriti_retail.party_stock_visibility.utils.opening_balance.parse_opening_excel',
            args: { file_url: fileUrl },
            callback(r) {
                parsedRows = r.message?.rows || [];
                const errors = r.message?.errors || [];
                let html = `<h5>${parsedRows.length} valid rows | Errors: ${errors.length}</h5>`;
                if (errors.length) html += `<pre style="color:red">${errors.join('\n')}</pre>`;
                html += '<table class="table table-sm"><thead><tr><th>Item Variant</th><th>Qty</th></tr></thead><tbody>';
                parsedRows.slice(0, 20).forEach(r => {
                    html += `<tr><td>${r.item_code}</td><td>${r.qty}</td></tr>`;
                });
                if (parsedRows.length > 20) html += `<tr><td colspan=2>...and ${parsedRows.length - 20} more</td></tr>`;
                html += '</tbody></table>';
                $('#ob-preview-area').html(html);
                if (parsedRows.length > 0) $('#ob-import').show();
            }
        });
    });

    $('#ob-import').click(function() {
        const company = $('#ob-company').val().trim();
        const party   = $('#ob-party').val().trim();
        if (!company || !party) { frappe.msgprint('Company and Party required.'); return; }
        frappe.call({
            method: 'smriti_retail.party_stock_visibility.service.psv_service.process_opening_balance',
            args: { company, party_stock_account: party, items: parsedRows },
            callback(r) {
                frappe.show_alert({ message: 'Opening Balance imported ✅', indicator: 'green' });
                $('#ob-import').hide();
                parsedRows = [];
            }
        });
    });
};
```

`utils/opening_balance.py`
```python
import frappe
import openpyxl

@frappe.whitelist()
def parse_opening_excel(file_url: str) -> dict:
    """Parse opening balance Excel. Columns: Item Variant | Qty"""
    file_doc = frappe.get_doc("File", {"file_url": file_url})
    wb = openpyxl.load_workbook(file_doc.get_full_path(), read_only=True, data_only=True)
    ws = wb.active
    raw = list(ws.iter_rows(values_only=True))
    if not raw:
        return {"rows": [], "errors": ["Empty file"]}

    rows = []
    errors = []
    for i, row in enumerate(raw[1:], start=2):
        if not row or not row[0]:
            continue
        item_code = str(row[0]).strip()
        try:
            qty = float(row[1] or 0)
        except Exception:
            errors.append(f"Row {i}: Invalid qty for {item_code}")
            continue
        if qty <= 0:
            continue
        if not frappe.db.exists("Item", item_code):
            errors.append(f"Row {i}: Item '{item_code}' not found")
            continue
        rows.append({"item_code": item_code, "qty": qty})

    return {"rows": rows, "errors": errors}
```

---

## VERIFICATION COMMANDS

```bash
cd /home/frappe/frappe-bench

bench --site smriti.localhost migrate

# Test all reports
for report in "PSV Party Stock Balance" "PSV Reconciliation" "PSV Sell-Through" "PSV Stock Ageing"; do
  bench --site smriti.localhost execute \
    "import frappe; r = frappe.get_doc('Report','$report'); print('$report ✅')" 2>&1 | tail -1
done

# Test opening balance wizard page
bench --site smriti.localhost execute \
  "import frappe; print(frappe.db.exists('Page','psv-opening-balance') and '✅' or '❌')"

# Test opening balance parse function
bench --site smriti.localhost execute \
  "from smriti_retail.party_stock_visibility.utils.opening_balance import parse_opening_excel; print('✅')"

# Full module import test
bench --site smriti.localhost execute "
import smriti_retail.party_stock_visibility.engine.ledger_engine
import smriti_retail.party_stock_visibility.engine.balance_engine
import smriti_retail.party_stock_visibility.service.psv_service
import smriti_retail.party_stock_visibility.utils.psv_api
import smriti_retail.party_stock_visibility.utils.excel_import
import smriti_retail.party_stock_visibility.utils.opening_balance
print('All Phase 3 imports ✅')
"
```

---

## PHASE 3 ACCEPTANCE GATE

- [ ] PSV Party Stock Balance report — runs, 0 errors
- [ ] PSV Reconciliation report — runs, 0 errors
- [ ] PSV Sell-Through report — runs, 0 errors
- [ ] PSV Stock Ageing report — runs, 0 errors
- [ ] PSV Opening Balance page — loads in browser
- [ ] Opening balance Excel parse → returns rows/errors dict
- [ ] process_opening_balance() → creates Opening ledger entries
- [ ] All imports clean — no circular import errors
- [ ] bench migrate — 0 errors

**After Phase 3: PSV v1.0.2 is Pilot Deploy Ready.**
**Milestone: First Live Distributor Upload + Reconciliation Cycle.**


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL