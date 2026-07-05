import frappe

def run():
    print("Checking PO 9839a92r89:")
    exists = frappe.db.exists("SMRITI Purchase Order", "9839a92r89")
    print(f"Exists: {exists}")
    
    print("\nRecent SMRITI Purchase Orders:")
    pos = frappe.get_all("SMRITI Purchase Order", fields=["name", "supplier", "grand_total", "status", "docstatus"], limit=5)
    for po in pos:
        print(f"Name: {po.name} | Supplier: {po.supplier} | Total: {po.grand_total} | Status: {po.status} | Docstatus: {po.docstatus}")
