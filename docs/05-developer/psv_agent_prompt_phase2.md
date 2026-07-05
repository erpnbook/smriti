---
Document ID: "DEV-042"
Title: "SMRITI PSV — Agent Prompt: Phase 2"
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

# SMRITI PSV — Agent Prompt: Phase 2
# Ledger Engine + Balance Engine + Hooks + Excel Import
# Spec Version: v1.0.2 Final Freeze
# Prerequisite: Phase 1 Acceptance Gate — ALL 10 PASSED

---

## CONTEXT REMINDER

- Item code = ALWAYS Item Variant (e.g. `KORA-1383-BLACK-38`)
- Ledger is immutable — SHA-256 hash, unique DB constraint
- Reversal uses `is_reversal=1`, `reversal_of=<original_hash>`, NEW unique hash
- Balance = `SUM(qty)` — dispatches positive, sales negative, adjustments +/-
- company is MANDATORY in all balance queries (multi-company ready)
- NO core file modifications

---

## TASK 2.1 — Ledger Engine

File: `party_stock_visibility/engine/ledger_engine.py`

```python
import hashlib
import frappe
from frappe.utils import now_datetime


def generate_ledger_hash(
    company: str,
    party_stock_account: str,
    item_code: str,
    voucher_type: str,
    voucher_no: str,
    qty: float,
    is_reversal: bool = False,
) -> str:
    """
    SHA-256 hash for idempotency.
    Reversal gets a unique salt so it never collides with the original.
    """
    salt = "REVERSAL" if is_reversal else "ENTRY"
    raw = f"{company}|{party_stock_account}|{item_code}|{voucher_type}|{voucher_no}|{qty}|{salt}"
    return hashlib.sha256(raw.encode()).hexdigest()


def make_ledger_entry(
    company: str,
    party_stock_account: str,
    item_code: str,
    qty: float,
    voucher_type: str,
    voucher_no: str,
    reason: str = "",
    adjustment_type: str = "",
    approved_by: str = None,
    is_reversal: bool = False,
    reversal_of: str = None,
) -> str:
    """
    Create one immutable PSV ledger entry.
    Returns the unique_hash of the created entry.
    Raises if duplicate hash detected (idempotency guard).
    """
    unique_hash = generate_ledger_hash(
        company, party_stock_account, item_code,
        voucher_type, voucher_no, qty, is_reversal
    )

    # Idempotency check
    if frappe.db.exists("SMRITI Party Stock Ledger Entry", {"unique_hash": unique_hash}):
        frappe.log_error(
            f"Duplicate ledger entry blocked: {unique_hash}",
            "PSV Ledger Duplicate"
        )
        return unique_hash  # Already exists — safe to return

    entry = frappe.get_doc({
        "doctype":             "SMRITI Party Stock Ledger Entry",
        "company":             company,
        "posting_datetime":    now_datetime(),
        "party_stock_account": party_stock_account,
        "item_code":           item_code,
        "qty":                 qty,
        "voucher_type":        voucher_type,
        "voucher_no":          voucher_no,
        "unique_hash":         unique_hash,
        "is_reversal":         1 if is_reversal else 0,
        "reversal_of":         reversal_of or "",
        "source_hash":         reversal_of or "",
        "adjustment_type":     adjustment_type,
        "reason":              reason,
        "approved_by":         approved_by,
        "approved_on":         now_datetime() if approved_by else None,
    })
    entry.insert(ignore_permissions=True)
    return unique_hash


def log_activity(
    action_type: str,
    severity: str,
    details: str,
    reference_doctype: str = "",
    reference_name: str = "",
    alert_key: str = "",
):
    """
    Write to PSV Activity Log with alert suppression.
    If same alert_key exists within 24 hours → update, not insert.
    """
    from frappe.utils import add_to_date, now_datetime

    existing = None
    if alert_key:
        existing = frappe.db.get_value(
            "SMRITI PSV Activity Log",
            {
                "alert_key": alert_key,
                "timestamp": [">=", add_to_date(now_datetime(), hours=-24)],
            },
            "name",
        )

    if existing:
        frappe.db.set_value("SMRITI PSV Activity Log", existing, {
            "timestamp": now_datetime(),
            "details": details,
            "severity": severity,
        })
    else:
        log = frappe.get_doc({
            "doctype":           "SMRITI PSV Activity Log",
            "timestamp":         now_datetime(),
            "user":              frappe.session.user,
            "action_type":       action_type,
            "severity":          severity,
            "alert_key":         alert_key,
            "reference_doctype": reference_doctype,
            "reference_name":    reference_name,
            "details":           details,
        })
        log.insert(ignore_permissions=True)
```

