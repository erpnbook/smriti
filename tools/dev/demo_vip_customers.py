"""
VIP Customer Supplementary Loader
Creates Aditi, Aarushi, Krish Nishad, Siddharth Mallah as loyal customers
+ loads their visit invoices using remaining stock.
"""
import frappe
from datetime import date, timedelta
import random

COMPANY   = 'SMRITI UAT Footwear Co'
WAREHOUSE = 'Stores - SUFC'
TODAY     = date.today()
random.seed(55)

VIP_CUSTOMERS = ['Aditi', 'Aarushi', 'Krish Nishad', 'Siddharth Mallah']

# Visit patterns per VIP customer
VIP_VISITS = {
    'Aditi':            [(78,72),(60,54),(44,38),(28,22),(12,6),(2,1)],
    'Aarushi':          [(86,80),(70,64),(54,48),(38,32),(18,12),(4,1)],
    'Krish Nishad':     [(81,75),(65,59),(49,43),(33,27),(17,11),(5,2),(1,1)],
    'Siddharth Mallah': [(83,77),(67,61),(51,45),(35,29),(19,13),(7,3),(2,1)],
}

def days_ago(n):
    return (TODAY - timedelta(days=n)).strftime('%Y-%m-%d')

def rand_date(from_d, to_d):
    return days_ago(random.randint(to_d, from_d))

def get_available_items():
    """Get items with enough stock for SI creation."""
    rows = frappe.db.sql("""
        SELECT b.item_code, b.actual_qty, i.standard_rate as rate
        FROM `tabBin` b
        JOIN `tabItem` i ON i.name = b.item_code
        WHERE b.warehouse = %s AND b.actual_qty >= 2
          AND b.item_code LIKE 'DEMO-%%'
        ORDER BY b.actual_qty DESC
        LIMIT 20
    """, WAREHOUSE, as_dict=True)
    return [(r.item_code, r.rate) for r in rows]

def make_si(customer, posting_date, items_list):
    cash = frappe.db.get_value('Account',
        {'company': COMPANY, 'account_type': 'Cash', 'is_group': 0}, 'name')
    recv = frappe.db.get_value('Account',
        {'company': COMPANY, 'account_type': 'Receivable', 'is_group': 0}, 'name')

    si = frappe.new_doc('Sales Invoice')
    si.company      = COMPANY
    si.customer     = customer
    si.posting_date = posting_date
    si.posting_time = '11:00:00'
    si.due_date     = posting_date
    si.debit_to     = recv
    si.is_pos       = 1
    si.update_stock = 1

    total = 0
    for item_code, qty, rate in items_list:
        si.append('items', {'item_code': item_code, 'qty': qty,
                            'rate': rate, 'warehouse': WAREHOUSE})
        total += qty * rate

    if total == 0:
        return None

    si.append('payments', {'mode_of_payment': 'Cash', 'account': cash, 'amount': total})
    si.insert(ignore_permissions=True)
    si.submit()

    if str(si.posting_date) != posting_date:
        frappe.db.set_value('Sales Invoice', si.name, 'posting_date',
                            posting_date, update_modified=False)
        frappe.db.commit()
    return si

def main():
    frappe.set_user('Administrator')
    print('=' * 60)
    print('VIP Customer Loader: Aditi, Aarushi, Krish Nishad, Siddharth Mallah')
    print('=' * 60)

    # Ensure customers exist
    for name in VIP_CUSTOMERS:
        if not frappe.db.exists('Customer', name):
            doc = frappe.new_doc('Customer')
            doc.customer_name  = name
            doc.customer_group = 'Individual'
            doc.customer_type  = 'Individual'
            doc.territory      = 'India'
            doc.insert(ignore_permissions=True)
            print(f'  Created customer: {name}')
        else:
            print(f'  Exists: {name}')
    frappe.db.commit()

    # Load invoices for each VIP
    created = 0
    errors  = 0

    for name in VIP_CUSTOMERS:
        visits = VIP_VISITS[name]
        print(f'\n  {name} ({len(visits)} visits):')
        for from_d, to_d in visits:
            avail = get_available_items()
            if not avail:
                print(f'    WARNING: No stock available for visit')
                continue
            chosen  = random.sample(avail, min(2, len(avail)))
            items   = [(code, 1, rate) for code, rate in chosen]
            pd      = rand_date(from_d, to_d)
            try:
                si = make_si(name, pd, items)
                if si:
                    total = sum(r * q for _, q, r in items)
                    print(f'    {pd}  ₹{total:,.0f}  ✓')
                    created += 1
                    frappe.db.commit()
            except Exception as e:
                print(f'    {pd}  ERROR: {str(e)[:60]}')
                errors += 1

    print()
    print(f'VIP invoices: {created} created, {errors} errors.')
    print()
    print('=' * 60)
    print('VIP Loader COMPLETE.')
    print('=' * 60)
