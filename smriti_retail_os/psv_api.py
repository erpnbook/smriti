# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/psv_api.py
# @description: SMRITI PSV Dashboard and Analytics APIs.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os.balance_engine import (
	get_party_balance,
	get_bulk_party_balances,
	get_reorder_recommendation
)

@frappe.whitelist()
def get_dashboard_summary(company):
	"""
	Returns a dict with key operational metrics for the PSV Dashboard:
	- total_units: SUM of all positive balances across all PSAs for the company
	- total_locations: count of active PSAs
	- negative_count: count of active PSAs with any item having negative balance
	- open_exceptions: count of exception records with status 'Pending Reconciliation'
	- critical_alerts: count of exception records with severity 'Critical' and status 'Pending Reconciliation'
	"""
	use_new = frappe.db.exists("PSV Ledger Entry", {"company": company})
	if use_new:
		total_units_res = frappe.db.sql("""
			SELECT COALESCE(SUM(item_bal), 0)
			FROM (
				SELECT SUM(ple.qty) as item_bal
				FROM `tabPSV Ledger Entry` ple
				INNER JOIN `tabPSV Channel Partner` psa ON ple.channel_partner = psa.name
				WHERE psa.company = %s
				GROUP BY ple.channel_partner, ple.item_variant
			) t WHERE item_bal > 0
		""", (company,))
		total_units = float(total_units_res[0][0]) if total_units_res else 0.0

		total_locations = frappe.db.count("PSV Channel Partner", {
			"company": company,
			"active": 1
		})

		negative_count_res = frappe.db.sql("""
			SELECT COUNT(DISTINCT channel_partner)
			FROM (
				SELECT ple.channel_partner, SUM(ple.qty) as item_bal
				FROM `tabPSV Ledger Entry` ple
				INNER JOIN `tabPSV Channel Partner` psa ON ple.channel_partner = psa.name
				WHERE psa.company = %s AND psa.active = 1
				GROUP BY ple.channel_partner, ple.item_variant
			) t WHERE item_bal < 0
		""", (company,))
		negative_count = negative_count_res[0][0] if negative_count_res else 0

	else:
		total_units_res = frappe.db.sql("""
			SELECT COALESCE(SUM(item_bal), 0)
			FROM (
				SELECT SUM(ple.qty) as item_bal
				FROM `tabSMRITI Party Stock Ledger Entry` ple
				INNER JOIN `tabSMRITI Party Stock Account` psa ON ple.party_stock_account = psa.name
				WHERE psa.company = %s
				GROUP BY ple.party_stock_account, ple.item_code
			) t WHERE item_bal > 0
		""", (company,))
		total_units = float(total_units_res[0][0]) if total_units_res else 0.0

		total_locations = frappe.db.count("SMRITI Party Stock Account", {
			"company": company,
			"active": 1
		})

		negative_count_res = frappe.db.sql("""
			SELECT COUNT(DISTINCT party_stock_account)
			FROM (
				SELECT ple.party_stock_account, SUM(ple.qty) as item_bal
				FROM `tabSMRITI Party Stock Ledger Entry` ple
				INNER JOIN `tabSMRITI Party Stock Account` psa ON ple.party_stock_account = psa.name
				WHERE psa.company = %s AND psa.active = 1
				GROUP BY ple.party_stock_account, ple.item_code
			) t WHERE item_bal < 0
		""", (company,))
		negative_count = negative_count_res[0][0] if negative_count_res else 0

	open_exceptions = frappe.db.sql("""
		SELECT COUNT(*)
		FROM `tabSMRITI PSV Exception Record` er
		INNER JOIN `tabSMRITI Party Stock Account` psa ON er.party_stock_account = psa.name
		WHERE psa.company = %s AND er.status = 'Pending Reconciliation'
	""", (company,))[0][0] if not use_new else frappe.db.sql("""
		SELECT COUNT(*)
		FROM `tabSMRITI PSV Exception Record` er
		INNER JOIN `tabPSV Channel Partner` psa ON er.party_stock_account = psa.name
		WHERE psa.company = %s AND er.status = 'Pending Reconciliation'
	""", (company,))[0][0]

	critical_alerts = frappe.db.sql("""
		SELECT COUNT(*)
		FROM `tabSMRITI PSV Exception Record` er
		INNER JOIN `tabSMRITI Party Stock Account` psa ON er.party_stock_account = psa.name
		WHERE psa.company = %s AND er.status = 'Pending Reconciliation' AND er.severity = 'Critical'
	""", (company,))[0][0] if not use_new else frappe.db.sql("""
		SELECT COUNT(*)
		FROM `tabSMRITI PSV Exception Record` er
		INNER JOIN `tabPSV Channel Partner` psa ON er.party_stock_account = psa.name
		WHERE psa.company = %s AND er.status = 'Pending Reconciliation' AND er.severity = 'Critical'
	""", (company,))[0][0]

	return {
		"total_units": total_units,
		"total_locations": total_locations,
		"negative_count": negative_count,
		"open_exceptions": open_exceptions,
		"critical_alerts": critical_alerts
	}