---

## TASK 2.2 — Balance Engine

File: `party_stock_visibility/engine/balance_engine.py`

```python
import frappe


def get_party_balance(
    company: str,
    party_stock_account: str,
    item_code: str,
    posting_datetime=None,
) -> float:
    """
    Return current shadow balance for one party+item combination.
    company: mandatory (multi-company ready)
    posting_datetime: if provided, balance as-of that datetime
    """
    filters = {
        "company":             company,
        "party_stock_account": party_stock_account,
        "item_code":           item_code,
    }
    if posting_datetime:
        filters["posting_datetime"] = ["<=", posting_datetime]

    result = frappe.db.get_value(
        "SMRITI Party Stock Ledger Entry",
        filters=filters,
        fieldname="SUM(qty)",
        as_dict=False,
    )
    return float(result or 0)


def get_bulk_party_balances(
    company: str,
    party_stock_account: str,
    item_codes: list,
) -> dict:
    """
    Return {item_code: balance} for a list of item codes.
    Single aggregate query — avoids N+1 problem.
    company: mandatory
    """
    if not item_codes:
        return {}

    placeholders = ", ".join(["%s"] * len(item_codes))
    rows = frappe.db.sql(
        f"""
        SELECT item_code, SUM(qty) AS balance
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE company = %s
          AND party_stock_account = %s
          AND item_code IN ({placeholders})
        GROUP BY item_code
        """,
        [company, party_stock_account] + list(item_codes),
        as_dict=True,
    )
    return {r.item_code: float(r.balance or 0) for r in rows}


def get_all_party_balances(company: str) -> list:
    """
    Return all party+item balances for dashboard summary.
    Used by health check and dashboard API.
    """
    return frappe.db.sql(
        """
        SELECT
            e.party_stock_account,
            p.location_name,
            p.zone,
            e.item_code,
            SUM(e.qty) AS balance
        FROM `tabSMRITI Party Stock Ledger Entry` e
        LEFT JOIN `tabSMRITI Party Stock Account` p
            ON p.name = e.party_stock_account
        WHERE e.company = %s
        GROUP BY e.party_stock_account, e.item_code
        HAVING SUM(e.qty) != 0
        ORDER BY e.party_stock_account, e.item_code
        """,
        [company],
        as_dict=True,
    )
```

---

## TASK 2.3 — PSV Service Layer

File: `party_stock_visibility/service/psv_service.py`

