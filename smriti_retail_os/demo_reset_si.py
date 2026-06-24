"""
Reset Phase 0 Sales Invoices and reload with correct backdating + stock deduction.
Does NOT touch Opening Stock, Items, Suppliers, or Purchase Invoices.
"""
import frappe

COMPANY = 'SMRITI UAT Footwear Co'

def reset_sales():
    frappe.set_user('Administrator')
    print('Cancelling and deleting Phase 0 Sales Invoices...')

    sis = frappe.db.get_all('Sales Invoice', {
        'company': COMPANY,
        'docstatus': ['!=', 2]   # not already cancelled
    }, ['name', 'docstatus'])

    for si in sis:
        try:
            doc = frappe.get_doc('Sales Invoice', si.name)
            if doc.docstatus == 1:
                doc.cancel()
            frappe.delete_doc('Sales Invoice', si.name, ignore_permissions=True)
            print(f'  Deleted: {si.name}')
        except Exception as e:
            print(f'  ERROR {si.name}: {e}')

    frappe.db.commit()
    print(f'Done. Deleted {len(sis)} SIs.')
