# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/sizewise_invoice_api.py
# @description: Backend API for SMRITI Sizewise B2B Sales Tax Invoice module
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-31
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json
from frappe.utils import flt, nowdate
from frappe import _
from smriti_retail_os.utils.invoice_utils import resolve_barcode, parse_pdt_file, detect_pdt_columns



# ─── Company / Master Data ────────────────────────────────────────────────────

@frappe.whitelist()
def get_company_details(company=None):
    """Returns company master details including GSTIN, address, bank details."""
    if company:
        company_name = company
    else:
        if frappe.flags.in_test:
            company_name = (frappe.defaults.get_user_default("company")
                            or frappe.get_all("Company", limit=1)[0].name)
        else:
            company_name = (
                frappe.defaults.get_user_default("company")
                or frappe.db.get_single_value("Global Defaults", "default_company")
                or frappe.get_all("Company", limit=1, pluck="name")[0]
            )
    
    company = frappe.get_doc("Company", company_name)

    # Company address
    address_data = {}
    addr_link = frappe.db.get_value(
        "Dynamic Link",
        {"link_doctype": "Company", "link_name": company_name, "parenttype": "Address"},
        "parent"
    )
    if addr_link:
        addr = frappe.get_doc("Address", addr_link)
        address_data = {
            "line1":   addr.address_line1 or "",
            "line2":   addr.address_line2 or "",
            "city":    addr.city or "",
            "state":   addr.state or "",
            "pincode": addr.pincode or "",
            "phone":   addr.phone or "",
            "email":   addr.email_id or "",
        }

    # Bank account details
    bank_data = {}
    bank_link = frappe.db.get_value(
        "Bank Account",
        {"company": company_name, "is_default": 1},
        ["bank", "bank_account_no", "branch_code"],
        as_dict=True
    )
    if bank_link:
        bank_data = {
            "bank_name":    bank_link.bank or "",
            "account_no":   bank_link.bank_account_no or "",
            "ifsc":         bank_link.branch_code or "",
        }

    gstin = (company.get("gstin") or company.get("tax_id") or "")

    return {
        "company_name":     company.company_name,
        "abbr":             company.abbr,
        "gstin":            gstin,
        "pan":              company.pan or "",
        "phone":            company.phone_no or "",
        "email":            company.email or "",
        "website":          company.website or "",
        "country":          company.country or "India",
        "default_currency": company.default_currency or "INR",
        "company_logo":     company.company_logo or "",
        "address":          address_data,
        "bank":             bank_data,
        "state_code":       gstin[:2] if len(gstin) >= 2 else "",
    }