```python
import frappe
from frappe.utils import now_datetime
from smriti_retail.party_stock_visibility.engine.ledger_engine import (
    make_ledger_entry, log_activity
)
from smriti_retail.party_stock_visibility.engine.balance_engine import (
    get_party_balance
)


# ── Sales Invoice Hooks ────────────────────────────────────────────

def process_sales_invoice_submit(doc, method):
    """
    on_submit hook.
    If Sales Invoice has custom_party_stock_account filled,
    create one PSV Dispatch ledger entry per line item.
    item_code on each line MUST be an Item Variant.
    """
    psa = doc.get("custom_party_stock_account")
    if not psa:
        return

    company = doc.company
    for item in doc.items:
        make_ledger_entry(
            company=company,
            party_stock_account=psa,
            item_code=item.item_code,
            qty=item.qty,                   # positive = stock sent
            voucher_type="Dispatch",
            voucher_no=doc.name,
            reason=f"Dispatch via {doc.name}",
        )

    log_activity(
        action_type="DISPATCH",
        severity="Info",
        details=f"Invoice {doc.name} dispatched {len(doc.items)} lines to {psa}",
        reference_doctype="Sales Invoice",
        reference_name=doc.name,
        alert_key=f"{psa}|DISPATCH|{doc.name}",
    )


def validate_sales_invoice_cancel(doc, method):
    """
    before_cancel hook.
    Check if cancellation would produce negative balances.
    If yes — do NOT block, but create Exception Record.
    Operational deadlock prevention per v1.0.2 spec.
    """
    psa = doc.get("custom_party_stock_account")
    if not psa:
        return

    company = doc.company
    for item in doc.items:
        current = get_party_balance(company, psa, item.item_code)
        if current - item.qty < 0:
            _create_exception(
                party_stock_account=psa,
                exception_type="Cancellation",
                severity="High",
                item_code=item.item_code,
                details=(
                    f"Cancellation of {doc.name} would produce negative balance "
                    f"for {item.item_code}. Current: {current}, Reversal: {item.qty}"
                ),
                reference_doctype="Sales Invoice",
                reference_name=doc.name,
            )


def process_sales_invoice_cancel(doc, method):
    """
    on_cancel hook.
    Create reversing ledger entries (is_reversal=1).
    New unique hash prevents collision with original entry.
    """
    psa = doc.get("custom_party_stock_account")
    if not psa:
        return

    company = doc.company
    for item in doc.items:
        # Get original dispatch hash
        original_hash = frappe.db.get_value(
            "SMRITI Party Stock Ledger Entry",
            {
                "company":             company,
                "party_stock_account": psa,
                "item_code":           item.item_code,
                "voucher_no":          doc.name,
                "voucher_type":        "Dispatch",
                "is_reversal":         0,
            },
            "unique_hash",
        )
        make_ledger_entry(
            company=company,
            party_stock_account=psa,
            item_code=item.item_code,
            qty=-item.qty,              # negative = reversal
            voucher_type="Return",
            voucher_no=doc.name,
            reason=f"Reversal of cancelled invoice {doc.name}",
            is_reversal=True,
            reversal_of=original_hash or "",
        )

    log_activity(
        action_type="CANCELLATION_REVERSAL",
        severity="Warning",
        details=f"Invoice {doc.name} cancelled — reversals created for {psa}",
        reference_doctype="Sales Invoice",
        reference_name=doc.name,
        alert_key=f"{psa}|CANCEL|{doc.name}",
    )


# ── Sales Upload Processing ────────────────────────────────────────

def process_sales_upload(upload_doc):
    """
    Called from SMRITI Party Sales Upload controller on_submit.
    Validates balance before each line, creates Sales ledger entries.
    Blocks if any line would cause negative balance.
    """
    company = upload_doc.company
    psa = upload_doc.party_stock_account
    errors = []

    for row in upload_doc.items:
        current = get_party_balance(company, psa, row.item_code)
        if current - row.qty_sold < 0:
            errors.append(
                f"{row.item_code}: Available {current}, Reported {row.qty_sold}"
            )

    if errors:
        frappe.throw(
            "Sales Upload blocked — oversell detected:\n" + "\n".join(errors)
        )

    for row in upload_doc.items:
        make_ledger_entry(
            company=company,
            party_stock_account=psa,
            item_code=row.item_code,
            qty=-row.qty_sold,          # negative = sold from party stock
            voucher_type="Sales",
            voucher_no=upload_doc.name,
            reason=f"Sales upload {upload_doc.name}",
        )

    frappe.db.set_value(
        "SMRITI Party Sales Upload", upload_doc.name, "status", "Imported"
    )
    log_activity(
        action_type="SALES_UPLOAD",
        severity="Info",
        details=f"Upload {upload_doc.name} imported {len(upload_doc.items)} lines for {psa}",
        reference_doctype="SMRITI Party Sales Upload",
        reference_name=upload_doc.name,
        alert_key=f"{psa}|UPLOAD|{upload_doc.name}",
    )


# ── Physical Snapshot Approval ─────────────────────────────────────

def process_snapshot_approval(snapshot_doc):
    """
    Called from SMRITI Party Physical Snapshot on approval.
    Creates Adjustment entries for variance lines only.
    """
    company = snapshot_doc.company
    psa = snapshot_doc.party_stock_account

    for row in snapshot_doc.items:
        if not row.variance or row.variance == 0:
            continue
        make_ledger_entry(
            company=company,
            party_stock_account=psa,
            item_code=row.item_code,
            qty=row.variance,           # positive or negative
            voucher_type="Adjustment",
            voucher_no=snapshot_doc.name,
            reason=row.variance_reason or "Physical Audit Adjustment",
            adjustment_type="Physical Audit",
            approved_by=snapshot_doc.approved_by,
        )

    log_activity(
        action_type="AUDIT_APPROVED",
        severity="Info",
        details=f"Snapshot {snapshot_doc.name} approved for {psa}",
        reference_doctype="SMRITI Party Physical Snapshot",
        reference_name=snapshot_doc.name,
    )


# ── Opening Balance ────────────────────────────────────────────────

def process_opening_balance(company: str, party_stock_account: str, items: list):
    """
    Called from PSV Opening Balance Wizard page.
    items: [{"item_code": "KORA-1383-BLACK-38", "qty": 500}, ...]
    Voucher type = Opening. One-time migration utility.
    """
    voucher_no = f"OB-{party_stock_account}-{frappe.utils.today()}"
    for item in items:
        make_ledger_entry(
            company=company,
            party_stock_account=party_stock_account,
            item_code=item["item_code"],
            qty=item["qty"],
            voucher_type="Opening",
            voucher_no=voucher_no,
            reason="Opening Balance Migration",
        )
    log_activity(
        action_type="OPENING_BALANCE",
        severity="Info",
        details=f"Opening balance loaded for {party_stock_account}: {len(items)} SKUs",
        reference_doctype="SMRITI Party Stock Account",
        reference_name=party_stock_account,
    )


# ── Daily Health Check ─────────────────────────────────────────────

def run_psv_daily_health_check():
    """
    Scheduled daily. Checks:
    1. Negative balances
    2. Pending reconciliations (snapshots > 30 days old, never approved)
    3. Late uploads (no upload in last 14 days for active parties)
    """
    settings = frappe.get_single("SMRITI PSV Settings")
    if not settings.health_check_enabled:
        return

    companies = frappe.get_all("Company", pluck="name")
    for company in companies:
        _check_negative_balances(company)
        _check_late_uploads(company)
        _check_never_audited(company)


def _check_negative_balances(company: str):
    rows = frappe.db.sql("""
        SELECT party_stock_account, item_code, SUM(qty) AS balance
        FROM `tabSMRITI Party Stock Ledger Entry`
        WHERE company = %s
        GROUP BY party_stock_account, item_code
        HAVING SUM(qty) < 0
    """, [company], as_dict=True)

    for row in rows:
        alert_key = f"{row.party_stock_account}|NEGATIVE_BALANCE|{row.item_code}"
        _create_exception(
            party_stock_account=row.party_stock_account,
            exception_type="Negative Balance",
            severity="Critical",
            item_code=row.item_code,
            details=f"Negative balance: {row.balance} for {row.item_code}",
        )
        log_activity(
            action_type="NEGATIVE_BALANCE",
            severity="Critical",
            details=f"Negative balance {row.balance} at {row.party_stock_account} for {row.item_code}",
            alert_key=alert_key,
        )


def _check_late_uploads(company: str):
    from frappe.utils import add_to_date, today
    cutoff = add_to_date(today(), days=-14)
    active_parties = frappe.get_all(
        "SMRITI Party Stock Account",
        filters={"active": 1, "company": company},
        pluck="name",
    )
    for psa in active_parties:
        last_upload = frappe.db.get_value(
            "SMRITI Party Sales Upload",
            {"party_stock_account": psa, "status": "Imported"},
            "MAX(upload_date)",
        )
        if not last_upload or str(last_upload) < str(cutoff):
            alert_key = f"{psa}|LATE_UPLOAD|"
            log_activity(
                action_type="LATE_UPLOAD",
                severity="Warning",
                details=f"No upload from {psa} since {last_upload or 'never'}",
                alert_key=alert_key,
            )


def _check_never_audited(company: str):
    from frappe.utils import add_to_date, today
    cutoff = add_to_date(today(), days=-30)
    active_parties = frappe.get_all(
        "SMRITI Party Stock Account",
        filters={"active": 1, "company": company},
        pluck="name",
    )
    for psa in active_parties:
        last_audit = frappe.db.get_value(
            "SMRITI Party Physical Snapshot",
            {"party_stock_account": psa, "status": "Approved"},
            "MAX(audit_date)",
        )
        if not last_audit or str(last_audit) < str(cutoff):
            alert_key = f"{psa}|AUDIT_OVERDUE|"
            log_activity(
                action_type="AUDIT_OVERDUE",
                severity="Warning",
                details=f"No approved audit for {psa} since {last_audit or 'never'}",
                alert_key=alert_key,
            )


# ── Internal Helpers ───────────────────────────────────────────────

def _create_exception(
    party_stock_account: str,
    exception_type: str,
    severity: str,
    item_code: str = "",
    details: str = "",
    reference_doctype: str = "",
    reference_name: str = "",
):
    exc = frappe.get_doc({
        "doctype":             "SMRITI PSV Exception Record",
        "party_stock_account": party_stock_account,
        "exception_type":      exception_type,
        "severity":            severity,
        "status":              "Open",
        "item_code":           item_code,
        "created_on":          now_datetime(),
        "resolution_notes":    details,
    })
    exc.insert(ignore_permissions=True)
```