@frappe.whitelist()
def get_party_balance_detail(company, party_stock_account):
	"""
	Returns list of dicts with item_code and balance for all items at a location.
	Uses a single aggregate SQL GROUP BY query.
	"""
	use_new = frappe.db.exists("PSV Ledger Entry", {"channel_partner": party_stock_account})
	if use_new:
		result = frappe.db.sql("""
			SELECT ple.item_variant as item_code, SUM(ple.qty) as balance
			FROM `tabPSV Ledger Entry` ple
			INNER JOIN `tabPSV Channel Partner` psa ON ple.channel_partner = psa.name
			WHERE psa.company = %s AND ple.channel_partner = %s
			GROUP BY ple.item_variant
		""", (company, party_stock_account), as_dict=True)
	else:
		result = frappe.db.sql("""
			SELECT ple.item_code, SUM(ple.qty) as balance
			FROM `tabSMRITI Party Stock Ledger Entry` ple
			INNER JOIN `tabSMRITI Party Stock Account` psa ON ple.party_stock_account = psa.name
			WHERE psa.company = %s AND ple.party_stock_account = %s
			GROUP BY ple.item_code
		""", (company, party_stock_account), as_dict=True)

	for r in result:
		r["balance"] = float(r["balance"]) if r["balance"] is not None else 0.0

	return result

@frappe.whitelist()
def get_reorder_dashboard_data(company):
	"""
	Returns Top 10 replenishment needs across all active PSAs.
	Sorted by priority order (Critical -> High -> Medium -> Low) and recommended_qty descending.
	"""
	use_new = frappe.db.exists("PSV Ledger Entry", {"company": company})
	if use_new:
		psas = frappe.get_all("PSV Channel Partner",
			filters={"company": company, "active": 1},
			fields=["name"]
		)
	else:
		psas = frappe.get_all("SMRITI Party Stock Account",
			filters={"company": company, "active": 1},
			fields=["name"]
		)

	all_recommendations = []

	priority_weight = {
		"Critical": 4,
		"High": 3,
		"Medium": 2,
		"Low": 1
	}

	for psa in psas:
		psa_name = psa.name
		balances = get_bulk_party_balances(psa_name)

		for item_code in balances.keys():
			reco = get_reorder_recommendation(company, psa_name, item_code)
			if reco and reco.get("recommended_qty", 0) > 0:
				all_recommendations.append({
					"location": psa_name,
					"item_code": item_code,
					"current_balance": reco.get("current_balance", 0.0),
					"weekly_sale_avg": reco.get("weekly_sale_avg", 0.0),
					"days_cover": reco.get("days_cover", 0.0),
					"reorder_level": reco.get("reorder_level", 0.0),
					"recommended_qty": reco.get("recommended_qty", 0.0),
					"priority": reco.get("priority", "Low"),
					"priority_weight": priority_weight.get(reco.get("priority", "Low"), 0)
				})

	all_recommendations.sort(key=lambda x: (x["priority_weight"], x["recommended_qty"]), reverse=True)

	for item in all_recommendations:
		item.pop("priority_weight", None)

	return all_recommendations[:10]


from frappe import _
from smriti_retail_os.psv_upload_service import process_upload
from smriti_retail_os.psv_balance_service import get_channel_balance

