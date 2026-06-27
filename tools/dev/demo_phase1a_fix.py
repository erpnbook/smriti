"""
OWNER-DEMO-001 — Phase 1A Post-Fix
Founder Spec Alignment

Fixes:
1. Creates 6 named loyal customers (Raj Mehta, Priya Sharma, etc.)
2. Creates 12 named lapsed customers (Indian retail names)
3. Loads their invoices with correct dates (loyal = recent, lapsed = > 60 days ago)
4. Adds 3 missing dead stock SKUs per Founder spec:
   - Platform Heel Silver Sz37
   - Ethnic Mojari Multicolor Sz43
   - Ankle Boot Black Sz38

These were in Founder spec but missing from Phase 0/1A.

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""

import frappe
from datetime import date, timedelta
import random

COMPANY   = 'SMRITI UAT Footwear Co'
ABBR      = 'SUFC'
WAREHOUSE = 'Stores - SUFC'
HSN       = '640299'
TODAY     = date.today()
random.seed(77)

def days_ago(n):
    return (TODAY - timedelta(days=n)).strftime('%Y-%m-%d')

def rand_date(from_days, to_days):
    return days_ago(random.randint(to_days, from_days))

def get_cash_account():
    return frappe.db.get_value('Account',
        {'company': COMPANY, 'account_type': 'Cash', 'is_group': 0}, 'name')

def get_receivable_account():
    return frappe.db.get_value('Account',
        {'company': COMPANY, 'account_type': 'Receivable', 'is_group': 0}, 'name')

def make_si(customer, posting_date, items_list, cash_acc, recv_acc):
    """Create and submit a backdated Sales Invoice with update_stock=1."""
    si = frappe.new_doc('Sales Invoice')
    si.company      = COMPANY
    si.customer     = customer
    si.posting_date = posting_date
    si.posting_time = '14:00:00'
    si.due_date     = posting_date
    si.debit_to     = recv_acc
    si.is_pos       = 1
    si.update_stock = 1

    total = 0
    for item_code, qty, rate in items_list:
        si.append('items', {'item_code': item_code, 'qty': qty,
                            'rate': rate, 'warehouse': WAREHOUSE})
        total += qty * rate

    if total == 0:
        return None

    si.append('payments', {'mode_of_payment': 'Cash', 'account': cash_acc, 'amount': total})
    si.insert(ignore_permissions=True)
    si.submit()

    # Force historical date (Frappe v16 POS overrides to today)
    if str(si.posting_date) != posting_date:
        frappe.db.set_value('Sales Invoice', si.name, 'posting_date',
                            posting_date, update_modified=False)
        frappe.db.commit()
    return si

# ─────────────────────────────────────────────────────────────────────────────
# PART 1: Missing Dead Stock SKUs
# ─────────────────────────────────────────────────────────────────────────────
MISSING_SKUS = [
    dict(item_code='DEMO-PH-SLV-37', item_name='Platform Heel Silver Sz37',
         item_group='Women Sandals', rate=2799, opening_qty=6),
    dict(item_code='DEMO-MJ-MLC-43', item_name='Ethnic Mojari Multicolor Sz43',
         item_group='Casual Shoes', rate=1899, opening_qty=5),
    dict(item_code='DEMO-AB-BLK-38', item_name='Ankle Boot Black Sz38',
         item_group='Formal Shoes', rate=3999, opening_qty=5),
]

def create_missing_skus():
    print('\n[A] Missing Dead Stock SKUs (3)...')
    created = 0
    for it in MISSING_SKUS:
        if frappe.db.exists('Item', it['item_code']):
            print(f'  SKIP: {it["item_code"]}')
            continue
        doc = frappe.new_doc('Item')
        doc.item_code     = it['item_code']
        doc.item_name     = it['item_name']
        doc.item_group    = it['item_group']
        doc.stock_uom     = 'Pair'
        doc.is_stock_item = 1
        doc.gst_hsn_code  = HSN
        doc.standard_rate = it['rate']
        doc.description   = it['item_name']
        doc.append('item_defaults', {'company': COMPANY, 'default_warehouse': WAREHOUSE})
        doc.insert(ignore_permissions=True)
        created += 1
        print(f'  Created: {it["item_code"]}')

    frappe.db.commit()

    # Opening stock for new dead stock SKUs
    if created > 0:
        se = frappe.new_doc('Stock Entry')
        se.stock_entry_type = 'Material Receipt'
        se.company          = COMPANY
        se.posting_date     = days_ago(91)
        se.posting_time     = '09:00:00'
        se.remarks          = 'DEMO-MISSING-SKU-OPENING'
        for it in MISSING_SKUS:
            if frappe.db.exists('Item', it['item_code']):
                se.append('items', {
                    'item_code':   it['item_code'],
                    'qty':         it['opening_qty'],
                    'basic_rate':  it['rate'] * 0.55,
                    't_warehouse': WAREHOUSE,
                })
        se.insert(ignore_permissions=True)
        se.submit()
        frappe.db.commit()
        print(f'  Opening stock: {se.name}')

    print(f'  {created} SKUs created.')

# ─────────────────────────────────────────────────────────────────────────────
# PART 2: Named Demo Customers
# ─────────────────────────────────────────────────────────────────────────────

# Founder spec: 6 loyal + 12 lapsed + 10 new + 22 walk-in
LOYAL_CUSTOMERS = [
    'Raj Mehta',
    'Priya Sharma',
    'Amit Patel',
    'Sunita Joshi',
    'Rakesh Verma',
    'Deepa Nair',
    # VIP names — Founder family
    'Aditi',
    'Aarushi',
    'Krish Nishad',
    'Siddharth Mallah',
]

LAPSED_CUSTOMERS = [
    'Kavita Desai',
    'Suresh Iyer',
    'Meena Pillai',
    'Rohit Gupta',
    'Anita Shetty',
    'Vikram Reddy',
    'Pooja Malhotra',
    'Arun Nambiar',
    'Shalini Rao',
    'Kiran Bhatia',
    'Manoj Thakur',
    'Rekha Chaudhary',
]

NEW_CUSTOMERS = [
    'Aditya Bansal',
    'Neha Saxena',
    'Sameer Kapoor',
    'Ritika Pandey',
    'Vivek Nair',
    'Divya Menon',
    'Gaurav Mishra',
    'Swati Jain',
    'Tarun Choudhury',
    'Preeti Varma',
]

def create_named_customers():
    print('\n[B] Named Demo Customers...')
    all_names = LOYAL_CUSTOMERS + LAPSED_CUSTOMERS + NEW_CUSTOMERS
    created = 0
    for name in all_names:
        if frappe.db.exists('Customer', name):
            continue
        doc = frappe.new_doc('Customer')
        doc.customer_name  = name
        doc.customer_group = 'Individual'
        doc.customer_type  = 'Individual'
        doc.territory      = 'India'
        doc.insert(ignore_permissions=True)
        created += 1

    frappe.db.commit()
    print(f'  {created} customers created.')

# ─────────────────────────────────────────────────────────────────────────────
# PART 3: Named Customer Invoice Stories
# ─────────────────────────────────────────────────────────────────────────────

# Fast items with enough remaining stock for named customer SIs
FAST_ITEMS = [
    ('DEMO-RS-GRY-39', 2499), ('DEMO-RS-NAV-40', 2499),
    ('DEMO-SS-BLK-36', 1299), ('DEMO-KD-BLU-29', 799),
    ('DEMO-WS-BRN-37', 1599), ('DEMO-ET-GLD-37', 1399),
]

REG_ITEMS = [
    ('DEMO-ML-BRN-41', 1499), ('DEMO-CL-BLK-41', 1099),
    ('DEMO-WF-BLK-38', 1199), ('DEMO-KD-PNK-28', 899),
    ('DEMO-SP-BLK-40', 1999), ('DEMO-WS-PNK-37', 1699),
]

def si_items(pool, n=2, qty_range=(1, 2)):
    chosen = random.sample(pool, min(n, len(pool)))
    return [(code, random.randint(*qty_range), rate) for code, rate in chosen]

def create_named_customer_invoices():
    print('\n[C] Named Customer Invoice Stories...')
    cash_acc = get_cash_account()
    recv_acc = get_receivable_account()
    created  = 0
    errors   = 0

    # ── Loyal: 6+ invoices in 90 days, recent, high value ───────────────────
    visit_dates = [
        [(82,78),(68,64),(55,50),(40,35),(25,20),(10,6),(3,1)],      # Raj: 7 visits
        [(85,80),(70,65),(54,48),(38,32),(22,16),(8,4)],              # Priya: 6 visits
        [(79,73),(62,56),(46,40),(30,24),(14,8),(4,1)],              # Amit: 6 visits
        [(88,82),(72,66),(58,52),(42,36),(26,20),(12,6),(2,1)],      # Sunita: 7 visits
        [(80,74),(64,58),(48,42),(32,26),(16,10),(5,1)],             # Rakesh: 6 visits
        [(84,78),(68,62),(52,46),(36,30),(20,14),(6,2)],             # Deepa: 6 visits
        [(78,72),(60,54),(44,38),(28,22),(12,6),(2,1)],              # Aditi: 6 visits
        [(86,80),(70,64),(54,48),(38,32),(18,12),(4,1)],             # Aarushi: 6 visits
        [(81,75),(65,59),(49,43),(33,27),(17,11),(5,2),(1,1)],       # Krish: 7 visits
        [(83,77),(67,61),(51,45),(35,29),(19,13),(7,3),(2,1)],       # Siddharth: 7 visits
    ]
    for i, cust in enumerate(LOYAL_CUSTOMERS):
        dates = visit_dates[i] if i < len(visit_dates) else [(85,5),(60,30),(20,5)]
        for from_d, to_d in dates:
            pd = rand_date(from_d, to_d)
            items = si_items(FAST_ITEMS + REG_ITEMS, n=2, qty_range=(1, 3))
            try:
                si = make_si(cust, pd, items, cash_acc, recv_acc)
                if si:
                    created += 1
            except Exception as e:
                errors += 1

    # ── Lapsed: 1-2 invoices, ALL dated 65-85 days ago, none recent ─────────
    for cust in LAPSED_CUSTOMERS:
        # First purchase: 85-75 days ago
        pd1 = rand_date(85, 75)
        items1 = si_items(FAST_ITEMS + REG_ITEMS, n=2, qty_range=(1, 2))
        try:
            si = make_si(cust, pd1, items1, cash_acc, recv_acc)
            if si:
                created += 1
        except Exception as e:
            errors += 1

        # Optional 2nd purchase: 75-65 days ago (still before D60)
        if random.random() < 0.5:
            pd2 = rand_date(74, 65)
            items2 = si_items(REG_ITEMS, n=1, qty_range=(1, 2))
            try:
                si = make_si(cust, pd2, items2, cash_acc, recv_acc)
                if si:
                    created += 1
            except Exception as e:
                errors += 1

    # ── New Customers: first purchase < 30 days ago ──────────────────────────
    for cust in NEW_CUSTOMERS:
        pd = rand_date(28, 3)
        items = si_items(FAST_ITEMS + REG_ITEMS, n=2, qty_range=(1, 2))
        try:
            si = make_si(cust, pd, items, cash_acc, recv_acc)
            if si:
                created += 1
        except Exception as e:
            errors += 1

    frappe.db.commit()
    print(f'  Named customer invoices: {created} created, {errors} errors.')

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def main():
    frappe.set_user('Administrator')
    print('=' * 60)
    print('OWNER-DEMO-001 — Phase 1A Post-Fix (Founder Spec Alignment)')
    print('=' * 60)

    create_missing_skus()
    create_named_customers()
    create_named_customer_invoices()

    print()
    print('=' * 60)
    print('Post-Fix COMPLETE. Run OWNER_DEMO_AUDIT next.')
    print('=' * 60)
