# -*- coding: utf-8 -*-
# SMRITI Purchase Studio — Purchase Order Service
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
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
    def create_purchase_order(supplier, items_list, schedule_date=None, remarks=None, warehouse=None, company=None, tc_name=None, terms=None, po_name=None, submit=0):
        # Resolve supplier to a valid SMRITI Supplier name
        smriti_sup_name = None
        if supplier:
            if frappe.db.exists("SMRITI Supplier", supplier):
                smriti_sup_name = supplier
            else:
                existing = frappe.db.get_value("SMRITI Supplier", {"supplier_name": supplier}, "name")
                if existing:
                    smriti_sup_name = existing
                else:
                    try:
                        sdoc = frappe.new_doc("SMRITI Supplier")
                        sdoc.supplier_name = supplier
                        sdoc.insert(ignore_permissions=True)
                        smriti_sup_name = sdoc.name
                    except Exception:
                        smriti_sup_name = frappe.db.get_value("SMRITI Supplier", {"supplier_name": supplier}, "name") or supplier

        is_existing = False
        if po_name and po_name != "PO-DRAFT-NEW" and frappe.db.exists("SMRITI Purchase Order", po_name):
            po = frappe.get_doc("SMRITI Purchase Order", po_name)
            po.items = []
            is_existing = True
        else:
            po = PurchaseRepository.new_doc("SMRITI Purchase Order")
            po.status = "Draft"
            po.naming_series = "SMRITI-PO-.YYYY.-"

        po.supplier = smriti_sup_name
        po.supplier_name = (
            smriti.db.get("SMRITI Supplier", smriti_sup_name, "supplier_name") or
            smriti.db.get("Supplier", supplier, "supplier_name") or
            supplier
        )
        po.transaction_date = nowdate()
        po.schedule_date = schedule_date or nowdate()
        po.company = company or frappe.defaults.get_user_default("Company") or smriti.db.get("Company", {}, "name")
        po.remarks = remarks
        if hasattr(po, "tc_name"):
            po.tc_name = tc_name
        if hasattr(po, "terms"):
            po.terms = terms

        default_hsn = frappe.db.get_value("GST HSN Code", {}, "name")
        if not default_hsn:
            try:
                hdoc = frappe.new_doc("GST HSN Code")
                hdoc.hsn_code = "6403"
                hdoc.insert(ignore_permissions=True)
                default_hsn = hdoc.name
            except Exception:
                default_hsn = "6403"

        for it in items_list:
            icode = it.get("item_code")
            iname = it.get("item_name") or icode
            
            # Ensure Item master record exists before appending to PO
            if icode and not frappe.db.exists("Item", icode):
                try:
                    item_doc = frappe.new_doc("Item")
                    item_doc.item_code = icode
                    item_doc.item_name = iname
                    item_doc.item_group = "All Item Groups"
                    item_doc.stock_uom = it.get("uom") or "Nos"
                    item_doc.valuation_rate = flt(it.get("rate"))
                    item_doc.gst_hsn_code = default_hsn
                    # reviewed-ignore-permissions: system matrix order creation
                    item_doc.insert(ignore_permissions=True)
                except Exception as e:
                    frappe.logger().error(f"Failed to auto-create item {icode}: {e}")

            po.append("items", {
                "item_code": icode,
                "item_name": iname,
                "qty": flt(it.get("qty")),
                "rate": flt(it.get("rate")),
                "warehouse": it.get("warehouse") or warehouse,
                "uom": it.get("uom") or smriti.db.get("Item", icode, "stock_uom") or "Nos",
                "article": it.get("article"),
                "attribute_summary": it.get("attribute_summary"),
                "barcode": it.get("barcode")
            })

        # Calculate amounts & validation
        PurchaseCalculationService.calculate_totals(po)
        PurchaseValidationService.validate_po(po)

        if is_existing:
            po.save(ignore_permissions=True)
        else:
            PurchaseRepository.insert_po(po)
        
        # Only submit if submit flag is 1 or '1'
        if int(submit or 0) == 1:
            PurchaseWorkflowService.submit(po.name)
            po.reload()

        return {
            "status": "submitted" if po.status in ("Approved", "Submitted") else "draft",
            "name": po.name,
            "grand_total": po.grand_total,
            "message": _("SMRITI Purchase Order {0} updated.").format(po.name) if is_existing else _("SMRITI Purchase Order {0} created.").format(po.name)
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
        total = smriti.db.count("SMRITI Purchase Order", filters=filters)
        return {
            "items": pos,
            "total": total
        }

    @staticmethod
    def get_dashboard_data(company=None):
        company = company or frappe.defaults.get_user_default("Company") or smriti.db.get("Company", {}, "name")

        # Count open SMRITI POs (intent + approval layer)
        open_pos = smriti.db.count("SMRITI Purchase Order", {
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
