# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/hooks_logic.py
# @description: Document event hooks -- syncs item taxes, customer addresses, and retail invoice state.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe.utils import flt, cint
from frappe import _
from smriti_retail_os import smriti

# Helper to get state from GSTIN using India Compliance utilities
def _get_company_state_fallback(company=None):
    """
    Returns the state of the company for GST jurisdiction determination.

    Returns None (instead of a hardcoded fallback) if the company state is not
    configured. This prevents silent application of incorrect intrastate tax rates
    while still allowing callers like resolve_address_state() to resolve state
    from GSTIN or address text before escalating.

    Callers that REQUIRE a state for tax calculations (e.g. _resolve_default_tax_template)
    should throw their own descriptive error when they receive None.
    """
    try:
        if not company:
            company = (
                frappe.defaults.get_user_default("company")
                or smriti.db.get("Company", {}, "name")
            )
        if company:
            state = smriti.db.get("Company", company, "state")
            if state:
                return state
            # State field is empty — log a warning so admins notice in Error Log.
            # DO NOT hardcode "Karnataka" — that silently produces incorrect GST
            # invoices for companies in any other state.
            smriti.errors.log_error(
                title="SMRITI: Company state not configured — GST risk",
                message=(
                    f"Company '{company}' has no 'State' configured. "
                    f"Go to Accounting → Company → {company} and set the 'State' field. "
                    f"Without this, intrastate vs interstate GST determination may be incorrect."
                )
            )
            return None
    except Exception:
        import sys
        _frappe = sys.modules.get('frappe')
        if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in hooks_logic.py:51: {sys.exc_info()[1]}")
    return None



def resolve_address_state(gstin, address_text="", fallback=None, company=None):
    if fallback is None:
        fallback = _get_company_state_fallback(company)
    if address_text:
        states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
            "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
            "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
            "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
            "Uttarakhand", "West Bengal", "Delhi", "Jammu & Kashmir", "Ladakh"
        ]
        text_lower = address_text.lower()
        for s in states:
            if s.lower() in text_lower:
                return s

    if not gstin or len(gstin) < 2:
        return fallback
    try:
        from india_compliance.gst_india.utils import get_state
        state = get_state(gstin[:2])
        return state or fallback
    except ImportError:
        return fallback

# --- Item (Product Master) Hooks ---

def get_gst_rate_from_hsn(hsn_code, company=None):
    """Derive the total GST rate from an HSN Code via India Compliance's HSN master.
    
    Lookup chain: gst_hsn_code → GST HSN Code.taxes → Item Tax Template → sum(tax_rate)
    Returns the total GST percentage (e.g. 18) or None if not determinable.
    """
    if not hsn_code:
        return None

    try:
        if not smriti.db.exists("GST HSN Code", hsn_code):
            return None

        hsn_doc = smriti.documents.get("GST HSN Code", hsn_code)
        if not hsn_doc.taxes:
            return None

        # Get the first matching Item Tax Template (prefer company-specific)
        template_name = None
        for tax in hsn_doc.taxes:
            if not tax.item_tax_template:
                continue
            if company:
                tmpl_company = smriti.db.get("Item Tax Template", tax.item_tax_template, "company")
                if tmpl_company == company:
                    template_name = tax.item_tax_template
                    break
            else:
                template_name = tax.item_tax_template
                break

        if not template_name and hsn_doc.taxes:
            # Fallback to first available template
            template_name = hsn_doc.taxes[0].item_tax_template

        if not template_name:
            return None

        # Sum up tax rates from the template details (CGST + SGST = total GST)
        total_rate = smriti.db.sql(
            "SELECT SUM(tax_rate) FROM `tabItem Tax Template Detail` WHERE parent = %s",
            (template_name,)
        )

        if total_rate and total_rate[0][0]:
            return int(total_rate[0][0])

        return None
    except Exception:
        return None