@frappe.whitelist()
def get_customer_details(customer):
    """Returns customer GSTIN, address, and contact details."""
    if not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer {0} not found.").format(customer))

    cust = frappe.get_doc("Customer", customer)

    # Billing address
    address_data = {}
    addr_link = frappe.db.get_value(
        "Dynamic Link",
        {"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
        "parent"
    )
    if addr_link:
        addr = frappe.get_doc("Address", addr_link)
        address_data = {
            "line1":   addr.address_line1 or "",
            "line2":   addr.address_line2 or "",
            "city":    addr.city or "",
            "state":   addr.state or "",
            "pincode": addr.pincode or "",
            "gstin":   addr.gstin or "",
        }

    gstin = (address_data.get("gstin")
             or cust.get("gstin")
             or cust.get("tax_id")
             or "")

    return {
        "customer":      cust.name,
        "customer_name": cust.get("customer_name") or cust.name,
        "gstin":         gstin,
        "state_code":    gstin[:2] if len(gstin) >= 2 else "",
        "address":       address_data,
        "mobile_no":     cust.get("mobile_no") or "",
        "credit_days":   cust.get("credit_days") or 0,
    }


@frappe.whitelist()
def search_customers(query=""):
    """Searches customers by name for autocomplete dropdown."""
    results = frappe.get_all(
        "Customer",
        filters=[["Customer", "customer_name", "like", f"%{query}%"],
                 ["Customer", "disabled", "=", 0]],
        fields=["name", "customer_name", "tax_id", "mobile_no"],
        limit=15
    )
    return results


@frappe.whitelist()
def search_items(query=""):
    """Searches items by name/code — used for article autocomplete in the grid."""
    filters = [["Item", "disabled", "=", 0],
               ["Item", "is_sales_item", "=", 1]]
    or_filters = []
    if query:
        or_filters = [
            ["Item", "item_code", "like", f"%{query}%"],
            ["Item", "item_name", "like", f"%{query}%"]
        ]
    results = frappe.get_all(
        "Item",
        filters=filters,
        or_filters=or_filters,
        fields=["name", "item_name", "item_group", "brand", "gst_hsn_code", "valuation_rate", "custom_gst_percentage"],
        limit=20
    )
    return results


@frappe.whitelist()
def resolve_barcode(barcode):
    """
    Resolves a barcode to full item variant details (imported from core utils).
    """
    from smriti_retail_os.utils.invoice_utils import resolve_barcode as core_resolve_barcode
    return core_resolve_barcode(barcode)



@frappe.whitelist()
def get_item_details_by_article(article, color=""):
    """
    Looks up an article and optional color in the Item Master.
    Returns:
    {
        "article": "20016",
        "color": "BLACK",
        "category": "SANDAL",
        "sub_category": "LASTIC PATTA",
        "brand": "SMRITI",
        "hsn_code": "64041990",
        "mrp": 1899,
        "rate": 1610.17,
        "gst_pct": 18
    }
    """
    if not article:
        return {}

    # Try parent item first
    parent = frappe.db.get_value(
        "Item",
        article,
        ["name", "item_name", "item_group", "brand", "gst_hsn_code", "custom_sub_category", "custom_mrp", "custom_gst_percentage", "valuation_rate"],
        as_dict=True
    )

    if not parent:
        # Fuzzy match by article name or code
        candidate = frappe.db.get_value(
            "Item",
            {"item_code": ["like", f"%{article}%"], "disabled": 0},
            ["name", "item_name", "item_group", "brand", "gst_hsn_code", "custom_sub_category", "custom_mrp", "custom_gst_percentage", "valuation_rate"],
            as_dict=True
        )
        if candidate:
            parent = candidate

    if not parent:
        return {}

    res = {
        "article": parent.name,
        "color": color,
        "category": parent.item_group or "",
        "sub_category": parent.custom_sub_category or "",
        "brand": parent.brand or "",
        "hsn_code": parent.gst_hsn_code or "",
        "mrp": flt(parent.custom_mrp or parent.valuation_rate or 0),
        "gst_pct": flt(parent.custom_gst_percentage or 12),
        "rate": 0
    }

    # Try to find a variant matching the color to get precise pricing/attributes
    if color:
        variant = frappe.db.get_value(
            "Item",
            {"variant_of": parent.name, "item_code": ["like", f"%{color}%"], "disabled": 0},
            ["name", "custom_mrp", "custom_gst_percentage", "gst_hsn_code"],
            as_dict=True
        )
        if variant:
            if variant.custom_mrp:
                res["mrp"] = flt(variant.custom_mrp)
            if variant.custom_gst_percentage:
                res["gst_pct"] = flt(variant.custom_gst_percentage)
            if variant.gst_hsn_code:
                res["hsn_code"] = variant.gst_hsn_code

    # Auto-calculate tax-exclusive Rate from MRP and GST% if MRP exists
    if res["mrp"] > 0:
        res["rate"] = flt(res["mrp"] / (1 + (res["gst_pct"] / 100.0)), 2)

    return res



@frappe.whitelist()
def get_states_list():
    """Returns list of Indian states with GST state codes."""
    return [
        {"code": "01", "name": "Jammu & Kashmir"},
        {"code": "02", "name": "Himachal Pradesh"},
        {"code": "03", "name": "Punjab"},
        {"code": "04", "name": "Chandigarh"},
        {"code": "05", "name": "Uttarakhand"},
        {"code": "06", "name": "Haryana"},
        {"code": "07", "name": "Delhi"},
        {"code": "08", "name": "Rajasthan"},
        {"code": "09", "name": "Uttar Pradesh"},
        {"code": "10", "name": "Bihar"},
        {"code": "11", "name": "Sikkim"},
        {"code": "12", "name": "Arunachal Pradesh"},
        {"code": "13", "name": "Nagaland"},
        {"code": "14", "name": "Manipur"},
        {"code": "15", "name": "Mizoram"},
        {"code": "16", "name": "Tripura"},
        {"code": "17", "name": "Meghalaya"},
        {"code": "18", "name": "Assam"},
        {"code": "19", "name": "West Bengal"},
        {"code": "20", "name": "Jharkhand"},
        {"code": "21", "name": "Odisha"},
        {"code": "22", "name": "Chhattisgarh"},
        {"code": "23", "name": "Madhya Pradesh"},
        {"code": "24", "name": "Gujarat"},
        {"code": "26", "name": "Dadra & Nagar Haveli and Daman & Diu"},
        {"code": "27", "name": "Maharashtra"},
        {"code": "28", "name": "Andhra Pradesh"},
        {"code": "29", "name": "Karnataka"},
        {"code": "30", "name": "Goa"},
        {"code": "31", "name": "Lakshadweep"},
        {"code": "32", "name": "Kerala"},
        {"code": "33", "name": "Tamil Nadu"},
        {"code": "34", "name": "Puducherry"},
        {"code": "35", "name": "Andaman & Nicobar Islands"},
        {"code": "36", "name": "Telangana"},
        {"code": "37", "name": "Andhra Pradesh"},
        {"code": "38", "name": "Ladakh"},
        {"code": "97", "name": "Other Territory"},
        {"code": "96", "name": "Foreign Country"},
    ]


# ─── Invoice CRUD ──────────────────────────────────────────────────────────────

def check_invoice_permissions():
    """Verifies that the user has cashier, biller, or manager roles to perform billing operations."""
    if frappe.session.user == "Administrator":
        return True
    user_roles = frappe.get_roles(frappe.session.user)
    allowed_roles = {"Biller", "Cashier", "Sales User", "Sales Manager", "System Manager", "SMRITI Cashier", "SMRITI Store Manager"}
    if not allowed_roles.intersection(user_roles):
        frappe.throw(_("Access Denied: You do not have the required permissions to perform B2B invoicing operations."), frappe.PermissionError)


def _find_tax_account(name_pattern, company):
    """Finds standard Output Tax first, then falls back to fuzzy match."""
    standard_name = f"Output Tax {name_pattern}"
    acc = frappe.db.get_value(
        "Account",
        {"account_name": standard_name, "company": company, "is_group": 0},
        "name"
    )
    if acc:
        return acc
    return frappe.db.get_value(
        "Account",
        {"account_name": ["like", f"%{name_pattern}%"], "company": company, "is_group": 0},
        "name"
    )


@frappe.whitelist()
def save_sizewise_invoice(payload):
    """
    Creates or updates a Sales Invoice from the sizewise matrix data.

    payload (JSON string or dict):
    {
        "invoice_name":   null | "SINV-SW-2026-00001",
        "invoice_date":   "2026-05-31",
        "customer":       "Customer Name",
        "place_of_supply": "27-Maharashtra",
        "tax_type":       "intrastate" | "interstate",
        "eway_bill_no":   "",
        "vehicle_no":     "",
        "transport_mode": "Road",
        "terms":          "",
        "size_columns":   ["36", "37", "38", ...],
        "rows": [
            {
                "article":      "20016",
                "color":        "BLACK",
                "category":     "SANDAL",
                "sub_category": "LASTIC PATTA",
                "sizes":        {"36": 0, "37": 9, "38": 9, ...},
                "mrp":          1899,
                "rate":         1610.17,
                "gst_pct":      18,
                "hsn_code":     "640311",
                "item_code":    ""
            }
        ]
    }
    """
    check_invoice_permissions()
    data = frappe.parse_json(payload) if isinstance(payload, str) else payload

    customer       = data.get("customer")
    invoice_date   = data.get("invoice_date") or nowdate()
    place_of_supply = data.get("place_of_supply") or ""
    tax_type       = data.get("tax_type") or "intrastate"
    size_columns   = data.get("size_columns") or ["36", "37", "38", "39", "40", "41", "42"]
    rows           = data.get("rows") or []

    if not customer:
        frappe.throw(_("Customer is required."))
    if not rows:
        frappe.throw(_("Please add at least one item row."))

    company = (frappe.defaults.get_user_default("company")
               or frappe.get_all("Company", limit=1)[0].name)

    # Load existing or create new
    invoice_name = data.get("invoice_name")
    if invoice_name and frappe.db.exists("Sales Invoice", invoice_name):
        si = frappe.get_doc("Sales Invoice", invoice_name)
        if si.docstatus != 0:
            frappe.throw(_("Cannot edit a submitted or cancelled invoice."))
        si.set("items", [])
        si.set("taxes", [])
    else:
        si = frappe.new_doc("Sales Invoice")

    si.customer        = customer
    si.posting_date    = invoice_date
    si.company         = company
    si.set_posting_time = 1
    si.update_stock    = 0
    si.is_pos          = 0

    # Auto-resolve Company Address (Required by India Compliance)
    if not si.company_address:
        addr = frappe.get_all(
            "Address",
            filters=[
                ["Dynamic Link", "link_doctype", "=", "Company"],
                ["Dynamic Link", "link_name", "=", company],
                ["Address", "is_your_company_address", "=", 1]
            ],
            order_by="is_primary_address desc",
            limit=1
        )
        if addr:
            si.company_address = addr[0].name
        else:
            addr = frappe.get_all(
                "Address",
                filters=[
                    ["Dynamic Link", "link_doctype", "=", "Company"],
                    ["Dynamic Link", "link_name", "=", company]
                ],
                limit=1
            )
            if addr:
                si.company_address = addr[0].name

    # Auto-resolve Customer Address
    if not si.customer_address:
        cust_addr = frappe.get_all(
            "Address",
            filters=[
                ["Dynamic Link", "link_doctype", "=", "Customer"],
                ["Dynamic Link", "link_name", "=", customer]
            ],
            order_by="is_primary_address desc",
            limit=1
        )
        if cust_addr:
            si.customer_address = cust_addr[0].name

    # Persist full matrix as JSON in custom_sizewise_json, set human-readable remarks
    matrix_snapshot = {
        "_sizewise_matrix": True,
        "size_columns":    size_columns,
        "rows":            rows,
        "place_of_supply": place_of_supply,
        "tax_type":        tax_type,
        "eway_bill_no":    data.get("eway_bill_no", ""),
        "vehicle_no":      data.get("vehicle_no", ""),
        "transport_mode":  data.get("transport_mode", "Road"),
        "terms":           data.get("terms", ""),
    }
    si.custom_sizewise_json = json.dumps(matrix_snapshot)
    si.remarks = f"Sizewise B2B Invoice for {customer}"

    # Find CGST, SGST, IGST accounts
    cgst_account = _find_tax_account("CGST", company) if tax_type == "intrastate" else None
    sgst_account = _find_tax_account("SGST", company) if tax_type == "intrastate" else None
    igst_account = _find_tax_account("IGST", company) if tax_type == "interstate" else None

    # Expand rows → Sales Invoice line items
    for row in rows:
        article      = row.get("article") or ""
        color        = row.get("color") or ""
        category     = row.get("category") or ""
        sub_category = row.get("sub_category") or ""
        sizes        = row.get("sizes") or {}
        mrp          = flt(row.get("mrp") or 0)
        rate         = flt(row.get("rate") or 0)
        gst_pct      = flt(row.get("gst_pct") or 0)
        hsn_code     = row.get("hsn_code") or ""
        item_code    = row.get("item_code") or ""
        discount_percentage = flt(row.get("discount_percentage") or 0)

        # Prepare item-wise tax rate mapping
        item_tax_dict = {}
        half_pct = flt(gst_pct) / 2
        if tax_type == "intrastate":
            if cgst_account:
                item_tax_dict[cgst_account] = half_pct
            if sgst_account:
                item_tax_dict[sgst_account] = half_pct
        else:
            if igst_account:
                item_tax_dict[igst_account] = gst_pct

        for size in size_columns:
            qty = flt(sizes.get(str(size)) or 0)
            if qty <= 0:
                continue

            resolved = _resolve_item_code(article, color, size, item_code)

            si.append("items", {
                "item_code":   resolved,
                "item_name":   f"{article} {color} {size}",
                "description": f"Article: {article} | Color: {color} | Category: {category} | Sub: {sub_category} | Size: {size} | MRP: ₹{mrp}",
                "qty":         qty,
                "price_list_rate": rate,
                "discount_percentage": discount_percentage,
                "rate":        rate * (1 - discount_percentage / 100.0),
                "uom":         "Nos",
                "gst_hsn_code": hsn_code,
                "item_tax_rate": json.dumps(item_tax_dict) if item_tax_dict else "{}"
            })

    if not si.items:
        frappe.throw(_("No items with qty > 0 found. Please enter quantities in the grid."))

    # Attach container GST tax rows
    _add_gst_taxes(si, tax_type, company)

    si.flags.ignore_permissions = True
    si.flags.ignore_mandatory   = True
    si.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "name":        si.name,
        "grand_total": flt(si.grand_total),
        "net_total":   flt(si.net_total),
        "message":     f"Invoice {si.name} saved as draft.",
    }


