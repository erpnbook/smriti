import frappe

def audit():
    frappe.set_user('Administrator')
    co = 'SMRITI UAT Footwear Co'

    items = frappe.db.count('Item', {'disabled': 0})
    customers = frappe.db.count('Customer', {'disabled': 0})
    suppliers = frappe.db.count('Supplier', {'disabled': 0})
    si = frappe.db.count('Sales Invoice', {'company': co, 'docstatus': 1})
    pi = frappe.db.count('Purchase Invoice', {'company': co, 'docstatus': 1})
    sle = frappe.db.count('Stock Ledger Entry', {'company': co})
    warehouses = frappe.db.get_all('Warehouse', {'company': co}, ['name'])
    si_range = frappe.db.sql(
        'SELECT MIN(posting_date), MAX(posting_date) FROM `tabSales Invoice` WHERE company=%s AND docstatus=1',
        co
    )
    item_groups = frappe.db.get_all('Item Group', {}, ['name'], limit=30)
    sample_items = frappe.db.sql(
        'SELECT item_code, item_name, item_group, standard_rate FROM `tabItem` WHERE disabled=0 LIMIT 15'
    )

    print('=== OWNER-DEMO-001 Data Audit ===')
    print('Company     :', co)
    print('Items       :', items)
    print('Customers   :', customers)
    print('Suppliers   :', suppliers)
    print('Sales Inv   :', si)
    print('SI date range:', si_range)
    print('Purchase Inv:', pi)
    print('SLE Entries :', sle)
    print('Warehouses  :', [w.name for w in warehouses])
    print('Item Groups :', [g.name for g in item_groups])
    print('Sample Items:')
    for it in sample_items:
        print('  ', it)