def sync_item_taxes_and_prices(doc, method):
    """
    Triggers before_save on Item.
    1. Enforces Master Data Governance validations.
    2. HSN-first: If gst_hsn_code is set, derive custom_gst_percentage from India Compliance's HSN master.
       Falls back to manual custom_gst_percentage only when HSN is absent or has no configured taxes.
    3. Maps the resolved GST percentage to the correct Item Tax Template.
    4. Syncs custom_mrp to standard Item Price.
    5. Handles UOM fallbacks.
    """
    # Enforce SMRITI Master Data Governance Foundation validations
    from smriti_retail_os.services.master_data_validator import validate as validate_master_data
    validate_master_data(doc, strict=True, collect_errors=False)

    if not doc.stock_uom:
        doc.stock_uom = "Nos"

    company = frappe.defaults.get_user_default("company") or smriti.db.get("Company", {}, "name")

    # HSN-first: derive GST % from HSN Code if available
    hsn_derived_rate = None
    if doc.gst_hsn_code:
        hsn_derived_rate = get_gst_rate_from_hsn(doc.gst_hsn_code, company)
        if hsn_derived_rate is not None:
            # Auto-populate custom_gst_percentage as a derived read-only value
            try:
                doc.custom_gst_percentage = str(hsn_derived_rate)
            except Exception:
                import sys
                _frappe = sys.modules.get('frappe')
                if _frappe: _frappe.logger().warning(f"SMRITI Warning: Financial/Data-integrity-adjacent exception in hooks_logic.py:158: {sys.exc_info()[1]}")

    # Resolve the effective GST percentage (HSN-derived takes priority)
    pct = hsn_derived_rate if hsn_derived_rate is not None else cint(doc.custom_gst_percentage or 0)

    if pct:
        template_name = smriti.db.get(
            "Item Tax Template", 
            {"name": ["like", f"%{pct}%"], "company": company}, 
            "name"
        )
        
        if not template_name:
            company_templates = smriti.db.get_list(
                "Item Tax Template",
                filters={"company": company},
                pluck="name"
            )
            if company_templates:
                details = smriti.db.get_list(
                    "Item Tax Template Detail",
                    filters={"tax_rate": pct, "parent": ["in", company_templates]},
                    pluck="parent",
                    limit=1
                )
                if details:
                    template_name = details[0]
                
        if template_name:
            # Skip if the correct template is already the sole entry (idempotent)
            existing = [t.item_tax_template for t in (doc.taxes or [])]
            if existing == [template_name]:
                return
            # Properly clear child table (doc.taxes = [] doesn't work in Frappe hooks)
            doc.set("taxes", [])
            doc.append("taxes", {
                "item_tax_template": template_name,
                "tax_category": ""
            })

def after_item_save(doc, method):
    """
    Triggers on_update on Item.
    """
    if doc.has_variants:
        return

    if doc.custom_mrp:
        sync_price_list_rate(doc.name, "MRP", flt(doc.custom_mrp), doc.stock_uom)
        
    if doc.standard_rate:
        sync_price_list_rate(doc.name, "Standard Selling", flt(doc.standard_rate), doc.stock_uom)

def sync_price_list_rate(item_code, price_list, rate, uom):
    if not smriti.db.exists("Price List", price_list):
        pl = smriti.documents.new("Price List")
        pl.price_list_name = price_list
        pl.enabled = 1
        pl.buying = 1 if price_list == "Standard Buying" else 0
        pl.selling = 0 if price_list == "Standard Buying" else 1
        pl.currency = "INR"
        pl.insert(ignore_permissions=True)

    filters = {
        "item_code": item_code,
        "price_list": price_list,
        "uom": uom
    }
    ip_name = smriti.db.get("Item Price", filters, "name")
    
    if ip_name:
        ip = smriti.documents.get("Item Price", ip_name)
        ip.price_list_rate = rate
        ip.save(ignore_permissions=True)
    else:
        ip = smriti.documents.new("Item Price")
        ip.item_code = item_code
        ip.price_list = price_list
        ip.price_list_rate = rate
        ip.uom = uom
        ip.currency = "INR"
        ip.insert(ignore_permissions=True)


# --- Customer Hooks ---

