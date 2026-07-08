# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/sales_studio/service/sales_service.py
# @desc:    Business logic and orchestration layer for SMRITI Sales Studio.
# @author:  Jawahar R. Mallah
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from frappe.utils import flt, cint, nowdate
from smriti_retail_os.sales_studio.repository.sales_repository import SalesRepository
from smriti_retail_os.sales_studio.service.sales_validation_service import SalesValidationService
from smriti_retail_os.sales_studio.service.sales_workflow_service import SalesWorkflowService

class SalesService:
    @staticmethod
    def get_allowed_roles():
        return ["SMRITI Store Manager", "System Manager", "Cashier"]

    @staticmethod
    def check_sales_access():
        """Enforces cashier or manager role access."""
        roles = frappe.get_roles(frappe.session.user)
        allowed = SalesService.get_allowed_roles()
        if not any(r in roles for r in allowed):
            frappe.throw(
                _("Access Denied: Sales Studio requires SMRITI cashier or manager permissions."),
                frappe.PermissionError
            )

    @staticmethod
    def resolve_item_details(item_code, company=None):
        """
        Resolves price, MRP, UOM, HSN, and default warehouse for an item.
        Uses native Item Price list resolution with custom fallbacks.
        """
        if not company:
            company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")

        item_doc = smriti.documents.get("Item", item_code)
        
        # Standard Selling Price lookup
        rate = smriti.db.get(
            "Item Price", 
            {"item_code": item_code, "price_list": "Standard Selling"}, 
            "price_list_rate"
        ) or item_doc.valuation_rate or 0.0

        # MRP Price lookup
        mrp = item_doc.custom_mrp or smriti.db.get(
            "Item Price", 
            {"item_code": item_code, "price_list": "MRP"}, 
            "price_list_rate"
        ) or rate

        # Resolve warehouse
        warehouse = smriti.db.get("Item Reorder", {"parent": item_code}, "warehouse") or item_doc.default_warehouse
        if not warehouse and company:
            warehouse = smriti.db.get("Warehouse", {"company": company, "is_group": 0}, "name")

        gst_percentage = cint(item_doc.custom_gst_percentage) if item_doc.custom_gst_percentage else 0
        if not gst_percentage and item_doc.gst_hsn_code:
            from smriti_retail_os.hooks_logic import get_gst_rate_from_hsn
            gst_percentage = get_gst_rate_from_hsn(item_doc.gst_hsn_code) or 0

        return {
            "item_code": item_code,
            "item_name": item_doc.item_name,
            "stock_uom": item_doc.stock_uom or "Nos",
            "brand": item_doc.brand,
            "rate": flt(rate),
            "mrp": flt(mrp),
            "gst_percentage": gst_percentage,
            "gst_hsn_code": item_doc.gst_hsn_code or "",
            "warehouse": warehouse
        }

    @staticmethod
    def create_quotation(customer, items_list, valid_till=None, remarks=None, company=None):
        """Creates and submits a Quotation."""
        SalesValidationService.validate_store_manager_role()

        if not items_list:
            frappe.throw(_("Cannot create Quotation with an empty items list."))

        if not company:
            company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")

        q = SalesRepository.new_doc("Quotation")
        q.quotation_to = "Customer"
        q.party_name = customer
        q.customer = customer
        q.transaction_date = nowdate()
        q.valid_till = valid_till or nowdate()
        q.company = company
        q.remarks = remarks
        q.docstatus = 0

        for it in items_list:
            item_code = it.get("item_code")
            qty = flt(it.get("qty") or 1)
            details = SalesService.resolve_item_details(item_code, company)

            q.append("items", {
                "item_code": item_code,
                "qty": qty,
                "rate": flt(it.get("rate") or details["rate"]),
                "warehouse": it.get("warehouse") or details["warehouse"],
                "uom": it.get("uom") or details["stock_uom"],
                "description": it.get("item_name") or details["item_name"]
            })

        # Set default tax / calculations
        q.run_method("set_missing_values")
        q.run_method("calculate_taxes_and_totals")

        # Hook to prevent India Compliance validate_item_wise_tax_detail TypeError
        from smriti_retail_os.hooks_logic import initialize_item_wise_tax_details
        initialize_item_wise_tax_details(q)

        SalesRepository.insert_quotation(q)
        SalesWorkflowService.submit_quotation(q.name)
        q.reload()

        return {
            "name": q.name,
            "grand_total": q.grand_total,
            "status": q.status,
            "message": _("Quotation {0} submitted successfully.").format(q.name)
        }

    @staticmethod
    def create_sales_order(customer, items_list, delivery_date=None, remarks=None, company=None):
        """Creates and submits a Sales Order."""
        SalesValidationService.validate_store_manager_role()

        if not items_list:
            frappe.throw(_("Cannot create Sales Order with an empty items list."))

        if not company:
            company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")

        so = SalesRepository.new_doc("Sales Order")
        so.customer = customer
        so.transaction_date = nowdate()
        so.delivery_date = delivery_date or nowdate()
        so.company = company
        so.remarks = remarks
        so.docstatus = 0

        for it in items_list:
            item_code = it.get("item_code")
            qty = flt(it.get("qty") or 1)
            details = SalesService.resolve_item_details(item_code, company)
            wh = it.get("warehouse") or details["warehouse"]

            # Perform live stock availability check
            SalesValidationService.check_stock_availability(item_code, qty, wh)

            so.append("items", {
                "item_code": item_code,
                "qty": qty,
                "rate": flt(it.get("rate") or details["rate"]),
                "warehouse": wh,
                "uom": it.get("uom") or details["stock_uom"],
                "delivery_date": delivery_date or nowdate(),
                "description": it.get("item_name") or details["item_name"]
            })

        # Run tax calculations
        so.run_method("set_missing_values")
        so.run_method("calculate_taxes_and_totals")

        # Hook validation bypass check
        from smriti_retail_os.hooks_logic import initialize_item_wise_tax_details
        initialize_item_wise_tax_details(so)

        SalesRepository.insert_sales_order(so)
        SalesWorkflowService.submit_sales_order(so.name)
        so.reload()

        return {
            "name": so.name,
            "grand_total": so.grand_total,
            "status": so.status,
            "message": _("Sales Order {0} booked successfully.").format(so.name)
        }

    @staticmethod
    def get_quotation_detail(name):
        SalesService.check_sales_access()
        doc = SalesRepository.get_quotation(name)
        items = []
        for it in doc.items:
            items.append({
                "item_code": it.item_code,
                "item_name": it.item_name,
                "qty": flt(it.qty),
                "rate": flt(it.rate),
                "amount": flt(it.amount),
                "warehouse": it.warehouse,
                "uom": it.uom
            })
        return {
            "name": doc.name,
            "customer": doc.customer,
            "customer_name": doc.customer_name or doc.customer,
            "company": doc.company,
            "transaction_date": str(doc.transaction_date),
            "valid_till": str(doc.valid_till or ""),
            "grand_total": flt(doc.grand_total),
            "status": doc.status,
            "remarks": doc.remarks or "",
            "items": items
        }

    @staticmethod
    def get_sales_order_detail(name):
        SalesService.check_sales_access()
        doc = SalesRepository.get_sales_order(name)
        items = []
        for it in doc.items:
            items.append({
                "item_code": it.item_code,
                "item_name": it.item_name,
                "qty": flt(it.qty),
                "delivered_qty": flt(it.delivered_qty or 0.0),
                "pending_qty": flt(it.qty) - flt(it.delivered_qty or 0.0),
                "rate": flt(it.rate),
                "amount": flt(it.amount),
                "warehouse": it.warehouse,
                "uom": it.uom
            })
        return {
            "name": doc.name,
            "customer": doc.customer,
            "customer_name": doc.customer_name or doc.customer,
            "company": doc.company,
            "transaction_date": str(doc.transaction_date),
            "delivery_date": str(doc.delivery_date or ""),
            "grand_total": flt(doc.grand_total),
            "status": doc.status,
            "remarks": doc.remarks or "",
            "per_delivered": flt(doc.per_delivered or 0.0),
            "items": items
        }

    @staticmethod
    def list_quotations(customer=None, status=None, limit=50):
        SalesService.check_sales_access()
        filters = {}
        if customer:
            filters["customer"] = customer
        if status:
            filters["status"] = status
        return SalesRepository.list_quotations(filters=filters, limit=limit)

    @staticmethod
    def list_sales_orders(customer=None, status=None, limit=50):
        SalesService.check_sales_access()
        filters = {}
        if customer:
            filters["customer"] = customer
        if status:
            filters["status"] = status
        return SalesRepository.list_sales_orders(filters=filters, limit=limit)

    @staticmethod
    def resolve_variant_item(article, color, size):
        """
        Returns the item_code for a variant matching the given article, color, and size.
        """
        SalesService.check_sales_access()

        if not article or not color or not size:
            return None

        # Resolve parent items matching article code
        items = smriti.db.get_list("Item", filters={
            "disabled": 0,
            "variant_of": article
        }, fields=["name"])

        if not items:
            items = smriti.db.get_list("Item", filters={
                "disabled": 0,
                "custom_style_code": article
            }, fields=["name"])

        if not items:
            if smriti.db.exists("Item", article):
                return article
            return None

        for item in items:
            attrs = smriti.db.get_list("Item Variant Attribute", filters={"parent": item.name}, fields=["attribute", "attribute_value"])
            attr_map = {a.attribute.lower(): a.attribute_value.lower() for a in attrs}

            has_color = False
            has_size = False

            c_val = attr_map.get("colour") or attr_map.get("color")
            if c_val and c_val == color.lower():
                has_color = True

            s_val = attr_map.get("size") or attr_map.get("shoe size")
            if s_val and s_val == size.lower():
                has_size = True

            if has_color and has_size:
                return item.name

        return None

