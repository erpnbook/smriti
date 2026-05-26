import frappe
from frappe.utils import flt, cint, nowdate
from frappe import _

def check_store_manager_role():
    """
    Enforces that only SMRITI Store Manager or System Manager can perform submissions.
    """
    roles = frappe.get_roles(frappe.session.user)
    if "SMRITI Store Manager" not in roles and "System Manager" not in roles:
        frappe.throw(_("Access Denied: Cashiers can only view. Only Store Managers or System Managers can submit purchase transactions."))

def get_or_create_batch(item_code, expiry_date=None):
    """
    Finds or creates a batch for an item, optionally with an expiry date.
    """
    if expiry_date:
        existing = frappe.db.get_value("Batch", {"item": item_code, "expiry_date": expiry_date, "disabled": 0}, "name")
        if existing:
            return existing
        
        batch_doc = frappe.new_doc("Batch")
        batch_doc.item = item_code
        batch_doc.expiry_date = expiry_date
        batch_doc.insert(ignore_permissions=True)
        return batch_doc.name
    else:
        existing = frappe.db.get_value("Batch", {"item": item_code, "disabled": 0}, "name", order_by="creation desc")
        if existing:
            return existing
        
        batch_doc = frappe.new_doc("Batch")
        batch_doc.item = item_code
        batch_doc.insert(ignore_permissions=True)
        return batch_doc.name

@frappe.whitelist()
def get_open_purchase_orders(supplier=None):
    """
    Fetches submitted and open Purchase Orders.
    """
    filters = {
        "docstatus": 1,
        "status": ["not in", ["Closed", "Completed"]]
    }
    if supplier:
        filters["supplier"] = supplier

    pos = frappe.get_all(
        "Purchase Order",
        filters=filters,
        fields=["name", "supplier", "supplier_name", "transaction_date", "grand_total", "per_received"],
        order_by="transaction_date desc"
    )
    return pos

@frappe.whitelist()
def get_po_details(po_name):
    """
    Fetches open item lines for a given Purchase Order.
    """
    if not frappe.db.exists("Purchase Order", po_name):
        return None

    po = frappe.get_doc("Purchase Order", po_name)
    items = []
    
    for item in po.items:
        # Calculate pending quantity to receive
        pending = flt(item.qty) - flt(item.received_qty)
        if pending > 0:
            has_batch_no = frappe.db.get_value("Item", item.item_code, "has_batch_no")
            items.append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "brand": item.brand,
                "qty": pending,
                "po_qty": item.qty,
                "received_qty": item.received_qty,
                "rate": item.rate,
                "stock_uom": item.stock_uom,
                "warehouse": item.warehouse,
                "po_item_name": item.name,
                "has_batch_no": cint(has_batch_no)
            })

    return {
        "name": po.name,
        "supplier": po.supplier,
        "supplier_name": po.supplier_name,
        "company": po.company,
        "items": items
    }

@frappe.whitelist()
def create_purchase_order(supplier, items):
    """
    Creates and submits a standard Purchase Order.
    """
    check_store_manager_role()

    if not items:
        frappe.throw(_("Cannot create Purchase Order with an empty items list."))

    items_list = frappe.parse_json(items)
    company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name
    warehouse = frappe.db.get_value("Warehouse", {"warehouse_name": "Stores"}, "name") or "Stores - _C"

    po = frappe.new_doc("Purchase Order")
    po.supplier = supplier
    po.transaction_date = nowdate()
    po.schedule_date = nowdate()
    po.company = company

    for it in items_list:
        item_code = it.get("item_code")
        qty = flt(it.get("qty"))
        rate = flt(it.get("rate"))
        wh = it.get("warehouse") or warehouse

        po.append("items", {
            "item_code": item_code,
            "qty": qty,
            "rate": rate,
            "warehouse": wh,
            "schedule_date": nowdate(),
            "uom": it.get("stock_uom") or frappe.db.get_value("Item", item_code, "stock_uom")
        })

    po.docstatus = 1  # Submit
    po.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "name": po.name,
        "message": _("Purchase Order {0} submitted successfully.").format(po.name)
    }

@frappe.whitelist()
def create_purchase_receipt(supplier, items, po_name=None):
    """
    Creates and submits a standard Purchase Receipt (GRN).
    Can be created against an existing Purchase Order or standalone (No PO).
    """
    check_store_manager_role()

    if not items:
        frappe.throw(_("Cannot create Purchase Receipt with an empty items list."))

    items_list = frappe.parse_json(items)
    company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name
    warehouse = frappe.db.get_value("Warehouse", {"warehouse_name": "Stores"}, "name") or "Stores - _C"

    pr = frappe.new_doc("Purchase Receipt")
    pr.supplier = supplier
    pr.posting_date = nowdate()
    pr.company = company

    # If linked to a PO, reference it at the header level as well
    if po_name and frappe.db.exists("Purchase Order", po_name):
        # Fetching details from the PO
        po_doc = frappe.get_doc("Purchase Order", po_name)
        pr.buying_price_list = po_doc.buying_price_list
        pr.currency = po_doc.currency
        pr.conversion_rate = po_doc.conversion_rate

    for it in items_list:
        item_code = it.get("item_code")
        qty = flt(it.get("qty"))
        rate = flt(it.get("rate"))
        wh = it.get("warehouse") or warehouse

        # Handle batch & expiry tracking
        batch_no = None
        has_batch_no = frappe.db.get_value("Item", item_code, "has_batch_no")
        if has_batch_no:
            expiry_date = it.get("expiry_date")
            batch_no = get_or_create_batch(item_code, expiry_date)

        row = {
            "item_code": item_code,
            "qty": qty,
            "rate": rate,
            "warehouse": wh,
            "batch_no": batch_no,
            "uom": it.get("stock_uom") or frappe.db.get_value("Item", item_code, "stock_uom")
        }

        # Map to Purchase Order if applicable
        if po_name:
            row["purchase_order"] = po_name
            row["purchase_order_item"] = it.get("po_item_name")

        pr.append("items", row)

    pr.docstatus = 1  # Submit
    pr.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "name": pr.name,
        "message": _("Purchase Receipt {0} submitted successfully.").format(pr.name)
    }
