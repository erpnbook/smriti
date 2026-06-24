"""
OWNER-DEMO-001 — Phase 1A: Full Dataset Expansion
72 total SKUs | 50 Customers | 6 Suppliers | 250 Sales Invoices | 40 Purchase Invoices

Builds on Phase 0 (12 SKUs, 20 SIs already exist — all skipped).
Adds 60 new SKUs, 4 suppliers, opening stock, 35 PIs, 230 SIs.

Technical lessons from Phase 0 (hardcoded):
  - HSN = 640299 (6-digit, india_compliance validated)
  - update_stock=1 on all Sales Invoices
  - Post-submit frappe.db.set_value for backdated posting_date

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
random.seed(99)   # Different seed from Phase 0

# ─────────────────────────────────────────────────────────────────────────────
# 60 NEW SKUs (Phase 0 already has 12 — total = 72)
# velocity: fast | regular | dead | lowstock
# ─────────────────────────────────────────────────────────────────────────────
NEW_ITEMS = [

    # ── Running Shoes — additional variants (5) ───────────────────────────────
    dict(item_code='DEMO-RS-NAV-40', item_name='Running Shoe Navy Sz40',
         item_group='Running Shoes', rate=2499, opening_qty=20, velocity='fast'),
    dict(item_code='DEMO-RS-NAV-41', item_name='Running Shoe Navy Sz41',
         item_group='Running Shoes', rate=2499, opening_qty=20, velocity='fast'),
    dict(item_code='DEMO-RS-GRY-39', item_name='Running Shoe Grey Sz39',
         item_group='Running Shoes', rate=2499, opening_qty=18, velocity='fast'),
    dict(item_code='DEMO-RS-GRY-40', item_name='Running Shoe Grey Sz40',
         item_group='Running Shoes', rate=2499, opening_qty=18, velocity='fast'),
    dict(item_code='DEMO-RS-GRY-41', item_name='Running Shoe Grey Sz41',
         item_group='Running Shoes', rate=2499, opening_qty=18, velocity='fast'),

    # ── School Shoes — additional sizes (5) ──────────────────────────────────
    dict(item_code='DEMO-SS-BLK-34', item_name='School Shoe Black Sz34',
         item_group='School Shoes', rate=1299, opening_qty=15, velocity='regular'),
    dict(item_code='DEMO-SS-BLK-36', item_name='School Shoe Black Sz36',
         item_group='School Shoes', rate=1299, opening_qty=18, velocity='fast'),
    dict(item_code='DEMO-SS-BLK-37', item_name='School Shoe Black Sz37',
         item_group='School Shoes', rate=1299, opening_qty=15, velocity='regular'),
    dict(item_code='DEMO-SS-BRN-35', item_name='School Shoe Brown Sz35',
         item_group='School Shoes', rate=1299, opening_qty=10, velocity='regular'),
    dict(item_code='DEMO-SS-BRN-36', item_name='School Shoe Brown Sz36',
         item_group='School Shoes', rate=1299, opening_qty=10, velocity='regular'),

    # ── Women's Sandals — additional variants (8) ─────────────────────────────
    dict(item_code='DEMO-WS-BRN-36', item_name="Women's Sandal Brown Sz36",
         item_group='Women Sandals', rate=1599, opening_qty=12, velocity='regular'),
    dict(item_code='DEMO-WS-BRN-37', item_name="Women's Sandal Brown Sz37",
         item_group='Women Sandals', rate=1599, opening_qty=12, velocity='regular'),
    dict(item_code='DEMO-WS-BRN-38', item_name="Women's Sandal Brown Sz38",
         item_group='Women Sandals', rate=1599, opening_qty=10, velocity='regular'),
    dict(item_code='DEMO-WS-PNK-37', item_name="Women's Sandal Pink Sz37",
         item_group='Women Sandals', rate=1699, opening_qty=8,  velocity='regular'),
    dict(item_code='DEMO-WS-PNK-38', item_name="Women's Sandal Pink Sz38",
         item_group='Women Sandals', rate=1699, opening_qty=8,  velocity='regular'),
    dict(item_code='DEMO-WH-NDE-36', item_name="Women's Heel Nude Sz36",
         item_group='Women Sandals', rate=1799, opening_qty=8,  velocity='regular'),
    dict(item_code='DEMO-WH-NDE-37', item_name="Women's Heel Nude Sz37",
         item_group='Women Sandals', rate=1799, opening_qty=8,  velocity='regular'),
    dict(item_code='DEMO-WH-NDE-38', item_name="Women's Heel Nude Sz38",
         item_group='Women Sandals', rate=1799, opening_qty=6,  velocity='lowstock'),

    # ── Men's Casual / Loafers (8) ────────────────────────────────────────────
    dict(item_code='DEMO-CL-BLK-41', item_name='Casual Slip-On Black Sz41',
         item_group='Casual Shoes', rate=1099, opening_qty=12, velocity='regular'),
    dict(item_code='DEMO-CL-BLK-42', item_name='Casual Slip-On Black Sz42',
         item_group='Casual Shoes', rate=1099, opening_qty=10, velocity='regular'),
    dict(item_code='DEMO-CL-BRN-40', item_name='Casual Slip-On Brown Sz40',
         item_group='Casual Shoes', rate=1099, opening_qty=12, velocity='regular'),
    dict(item_code='DEMO-CL-BRN-42', item_name='Casual Slip-On Brown Sz42',
         item_group='Casual Shoes', rate=1099, opening_qty=8,  velocity='regular'),
    dict(item_code='DEMO-ML-BLK-40', item_name="Men's Loafer Black Sz40",
         item_group='Casual Shoes', rate=1499, opening_qty=10, velocity='regular'),
    dict(item_code='DEMO-ML-BLK-41', item_name="Men's Loafer Black Sz41",
         item_group='Casual Shoes', rate=1499, opening_qty=10, velocity='regular'),
    dict(item_code='DEMO-ML-BLK-42', item_name="Men's Loafer Black Sz42",
         item_group='Casual Shoes', rate=1499, opening_qty=8,  velocity='regular'),
    dict(item_code='DEMO-ML-BRN-41', item_name="Men's Loafer Brown Sz41",
         item_group='Casual Shoes', rate=1499, opening_qty=8,  velocity='regular'),

    # ── Kids Shoes — additional variants (7) ─────────────────────────────────
    dict(item_code='DEMO-KD-BLU-28', item_name='Kids Shoe Blue Sz28',
         item_group='Kids Shoes', rate=799, opening_qty=12, velocity='regular'),
    dict(item_code='DEMO-KD-BLU-29', item_name='Kids Shoe Blue Sz29',
         item_group='Kids Shoes', rate=799, opening_qty=12, velocity='regular'),
    dict(item_code='DEMO-KD-BLU-30', item_name='Kids Shoe Blue Sz30',
         item_group='Kids Shoes', rate=799, opening_qty=10, velocity='regular'),
    dict(item_code='DEMO-KD-RED-28', item_name='Kids Shoe Red Sz28',
         item_group='Kids Shoes', rate=799, opening_qty=10, velocity='regular'),
    dict(item_code='DEMO-KD-RED-30', item_name='Kids Shoe Red Sz30',
         item_group='Kids Shoes', rate=799, opening_qty=10, velocity='regular'),
    dict(item_code='DEMO-KD-PNK-28', item_name='Kids Shoe Pink Sz28',
         item_group='Kids Shoes', rate=899, opening_qty=8,  velocity='regular'),
    dict(item_code='DEMO-KD-PNK-29', item_name='Kids Shoe Pink Sz29',
         item_group='Kids Shoes', rate=899, opening_qty=8,  velocity='regular'),

    # ── Sports Shoes — additional variants (5) ────────────────────────────────
    dict(item_code='DEMO-SP-BLK-40', item_name='Sports Shoe Black Sz40',
         item_group='Sports Shoes', rate=1999, opening_qty=15, velocity='regular'),
    dict(item_code='DEMO-SP-BLK-41', item_name='Sports Shoe Black Sz41',
         item_group='Sports Shoes', rate=1999, opening_qty=15, velocity='regular'),
    dict(item_code='DEMO-SP-BLK-42', item_name='Sports Shoe Black Sz42',
         item_group='Sports Shoes', rate=1999, opening_qty=12, velocity='regular'),
    dict(item_code='DEMO-SP-WHT-40', item_name='Sports Shoe White Sz40',
         item_group='Sports Shoes', rate=1999, opening_qty=5,  velocity='lowstock'),
    dict(item_code='DEMO-SP-WHT-41', item_name='Sports Shoe White Sz41',
         item_group='Sports Shoes', rate=1999, opening_qty=4,  velocity='lowstock'),

    # ── Formal Shoes — dead stock story (6) ──────────────────────────────────
    dict(item_code='DEMO-FS-BLK-40', item_name='Formal Shoe Black Sz40',
         item_group='Formal Shoes', rate=3499, opening_qty=8,  velocity='dead'),
    dict(item_code='DEMO-FS-BLK-41', item_name='Formal Shoe Black Sz41',
         item_group='Formal Shoes', rate=3499, opening_qty=8,  velocity='dead'),
    dict(item_code='DEMO-FS-BLK-42', item_name='Formal Shoe Black Sz42',
         item_group='Formal Shoes', rate=3499, opening_qty=6,  velocity='dead'),
    dict(item_code='DEMO-FS-BLK-43', item_name='Formal Shoe Black Sz43',
         item_group='Formal Shoes', rate=3499, opening_qty=5,  velocity='dead'),
    dict(item_code='DEMO-FS-MRN-40', item_name='Formal Shoe Maroon Sz40',
         item_group='Formal Shoes', rate=3199, opening_qty=6,  velocity='dead'),
    dict(item_code='DEMO-FS-MRN-41', item_name='Formal Shoe Maroon Sz41',
         item_group='Formal Shoes', rate=3199, opening_qty=5,  velocity='dead'),

    # ── Ethnic / Traditional (6) ──────────────────────────────────────────────
    dict(item_code='DEMO-ET-GLD-36', item_name='Ethnic Sandal Gold Sz36',
         item_group='Women Sandals', rate=1399, opening_qty=8,  velocity='regular'),
    dict(item_code='DEMO-ET-GLD-37', item_name='Ethnic Sandal Gold Sz37',
         item_group='Women Sandals', rate=1399, opening_qty=8,  velocity='regular'),
    dict(item_code='DEMO-ET-GLD-38', item_name='Ethnic Sandal Gold Sz38',
         item_group='Women Sandals', rate=1399, opening_qty=6,  velocity='regular'),
    dict(item_code='DEMO-KP-TAN-39', item_name='Kolhapuri Chappal Tan Sz39',
         item_group='Casual Shoes', rate=899, opening_qty=10,  velocity='regular'),
    dict(item_code='DEMO-KP-TAN-40', item_name='Kolhapuri Chappal Tan Sz40',
         item_group='Casual Shoes', rate=899, opening_qty=10,  velocity='regular'),
    dict(item_code='DEMO-KP-TAN-41', item_name='Kolhapuri Chappal Tan Sz41',
         item_group='Casual Shoes', rate=899, opening_qty=6,   velocity='regular'),

    # ── Hawai Chappals / Slippers (8) — budget segment ───────────────────────
    dict(item_code='DEMO-HW-BLU-39', item_name='Hawai Chappal Blue Sz39',
         item_group='Casual Shoes', rate=199, opening_qty=25, velocity='fast'),
    dict(item_code='DEMO-HW-BLU-40', item_name='Hawai Chappal Blue Sz40',
         item_group='Casual Shoes', rate=199, opening_qty=25, velocity='fast'),
    dict(item_code='DEMO-HW-BLU-41', item_name='Hawai Chappal Blue Sz41',
         item_group='Casual Shoes', rate=199, opening_qty=20, velocity='fast'),
    dict(item_code='DEMO-HW-RED-40', item_name='Hawai Chappal Red Sz40',
         item_group='Casual Shoes', rate=199, opening_qty=20, velocity='fast'),
    dict(item_code='DEMO-HW-RED-41', item_name='Hawai Chappal Red Sz41',
         item_group='Casual Shoes', rate=199, opening_qty=18, velocity='fast'),
    dict(item_code='DEMO-SL-BLU-38', item_name='Bath Slipper Blue Sz38',
         item_group='Casual Shoes', rate=149, opening_qty=20, velocity='regular'),
    dict(item_code='DEMO-SL-BLU-39', item_name='Bath Slipper Blue Sz39',
         item_group='Casual Shoes', rate=149, opening_qty=20, velocity='regular'),
    dict(item_code='DEMO-SL-BLU-40', item_name='Bath Slipper Blue Sz40',
         item_group='Casual Shoes', rate=149, opening_qty=18, velocity='regular'),

    # ── Work / Safety Boots (2) — dead stock ─────────────────────────────────
    dict(item_code='DEMO-WB-BRN-43', item_name='Work Boot Brown Sz43',
         item_group='Formal Shoes', rate=4499, opening_qty=5,  velocity='dead'),
    dict(item_code='DEMO-WB-BRN-44', item_name='Work Boot Brown Sz44',
         item_group='Formal Shoes', rate=4499, opening_qty=5,  velocity='dead'),

    # ── Women's Flats — additional sizes (4) ─────────────────────────────────
    dict(item_code='DEMO-WF-BLK-36', item_name="Women's Flat Black Sz36",
         item_group='Women Sandals', rate=1199, opening_qty=10, velocity='regular'),
    dict(item_code='DEMO-WF-BLK-38', item_name="Women's Flat Black Sz38",
         item_group='Women Sandals', rate=1199, opening_qty=10, velocity='regular'),
    dict(item_code='DEMO-WF-BLK-39', item_name="Women's Flat Black Sz39",
         item_group='Women Sandals', rate=1199, opening_qty=8,  velocity='regular'),
    dict(item_code='DEMO-WF-PNK-37', item_name="Women's Flat Pink Sz37",
         item_group='Women Sandals', rate=1299, opening_qty=6,  velocity='lowstock'),
]

# ── 4 New Suppliers (Phase 0 already has 2) ────────────────────────────────
NEW_SUPPLIERS = [
    'Kolhapur Footwear House',
    'Kanpur Leather Works',
    'Chennai Shoe Exports',
    'Delhi Footwear Distributors',
]

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS (same as Phase 0)
# ─────────────────────────────────────────────────────────────────────────────
def days_ago(n):
    return (TODAY - timedelta(days=n)).strftime('%Y-%m-%d')

def rand_date(from_days, to_days):
    n = random.randint(to_days, from_days)
    return days_ago(n)

def get_cash_account():
    acc = frappe.db.get_value('Account', {'company': COMPANY, 'account_type': 'Cash', 'is_group': 0}, 'name')
    return acc or f'Cash - {ABBR}'

def get_receivable_account():
    acc = frappe.db.get_value('Account', {'company': COMPANY, 'account_type': 'Receivable', 'is_group': 0}, 'name')
    return acc or f'Debtors - {ABBR}'

def get_payable_account():
    acc = frappe.db.get_value('Account', {'company': COMPANY, 'account_type': 'Payable', 'is_group': 0}, 'name')
    return acc or f'Creditors - {ABBR}'

def make_si(customer, posting_date, items_with_qty, cash_acc, recv_acc):
    """Create and submit a Sales Invoice, force historical posting_date."""
    si = frappe.new_doc('Sales Invoice')
    si.company       = COMPANY
    si.customer      = customer
    si.posting_date  = posting_date
    si.posting_time  = '12:00:00'
    si.due_date      = posting_date
    si.debit_to      = recv_acc
    si.is_pos        = 1
    si.update_stock  = 1   # Deduct stock at invoice

    total = 0
    for item_code, qty, rate in items_with_qty:
        si.append('items', {'item_code': item_code, 'qty': qty,
                            'rate': rate, 'warehouse': WAREHOUSE})
        total += qty * rate

    if total == 0:
        return None

    si.append('payments', {'mode_of_payment': 'Cash', 'account': cash_acc, 'amount': total})
    si.insert(ignore_permissions=True)
    si.submit()

    # Force historical date (Frappe v16 POS overrides posting_date to today)
    if str(si.posting_date) != posting_date:
        frappe.db.set_value('Sales Invoice', si.name, 'posting_date', posting_date,
                            update_modified=False)
        frappe.db.commit()
    return si

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1A BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def create_new_items():
    print('\n[1/5] New Items (60 SKUs)...')
    created = 0
    for it in NEW_ITEMS:
        if frappe.db.exists('Item', it['item_code']):
            continue
        doc = frappe.new_doc('Item')
        doc.item_code     = it['item_code']
        doc.item_name     = it['item_name']
        doc.item_group    = it['item_group']
        doc.stock_uom     = 'Pair'
        doc.is_stock_item = 1
        doc.include_item_in_manufacturing = 0
        doc.gst_hsn_code  = HSN
        doc.standard_rate = it['rate']
        doc.description   = it['item_name']
        doc.append('item_defaults', {'company': COMPANY, 'default_warehouse': WAREHOUSE})
        doc.insert(ignore_permissions=True)

        if not frappe.db.exists('Item Price', {'item_code': it['item_code'], 'price_list': 'Standard Selling'}):
            ip = frappe.new_doc('Item Price')
            ip.item_code = it['item_code']
            ip.price_list = 'Standard Selling'
            ip.currency = 'INR'
            ip.price_list_rate = it['rate']
            ip.insert(ignore_permissions=True)

        created += 1

    frappe.db.commit()
    print(f'  Created {created} new items ({len(NEW_ITEMS) - created} skipped).')

def create_new_suppliers():
    print('\n[2/5] New Suppliers (4)...')
    created = 0
    for name in NEW_SUPPLIERS:
        if frappe.db.exists('Supplier', name):
            print(f'  SKIP: {name}')
            continue
        doc = frappe.new_doc('Supplier')
        doc.supplier_name  = name
        doc.supplier_group = 'Local'
        doc.supplier_type  = 'Company'
        doc.country        = 'India'
        doc.insert(ignore_permissions=True)
        print(f'  Created: {name}')
        created += 1
    frappe.db.commit()
    print(f'  {created} suppliers created.')

def create_opening_stock_1a():
    print('\n[3/5] Opening Stock for new 60 SKUs...')
    existing = frappe.db.get_value('Stock Entry', {
        'company': COMPANY,
        'stock_entry_type': 'Material Receipt',
        'docstatus': 1,
        'remarks': 'DEMO-PHASE1A-OPENING'
    }, 'name')
    if existing:
        print(f'  SKIP: {existing}')
        return

    se = frappe.new_doc('Stock Entry')
    se.stock_entry_type = 'Material Receipt'
    se.company          = COMPANY
    se.posting_date     = days_ago(92)
    se.posting_time     = '10:00:00'
    se.remarks          = 'DEMO-PHASE1A-OPENING'

    for it in NEW_ITEMS:
        se.append('items', {
            'item_code':   it['item_code'],
            'qty':         it['opening_qty'],
            'basic_rate':  it['rate'] * 0.55,
            't_warehouse': WAREHOUSE,
        })

    se.insert(ignore_permissions=True)
    se.submit()
    frappe.db.commit()
    print(f'  Opening stock submitted: {se.name}')

def create_purchase_invoices_1a():
    """35 additional Purchase Invoices using all 6 suppliers, covering new items."""
    print('\n[4/5] Purchase Invoices (35)...')

    all_suppliers = [
        'Mumbai Footwear Traders', 'Agra Shoe Wholesalers',
        'Kolhapur Footwear House', 'Kanpur Leather Works',
        'Chennai Shoe Exports',    'Delhi Footwear Distributors',
    ]
    payable = get_payable_account()

    # Replenishment patterns showing: fast movers bought 3x, regular 1-2x, dead never again
    pi_specs = [
        # ── Mumbai Footwear Traders: Running shoes specialist ──────────────────
        dict(d=88, sup=all_suppliers[0],
             items=[('DEMO-RS-NAV-40',15,1374),('DEMO-RS-NAV-41',15,1374),
                    ('DEMO-RS-GRY-39',12,1374),('DEMO-RS-GRY-40',12,1374)]),
        dict(d=55, sup=all_suppliers[0],
             items=[('DEMO-RS-NAV-40',10,1374),('DEMO-RS-GRY-40',10,1374),
                    ('DEMO-RS-GRY-41',10,1374)]),
        dict(d=22, sup=all_suppliers[0],
             items=[('DEMO-RS-NAV-40',8,1374),('DEMO-RS-NAV-41',8,1374),
                    ('DEMO-RS-GRY-39',8,1374)]),

        # ── Agra Shoe Wholesalers: School + formal specialist ──────────────────
        dict(d=85, sup=all_suppliers[1],
             items=[('DEMO-SS-BLK-34',10,714),('DEMO-SS-BLK-36',12,714),
                    ('DEMO-SS-BLK-37',10,714),('DEMO-SS-BRN-35',8,714)]),
        dict(d=50, sup=all_suppliers[1],
             items=[('DEMO-SS-BLK-36',10,714),('DEMO-SS-BRN-36',8,714)]),
        # Formal shoes: only 1 purchase (dead stock story — never reordered)
        dict(d=89, sup=all_suppliers[1],
             items=[('DEMO-FS-BLK-40',8,1924),('DEMO-FS-BLK-41',8,1924),
                    ('DEMO-FS-BLK-42',6,1924),('DEMO-WB-BRN-43',5,2474)]),

        # ── Kolhapur Footwear House: Ethnic + chappal specialist ───────────────
        dict(d=87, sup=all_suppliers[2],
             items=[('DEMO-KP-TAN-39',10,494),('DEMO-KP-TAN-40',10,494),
                    ('DEMO-ET-GLD-36',8,769),('DEMO-ET-GLD-37',8,769)]),
        dict(d=52, sup=all_suppliers[2],
             items=[('DEMO-KP-TAN-40',8,494),('DEMO-KP-TAN-41',6,494),
                    ('DEMO-HW-BLU-39',15,109),('DEMO-HW-BLU-40',15,109)]),
        dict(d=18, sup=all_suppliers[2],
             items=[('DEMO-HW-BLU-40',12,109),('DEMO-HW-RED-40',12,109),
                    ('DEMO-HW-BLU-41',10,109)]),

        # ── Kanpur Leather Works: Men's leather specialist ────────────────────
        dict(d=83, sup=all_suppliers[3],
             items=[('DEMO-ML-BLK-40',10,824),('DEMO-ML-BLK-41',10,824),
                    ('DEMO-ML-BLK-42',8,824),('DEMO-ML-BRN-41',8,824)]),
        dict(d=45, sup=all_suppliers[3],
             items=[('DEMO-ML-BLK-41',8,824),('DEMO-CL-BLK-41',10,604),
                    ('DEMO-CL-BLK-42',8,604)]),
        dict(d=15, sup=all_suppliers[3],
             items=[('DEMO-ML-BLK-40',6,824),('DEMO-ML-BLK-42',6,824),
                    ('DEMO-CL-BRN-40',8,604)]),

        # ── Chennai Shoe Exports: Women's + kids specialist ───────────────────
        dict(d=86, sup=all_suppliers[4],
             items=[('DEMO-WS-BRN-36',10,879),('DEMO-WS-BRN-37',10,879),
                    ('DEMO-WH-NDE-36',8,989),('DEMO-WH-NDE-37',8,989)]),
        dict(d=53, sup=all_suppliers[4],
             items=[('DEMO-WS-PNK-37',8,934),('DEMO-WS-PNK-38',8,934),
                    ('DEMO-WF-BLK-36',8,659),('DEMO-WF-BLK-38',8,659)]),
        dict(d=20, sup=all_suppliers[4],
             items=[('DEMO-WS-BRN-37',8,879),('DEMO-WS-BRN-38',6,879),
                    ('DEMO-ET-GLD-37',6,769)]),

        # ── Delhi Footwear Distributors: Multi-category ───────────────────────
        dict(d=84, sup=all_suppliers[5],
             items=[('DEMO-KD-BLU-28',10,439),('DEMO-KD-BLU-29',10,439),
                    ('DEMO-KD-BLU-30',8,439),('DEMO-KD-PNK-28',8,494)]),
        dict(d=60, sup=all_suppliers[5],
             items=[('DEMO-KD-RED-28',8,439),('DEMO-KD-RED-30',8,439),
                    ('DEMO-SP-BLK-40',10,1099),('DEMO-SP-BLK-41',10,1099)]),
        dict(d=28, sup=all_suppliers[5],
             items=[('DEMO-SP-BLK-40',8,1099),('DEMO-SP-BLK-42',8,1099),
                    ('DEMO-SL-BLU-38',12,82),('DEMO-SL-BLU-39',12,82)]),

        # ── Additional top-up PIs (fast movers — 3rd replenishment cycle) ─────
        dict(d=12, sup=all_suppliers[0],
             items=[('DEMO-RS-GRY-40',10,1374),('DEMO-RS-GRY-41',10,1374)]),
        dict(d=10, sup=all_suppliers[2],
             items=[('DEMO-HW-BLU-39',15,109),('DEMO-HW-RED-41',10,109)]),
        dict(d=8,  sup=all_suppliers[4],
             items=[('DEMO-WS-BRN-36',6,879),('DEMO-WH-NDE-37',5,989)]),
        dict(d=6,  sup=all_suppliers[5],
             items=[('DEMO-KD-BLU-28',8,439),('DEMO-KD-PNK-29',6,494)]),
        dict(d=5,  sup=all_suppliers[3],
             items=[('DEMO-ML-BLK-41',6,824),('DEMO-CL-BRN-40',6,604)]),
        dict(d=48, sup=all_suppliers[1],
             items=[('DEMO-SS-BLK-37',8,714),('DEMO-FS-MRN-40',6,1754)]),
        dict(d=35, sup=all_suppliers[0],
             items=[('DEMO-RS-NAV-41',8,1374),('DEMO-RS-GRY-39',8,1374)]),

        # Round out to 35 PIs
        dict(d=75, sup=all_suppliers[2],
             items=[('DEMO-KP-TAN-39',8,494),('DEMO-ET-GLD-38',6,769)]),
        dict(d=68, sup=all_suppliers[4],
             items=[('DEMO-WF-BLK-39',8,659),('DEMO-WS-PNK-37',6,934)]),
        dict(d=62, sup=all_suppliers[3],
             items=[('DEMO-CL-BRN-42',8,604),('DEMO-ML-BRN-41',6,824)]),
        dict(d=42, sup=all_suppliers[5],
             items=[('DEMO-KD-PNK-28',6,494),('DEMO-SP-BLK-42',8,1099)]),
        dict(d=38, sup=all_suppliers[1],
             items=[('DEMO-SS-BRN-36',6,714),('DEMO-SS-BLK-34',8,714)]),
        dict(d=32, sup=all_suppliers[0],
             items=[('DEMO-RS-GRY-39',6,1374),('DEMO-RS-BLK-40',6,1374)]),
        dict(d=25, sup=all_suppliers[2],
             items=[('DEMO-HW-BLU-41',10,109),('DEMO-SL-BLU-40',10,82)]),
        dict(d=16, sup=all_suppliers[4],
             items=[('DEMO-WH-NDE-36',5,989),('DEMO-ET-GLD-36',5,769)]),
        dict(d=4,  sup=all_suppliers[5],
             items=[('DEMO-KD-BLU-30',6,439),('DEMO-SP-BLK-41',6,1099)]),
    ]

    created = 0
    for p in pi_specs:
        date_str = days_ago(p['d'])
        dup = frappe.db.get_value('Purchase Invoice', {
            'company': COMPANY,
            'supplier': p['sup'],
            'posting_date': date_str,
            'docstatus': 1
        }, 'name')
        if dup:
            print(f'  SKIP: {dup}')
            continue

        pi = frappe.new_doc('Purchase Invoice')
        pi.company      = COMPANY
        pi.supplier     = p['sup']
        pi.posting_date = date_str
        pi.credit_to    = get_payable_account()
        pi.bill_no      = f'DEMO1A-{p["d"]}-{p["sup"][:4].upper()}'
        pi.bill_date    = date_str
        pi.update_stock = 0

        for item_code, qty, rate in p['items']:
            pi.append('items', {'item_code': item_code, 'qty': qty,
                                'rate': rate, 'warehouse': WAREHOUSE})

        try:
            pi.insert(ignore_permissions=True)
            pi.submit()
            created += 1
            print(f'  PI-{created:02d}: {p["sup"][:25]:<25} {date_str}')
        except Exception as e:
            print(f'  ERROR PI ({p["sup"]}, {date_str}): {e}')

    frappe.db.commit()
    print(f'  {created} purchase invoices created.')

def get_all_customers():
    """Get 50 customers from existing pool, grouped by story role."""
    print('\n[5/5] Loading customers...')
    all_custs = frappe.db.get_all('Customer', {'disabled': 0}, ['name'], limit=60)
    names = [c.name for c in all_custs]

    # Phase 0 already used first 10. Get the next 40+ from the pool.
    phase0_used = {
        '_Test Clienteling Cust', 'Test Customer SFC', 'Test Customer SFM',
        'Compat Customer C', 'Compat Customer B', 'MIG Test Customer 001',
        'UAT Dealer Customer 0100', 'UAT Dealer Customer 0099',
        'UAT Dealer Customer 0098', 'UAT Dealer Customer 0097',
    }
    # Classify Phase 0 customers into their story roles
    p0_loyal   = ['_Test Clienteling Cust', 'Test Customer SFC']
    p0_lapsed  = ['Test Customer SFM', 'Compat Customer C', 'Compat Customer B']

    # New customers for Phase 1A
    fresh = [n for n in names if n not in phase0_used]

    # Assign roles from fresh pool
    loyal_new   = fresh[:6]      # 6 loyal customers (fresh)
    lapsed_new  = fresh[6:18]    # 12 lapsed customers
    new_custs   = fresh[18:28]   # 10 new customers (first purchase < 30 days)
    walkin      = fresh[28:48]   # 20 walk-in (1 invoice each)
    random_pool = fresh[:40]     # General traffic pool

    print(f'  Loyal (new):   {len(loyal_new)}')
    print(f'  Lapsed (new): {len(lapsed_new)}')
    print(f'  New (<30d):   {len(new_custs)}')
    print(f'  Walk-in:      {len(walkin)}')

    return dict(
        loyal_new=loyal_new, lapsed_new=lapsed_new,
        new_custs=new_custs, walkin=walkin,
        random_pool=random_pool,
    )

def create_sales_invoices_1a(custs):
    """230 additional Sales Invoices completing the 250-SI dataset."""
    print('\nCreating 230 Sales Invoices...')

    cash_acc = get_cash_account()
    recv_acc = get_receivable_account()

    # Item pools by velocity
    fast_p0   = ['DEMO-RS-BLK-40', 'DEMO-RS-BLK-41', 'DEMO-SS-BLK-35']
    fast_1a   = ['DEMO-RS-NAV-40', 'DEMO-RS-NAV-41', 'DEMO-RS-GRY-40',
                 'DEMO-SS-BLK-36', 'DEMO-HW-BLU-40', 'DEMO-HW-RED-40']
    fast_all  = fast_p0 + fast_1a
    reg_p0    = ['DEMO-WS-BGE-37', 'DEMO-CL-BLK-40', 'DEMO-CL-BRN-41', 'DEMO-KD-RED-29']
    reg_1a    = ['DEMO-WS-BRN-37', 'DEMO-WS-PNK-37', 'DEMO-ML-BLK-41',
                 'DEMO-KD-BLU-29', 'DEMO-SP-BLK-40', 'DEMO-KP-TAN-40',
                 'DEMO-ET-GLD-37', 'DEMO-SL-BLU-39', 'DEMO-CL-BLK-41',
                 'DEMO-WF-BLK-38', 'DEMO-SS-BLK-34']
    reg_all   = reg_p0 + reg_1a
    # dead items: never appear in any SI (by design)

    all_items = {}
    for it in NEW_ITEMS:
        all_items[it['item_code']] = it['rate']
    # Add Phase 0 items from memory
    for code, rate in [('DEMO-RS-BLK-40',2499),('DEMO-RS-BLK-41',2499),('DEMO-SS-BLK-35',1299),
                       ('DEMO-WS-BGE-37',1599),('DEMO-CL-BLK-40',1099),('DEMO-CL-BRN-41',1099),
                       ('DEMO-KD-RED-29',799)]:
        all_items[code] = rate

    def si_items(pool, n=2, qty_range=(1,2)):
        pool = [p for p in pool if p in all_items]
        chosen = random.sample(pool, min(n, len(pool)))
        return [(c, random.randint(*qty_range), all_items[c]) for c in chosen]

    created = 0
    errors  = 0

    # ── Block A: Loyal customers (6 new × 8 invoices = 48) ───────────────────
    for cust in custs['loyal_new']:
        if not cust:
            continue
        date_buckets = [(85,80),(72,68),(60,55),(48,43),(35,30),(22,18),(10,7),(3,1)]
        for from_d, to_d in date_buckets:
            pd = rand_date(from_d, to_d)
            items = si_items(fast_all + reg_all, n=2, qty_range=(1,3))
            try:
                si = make_si(cust, pd, items, cash_acc, recv_acc)
                if si:
                    created += 1
                    if created % 20 == 0:
                        print(f'  ... {created} SIs created')
            except Exception as e:
                errors += 1

    # ── Block B: Lapsed customers (12 × 1 invoice, all > 60 days ago) ────────
    for cust in custs['lapsed_new']:
        if not cust:
            continue
        pd = rand_date(82, 63)   # All well before the 60-day cutoff
        items = si_items(fast_all + reg_all, n=2, qty_range=(1,2))
        try:
            si = make_si(cust, pd, items, cash_acc, recv_acc)
            if si:
                created += 1
        except Exception as e:
            errors += 1

    # ── Block C: New customers (10 × 1 invoice, last 30 days) ────────────────
    for cust in custs['new_custs']:
        if not cust:
            continue
        pd = rand_date(29, 1)
        items = si_items(fast_all + reg_all, n=2, qty_range=(1,2))
        try:
            si = make_si(cust, pd, items, cash_acc, recv_acc)
            if si:
                created += 1
        except Exception as e:
            errors += 1

    # ── Block D: Walk-in customers (20 × 1 invoice) ───────────────────────────
    for cust in custs['walkin']:
        if not cust:
            continue
        pd = rand_date(85, 2)
        items = si_items(fast_all + reg_all, n=1, qty_range=(1,2))
        try:
            si = make_si(cust, pd, items, cash_acc, recv_acc)
            if si:
                created += 1
        except Exception as e:
            errors += 1

    # ── Block E: General traffic (remaining ~140 invoices) ────────────────────
    # Distribute remaining to reach ~230 total added
    target_remaining = 230 - created
    pool = [c for c in custs['random_pool'] if c]

    if not pool:
        print(f'  WARNING: No random pool customers. Skipping Block E.')
    else:
        for i in range(target_remaining):
            cust = random.choice(pool)
            pd   = rand_date(88, 1)
            # Mix fast and regular items
            use_fast = random.random() < 0.6
            item_pool = fast_all if use_fast else reg_all
            items = si_items(item_pool, n=random.randint(1,2), qty_range=(1,2))
            try:
                si = make_si(cust, pd, items, cash_acc, recv_acc)
                if si:
                    created += 1
                    if created % 50 == 0:
                        print(f'  ... {created} SIs created')
                        frappe.db.commit()
            except Exception as e:
                errors += 1

    frappe.db.commit()
    print(f'\n  Phase 1A SIs: {created} created, {errors} errors.')
    print(f'  Phase 0 SIs: 20 (already exist)')
    print(f'  Total approx: {created + 20}')

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# SUB-PHASE ENTRY POINTS
# ─────────────────────────────────────────────────────────────────────────────

def phase1a_1():
    """Phase 1A.1 — Items, Suppliers, Opening Stock."""
    frappe.set_user('Administrator')
    print('=== PHASE 1A.1: Items + Suppliers + Opening Stock ===')
    create_new_items()
    create_new_suppliers()
    create_opening_stock_1a()
    print('=== Phase 1A.1 COMPLETE ===')

def phase1a_2():
    """Phase 1A.2 — Customer segmentation preview (no transactions)."""
    frappe.set_user('Administrator')
    print('=== PHASE 1A.2: Customer Segmentation Preview ===')
    custs = get_all_customers()
    print()
    print('Customer Segments:')
    print(f'  Loyal (new)   : {len(custs["loyal_new"])} customers')
    print(f'  Lapsed (new)  : {len(custs["lapsed_new"])} customers')
    print(f'  New (<30 days): {len(custs["new_custs"])} customers')
    print(f'  Walk-in       : {len(custs["walkin"])} customers')
    print(f'  Traffic pool  : {len(custs["random_pool"])} customers')
    print()
    total = (len(custs["loyal_new"]) + len(custs["lapsed_new"]) +
             len(custs["new_custs"]) + len(custs["walkin"]))
    print(f'  Total segmented: {total} / 50 target')
    print('=== Phase 1A.2 COMPLETE ===')

def phase1a_3():
    """Phase 1A.3 — 250 Sales Invoices + 40 Purchase Invoices."""
    frappe.set_user('Administrator')
    print('=== PHASE 1A.3: Transactions (250 SI + 40 PI) ===')
    create_purchase_invoices_1a()
    custs = get_all_customers()
    create_sales_invoices_1a(custs)
    print('=== Phase 1A.3 COMPLETE ===')

def main():
    """Full Phase 1A in sequence."""
    frappe.set_user('Administrator')
    print('=' * 60)
    print('OWNER-DEMO-001 — Phase 1A: Full Dataset Expansion')
    print('Company:', COMPANY)
    print('=' * 60)
    create_new_items()
    create_new_suppliers()
    create_opening_stock_1a()
    create_purchase_invoices_1a()
    custs = get_all_customers()
    create_sales_invoices_1a(custs)
    print('\n' + '=' * 60)
    print('Phase 1A COMPLETE. Run OWNER_DEMO_AUDIT next.')
    print('=' * 60)
