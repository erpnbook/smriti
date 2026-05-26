import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_item_stock(item_code, warehouse=None):
    """
    Returns the actual stock quantity of an item.
    Aggregates across all warehouses if no warehouse is specified.
    """
    if warehouse:
        actual_qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0.0
    else:
        res = frappe.db.sql(
            "SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s",
            (item_code,)
        )
        actual_qty = res[0][0] if res and res[0][0] is not None else 0.0
        
    return {
        "actual_qty": flt(actual_qty)
    }