def sync_customer_address(doc, method):
    """
    Triggers on_update on Customer.
    Auto-creates or updates standard linked Address record from custom_address_text
    and custom_shipping_address_text.
    M-01: Both sync blocks are wrapped in try/except — address sync is a convenience
    feature and must NEVER roll back the parent Customer save on failure.
    """
    # --- Billing Address ---
    if doc.custom_address_text:
        try:
            address_title = f"{doc.customer_name} - Retail Billing"
            address_lines = [line.strip() for line in doc.custom_address_text.split("\n") if line.strip()]

            address_line1 = address_lines[0] if len(address_lines) > 0 else "N/A"
            address_line2 = ", ".join(address_lines[1:]) if len(address_lines) > 1 else ""

            state = resolve_address_state(doc.tax_id or doc.get("gstin"), doc.custom_address_text)

            gstin_state = resolve_address_state(doc.tax_id or doc.get("gstin"))
            resolved_gstin = doc.tax_id if state == gstin_state else None

            existing_address = smriti.db.get(
                "Address",
                {
                    "links.link_doctype": "Customer",
                    "links.link_name": doc.name,
                    "address_type": "Billing"
                },
                "name"
            )

            if existing_address:
                addr = smriti.documents.get("Address", existing_address)
                addr.address_line1 = address_line1[:140]
                addr.address_line2 = address_line2[:140] if address_line2 else None
                addr.gstin = resolved_gstin
                addr.state = state
                addr.save(ignore_permissions=True)
            else:
                addr = smriti.documents.new("Address")
                addr.address_title = address_title[:140]
                addr.address_type = "Billing"
                addr.address_line1 = address_line1[:140]
                addr.address_line2 = address_line2[:140] if address_line2 else None
                addr.city = "Unknown"
                addr.country = "India"
                addr.state = state
                addr.gstin = resolved_gstin
                addr.append("links", {
                    "link_doctype": "Customer",
                    "link_name": doc.name
                })
                addr.insert(ignore_permissions=True)
        except Exception:
            smriti.errors.log_error(
                title=f"SMRITI: Billing address sync failed for Customer {doc.name}",
                message=frappe.get_traceback()
            )

    # --- Shipping Address ---
    if doc.get("custom_shipping_address_text"):
        try:
            address_title = f"{doc.customer_name} - Retail Shipping"
            address_lines = [line.strip() for line in doc.custom_shipping_address_text.split("\n") if line.strip()]

            address_line1 = address_lines[0] if len(address_lines) > 0 else "N/A"
            address_line2 = ", ".join(address_lines[1:]) if len(address_lines) > 1 else ""

            state = resolve_address_state(doc.tax_id or doc.get("gstin"), doc.custom_shipping_address_text)

            gstin_state = resolve_address_state(doc.tax_id or doc.get("gstin"))
            resolved_gstin = doc.tax_id if state == gstin_state else None

            existing_address = smriti.db.get(
                "Address",
                {
                    "links.link_doctype": "Customer",
                    "links.link_name": doc.name,
                    "address_type": "Shipping"
                },
                "name"
            )

            if existing_address:
                addr = smriti.documents.get("Address", existing_address)
                addr.address_line1 = address_line1[:140]
                addr.address_line2 = address_line2[:140] if address_line2 else None
                addr.gstin = resolved_gstin
                addr.state = state
                addr.save(ignore_permissions=True)
            else:
                addr = smriti.documents.new("Address")
                addr.address_title = address_title[:140]
                addr.address_type = "Shipping"
                addr.address_line1 = address_line1[:140]
                addr.address_line2 = address_line2[:140] if address_line2 else None
                addr.city = "Unknown"
                addr.country = "India"
                addr.state = state
                addr.gstin = resolved_gstin
                addr.append("links", {
                    "link_doctype": "Customer",
                    "link_name": doc.name
                })
                addr.insert(ignore_permissions=True)
        except Exception:
            smriti.errors.log_error(
                title=f"SMRITI: Shipping address sync failed for Customer {doc.name}",
                message=frappe.get_traceback()
            )


# --- Supplier Hooks ---

