import frappe
from datetime import date, timedelta

COMPANY   = 'SMRITI UAT Footwear Co'
WAREHOUSE = 'Stores - SUFC'
TODAY     = date.today()
D60 = (TODAY - timedelta(days=60)).strftime('%Y-%m-%d')

def diag():
    frappe.set_user('Administrator')
    print('=== DIAGNOSTICS ===')
    print(f'TODAY = {TODAY}')
    print(f'D60   = {D60}')
    print()

    # All SIs with dates and customers
    rows = frappe.db.sql("""
        SELECT customer, posting_date, grand_total
        FROM `tabSales Invoice`
        WHERE company = %s AND docstatus = 1
        ORDER BY posting_date
    """, COMPANY, as_dict=True)

    print(f'All SIs ({len(rows)} total):')
    for r in rows:
        flag = ' < D60' if str(r.posting_date) < D60 else ' >= D60'
        print(f'  {str(r.posting_date)}  {r.customer[:30]:<30} {flag}')

    print()

    # MAX(posting_date) per customer
    max_rows = frappe.db.sql("""
        SELECT customer, MAX(posting_date) as last_purchase
        FROM `tabSales Invoice`
        WHERE company = %s AND docstatus = 1
        GROUP BY customer
    """, COMPANY, as_dict=True)

    print('Max posting date per customer:')
    for r in max_rows:
        lapsed = ' <- LAPSED' if str(r.last_purchase) < D60 else ''
        print(f'  {r.customer[:35]:<35} last={r.last_purchase}{lapsed}')

    print()

    # Bin quantities for DEMO items
    bin_rows = frappe.db.sql("""
        SELECT item_code, actual_qty
        FROM `tabBin`
        WHERE warehouse = %s AND item_code LIKE 'DEMO-%%'
        ORDER BY actual_qty
    """, WAREHOUSE, as_dict=True)

    print('Bin quantities (DEMO items):')
    for r in bin_rows:
        flag = ' <- REORDER' if r.actual_qty < 15 else ''
        print(f'  {r.item_code:<25} qty={r.actual_qty}{flag}')