---

## TASK 2.4 — Excel Import Utility

File: `party_stock_visibility/utils/excel_import.py`

```python
import frappe
from frappe import _
import openpyxl

# Flexible column aliases — item_code must be Item Variant
COLUMN_ALIASES = {
    "item_code": ["item", "sku", "article", "product", "style", "item code",
                  "style code", "product code", "variant", "item variant"],
    "qty_sold":  ["qty", "quantity", "sold qty", "sales qty", "qty sold",
                  "units", "pcs", "pieces"],
    "sale_date": ["date", "sale date", "sales date", "transaction date"],
}


def _normalize(header):
    return str(header).strip().lower().replace("_", " ").replace("-", " ")


def _detect_columns(headers):
    normalized = [_normalize(h) for h in headers]
    mapping = {}
    for field, aliases in COLUMN_ALIASES.items():
        for i, h in enumerate(normalized):
            if h in aliases:
                mapping[field] = i
                break
    return mapping


@frappe.whitelist()
def parse_sales_upload_excel(file_url: str, party_stock_account: str) -> dict:
    """
    Parse Excel and return validated rows.
    Validates:
    - Required columns exist
    - item_code is a valid Item Variant (not template)
    - qty_sold > 0
    Returns: {"rows": [...], "errors": [...], "total_qty": int}
    """
    file_doc = frappe.get_doc("File", {"file_url": file_url})
    wb = openpyxl.load_workbook(file_doc.get_full_path(), read_only=True, data_only=True)
    ws = wb.active
    raw_rows = list(ws.iter_rows(values_only=True))

    if not raw_rows:
        frappe.throw(_("Excel file is empty"))

    # Detect header row
    col_map = {}
    header_idx = 0
    for i, row in enumerate(raw_rows[:5]):
        col_map = _detect_columns([str(c) if c else "" for c in row])
        if "item_code" in col_map and "qty_sold" in col_map:
            header_idx = i
            break

    if "item_code" not in col_map or "qty_sold" not in col_map:
        frappe.throw(_(
            "Required columns not found. Excel must have: "
            "Item/SKU/Article (Item Variant code) and Qty/Quantity. "
            f"Found: {list(raw_rows[0])}"
        ))

    rows = []
    errors = []
    total_qty = 0

    for ri, row in enumerate(raw_rows[header_idx + 1:], start=header_idx + 2):
        if not row or not row[col_map["item_code"]]:
            continue

        item_code = str(row[col_map["item_code"]]).strip()
        qty_raw = row[col_map["qty_sold"]]
        sale_date = row[col_map["sale_date"]] if "sale_date" in col_map and row[col_map.get("sale_date", -1)] else None

        try:
            qty = int(float(qty_raw or 0))
        except Exception:
            errors.append(f"Row {ri}: Invalid qty '{qty_raw}' for {item_code}")
            continue

        if qty <= 0:
            continue

        # Validate item variant exists
        if not frappe.db.exists("Item", item_code):
            errors.append(f"Row {ri}: Item '{item_code}' not found in ERPNext")
            continue

        # Warn if template (no variants attribute set)
        variant_of = frappe.db.get_value("Item", item_code, "variant_of")
        if not variant_of:
            # Could be a template — warn but don't block
            errors.append(
                f"Row {ri}: '{item_code}' appears to be a template, not a variant. "
                "PSV requires Item Variant codes."
            )
            continue

        rows.append({
            "item_code":  item_code,
            "qty_sold":   qty,
            "sales_date": str(sale_date) if sale_date else None,
        })
        total_qty += qty

    return {"rows": rows, "errors": errors, "total_qty": total_qty}
```