@frappe.whitelist()
def create_psa(company: str, customer: str, location_name: str,
               zone: str = None, region: str = None, area_manager: str = None,
               contact_person: str = None, mobile: str = None, email: str = None,
               active: int = 1):
    """
    Creates a new SMRITI Party Stock Account.
    Requires SMRITI Store Manager or System Manager role.
    Routes through the service layer — frontend must NOT call frappe.client.insert directly.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])

    if not company or not customer or not location_name:
        frappe.throw(_("Company, Customer, and Location Name are required."))

    # Prevent duplicate PSA for same customer + location
    existing = frappe.db.exists(
        "SMRITI Party Stock Account",
        {"customer": customer, "location_name": location_name}
    )
    if existing:
        frappe.throw(
            _("A Party Stock Account already exists for customer {0} at location '{1}' ({2})."
              ).format(customer, location_name, existing)
        )

    doc = frappe.get_doc({
        "doctype": "SMRITI Party Stock Account",
        "company": company,
        "customer": customer,
        "location_name": location_name,
        "zone": zone,
        "region": region,
        "area_manager": area_manager or None,
        "contact_person": contact_person,
        "mobile": mobile,
        "email": email,
        "active": int(active),
        "status": "Active"
    })
    doc.insert(ignore_permissions=False)  # Respect Frappe role permissions
    frappe.db.commit()

    return {"name": doc.name, "status": "created"}


@frappe.whitelist()
def update_psa(name: str, zone: str = None, region: str = None,
               area_manager: str = None, contact_person: str = None,
               mobile: str = None, email: str = None, active: int = 1):
    """
    Updates mutable fields on an existing SMRITI Party Stock Account.
    Company, Customer, and Location Name are immutable after creation.
    Requires SMRITI Store Manager or System Manager role.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])

    if not frappe.db.exists("SMRITI Party Stock Account", name):
        frappe.throw(_("Party Stock Account {0} not found.").format(name))

    frappe.db.set_value(
        "SMRITI Party Stock Account",
        name,
        {
            "zone": zone,
            "region": region,
            "area_manager": area_manager or None,
            "contact_person": contact_person,
            "mobile": mobile,
            "email": email,
            "active": int(active),
        }
    )
    frappe.db.commit()

    return {"name": name, "status": "updated"}


@frappe.whitelist()
def get_psa(name: str):
    """
    Returns full details of a SMRITI Party Stock Account.
    Requires read access to the DocType (enforced via frappe.get_doc).
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager", "SMRITI Cashier"])

    doc = frappe.get_doc("SMRITI Party Stock Account", name)
    return {
        "name": doc.name,
        "company": doc.company,
        "customer": doc.customer,
        "location_name": doc.location_name,
        "zone": doc.zone,
        "region": doc.region,
        "area_manager": doc.area_manager,
        "contact_person": doc.contact_person,
        "mobile": doc.mobile,
        "email": doc.email,
        "active": doc.active,
        "status": doc.status,
        "tracking_mode": doc.tracking_mode,
    }


@frappe.whitelist()
def list_psas(company: str = None, active: int = None):
    """
    Returns a list of SMRITI Party Stock Accounts with key fields.
    Optionally filtered by company and/or active status.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager", "SMRITI Cashier"])

    filters = {}
    if company:
        filters["company"] = company
    if active is not None:
        filters["active"] = int(active)

    return frappe.get_all(
        "SMRITI Party Stock Account",
        filters=filters,
        fields=[
            "name", "company", "customer", "location_name", "zone", "region",
            "area_manager", "contact_person", "mobile", "email", "active", "status"
        ],
        order_by="modified desc",
        limit=500
    )