def _resolve_item_code(article, color, size, fallback_item_code):
    """Resolves the best-match ERPNext item code for a given article/color/size."""
    # Try most specific first: ARTICLE-COLOR-SIZE
    for candidate in [
        f"{article}-{color}-{size}",
        f"{article}-{color}",
        article,
        fallback_item_code,
    ]:
        if candidate and frappe.db.exists("Item", candidate):
            return candidate

    # Fuzzy name match
    found = frappe.db.get_value("Item", {"item_name": ["like", f"%{article}%"], "disabled": 0}, "name")
    if found:
        return found

    # Graceful fallback: dynamically ensure '_SIZEWISE_ITEM_' exists and use it
    if not frappe.db.exists("Item", "_SIZEWISE_ITEM_"):
        try:
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": "_SIZEWISE_ITEM_",
                "item_name": "Sizewise General Article",
                "item_group": "All Item Groups",
                "is_stock_item": 0,
                "is_sales_item": 1,
                "stock_uom": "Nos"
            })
            item.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            first_item = frappe.db.get_value("Item", {"is_sales_item": 1, "disabled": 0}, "name")
            if first_item:
                return first_item

    return "_SIZEWISE_ITEM_"


def _add_gst_taxes(si, tax_type, company):
    """Attaches CGST+SGST (intrastate) or IGST (interstate) accounts to the invoice with correct blended rates."""
    accounts_to_add = []
    if tax_type == "intrastate":
        cgst = _find_tax_account("CGST", company)
        sgst = _find_tax_account("SGST", company)
        if cgst:
            accounts_to_add.append(("CGST", cgst))
        if sgst:
            accounts_to_add.append(("SGST", sgst))
    else:
        igst = _find_tax_account("IGST", company)
        if igst:
            accounts_to_add.append(("IGST", igst))

    for desc, acc in accounts_to_add:
        # Calculate blended rate for this tax account based on item line taxes
        total_taxable = 0.0
        total_tax = 0.0
        for item in si.items:
            qty = flt(item.qty)
            rate = flt(item.rate)
            item_tax_rate_str = item.get("item_tax_rate")
            if item_tax_rate_str:
                try:
                    tax_rates = json.loads(item_tax_rate_str)
                    if acc in tax_rates:
                        tax_pct = flt(tax_rates[acc])
                        taxable = qty * rate
                        total_taxable += taxable
                        total_tax += taxable * (tax_pct / 100.0)
                except Exception:
                    pass
        
        blended_rate = (total_tax / total_taxable * 100.0) if total_taxable > 0 else 0.0
        blended_rate = round(blended_rate, 4)

        si.append("taxes", {
            "charge_type": "On Net Total",
            "account_head": acc,
            "description": desc,
            "rate": blended_rate
        })