---

## TASK 2.5 — Sales Upload Controller (on_submit hook)

In `doctype/smriti_party_sales_upload/smriti_party_sales_upload.py`, UPDATE:

```python
import frappe
from frappe.model.document import Document
from smriti_retail.party_stock_visibility.service.psv_service import process_sales_upload

class SMRITIPartySalesUpload(Document):
    def validate(self):
        if self.period_end_date and self.period_start_date:
            if self.period_end_date < self.period_start_date:
                frappe.throw("Period End Date cannot be before Period Start Date.")
        total = sum(row.qty_sold for row in self.items if row.qty_sold)
        if total == 0 and self.status not in ("Draft",):
            frappe.throw("Cannot validate upload with zero total qty.")

    def on_submit(self):
        process_sales_upload(self)
```

---

## TASK 2.6 — Physical Snapshot Controller (on_approve)

In `doctype/smriti_party_physical_snapshot/smriti_party_physical_snapshot.py`, UPDATE:

```python
import frappe
from frappe.model.document import Document
from smriti_retail.party_stock_visibility.service.psv_service import process_snapshot_approval

class SMRITIPartyPhysicalSnapshot(Document):
    def validate(self):
        for row in self.items:
            row.variance = (row.physical_qty or 0) - (row.system_qty or 0)

    def on_submit(self):
        self.status = "Pending Approval"

    @frappe.whitelist()
    def approve(self):
        if frappe.session.user == frappe.db.get_value("SMRITI Party Stock Account",
                                                       self.party_stock_account,
                                                       "area_manager"):
            frappe.throw("Area Manager cannot approve their own location's snapshot.")
        self.approved_by = frappe.session.user
        self.status = "Approved"
        self.save()
        process_snapshot_approval(self)
```

