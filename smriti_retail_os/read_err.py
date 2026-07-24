import frappe

def test():
    errs = frappe.db.sql("""SELECT name, method, error FROM `tabError Log` ORDER BY creation DESC LIMIT 3""", as_dict=True)
    for e in errs:
        print("=== METHOD ===")
        print(e.method)
        print("=== ERROR TRACEBACK ===")
        print(e.error)
        print("--------------------------------------------------")