@frappe.whitelist()
def submit_sizewise_invoice(invoice_name):
    """Submits a draft sizewise sales invoice."""
    check_invoice_permissions()
    si = frappe.get_doc("Sales Invoice", invoice_name)
    if si.docstatus != 0:
        frappe.throw(_("Invoice {0} is already submitted or cancelled.").format(invoice_name))
    si.submit()
    frappe.db.commit()
    return {"name": si.name, "message": f"Invoice {si.name} submitted successfully."}


@frappe.whitelist()
def get_sizewise_invoice(invoice_name):
    """Loads a saved sizewise invoice and reconstructs the matrix payload."""
    check_invoice_permissions()
    if not frappe.db.exists("Sales Invoice", invoice_name):
        frappe.throw(_("Invoice {0} not found.").format(invoice_name))

    si = frappe.get_doc("Sales Invoice", invoice_name)

    try:
        raw_json = si.get("custom_sizewise_json") or si.remarks
        meta = json.loads(raw_json or "{}")
        if meta.get("_sizewise_matrix"):
            return {
                "invoice_name":    si.name,
                "invoice_date":    str(si.posting_date),
                "customer":        si.customer,
                "docstatus":       si.docstatus,
                "grand_total":     flt(si.grand_total),
                "net_total":       flt(si.net_total),
                "total_qty":       sum(flt(it.qty) for it in si.items),
                **meta
            }
    except Exception:
        pass

    frappe.throw(_(
        f"Invoice {invoice_name} was not created via Sizewise Invoice module "
        f"or its matrix data is missing."
    ))