---

## TASK 2.7 — Whitelisted Balance API

File: `party_stock_visibility/utils/psv_api.py`

```python
import frappe
from smriti_retail.party_stock_visibility.engine.balance_engine import (
    get_all_party_balances, get_bulk_party_balances
)

@frappe.whitelist()
def get_dashboard_summary(company: str) -> dict:
    """Dashboard KPI summary."""
    balances = get_all_party_balances(company)
    total_units = sum(r.balance for r in balances if r.balance > 0)
    negative_count = sum(1 for r in balances if r.balance < 0)
    open_exceptions = frappe.db.count(
        "SMRITI PSV Exception Record", {"status": "Open"}
    )
    critical_alerts = frappe.db.count(
        "SMRITI PSV Activity Log", {"severity": "Critical"}
    )
    party_summary = {}
    for r in balances:
        psa = r.party_stock_account
        if psa not in party_summary:
            party_summary[psa] = {
                "party_stock_account": psa,
                "location_name": r.location_name,
                "zone": r.zone,
                "total_balance": 0,
                "sku_count": 0,
            }
        if r.balance > 0:
            party_summary[psa]["total_balance"] += r.balance
            party_summary[psa]["sku_count"] += 1

    return {
        "total_units":     total_units,
        "negative_count":  negative_count,
        "open_exceptions": open_exceptions,
        "critical_alerts": critical_alerts,
        "parties":         list(party_summary.values()),
    }


@frappe.whitelist()
def get_party_balance_detail(company: str, party_stock_account: str) -> list:
    """All SKU balances for one party."""
    all_balances = get_all_party_balances(company)
    return [r for r in all_balances if r.party_stock_account == party_stock_account]
```