def sync_supplier_address_and_credit_days(doc, method):
    """
    Triggers on_update on Supplier.
    1. Ensures SMRITI Supplier counterpart exists and stays in sync.
    2. Auto-creates standard linked Address from custom_address_text and custom_shipping_address_text.
    3. Resolves custom_credit_days to a standard Payment Terms Template and links it.
    """
    # ── Sync/Ensure SMRITI Supplier Counterpart ───────────────────────────
    smriti_sup_name = smriti.db.get("SMRITI Supplier", {"supplier_name": doc.supplier_name}, "name")
    if not smriti_sup_name:
        s = smriti.documents.new("SMRITI Supplier")
        s.supplier_name = doc.supplier_name
        s.supplier_type = doc.supplier_type or "Company"
        s.supplier_group = doc.supplier_group or "Local"
        s.tax_id = doc.tax_id
        s.mobile_no = doc.mobile_no
        s.email_id = doc.email_id
        s.disabled = doc.disabled
        s.erpnext_supplier = doc.name
        s.insert(ignore_permissions=True)
    else:
        s = smriti.documents.get("SMRITI Supplier", smriti_sup_name)
        if s.erpnext_supplier != doc.name or s.supplier_name != doc.supplier_name or s.disabled != doc.disabled:
            s.erpnext_supplier = doc.name
            s.supplier_name = doc.supplier_name
            s.disabled = doc.disabled
            s.save(ignore_permissions=True)

    # 1. Sync Address (Billing)
    if doc.custom_address_text:
        try:
            address_title = f"{doc.supplier_name} - Retail Purchase"
            address_lines = [line.strip() for line in doc.custom_address_text.split("\n") if line.strip()]
            
            address_line1 = address_lines[0] if len(address_lines) > 0 else "N/A"
            address_line2 = ", ".join(address_lines[1:]) if len(address_lines) > 1 else ""
            
            state = resolve_address_state(doc.gstin or doc.tax_id, doc.custom_address_text)
            
            gstin_state = resolve_address_state(doc.gstin or doc.tax_id)
            resolved_gstin = (doc.gstin or doc.tax_id) if state == gstin_state else None

            existing_address = smriti.db.get(
                "Address",
                {
                    "links.link_doctype": "Supplier",
                    "links.link_name": doc.name,
                    "address_type": "Billing"
                },
                "name"
            )

            if existing_address:
                addr = smriti.documents.get("Address", existing_address)
                addr.address_line1 = address_line1[:140]
                addr.address_line2 = address_line2[:140] if address_line2 else None
                addr.gstin = resolved_gstin
                addr.state = state
                addr.save(ignore_permissions=True)
            else:
                addr = smriti.documents.new("Address")
                addr.address_title = address_title[:140]
                addr.address_type = "Billing"
                addr.address_line1 = address_line1[:140]
                addr.address_line2 = address_line2[:140] if address_line2 else None
                addr.city = "Unknown"
                addr.country = "India"
                addr.state = state
                addr.gstin = resolved_gstin
                addr.append("links", {
                    "link_doctype": "Supplier",
                    "link_name": doc.name
                })
                addr.insert(ignore_permissions=True)
        except Exception:
            smriti.errors.log_error(
                title=f"SMRITI: Billing address sync failed for Supplier {doc.name}",
                message=frappe.get_traceback()
            )

    # 1b. Sync Address (Shipping)
    if doc.get("custom_shipping_address_text"):
        try:
            address_title = f"{doc.supplier_name} - Retail Supplier Shipping"
            address_lines = [line.strip() for line in doc.custom_shipping_address_text.split("\n") if line.strip()]
            
            address_line1 = address_lines[0] if len(address_lines) > 0 else "N/A"
            address_line2 = ", ".join(address_lines[1:]) if len(address_lines) > 1 else ""
            
            state = resolve_address_state(doc.gstin or doc.tax_id, doc.custom_shipping_address_text)
            
            gstin_state = resolve_address_state(doc.gstin or doc.tax_id)
            resolved_gstin = (doc.gstin or doc.tax_id) if state == gstin_state else None

            existing_address = smriti.db.get(
                "Address",
                {
                    "links.link_doctype": "Supplier",
                    "links.link_name": doc.name,
                    "address_type": "Shipping"
                },
                "name"
            )

            if existing_address:
                addr = smriti.documents.get("Address", existing_address)
                addr.address_line1 = address_line1[:140]
                addr.address_line2 = address_line2[:140] if address_line2 else None
                addr.gstin = resolved_gstin
                addr.state = state
                addr.save(ignore_permissions=True)
            else:
                addr = smriti.documents.new("Address")
                addr.address_title = address_title[:140]
                addr.address_type = "Shipping"
                addr.address_line1 = address_line1[:140]
                addr.address_line2 = address_line2[:140] if address_line2 else None
                addr.city = "Unknown"
                addr.country = "India"
                addr.state = state
                addr.gstin = resolved_gstin
                addr.append("links", {
                    "link_doctype": "Supplier",
                    "link_name": doc.name
                })
                addr.insert(ignore_permissions=True)
        except Exception:
            smriti.errors.log_error(
                title=f"SMRITI: Shipping address sync failed for Supplier {doc.name}",
                message=frappe.get_traceback()
            )

    # 2. Sync Credit Days -> Payment Terms Template
    if doc.custom_credit_days:
        days = cint(doc.custom_credit_days)
        template_name = f"Credit Term - {days} Days"

        if not smriti.db.exists("Payment Terms Template", template_name):
            ptt = smriti.documents.new("Payment Terms Template")
            ptt.template_name = template_name
            ptt.append("terms", {
                "invoice_portion": 100.0,
                "credit_days": days,
                "due_date_based_on": "Day(s) after invoice date"
            })
            ptt.insert(ignore_permissions=True)

        if doc.payment_terms != template_name:
            smriti.db.set_value("Supplier", doc.name, "payment_terms", template_name)


