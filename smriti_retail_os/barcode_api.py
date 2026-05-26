import frappe
from frappe.utils import flt, cint
from frappe import _

@frappe.whitelist()
def get_barcode_filters():
    """
    Returns available brands, categories, and custom barcode sizes
    to populate filters on the printing interface.
    """
    brands = [b.name for b in frappe.get_all("Brand", fields=["name"], order_by="name asc")]
    categories = [ig.name for ig in frappe.get_all("Item Group", fields=["name"], order_by="name asc")]
    sizes = ["50x25", "50x30", "75x50", "100x50"]
    return {
        "brands": brands,
        "categories": categories,
        "sizes": sizes
    }

@frappe.whitelist()
def get_items_for_printing(filters=None, source_doctype=None, source_name=None):
    """
    Loads items for barcode printing based on either a transaction source
    (Purchase Receipt or Stock Entry) or manual filter selection.
    """
    items = []

    if source_doctype and source_name:
        # Transaction-based loading
        if source_doctype == "Purchase Receipt":
            if not frappe.db.exists("Purchase Receipt", source_name):
                frappe.throw(_("Purchase Receipt {0} not found.").format(source_name))
            
            pr = frappe.get_doc("Purchase Receipt", source_name)
            for it in pr.items:
                items.append(get_item_print_details(it.item_code, it.qty))

        elif source_doctype == "Stock Entry":
            if not frappe.db.exists("Stock Entry", source_name):
                frappe.throw(_("Stock Entry {0} not found.").format(source_name))
            
            se = frappe.get_doc("Stock Entry", source_name)
            for it in se.items:
                items.append(get_item_print_details(it.item_code, it.qty))
                
    elif filters:
        # Manual bulk filter mode
        flt_dict = frappe.parse_json(filters)
        db_filters = {"disabled": 0, "custom_is_retail_item": 1}
        
        if flt_dict.get("brand"):
            db_filters["brand"] = flt_dict.get("brand")
        if flt_dict.get("item_group"):
            db_filters["item_group"] = flt_dict.get("item_group")
        if flt_dict.get("custom_barcode_size"):
            db_filters["custom_barcode_size"] = flt_dict.get("custom_barcode_size")
            
        or_filters = {}
        if flt_dict.get("search_text"):
            txt = flt_dict.get("search_text")
            or_filters = {
                "item_code": ["like", f"%{txt}%"],
                "item_name": ["like", f"%{txt}%"]
            }

        item_list = frappe.db.get_all(
            "Item",
            filters=db_filters,
            or_filters=or_filters,
            fields=["name"],
            limit=100
        )
        
        for it in item_list:
            items.append(get_item_print_details(it.name, 1))

    return items

def get_item_print_details(item_code, default_print_qty):
    """
    Helper function to resolve standard printing parameters for a single item.
    """
    item_doc = frappe.get_doc("Item", item_code)
    
    # 1. Fetch Barcode
    barcode = frappe.db.get_value("Item Barcode", {"parent": item_code}, "barcode") or item_code
    
    # 2. Fetch MRP or standard price
    mrp = item_doc.custom_mrp or frappe.db.get_value(
        "Item Price", 
        {"item_code": item_code, "price_list": "MRP"}, 
        "price_list_rate"
    ) or frappe.db.get_value(
        "Item Price", 
        {"item_code": item_code, "price_list": "Standard Selling"}, 
        "price_list_rate"
    ) or item_doc.valuation_rate or 0.0

    # 3. Resolve Size from attributes or default
    size = "L"
    if item_doc.attributes:
        for attr in item_doc.attributes:
            if attr.attribute in ["Size", "size", "SIZE"]:
                size = attr.attribute_value
                break

    return {
        "item_code": item_doc.name,
        "item_name": item_doc.item_name,
        "brand": item_doc.brand or "SMRITI",
        "item_group": item_doc.item_group,
        "barcode": barcode,
        "mrp": flt(mrp),
        "size": size,
        "print_qty": cint(default_print_qty) or 1,
        "label_size": item_doc.custom_barcode_size or "50x25"
    }

@frappe.whitelist()
def generate_prn(items):
    """
    Takes a JSON string of items and returns a merged Zebra ZPL PRN instructions string.
    """
    if not items:
        return ""

    items_list = frappe.parse_json(items)
    prn_output = []

    for it in items_list:
        barcode = it.get("barcode")
        item_name = it.get("item_name")[:25]  # Limit to fit label
        mrp = flt(it.get("mrp"))
        brand = it.get("brand") or "SMRITI"
        size = it.get("size") or "Nos"
        qty = cint(it.get("print_qty")) or 1
        label_size = it.get("label_size") or "50x25"

        # Generate ZPL coordinates depending on label size
        # standard 50x25 label (small)
        x_offset = 20
        y_offset_bc = 10
        y_offset_name = 80
        y_offset_mrp = 100
        y_offset_brand = 120
        
        if label_size == "50x30":
            y_offset_name = 85
            y_offset_mrp = 110
            y_offset_brand = 135
        elif label_size == "75x50":
            x_offset = 40
            y_offset_bc = 20
            y_offset_name = 120
            y_offset_mrp = 155
            y_offset_brand = 190
        elif label_size == "100x50":
            x_offset = 50
            y_offset_bc = 20
            y_offset_name = 130
            y_offset_mrp = 170
            y_offset_brand = 210

        label_zpl = (
            f"^XA\n"
            f"^FO{x_offset},{y_offset_bc}^BCN,60,Y,N,N^FD{barcode}^FS\n"
            f"^FO{x_offset},{y_offset_name}^ADN,18,10^FD{item_name}^FS\n"
            f"^FO{x_offset},{y_offset_mrp}^ADN,18,10^FDMRP: Rs.{mrp:.2f}^FS\n"
            f"^FO{x_offset},{y_offset_brand}^ADN,14,8^FD{brand} | {size}^FS\n"
            f"^XZ"
        )

        for _ in range(qty):
            prn_output.append(label_zpl)

    return "\n".join(prn_output)