---

## VERIFICATION COMMANDS

```bash
cd /home/frappe/frappe-bench

bench --site smriti.localhost migrate

# Test ledger engine
bench --site smriti.localhost execute \
  "from smriti_retail.party_stock_visibility.engine.ledger_engine import generate_ledger_hash; \
   h = generate_ledger_hash('Tattly Threads','PSA-001','KORA-1383-BLACK-38','Dispatch','SINV-001',10); \
   print('Hash:', h[:16], '✅')"

# Test balance engine import
bench --site smriti.localhost execute \
  "from smriti_retail.party_stock_visibility.engine.balance_engine import get_party_balance; \
   b = get_party_balance('Tattly Threads','PSA-001','KORA-1383-BLACK-38'); print('Balance:', b, '✅')"

# Test service layer import
bench --site smriti.localhost execute \
  "from smriti_retail.party_stock_visibility.service.psv_service import run_psv_daily_health_check; print('✅')"

# Test API import
bench --site smriti.localhost execute \
  "from smriti_retail.party_stock_visibility.utils.psv_api import get_dashboard_summary; print('✅')"

# Test Excel import
bench --site smriti.localhost execute \
  "from smriti_retail.party_stock_visibility.utils.excel_import import parse_sales_upload_excel; print('✅')"
```

---

## PHASE 2 ACCEPTANCE GATE

- [ ] ledger_engine.py — imports clean, generate_ledger_hash returns 64-char hex
- [ ] balance_engine.py — imports clean, get_party_balance returns float
- [ ] psv_service.py — all 6 functions importable, no syntax errors
- [ ] excel_import.py — imports clean
- [ ] psv_api.py — imports clean
- [ ] Sales Invoice submit with custom_party_stock_account filled → PSV Dispatch ledger entry created
- [ ] Sales Invoice cancel → reversal entry with is_reversal=1, reversal_of set
- [ ] Sales Upload on_submit → calls process_sales_upload, oversell blocked
- [ ] Physical Snapshot approve → adjustment entries created for variance rows only
- [ ] run_psv_daily_health_check() → runs without error (no data = no crash)
- [ ] Duplicate hash → blocked silently (idempotency)
- [ ] bench migrate — 0 errors

**DO NOT proceed to Phase 3 (Reports + Dashboard) until all 12 gates pass.**


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