def initialize_item_wise_tax_details(doc, method=None):
    """Ensure _item_wise_tax_details is always initialized to an empty list
    to prevent TypeError inside india_compliance's validate_item_wise_tax_detail.
    """
    if not hasattr(doc, "_item_wise_tax_details") or getattr(doc, "_item_wise_tax_details") is None:
        doc._item_wise_tax_details = []


# --- POS Invoice / Sales Invoice Hooks ---

def validate_and_reconcile_retail_invoice(doc, method):
    """
    Triggers before_validate/before_save/before_submit on POS Invoice and Sales Invoice.
    Validates loyalty redemption credits, wallet deductions, and coupon limits on the server.
    """
    initialize_item_wise_tax_details(doc)
    if doc.docstatus == 2:
        return
        
    # 1. Validate Loyalty Redemption Credits
    if doc.redeem_loyalty_points and doc.loyalty_points > 0:
        try:
            from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_details
            if doc.customer:
                loyalty_details = get_loyalty_details(doc.customer, doc.posting_date)
                available_points = loyalty_details.get("loyalty_points", 0)
                if doc.loyalty_points > available_points:
                    frappe.throw(
                        _("Customer loyalty points balance ({0}) is less than points requested for redemption ({1}).").format(
                            available_points, doc.loyalty_points
                        )
                    )
        except ImportError:
            # C-05 FIX: Only catch ImportError (india_compliance/erpnext module not installed).
            # Fallback raw database check when the module is not available:
            loyalty_program = smriti.db.get("Customer", doc.customer, "loyalty_program")
            if loyalty_program:
                points = smriti.db.sql(
                    "SELECT SUM(remaining_points) FROM `tabLoyalty Point Entry` WHERE customer=%s AND loyalty_program=%s",
                    (doc.customer, loyalty_program)
                )
                available_points = (points[0][0] if points and points[0][0] else 0)
                if doc.loyalty_points > available_points:
                    frappe.throw(
                        _("Customer loyalty points balance ({0}) is less than points requested for redemption ({1}).").format(
                            available_points, doc.loyalty_points
                        )
                    )

    # 2. Validate CGE Wallet Deduction (AUD-03 & AUD-04)
    settings = smriti.documents.get_single("CGESettings")
    wallet_ded_amt = flt(doc.get("custom_wallet_deduction"))
    if wallet_ded_amt > 0.0:
        if not settings.enable_cashback:
            frappe.throw(_("Cashback Wallet is disabled in CGE settings."), frappe.ValidationError)
            
        from smriti_retail_os.cge.service.cge_service import get_active_wallet_balance
        active_bal = get_active_wallet_balance(doc.customer)
        if wallet_ded_amt > active_bal:
            frappe.throw(
                _("Requested wallet deduction {0} exceeds active cashback balance {1}.").format(
                    wallet_ded_amt, active_bal
                ),
                frappe.ValidationError
            )

    # 3. Validate Coupon Code (AUD-02 & AUD-04)
    coupon_code = doc.get("coupon_code") or doc.get("custom_coupon_code")
    if coupon_code:
        if not settings.enable_coupon:
            frappe.throw(_("Coupon Studio is disabled in CGE settings."), frappe.ValidationError)
            
        from smriti_retail_os.cge.service.cge_service import validate_coupon_code
        coupon = validate_coupon_code(coupon_code, doc.customer, doc.name)
        
        # Check campaign budget limits
        coupon_disc_amt = flt(doc.get("custom_coupon_discount") or doc.get("discount_amount"))
        if coupon.custom_campaign and settings.enable_campaign_budget:
            campaign = smriti.documents.get("SMRITI Coupon Campaign", coupon.custom_campaign)
            if campaign.stop_on_limit:
                total_exposure = flt(campaign.budget_consumed) + flt(campaign.budget_reserved) + coupon_disc_amt
                if total_exposure > flt(campaign.budget_limit):
                    frappe.throw(
                        _("Campaign budget limit exceeded for campaign {0}.").format(campaign.campaign_name),
                        frappe.ValidationError
                    )


