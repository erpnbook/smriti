# -*- coding: utf-8 -*-
# SMRITI Purchase Studio — Purchase Order Service
import frappe
from frappe import _
from frappe.utils import flt, cint, nowdate, now_datetime
from smriti_retail_os.purchase_studio.repository import PurchaseRepository
from smriti_retail_os.purchase_studio.service.purchase_calculation_service import PurchaseCalculationService
from smriti_retail_os.purchase_studio.service.purchase_validation_service import PurchaseValidationService
from smriti_retail_os.purchase_studio.service.purchase_workflow_service import PurchaseWorkflowService
from smriti_retail_os.purchase_studio.adapter import erp_adapter

class PurchaseOrderService:
    @staticmethod
    def create_supplier(supplier_data):
        doc = PurchaseRepository.new_doc("SMRITI Supplier")
        doc.supplier_name = supplier_data.get("supplier_name")
        doc.supplier_type = supplier_data.get("supplier_type", "Company")
        doc.supplier_group = supplier_data.get("supplier_group")
        doc.tax_id = supplier_data.get("tax_id")
        doc.mobile_no = supplier_data.get("mobile_no")
        doc.email_id = supplier_data.get("email_id")
        doc.billing_address = supplier_data.get("billing_address")
        doc.shipping_address = supplier_data.get("shipping_address")
        doc.disabled = supplier_data.get("disabled", 0)
        
        PurchaseRepository.save_supplier(doc)
        return doc.name

    @staticmethod
    def get_supplier_detail(supplier_id):
        doc = PurchaseRepository.get_supplier(supplier_id)
        return {
            "name": doc.name,
            "supplier_name": doc.supplier_name,
            "supplier_type": doc.supplier_type,
            "supplier_group": doc.supplier_group,
            "tax_id": doc.tax_id,
            "mobile_no": doc.mobile_no,
            "email_id": doc.email_id,
            "billing_address": doc.billing_address,
            "shipping_address": doc.shipping_address,
            "disabled": doc.disabled
        }

    @staticmethod
    def list_suppliers(search_term=None, limit=50):
        filters = {"disabled": 0}
        if search_term:
            filters["supplier_name"] = ["like", f"%{search_term}%"]
        return PurchaseRepository.list_suppliers(filters=filters, limit=limit)

    @staticmethod
    def create_purchase_order(supplier, items_list, schedule_date=None, remarks=None, warehouse=None, company=None):
        po = PurchaseRepository.new_doc("SMRITI Purchase Order")
        po.supplier = supplier
        po.supplier_name = frappe.db.get_value("SMRITI Supplier", supplier, "supplier_name") or supplier
        po.transaction_date = nowdate()
        po.schedule_date = schedule_date or nowdate()
        po.company = company or frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
        po.remarks = remarks
        po.status = "Draft"
        po.naming_series = "SMRITI-PO-.YYYY.-"

        for it in items_list:
            po.append("items", {
                "item_code": it.get("item_code"),
                "item_name": it.get("item_name") or frappe.db.get_value("Item", it.get("item_code"), "item_name"),
                "qty": flt(it.get("qty")),
                "rate": flt(it.get("rate")),
                "warehouse": it.get("warehouse") or warehouse,
                "uom": it.get("uom") or frappe.db.get_value("Item", it.get("item_code"), "stock_uom"),
                "article": it.get("article"),
                "attribute_summary": it.get("attribute_summary"),
                "barcode": it.get("barcode")
            })

        # Calculate amounts & validation
        PurchaseCalculationService.calculate_totals(po)
        PurchaseValidationService.validate_po(po)

        # Check approval requirement and save/workflow transition
        PurchaseRepository.insert_po(po)
        
        # Trigger workflow transition from Draft -> Submitted/Approved
        PurchaseWorkflowService.submit(po.name)
        
        # Retrieve the updated status
        po.reload()
        return {
            "status": "submitted" if po.status == "Approved" else "pending_approval",
            "name": po.name,
            "grand_total": po.grand_total,
            "message": _("SMRITI Purchase Order {0} created.").format(po.name)
        }

    @staticmethod
    def resolve_po_approval(po_name, action, reason=None):
        if action == "approve":
            po = PurchaseWorkflowService.approve(po_name, frappe.session.user)
            return {
                "status": "approved",
                "name": po_name,
                "message": _("Purchase Order {0} approved successfully.").format(po_name)
            }
        elif action == "reject":
            if not reason:
                frappe.throw(_("Rejection reason is mandatory."))
            po = PurchaseWorkflowService.reject(po_name, reason)
            return {
                "status": "rejected",
                "name": po_name,
                "message": _("Purchase Order {0} rejected.").format(po_name)
            }
        else:
            frappe.throw(_("Invalid approval action."))

    @staticmethod
    def get_purchase_order_detail(po_name):
        po = PurchaseRepository.get_po(po_name)
        items = []
        for item in po.items:
            items.append({
                "name": item.name,
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": flt(item.qty),
                "received_qty": flt(item.received_qty),
                "pending_qty": flt(item.pending_qty),
                "rate": flt(item.rate),
                "amount": flt(item.amount),
                "warehouse": item.warehouse,
                "uom": item.uom,
                "article": item.article,
                "attribute_summary": item.attribute_summary,
                "barcode": item.barcode
            })
        return {
            "name": po.name,
            "supplier": po.supplier,
            "supplier_name": po.supplier_name,
            "company": po.company,
            "transaction_date": str(po.transaction_date or ""),
            "schedule_date": str(po.schedule_date or ""),
            "remarks": po.remarks or "",
            "status": po.status,
            "grand_total": flt(po.grand_total),
            "total_qty": flt(po.total_qty),
            "per_received": flt(po.per_received),
            "approved_by": po.approved_by or "",
            "approved_on": str(po.approved_on or ""),
            "rejection_reason": po.rejection_reason or "",
            "items": items
        }

    @staticmethod
    def list_purchase_orders(company=None, supplier=None, status=None, from_date=None, to_date=None, search_term=None, page=1, page_size=50):
        filters = {}
        if company:
            filters["company"] = company
        if supplier:
            filters["supplier"] = supplier
        if status:
            filters["status"] = status
        if from_date:
            filters["transaction_date"] = [">=", from_date]
        if to_date:
            filters.setdefault("transaction_date", ["<=", to_date])
        if search_term:
            filters["name"] = ["like", f"%{search_term}%"]

        limit_start = (int(page) - 1) * int(page_size)
        pos = frappe.get_list(
            "SMRITI Purchase Order",
            filters=filters,
            fields=["name", "supplier", "supplier_name", "transaction_date", "grand_total", "per_received", "status"],
            order_by="creation desc",
            limit_start=limit_start,
            limit_page_length=int(page_size)
        )
        total = frappe.db.count("SMRITI Purchase Order", filters=filters)
        return {
            "items": pos,
            "total": total
        }

    @staticmethod
    def get_dashboard_data(company=None):
        company = company or frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")

        # Count open SMRITI POs (intent + approval layer)
        open_pos = frappe.db.count("SMRITI Purchase Order", {
            "company": company,
            "status": ["in", ["Submitted", "Approved", "Ordered", "Partially Received"]]
        })

        # Real GRNs pending full billing (Purchase Receipts with per_billed < 100%)
        pending_grns = erp_adapter.count_pending_grns(company)

        # Real outstanding payable from ERPNext Purchase Invoices (GST-inclusive)
        unpaid_invoices_amt = erp_adapter.get_outstanding_payables_total(company)

        # Monthly spend from ERPNext Purchase Invoices (actual GST-inclusive payments)
        from datetime import date
        month_start = date.today().replace(day=1).isoformat()
        month_spend = erp_adapter.get_monthly_spend_total(company, month_start)

        # Recent cross-doctype activity: PO + GRN + PI from ERPNext
        recent_activities = erp_adapter.get_recent_activities(company, limit=10)

        return {
            "open_pos": open_pos,
            "pending_grns": pending_grns,
            "unpaid_invoices_amt": unpaid_invoices_amt,
            "month_spend": month_spend,
            "recent_activity": recent_activities
        }