@frappe.whitelist()
def upload_sell_through(upload_doc_name: str):
    """
    API endpoint to trigger the processing of a Draft PSV Sell-Through Upload.
    SEC-002 FIX: Now checks SMRITI Party Stock Account permission (which exists)
    rather than the non-existent "PSV Sell-Through Upload" DocType.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager"])

    doc = frappe.get_doc("PSV Sell-Through Upload", upload_doc_name)
    if doc.status == "Processed":
        return {"status": "failed", "message": "Document is already processed."}

    # process_upload handles atomic commits and error logging internally.
    process_upload(upload_doc_name)

    doc.reload()

    if doc.status == "Processed":
        return {"status": "success", "rows_processed": doc.total_rows}
    else:
        return {"status": "failed", "error_count": len(doc.get("errors", []))}


@frappe.whitelist()
def fetch_channel_balance(customer: str, item_code: str = None):
    """
    API endpoint to retrieve current stock balance for a channel/customer.
    SEC-002 FIX: Now checks SMRITI Party Stock Account read permission (DocType
    exists) rather than the non-existent "PSV Balance" DocType.
    """
    frappe.only_for(["System Manager", "SMRITI Store Manager", "SMRITI Cashier"])

    return {
        "status": "success",
        "data": get_channel_balance(customer, item_code)
    }


@frappe.whitelist()
def get_psv_health():
	"""
	Exposes startup / health validation checks for PSV.
	"""
	checks = {
		"psv_settings_exists": False,
		"psa_doctype_exists": False,
		"delivery_note_psa_field_exists": False,
		"stock_entry_psa_field_exists": False,
		"unique_hash_index_exists": False,
		"exception_record_schema_valid": False
	}

	# 1. PSV Settings exists
	if frappe.db.exists("DocType", "SMRITI PSV Settings"):
		checks["psv_settings_exists"] = True

	# 2. PSA DocType exists
	if frappe.db.exists("DocType", "SMRITI Party Stock Account"):
		checks["psa_doctype_exists"] = True

	# 3. Delivery Note PSA field exists
	try:
		if frappe.get_meta("Delivery Note").has_field("custom_party_stock_account"):
			checks["delivery_note_psa_field_exists"] = True
	except Exception:
		import sys
		_frappe = sys.modules.get('frappe')
		if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in psv_api.py:407: {sys.exc_info()[1]}")

	# 4. Stock Entry PSA field exists
	try:
		if frappe.get_meta("Stock Entry").has_field("custom_party_stock_account"):
			checks["stock_entry_psa_field_exists"] = True
	except Exception:
		import sys
		_frappe = sys.modules.get('frappe')
		if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in psv_api.py:414: {sys.exc_info()[1]}")

	# 5. Unique hash index exists
	try:
		indices = frappe.db.sql(f"SHOW INDEX FROM {chr(96)}tabSMRITI Party Stock Ledger Entry{chr(96)}", as_dict=True)
		if any(idx.get("Key_name") == "unique_hash" for idx in indices):
			checks["unique_hash_index_exists"] = True
	except Exception:
		import sys
		_frappe = sys.modules.get('frappe')
		if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in psv_api.py:422: {sys.exc_info()[1]}")

	# 6. Exception Record schema valid
	try:
		if frappe.db.exists("DocType", "SMRITI PSV Exception Record"):
			meta = frappe.get_meta("SMRITI PSV Exception Record")
			if (meta.has_field("alert_type") and 
				meta.has_field("reconciliation_notes") and 
				meta.has_field("timestamp")):
				checks["exception_record_schema_valid"] = True
	except Exception:
		import sys
		_frappe = sys.modules.get('frappe')
		if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in psv_api.py:433: {sys.exc_info()[1]}")

	# Overall status
	all_passed = all(checks.values())
	return {
		"status": "Healthy" if all_passed else "Unhealthy",
		"checks": checks
	}


# ── P4: Stock Audit & Sales Upload service layer ──────────────────────────────
# Replaces frappe.client.insert/submit/get/get_list from stock-audit.html
# and sales-upload.html. All write operations are here; HTML never touches
# frappe.client directly.

@frappe.whitelist()
def list_physical_audits(company=None, limit=100):
	"""List SMRITI Party Physical Snapshot records. Replaces frappe.client.get_list."""
	filters = {}
	if company:
		filters["company"] = company
	return frappe.get_list(
		"SMRITI Party Physical Snapshot",
		filters=filters,
		fields=["name", "company", "party_stock_account", "audit_date",
				"status", "approved_by", "approved_on"],
		order_by="creation desc",
		limit_page_length=int(limit),
	)


@frappe.whitelist()
def list_party_stock_accounts_for_audit(company, active=1):
	"""List PSAs for a company. Replaces frappe.client.get_list on SMRITI Party Stock Account."""
	return frappe.get_list(
		"SMRITI Party Stock Account",
		filters={"company": company, "active": int(active)},
		fields=["name", "customer", "location_name"],
	)


@frappe.whitelist()
def create_physical_audit(company, party_stock_account, audit_date, items):
	"""
	Create a SMRITI Party Physical Snapshot in Pending Approval status.
	Replaces frappe.client.insert from stock-audit.html.
	items: JSON list of {item_code, system_qty, physical_qty, variance_reason}
	"""
	import json
	if not frappe.has_permission("SMRITI Party Physical Snapshot", "create"):
		frappe.throw(_("Not authorized to create stock audits."), frappe.PermissionError)

	item_list = json.loads(items) if isinstance(items, str) else items

	doc = frappe.get_doc({
		"doctype": "SMRITI Party Physical Snapshot",
		"company": company,
		"party_stock_account": party_stock_account,
		"audit_date": audit_date,
		"status": "Pending Approval",
	})
	for item in item_list:
		doc.append("items", item)
	doc.insert(ignore_permissions=False)
	frappe.db.commit()
	return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def submit_physical_audit(name):
	"""
	Submit a SMRITI Party Physical Snapshot.
	Replaces frappe.client.submit from stock-audit.html.
	"""
	if not frappe.has_permission("SMRITI Party Physical Snapshot", "submit"):
		frappe.throw(_("Not authorized to submit stock audits."), frappe.PermissionError)
	doc = frappe.get_doc("SMRITI Party Physical Snapshot", name)
	doc.submit()
	frappe.db.commit()
	return {"name": doc.name, "status": doc.docstatus}


@frappe.whitelist()
def get_physical_audit(name):
	"""
	Fetch a SMRITI Party Physical Snapshot with items.
	Replaces frappe.client.get from stock-audit.html.
	"""
	if not frappe.has_permission("SMRITI Party Physical Snapshot", "read"):
		frappe.throw(_("Not authorized to view stock audits."), frappe.PermissionError)
	doc = frappe.get_doc("SMRITI Party Physical Snapshot", name)
	return {
		"name": doc.name,
		"company": doc.company,
		"party_stock_account": doc.party_stock_account,
		"audit_date": str(doc.audit_date),
		"status": doc.status,
		"items": [
			{
				"item_code": i.item_code,
				"system_qty": i.system_qty,
				"physical_qty": i.physical_qty,
				"variance": i.variance,
				"variance_reason": i.variance_reason,
			} for i in doc.items
		],
	}


@frappe.whitelist()
def list_sales_uploads(company=None, limit=100):
	"""List SMRITI Party Sales Upload records. Replaces frappe.client.get_list."""
	filters = {}
	if company:
		filters["company"] = company
	return frappe.get_list(
		"SMRITI Party Sales Upload",
		filters=filters,
		fields=["name", "company", "party_stock_account", "period_start_date",
				"period_end_date", "status", "excel_file", "creation"],
		order_by="creation desc",
		limit_page_length=int(limit),
	)


@frappe.whitelist()
def create_sales_upload(
	company, party_stock_account, period_start_date,
	period_end_date, excel_file=None, items=None
):
	"""
	Create a SMRITI Party Sales Upload record in Draft status.
	Replaces frappe.client.insert from sales-upload.html.
	"""
	import json
	if not frappe.has_permission("SMRITI Party Sales Upload", "create"):
		frappe.throw(_("Not authorized to create sales uploads."), frappe.PermissionError)

	item_list = json.loads(items) if isinstance(items, str) else (items or [])

	doc = frappe.get_doc({
		"doctype": "SMRITI Party Sales Upload",
		"company": company,
		"party_stock_account": party_stock_account,
		"period_start_date": period_start_date,
		"period_end_date": period_end_date,
		"excel_file": excel_file,
	})
	for item in item_list:
		doc.append("items", item)
	doc.insert(ignore_permissions=False)
	frappe.db.commit()
	return {"name": doc.name}


@frappe.whitelist()
def submit_sales_upload(name):
	"""
	Submit a SMRITI Party Sales Upload to trigger PSV ledger processing.
	Replaces frappe.client.submit from sales-upload.html.
	"""
	if not frappe.has_permission("SMRITI Party Sales Upload", "submit"):
		frappe.throw(_("Not authorized to submit sales uploads."), frappe.PermissionError)
	doc = frappe.get_doc("SMRITI Party Sales Upload", name)
	doc.submit()
	frappe.db.commit()
	return {"name": doc.name, "status": doc.docstatus}