@frappe.whitelist()
def list_sizewise_invoices(customer="", limit=30):
    """Lists recent sizewise sales invoices."""
    check_invoice_permissions()
    filters = []
    if customer:
        filters.append(["Sales Invoice", "customer", "=", customer])

    or_filters = [
        ["Sales Invoice", "remarks", "like", "%_sizewise_matrix%"],
        ["Sales Invoice", "custom_sizewise_json", "!=", ""]
    ]

    return frappe.get_all(
        "Sales Invoice",
        filters=filters,
        or_filters=or_filters,
        fields=["name", "customer", "posting_date", "grand_total", "net_total", "docstatus"],
        order_by="creation desc",
        limit=int(limit)
    )


@frappe.whitelist()
def cancel_sizewise_invoice(invoice_name):
    """Cancels a submitted sizewise invoice."""
    check_invoice_permissions()
    si = frappe.get_doc("Sales Invoice", invoice_name)
    if si.docstatus != 1:
        frappe.throw(_("Only submitted invoices can be cancelled."))
    si.cancel()
    frappe.db.commit()
    return {"name": si.name, "message": f"Invoice {si.name} cancelled."}


@frappe.whitelist()
def get_admin_session_for_pdf():
    """Returns the most recent active Administrator session ID.
    Restricted to System Manager role to prevent session hijacking."""
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Access Denied: Only System Managers can retrieve session data."), frappe.PermissionError)
    sid = frappe.db.sql(
        "SELECT sid FROM tabSessions WHERE user = 'Administrator' ORDER BY lastupdate DESC LIMIT 1"
    )
    if sid:
        return sid[0][0]
    return ""


