# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/analytics_studio/dataset_engine.py
# @description: SMRITI Analytics Studio — Dataset Registry & Query Engine
#               Datasets are reusable SQL templates shared across multiple reports.
#               Reports reference a dataset_key; filters applied at dataset level.
# @author: Jawahar R. Mallah
# @version: 1.0.0
#

import frappe
from frappe.utils import flt, cint, nowdate, get_first_day, get_last_day

# ─────────────────────────────────────────────────────────────────────────────
# DATASET REGISTRY
# Each dataset defines: base_sql, available joins (applied conditionally),
# available_columns, available_filters, default_date_field.
# Reports reference dataset_key and select a subset of columns/filters.
# ─────────────────────────────────────────────────────────────────────────────

DATASET_REGISTRY = {

    "sales": {
        "label": "Sales Dataset",
        "description": "POS Invoice + Sales Invoice transactions",
        "default_date_field": "posting_date",
        "base_sql": """
            SELECT
                pi.name                         AS invoice_no,
                pi.posting_date,
                pi.customer,
                pi.customer_name,
                pi.company,
                pi.warehouse,
                pi.cashier,
                pi.grand_total,
                pi.net_total                    AS taxable_amount,
                pi.total_taxes_and_charges      AS tax_amount,
                COALESCE(pi.discount_amount, 0) AS discount_amount,
                pi.total_qty                    AS qty_sold,
                pi.mode_of_payment,
                pi.is_return,
                pi.pos_profile
            FROM `tabPOS Invoice` pi
            WHERE pi.docstatus = 1
        """,
        "filter_map": {
            "company":    "pi.company = %(company)s",
            "warehouse":  "pi.warehouse = %(warehouse)s",
            "from_date":  "pi.posting_date >= %(from_date)s",
            "to_date":    "pi.posting_date <= %(to_date)s",
            "cashier":    "pi.cashier = %(cashier)s",
            "is_return":  "pi.is_return = %(is_return)s",
        },
        "group_by_candidates": [
            "posting_date", "customer", "warehouse", "cashier",
            "mode_of_payment", "company", "pos_profile",
        ],
        "numeric_fields": [
            "grand_total", "taxable_amount", "tax_amount",
            "discount_amount", "qty_sold",
        ],
    },

    "sales_items": {
        "label": "Sales Item-wise Dataset",
        "description": "POS Invoice line items with parent invoice metadata",
        "default_date_field": "posting_date",
        "base_sql": """
            SELECT
                pi.posting_date,
                pi.company,
                pi.warehouse,
                pi.cashier,
                ii.item_code,
                ii.item_name,
                ii.item_group,
                ii.brand,
                ii.qty,
                ii.rate,
                ii.net_amount,
                ii.amount                   AS gross_amount,
                COALESCE(ii.discount_amount, 0) AS item_discount,
                pi.is_return
            FROM `tabPOS Invoice Item` ii
            JOIN `tabPOS Invoice` pi ON ii.parent = pi.name
            LEFT JOIN `tabItem` it ON ii.item_code = it.name
            WHERE pi.docstatus = 1
        """,
        "filter_map": {
            "company":     "pi.company = %(company)s",
            "warehouse":   "pi.warehouse = %(warehouse)s",
            "from_date":   "pi.posting_date >= %(from_date)s",
            "to_date":     "pi.posting_date <= %(to_date)s",
            "item_group":  "ii.item_group = %(item_group)s",
            "brand":       "ii.brand = %(brand)s",
            "cashier":     "pi.cashier = %(cashier)s",
        },
        "group_by_candidates": [
            "posting_date", "item_code", "item_group", "brand",
            "warehouse", "cashier",
        ],
        "numeric_fields": ["qty", "rate", "net_amount", "gross_amount", "item_discount"],
    },

    "inventory": {
        "label": "Inventory Dataset",
        "description": "Current stock position from Bin table",
        "default_date_field": None,
        "base_sql": """
            SELECT
                b.item_code,
                i.item_name,
                i.item_group,
                i.brand,
                b.warehouse,
                b.actual_qty,
                b.reserved_qty,
                b.ordered_qty,
                b.valuation_rate,
                b.stock_value,
                CASE
                    WHEN b.actual_qty <= 0 THEN 'Out of Stock'
                    WHEN b.actual_qty <= 5 THEN 'Low Stock'
                    ELSE 'In Stock'
                END AS stock_status
            FROM `tabBin` b
            JOIN `tabItem` i ON b.item_code = i.name
            WHERE 1=1
        """,
        "filter_map": {
            "warehouse":   "b.warehouse = %(warehouse)s",
            "item_group":  "i.item_group = %(item_group)s",
            "brand":       "i.brand = %(brand)s",
        },
        "group_by_candidates": [
            "item_code", "item_group", "brand", "warehouse", "stock_status",
        ],
        "numeric_fields": [
            "actual_qty", "reserved_qty", "ordered_qty",
            "valuation_rate", "stock_value",
        ],
    },

    "purchase": {
        "label": "Purchase Dataset",
        "description": "Purchase Invoice transactions",
        "default_date_field": "posting_date",
        "base_sql": """
            SELECT
                pi.name                         AS invoice_no,
                pi.posting_date,
                pi.supplier,
                pi.supplier_name,
                pi.company,
                pi.grand_total,
                pi.net_total                    AS taxable_amount,
                pi.total_taxes_and_charges      AS tax_amount,
                pi.outstanding_amount,
                pi.is_return,
                pi.currency
            FROM `tabPurchase Invoice` pi
            WHERE pi.docstatus = 1
        """,
        "filter_map": {
            "company":    "pi.company = %(company)s",
            "from_date":  "pi.posting_date >= %(from_date)s",
            "to_date":    "pi.posting_date <= %(to_date)s",
            "supplier":   "pi.supplier = %(supplier)s",
        },
        "group_by_candidates": [
            "posting_date", "supplier", "company", "currency",
        ],
        "numeric_fields": [
            "grand_total", "taxable_amount", "tax_amount", "outstanding_amount",
        ],
    },

    "finance": {
        "label": "Finance Dataset",
        "description": "GL Entry level financial data",
        "default_date_field": "posting_date",
        "base_sql": """
            SELECT
                gle.posting_date,
                gle.account,
                gle.party_type,
                gle.party,
                gle.debit,
                gle.credit,
                gle.voucher_type,
                gle.voucher_no,
                gle.company,
                gle.cost_center
            FROM `tabGL Entry` gle
            WHERE gle.is_cancelled = 0
        """,
        "filter_map": {
            "company":    "gle.company = %(company)s",
            "from_date":  "gle.posting_date >= %(from_date)s",
            "to_date":    "gle.posting_date <= %(to_date)s",
            "account":    "gle.account = %(account)s",
        },
        "group_by_candidates": [
            "posting_date", "account", "party_type", "party",
            "voucher_type", "company",
        ],
        "numeric_fields": ["debit", "credit"],
    },

    "customer": {
        "label": "Customer Dataset",
        "description": "Customer master + transaction summary",
        "default_date_field": None,
        "base_sql": """
            SELECT
                c.name                      AS customer_id,
                c.customer_name,
                c.customer_group,
                c.territory,
                c.customer_type,
                c.mobile_no,
                c.email_id,
                COALESCE(c.loyalty_points, 0) AS loyalty_points
            FROM `tabCustomer` c
            WHERE c.disabled = 0
        """,
        "filter_map": {
            "customer_group": "c.customer_group = %(customer_group)s",
            "territory":      "c.territory = %(territory)s",
        },
        "group_by_candidates": [
            "customer_group", "territory", "customer_type",
        ],
        "numeric_fields": ["loyalty_points"],
    },

    "psv": {
        "label": "PSV / Channel Stock Dataset",
        "description": "Party Stock Visibility ledger data",
        "default_date_field": "posting_date",
        "base_sql": """
            SELECT
                pl.posting_date,
                pl.party,
                pl.party_name,
                pl.item_code,
                pl.brand,
                pl.qty_in,
                pl.qty_out,
                pl.closing_qty,
                pl.transaction_type,
                pl.company
            FROM `tabPSV Ledger Entry` pl
            WHERE 1=1
        """,
        "filter_map": {
            "company":    "pl.company = %(company)s",
            "from_date":  "pl.posting_date >= %(from_date)s",
            "to_date":    "pl.posting_date <= %(to_date)s",
            "party":      "pl.party = %(party)s",
            "brand":      "pl.brand = %(brand)s",
        },
        "group_by_candidates": [
            "posting_date", "party", "brand", "item_code",
            "transaction_type", "company",
        ],
        "numeric_fields": ["qty_in", "qty_out", "closing_qty"],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# DATASET ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class DatasetEngine:
    """
    Core query engine. Takes a dataset_key, filters, optional group_by and sort,
    returns paginated rows and total count.
    """

    def __init__(self, dataset_key, filters=None, group_by=None,
                 sort_by=None, sort_dir="ASC", page=1, page_size=500):
        self.dataset_key = dataset_key
        self.filters = filters or {}
        self.group_by = group_by or []
        self.sort_by = sort_by
        self.sort_dir = sort_dir.upper() if sort_dir else "ASC"
        self.page = max(1, cint(page))
        self.page_size = max(1, min(cint(page_size), 5000))

        if dataset_key not in DATASET_REGISTRY:
            frappe.throw(f"Dataset '{dataset_key}' not registered in DatasetEngine.")

        self.spec = DATASET_REGISTRY[dataset_key]

    def _build_where_clause(self):
        """Build parametric WHERE clause from active filters."""
        conditions = []
        params = {}
        filter_map = self.spec.get("filter_map", {})

        for key, value in self.filters.items():
            if value is None or value == "":
                continue
            if key in filter_map:
                conditions.append(filter_map[key])
                params[key] = value

        return conditions, params

    def _build_group_by_clause(self):
        """Validate and build GROUP BY clause."""
        if not self.group_by:
            return ""
        safe_cols = self.spec.get("group_by_candidates", [])
        validated = [col for col in self.group_by if col in safe_cols]
        if not validated:
            return ""
        return "GROUP BY " + ", ".join(validated)

    def _build_order_clause(self):
        """Build safe ORDER BY clause."""
        if self.sort_by:
            # Whitelist: must be in columns or group_by_candidates
            allowed = (
                self.spec.get("group_by_candidates", []) +
                self.spec.get("numeric_fields", [])
            )
            if self.sort_by in allowed:
                direction = "ASC" if self.sort_dir == "ASC" else "DESC"
                return f"ORDER BY {self.sort_by} {direction}"
        # Default: date field DESC if available
        date_field = self.spec.get("default_date_field")
        if date_field:
            return f"ORDER BY {date_field} DESC"
        return ""

    def fetch(self):
        """Execute query and return rows + total_count."""
        base_sql = self.spec["base_sql"].strip()
        conditions, params = self._build_where_clause()

        # Append conditions
        if conditions:
            # The base_sql already ends with WHERE 1=1 or WHERE ... conditions
            # Handle both cases
            if "WHERE 1=1" in base_sql or "WHERE" in base_sql.upper().split("FROM")[1] if "FROM" in base_sql.upper() else False:
                base_sql += " AND " + " AND ".join(conditions)
            else:
                base_sql += " WHERE " + " AND ".join(conditions)

        group_clause = self._build_group_by_clause()
        order_clause = self._build_order_clause()

        count_sql = f"SELECT COUNT(*) as cnt FROM ({base_sql} {group_clause}) _cnt_wrap"

        try:
            count_result = frappe.db.sql(count_sql, params, as_dict=True)
            total_count = cint(count_result[0].get("cnt", 0)) if count_result else 0
        except Exception:
            total_count = 0

        offset = (self.page - 1) * self.page_size
        data_sql = f"""
            {base_sql}
            {group_clause}
            {order_clause}
            LIMIT %(limit)s OFFSET %(offset)s
        """
        params["limit"] = self.page_size
        params["offset"] = offset

        try:
            rows = frappe.db.sql(data_sql, params, as_dict=True)
        except Exception as e:
            frappe.log_error(f"DatasetEngine.fetch error for {self.dataset_key}: {str(e)}")
            rows = []

        return {
            "rows": [dict(r) for r in rows],
            "total_count": total_count,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": max(1, (total_count + self.page_size - 1) // self.page_size),
        }

    def fetch_aggregates(self, numeric_fields=None):
        """Compute SUM/AVG/MIN/MAX for numeric fields — used for grand totals and KPI cards."""
        if not numeric_fields:
            numeric_fields = self.spec.get("numeric_fields", [])

        if not numeric_fields:
            return {}

        agg_exprs = []
        for field in numeric_fields:
            agg_exprs.append(f"COALESCE(SUM(`{field}`), 0) AS `sum_{field}`")
            agg_exprs.append(f"COALESCE(AVG(`{field}`), 0) AS `avg_{field}`")
            agg_exprs.append(f"COUNT(*) AS `_row_count`")

        base_sql = self.spec["base_sql"].strip()
        conditions, params = self._build_where_clause()
        if conditions:
            if "WHERE 1=1" in base_sql:
                base_sql += " AND " + " AND ".join(conditions)
            else:
                base_sql += " WHERE " + " AND ".join(conditions)

        agg_sql = f"SELECT {', '.join(agg_exprs)} FROM ({base_sql}) _agg_wrap"

        try:
            result = frappe.db.sql(agg_sql, params, as_dict=True)
            return dict(result[0]) if result else {}
        except Exception as e:
            frappe.log_error(f"DatasetEngine.fetch_aggregates error: {str(e)}")
            return {}


def get_dataset_list():
    """Returns list of available datasets for the UI."""
    return [
        {
            "key": k,
            "label": v["label"],
            "description": v["description"],
            "numeric_fields": v.get("numeric_fields", []),
            "group_by_candidates": v.get("group_by_candidates", []),
        }
        for k, v in DATASET_REGISTRY.items()
    ]
