"""
OWNER-DEMO-001 — Phase 0: Story Validation Dataset
12 SKUs | 10 Customers | 2 Suppliers | 20 Sales Invoices | 5 Purchase Invoices

Validates all 7 business stories before expanding to full 72-SKU dataset.
Run via: docker cp + bench execute smriti_retail_os.demo_phase0.main

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""

import frappe
from frappe.utils import flt, nowdate
from datetime import date, timedelta
import random

COMPANY   = 'SMRITI UAT Footwear Co'
ABBR      = 'SUFC'
WAREHOUSE = 'Stores - SUFC'
TODAY     = date.today()

# ── Seed random for reproducible dataset ─────────────────────────────────────
random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# ITEM CATALOG — 12 SKUs
# velocity: fast | regular | dead | lowstock
# ─────────────────────────────────────────────────────────────────────────────
ITEMS = [
    # Fast Movers (3) — high sales, trigger PDT reorder story
    dict(item_code='DEMO-RS-BLK-40', item_name='Running Shoe Black Sz40',
         item_group='Running Shoes', rate=2499, hsn='640299',
         opening_qty=25, velocity='fast'),
    dict(item_code='DEMO-RS-BLK-41', item_name='Running Shoe Black Sz41',
         item_group='Running Shoes', rate=2499, hsn='640299',
         opening_qty=25, velocity='fast'),
    dict(item_code='DEMO-SS-BLK-35', item_name='School Shoe Black Sz35',
         item_group='School Shoes', rate=1299, hsn='640299',
         opening_qty=20, velocity='fast'),

    # Regular Movers (4) — healthy, no alerts
    dict(item_code='DEMO-WS-BGE-37', item_name="Women's Sandal Beige Sz37",
         item_group='Women Sandals', rate=1599, hsn='640299',
         opening_qty=15, velocity='regular'),
    dict(item_code='DEMO-CL-BLK-40', item_name='Casual Slip-On Black Sz40',
         item_group='Casual Shoes', rate=1099, hsn='640299',
         opening_qty=15, velocity='regular'),
    dict(item_code='DEMO-CL-BRN-41', item_name='Casual Slip-On Brown Sz41',
         item_group='Casual Shoes', rate=1099, hsn='640299',
         opening_qty=15, velocity='regular'),
    dict(item_code='DEMO-KD-RED-29', item_name='Kids Shoe Red Sz29',
         item_group='Kids Shoes', rate=799, hsn='640299',
         opening_qty=15, velocity='regular'),

    # Dead Stock (3) — 0 sales, capital locked, triggers working capital story
    dict(item_code='DEMO-FS-BRN-41', item_name='Formal Shoe Brown Sz41',
         item_group='Formal Shoes', rate=3499, hsn='640299',
         opening_qty=10, velocity='dead'),
    dict(item_code='DEMO-FS-BRN-42', item_name='Formal Shoe Brown Sz42',
         item_group='Formal Shoes', rate=3499, hsn='640299',
         opening_qty=10, velocity='dead'),
    dict(item_code='DEMO-PW-GLD-42', item_name='Party Loafer Gold Sz42',
         item_group='Formal Shoes', rate=2999, hsn='640299',
         opening_qty=8, velocity='dead'),

    # Low Stock Critical (2) — triggers inventory alert + PDT story
    dict(item_code='DEMO-SP-WHT-42', item_name='Sports Shoe White Sz42',
         item_group='Sports Shoes', rate=1999, hsn='640299',
         opening_qty=5, velocity='lowstock'),
    dict(item_code='DEMO-WF-BLK-37', item_name="Women's Flat Black Sz37",
         item_group='Women Sandals', rate=1199, hsn='640299',
         opening_qty=4, velocity='lowstock'),
]

# ── 10 Customers (picked from existing 120) ───────────────────────────────────
# Loyal: buy 5+ times | Lapsed: silent 65+ days | Walk-in: recent single visit
DEMO_CUSTOMERS = {
    'loyal':   ['Raj Mehta', 'Priya Sharma'],
    'lapsed':  ['Amit Patel', 'Sunita Joshi', 'Rakesh Verma'],
    'walkin':  ['Deepa Nair', 'Suresh Kumar', 'Kavitha Reddy', 'Mohammed Ali', 'Lata Mishra'],
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def days_ago(n):
    return (TODAY - timedelta(days=n)).strftime('%Y-%m-%d')

def rand_date(from_days, to_days):
    """Random date between from_days ago and to_days ago."""
    n = random.randint(to_days, from_days)
    return days_ago(n)

def get_or_create_item_group(group_name):
    if not frappe.db.exists('Item Group', group_name):
        ig = frappe.new_doc('Item Group')
        ig.item_group_name = group_name
        ig.parent_item_group = 'Products'
        ig.insert(ignore_permissions=True)
        frappe.db.commit()
        print('  Created item group:', group_name)
    return group_name

def ensure_uom(uom):
    if not frappe.db.exists('UOM', uom):
        u = frappe.new_doc('UOM')
        u.uom_name = uom
        u.insert(ignore_permissions=True)
        frappe.db.commit()

def get_cash_account():
    acc = frappe.db.get_value('Account', {
        'company': COMPANY,
        'account_type': 'Cash',
        'is_group': 0
    }, 'name')
    if not acc:
        acc = f'Cash - {ABBR}'
    return acc

def get_receivable_account():
    acc = frappe.db.get_value('Account', {
        'company': COMPANY,
        'account_type': 'Receivable',
        'is_group': 0
    }, 'name')
    if not acc:
        acc = f'Debtors - {ABBR}'
    return acc

def get_payable_account():
    acc = frappe.db.get_value('Account', {
        'company': COMPANY,
        'account_type': 'Payable',
        'is_group': 0
    }, 'name')
    if not acc:
        acc = f'Creditors - {ABBR}'
    return acc

def get_stock_adjustment_account():
    """Account for opening stock adjustments."""
    acc = frappe.db.get_value('Account', {
        'company': COMPANY,
        'root_type': ['in', ['Asset', 'Expense']],
        'is_group': 0
    }, 'name')
    if not acc:
        acc = f'Stock Adjustment - {ABBR}'
    return acc

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 0 BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def create_item_groups():
    print('\n[1/7] Item Groups...')
    ensure_uom('Pair')
    # Ensure "Products" parent exists
    if not frappe.db.exists('Item Group', 'Products'):
        ig = frappe.new_doc('Item Group')
        ig.item_group_name = 'Products'
        ig.parent_item_group = 'All Item Groups'
        ig.insert(ignore_permissions=True)
        frappe.db.commit()
    groups = ['Running Shoes', 'School Shoes', 'Women Sandals', 'Casual Shoes',
              'Kids Shoes', 'Formal Shoes', 'Sports Shoes']
    for g in groups:
        get_or_create_item_group(g)
    print('  Done.')

def create_items():
    print('\n[2/7] Items (12 SKUs)...')
    created = 0
    for it in ITEMS:
        if frappe.db.exists('Item', it['item_code']):
            print('  SKIP (exists):', it['item_code'])
            continue
        doc = frappe.new_doc('Item')
        doc.item_code          = it['item_code']
        doc.item_name          = it['item_name']
        doc.item_group         = it['item_group']
        doc.stock_uom          = 'Pair'
        doc.is_stock_item      = 1
        doc.include_item_in_manufacturing = 0
        doc.gst_hsn_code       = it['hsn']
        doc.standard_rate      = it['rate']
        doc.description        = it['item_name']
        # Append item defaults
        doc.append('item_defaults', {
            'company':        COMPANY,
            'default_warehouse': WAREHOUSE,
        })
        doc.insert(ignore_permissions=True)
        # Create item price (Standard Selling)
        if not frappe.db.exists('Item Price', {'item_code': it['item_code'], 'price_list': 'Standard Selling'}):
            ip = frappe.new_doc('Item Price')
            ip.item_code       = it['item_code']
            ip.price_list      = 'Standard Selling'
            ip.currency        = 'INR'
            ip.price_list_rate = it['rate']
            ip.insert(ignore_permissions=True)
        created += 1
    frappe.db.commit()
    print(f'  Created {created} items.')

def create_suppliers():
    print('\n[3/7] Suppliers (2)...')
    suppliers = [
        dict(name='Mumbai Footwear Traders', group='Local', city='Mumbai'),
        dict(name='Agra Shoe Wholesalers',   group='Local', city='Agra'),
    ]
    for s in suppliers:
        if frappe.db.exists('Supplier', s['name']):
            print('  SKIP:', s['name'])
            continue
        doc = frappe.new_doc('Supplier')
        doc.supplier_name  = s['name']
        doc.supplier_group = 'Local'
        doc.supplier_type  = 'Company'
        doc.country        = 'India'
        doc.insert(ignore_permissions=True)
        print('  Created:', s['name'])
    frappe.db.commit()

def get_demo_customers():
    """Pick 10 demo customers from existing 120."""
    print('\n[4/7] Customers (from existing)...')
    all_customers = frappe.db.get_all('Customer', {'disabled': 0},
                                       ['name'], limit=20)
    names = [c.name for c in all_customers]

    # Map story roles to actual customer names
    # Use first available names, falling back to creating placeholders
    result = {'loyal': [], 'lapsed': [], 'walkin': []}

    # Try to find customers by demo name first
    for role, wanted in DEMO_CUSTOMERS.items():
        for w in wanted:
            if frappe.db.exists('Customer', w):
                result[role].append(w)
            else:
                # Use an existing customer
                if names:
                    result[role].append(names.pop(0))

    print('  Loyal  :', result['loyal'])
    print('  Lapsed :', result['lapsed'])
    print('  Walk-in:', result['walkin'])
    return result

def create_opening_stock():
    """Stock Entry: Material Receipt to seed opening inventory."""
    print('\n[5/7] Opening Stock...')

    # Check if already done
    existing = frappe.db.get_value('Stock Entry', {
        'company': COMPANY,
        'stock_entry_type': 'Material Receipt',
        'docstatus': 1,
        'remarks': 'DEMO-PHASE0-OPENING'
    }, 'name')
    if existing:
        print('  SKIP: Opening stock already exists:', existing)
        return

    se = frappe.new_doc('Stock Entry')
    se.stock_entry_type = 'Material Receipt'
    se.company          = COMPANY
    se.posting_date     = days_ago(92)  # Before all demo transactions
    se.remarks          = 'DEMO-PHASE0-OPENING'

    for it in ITEMS:
        se.append('items', {
            'item_code':   it['item_code'],
            'qty':         it['opening_qty'],
            'basic_rate':  it['rate'] * 0.55,  # Cost = ~55% of MRP
            't_warehouse': WAREHOUSE,
        })

    se.insert(ignore_permissions=True)
    se.submit()
    frappe.db.commit()
    print(f'  Opening stock submitted: {se.name}')

def create_purchase_invoices():
    """5 Purchase Invoices — replenishment pattern showing fast movers bought 2x."""
    print('\n[6/7] Purchase Invoices (5)...')

    suppliers = ['Mumbai Footwear Traders', 'Agra Shoe Wholesalers']
    payable   = get_payable_account()

    # PI 1: Initial stock purchase (90 days ago) — all fast movers
    # PI 2: Replenishment fast movers (50 days ago)
    # PI 3: Replenishment fast movers (20 days ago) — reorder story
    # PI 4: Regular items (70 days ago)
    # PI 5: Mixed (40 days ago)
    purchases = [
        dict(date_ago=90, supplier=suppliers[0],
             items=[('DEMO-RS-BLK-40', 15, 1374), ('DEMO-RS-BLK-41', 15, 1374),
                    ('DEMO-SS-BLK-35', 12, 714)]),
        dict(date_ago=50, supplier=suppliers[0],
             items=[('DEMO-RS-BLK-40', 10, 1374), ('DEMO-RS-BLK-41', 10, 1374)]),
        dict(date_ago=20, supplier=suppliers[0],
             items=[('DEMO-RS-BLK-40', 8, 1374), ('DEMO-SS-BLK-35', 10, 714)]),
        dict(date_ago=70, supplier=suppliers[1],
             items=[('DEMO-WS-BGE-37', 12, 879), ('DEMO-CL-BLK-40', 10, 604),
                    ('DEMO-KD-RED-29', 10, 439)]),
        dict(date_ago=40, supplier=suppliers[1],
             items=[('DEMO-CL-BRN-41', 10, 604), ('DEMO-WF-BLK-37', 8, 659)]),
    ]

    created = 0
    for p in purchases:
        # Check for duplicate
        dup = frappe.db.get_value('Purchase Invoice', {
            'company': COMPANY,
            'supplier': p['supplier'],
            'posting_date': days_ago(p['date_ago']),
            'docstatus': 1
        }, 'name')
        if dup:
            print('  SKIP:', dup)
            continue

        pi = frappe.new_doc('Purchase Invoice')
        pi.company        = COMPANY
        pi.supplier       = p['supplier']
        pi.posting_date   = days_ago(p['date_ago'])
        pi.credit_to      = payable
        pi.bill_no        = f'DEMO-BILL-{p["date_ago"]}'
        pi.bill_date      = days_ago(p['date_ago'])
        pi.update_stock   = 0  # Opening stock already done via Stock Entry

        for item_code, qty, rate in p['items']:
            pi.append('items', {
                'item_code':   item_code,
                'qty':         qty,
                'rate':        rate,
                'warehouse':   WAREHOUSE,
            })

        pi.insert(ignore_permissions=True)
        pi.submit()
        created += 1
        print(f'  Created PI: {pi.name}  ({p["supplier"]}, {days_ago(p["date_ago"])})')

    frappe.db.commit()
    print(f'  {created} purchase invoices created.')

def create_sales_invoices(customers):
    """
    20 Sales Invoices — business stories embedded in date + customer pattern.

    Story map:
    - Loyal   : Customer A = 7 invoices spread across 90 days
                Customer B = 5 invoices spread across 90 days
    - Lapsed  : Customers C/D/E = 1 invoice each, 65-80 days ago
    - Walk-in : 5 customers, 1 invoice each, last 30 days
    - Dead stock : NEVER appears in any invoice
    """
    print('\n[7/7] Sales Invoices (20)...')

    cash_acc = get_cash_account()
    recv_acc = get_receivable_account()

    fast   = ['DEMO-RS-BLK-40', 'DEMO-RS-BLK-41', 'DEMO-SS-BLK-35']
    reg    = ['DEMO-WS-BGE-37', 'DEMO-CL-BLK-40', 'DEMO-CL-BRN-41', 'DEMO-KD-RED-29']
    low    = ['DEMO-SP-WHT-42', 'DEMO-WF-BLK-37']
    # dead = ['DEMO-FS-BRN-41', 'DEMO-FS-BRN-42', 'DEMO-PW-GLD-42']  # NEVER sold

    loyal_a  = customers['loyal'][0]  if customers['loyal']  else None
    loyal_b  = customers['loyal'][1]  if len(customers['loyal'])>1 else loyal_a
    lapsed_c = customers['lapsed'][0] if customers['lapsed'] else None
    lapsed_d = customers['lapsed'][1] if len(customers['lapsed'])>1 else lapsed_c
    lapsed_e = customers['lapsed'][2] if len(customers['lapsed'])>2 else lapsed_c
    walkins  = customers['walkin']

    # Invoice spec: (customer, days_ago_from, days_ago_to, items_pool, qty_range)
    invoice_specs = [
        # Loyal A — 7 invoices spread across 90 days (recent + historical)
        (loyal_a, 88, 82, fast + reg, (1, 2)),
        (loyal_a, 72, 68, fast,       (2, 3)),
        (loyal_a, 55, 50, fast + reg, (1, 2)),
        (loyal_a, 40, 35, fast,       (2, 2)),
        (loyal_a, 25, 20, fast + reg, (1, 2)),
        (loyal_a, 12,  8, fast,       (2, 3)),
        (loyal_a,  3,  1, fast + reg, (1, 2)),

        # Loyal B — 5 invoices
        (loyal_b, 80, 75, fast + reg, (1, 2)),
        (loyal_b, 60, 55, fast,       (2, 2)),
        (loyal_b, 38, 32, reg,        (1, 2)),
        (loyal_b, 18, 14, fast,       (1, 2)),
        (loyal_b,  5,  2, fast + reg, (1, 2)),

        # Lapsed C/D/E — 1 invoice each, all old (65-80 days ago)
        (lapsed_c, 80, 72, fast + reg, (1, 2)),
        (lapsed_d, 73, 65, reg,        (1, 2)),
        (lapsed_e, 78, 70, fast,       (1, 2)),

        # Walk-in customers — recent single purchases (last 30 days)
        (walkins[0] if walkins else loyal_a, 28, 22, fast,       (1, 2)),
        (walkins[1] if len(walkins)>1 else loyal_a, 20, 15, reg, (1, 2)),
        (walkins[2] if len(walkins)>2 else loyal_a, 15, 10, fast + low, (1, 2)),
        (walkins[3] if len(walkins)>3 else loyal_a,  8,  5, reg, (1, 2)),
        (walkins[4] if len(walkins)>4 else loyal_a,  3,  1, fast, (1, 2)),
    ]

    created = 0
    for idx, spec in enumerate(invoice_specs, 1):
        customer, from_days, to_days, pool, qty_range = spec

        if not customer:
            print(f'  SKIP invoice {idx}: no customer available')
            continue

        posting_date = rand_date(from_days, to_days)

        # Pick 1-2 items from pool
        n_items = random.randint(1, min(2, len(pool)))
        chosen  = random.sample(pool, n_items)

        si = frappe.new_doc('Sales Invoice')
        si.company          = COMPANY
        si.customer         = customer
        si.posting_date     = posting_date
        si.posting_time     = '12:00:00'
        si.due_date         = posting_date
        si.debit_to         = recv_acc
        si.is_pos           = 1
        si.update_stock     = 1   # Deduct stock at invoice (no Delivery Note)

        total = 0
        for item_code in chosen:
            it_data = next((i for i in ITEMS if i['item_code'] == item_code), None)
            if not it_data:
                continue
            qty  = random.randint(*qty_range)
            rate = it_data['rate']
            si.append('items', {
                'item_code': item_code,
                'qty':       qty,
                'rate':      rate,
                'warehouse': WAREHOUSE,
            })
            total += qty * rate

        if total == 0:
            print(f'  SKIP invoice {idx}: no items added')
            continue

        si.append('payments', {
            'mode_of_payment': 'Cash',
            'account':         cash_acc,
            'amount':          total,
        })

        try:
            si.flags.ignore_validate_update_after_submit = True
            si.insert(ignore_permissions=True)
            si.submit()
            # Frappe v16 overrides posting_date to today on submit for POS.
            # Force the correct historical date via direct DB update.
            if si.posting_date != posting_date:
                frappe.db.set_value('Sales Invoice', si.name,
                                    'posting_date', posting_date, update_modified=False)
                frappe.db.commit()
            created += 1
            print(f'  SI-{idx:02d}: {customer[:20]:<20} {posting_date}  Rs{total:,.0f}')
        except Exception as e:
            print(f'  ERROR SI-{idx:02d} ({customer}): {e}')

    frappe.db.commit()
    print(f'\n  {created}/20 sales invoices created.')

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def main():
    frappe.set_user('Administrator')
    print('=' * 60)
    print('OWNER-DEMO-001 — Phase 0: Story Validation Dataset')
    print('Company:', COMPANY)
    print('=' * 60)

    create_item_groups()
    create_items()
    create_suppliers()
    customers = get_demo_customers()
    create_opening_stock()
    create_purchase_invoices()
    create_sales_invoices(customers)

    print('\n' + '=' * 60)
    print('Phase 0 COMPLETE. Run verify_stories.py next.')
    print('=' * 60)