def after_address_save(doc, method=None):
    """Frappe Address on_update doc_event hook to write changes to SMRITI Address Audit Log."""
    # Check if this Address is linked to a Company
    company_link = None
    for link in doc.get("links") or []:
        if link.link_doctype == "Company":
            company_link = link.link_name
            break
            
    if not company_link:
        return
        
    meta = frappe.get_meta("Address")
    address_fields = [
        "address_title", "address_line1", "address_line2",
        "city", "state", "country", "pincode",
        "gstin", "gst_state", "gst_state_number",
        "landmark", "latitude", "longitude"
    ]
    valid_fields = [f for f in address_fields if meta.has_field(f)]
    
    for field in valid_fields:
        old_val = doc.get_db_value(field)
        new_val = doc.get(field)
        
        # Normalize to string
        old_str = str(old_val or "").strip()
        new_str = str(new_val or "").strip()
        
        if old_str != new_str:
            try:
                # Write to SMRITI Address Audit Log
                log_doc = smriti.documents.new("SMRITI Address Audit Log")
                log_doc.changed_by = frappe.session.user
                log_doc.changed_at = frappe.utils.now_datetime()
                log_doc.field_name = field
                log_doc.old_value = old_str
                log_doc.new_value = new_str
                log_doc.company = company_link
                log_doc.insert(ignore_permissions=True)
            except Exception as audit_ex:
                smriti.errors.log_error(f"Error logging address audit trail: {str(audit_ex)}")


def release_reserved_budget_on_trash(doc, method=None):
    """
    Hook handler on POS/Sales Invoice trash/delete.
    Releases campaign budget reservation from Redis and DB (AUD-17).
    """
    from frappe.utils import flt
    settings = smriti.documents.get_single("CGESettings")
    if not settings.enable_coupon:
        return
        
    coupon_code = doc.get("coupon_code") or doc.get("custom_coupon_code")
    if not coupon_code:
        return
        
    session_id = doc.get("custom_billing_session_id") or f"pos_{doc.name}"
    cache_key = f"{session_id}_{coupon_code}"
    
    # Check Redis reservation first
    reservation = smriti.cache().hget("cge_budget_reservations", cache_key)
    if reservation:
        campaign_name = reservation.get("campaign")
        amount = flt(reservation.get("amount"))
        
        if smriti.db.exists("SMRITI Coupon Campaign", campaign_name):
            campaign = smriti.documents.get("SMRITI Coupon Campaign", campaign_name)
            campaign.budget_reserved = max(0.0, flt(campaign.budget_reserved) - amount)
            campaign.save(ignore_permissions=True)
            
        smriti.cache().hdel("cge_budget_reservations", cache_key)