# ─── PDT Import APIs ──────────────────────────────────────────────────────────

@frappe.whitelist()
def get_pdt_column_map(file_content, file_type="csv"):
    """
    Detect columns from an uploaded PDT file (base64 encoded) and propose
    a default column mapping based on known aliases.

    Returns:
        { "headers": [...], "mapping": { "barcode": "BARCODE NO", ... } }
    """
    check_invoice_permissions()
    import base64
    if not file_content:
        frappe.throw("No file content provided.")
    try:
        raw = base64.b64decode(file_content)
    except Exception:
        frappe.throw("Invalid base64 file content.")

    headers, mapping = detect_pdt_columns(raw, file_type)
    return {"headers": headers, "mapping": mapping}


@frappe.whitelist()
def preview_pdt_import(file_content, file_type="csv", mapping=None, price_type="Selling", supplier=None):
    """
    Parse a PDT file and resolve each barcode against Item Master.
    Returns a list of row dicts ready for the preview table.
    """
    check_invoice_permissions()
    import base64
    import json
    if not file_content:
        frappe.throw("No file content provided.")
    try:
        raw = base64.b64decode(file_content)
    except Exception:
        frappe.throw("Invalid base64 file content.")

    if isinstance(mapping, str):
        mapping = json.loads(mapping)

    rows = parse_pdt_file(raw, file_type, col_mapping=mapping, price_type=price_type, supplier=supplier)
    return rows
