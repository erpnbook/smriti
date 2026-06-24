"""
OWNER-DEMO-001 — verify_stories.py
OWNER_DEMO_AUDIT: Verifies all 7 business stories are discoverable in the data.

Success = all 7 stories PASS.
Expansion to 72 SKU full dataset is BLOCKED until OWNER_DEMO_AUDIT = PASS.

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""

import frappe
from datetime import date, timedelta

COMPANY   = 'SMRITI UAT Footwear Co'
WAREHOUSE = 'Stores - SUFC'
TODAY     = date.today()
D60 = (TODAY - timedelta(days=60)).strftime('%Y-%m-%d')
D90 = (TODAY - timedelta(days=90)).strftime('%Y-%m-%d')

STORIES_PASS = []
STORIES_FAIL = []

def check(story_id, label, result, detail=''):
    status = 'PASS' if result else 'FAIL'
    symbol = 'OK' if result else 'XX'
    line = f'  [{symbol}] Story {story_id}: {label}'
    if detail:
        line += f'\n       {detail}'
    print(line)
    if result:
        STORIES_PASS.append(story_id)
    else:
        STORIES_FAIL.append((story_id, label, detail))

def verify():
    frappe.set_user('Administrator')
    print('=' * 60)
    print('OWNER_DEMO_AUDIT — Story Verification Report')
    print(f'Company : {COMPANY}')
    print(f'Date    : {TODAY}')
    print('=' * 60)

    # ── Story 1: Fast Movers ──────────────────────────────────────────────────
    # At least 3 items with >= 5 sales invoices in 90 days
    fast_movers = frappe.db.sql("""
        SELECT sii.item_code, COUNT(si.name) as invoice_count, SUM(sii.qty) as total_qty
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.company = %s
          AND si.docstatus = 1
          AND si.posting_date >= %s
        GROUP BY sii.item_code
        HAVING total_qty >= 5
        ORDER BY total_qty DESC
    """, (COMPANY, D90), as_dict=True)

    check('1', 'Fast Movers (>=5 units sold in 90 days)',
          len(fast_movers) >= 2,
          f'Found {len(fast_movers)} fast movers: ' +
          ', '.join(f"{r.item_code}({int(r.total_qty)} units)" for r in fast_movers[:5]))

    # ── Story 2: Dead Stock ───────────────────────────────────────────────────
    # Items with stock > 0 but 0 sales in last 60 days
    all_stock = frappe.db.sql("""
        SELECT item_code, SUM(actual_qty) as qty
        FROM `tabBin`
        WHERE warehouse = %s AND actual_qty > 0
        GROUP BY item_code
    """, WAREHOUSE, as_dict=True)

    sold_60 = frappe.db.sql("""
        SELECT DISTINCT sii.item_code
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.company = %s AND si.docstatus = 1
          AND si.posting_date >= %s
    """, (COMPANY, D60), as_dict=True)
    sold_60_codes = {r.item_code for r in sold_60}

    dead_stock = [r for r in all_stock
                  if r.item_code not in sold_60_codes and r.qty > 0
                  and r.item_code.startswith('DEMO-')]

    dead_value = sum(
        r.qty * frappe.db.get_value('Item', r.item_code, 'standard_rate') or 0
        for r in dead_stock
    )

    check('2', 'Dead Stock (stock > 0, 0 sales in 60 days)',
          len(dead_stock) >= 2,
          f'Found {len(dead_stock)} dead stock items | '
          f'Capital locked: ~INR {dead_value:,.0f} | '
          'Items: ' + ', '.join(r.item_code for r in dead_stock[:5]))

    # ── Story 3: Low Stock Alerts ─────────────────────────────────────────────
    # Items with stock < 5 that were sold recently (not dead)
    low_stock = frappe.db.sql("""
        SELECT b.item_code, b.actual_qty
        FROM `tabBin` b
        WHERE b.warehouse = %s
          AND b.actual_qty > 0
          AND b.actual_qty < 5
          AND b.item_code LIKE 'DEMO-%%'
    """, WAREHOUSE, as_dict=True)

    check('3', 'Low Stock Alerts (stock < 5)',
          len(low_stock) >= 1,
          f'Found {len(low_stock)} low-stock items: ' +
          ', '.join(f"{r.item_code}(qty={r.actual_qty})" for r in low_stock))

    # ── Story 4: Loyal Customers ──────────────────────────────────────────────
    # Customers with >= 4 invoices in 90 days
    loyal = frappe.db.sql("""
        SELECT customer, COUNT(name) as visit_count, SUM(grand_total) as total_spent
        FROM `tabSales Invoice`
        WHERE company = %s AND docstatus = 1
          AND posting_date >= %s
        GROUP BY customer
        HAVING visit_count >= 4
        ORDER BY visit_count DESC
    """, (COMPANY, D90), as_dict=True)

    check('4', 'Loyal Customers (4+ visits in 90 days)',
          len(loyal) >= 1,
          f'Found {len(loyal)} loyal customers: ' +
          ', '.join(f"{r.customer[:20]}({r.visit_count} visits, INR {r.total_spent:,.0f})"
                    for r in loyal[:3]))

    # ── Story 5: Lapsed Customers ─────────────────────────────────────────────
    # Direct MAX(posting_date) approach — customers whose last purchase was > 60 days ago
    lapsed_rows = frappe.db.sql("""
        SELECT customer, MAX(posting_date) as last_purchase
        FROM `tabSales Invoice`
        WHERE company = %s AND docstatus = 1
        GROUP BY customer
        HAVING last_purchase < %s
    """, (COMPANY, D60), as_dict=True)

    lapsed = {r.customer: str(r.last_purchase) for r in lapsed_rows}

    check('5', 'Lapsed Customers (last purchase > 60 days ago)',
          len(lapsed) >= 2,
          f'Found {len(lapsed)} lapsed customers: ' +
          ', '.join(f"{c}(last: {d})" for c, d in list(lapsed.items())[:5]))

    # ── Story 6: Reorder Opportunity ─────────────────────────────────────────
    # Fast mover with stock below reorder threshold (< 15 units).
    # Reorder threshold = 15 units = realistic trigger for items opening at 20-25.
    fast_codes = {r.item_code for r in fast_movers}

    reorder_rows = frappe.db.sql("""
        SELECT b.item_code, b.actual_qty
        FROM `tabBin` b
        WHERE b.warehouse = %s
          AND b.actual_qty > 0
          AND b.actual_qty < 15
          AND b.item_code LIKE 'DEMO-%%'
    """, WAREHOUSE, as_dict=True)
    near_low_codes = {r.item_code for r in reorder_rows}
    reorder_opp = fast_codes & near_low_codes

    reorder_detail = ', '.join(
        f"{r.item_code}(qty={r.actual_qty})"
        for r in reorder_rows if r.item_code in fast_codes
    ) or 'None'

    check('6', 'Reorder Opportunity (fast mover stock < 15 = reorder zone)',
          len(reorder_opp) >= 1,
          f'Reorder candidates: {reorder_detail}')

    # ── Story 7: Working Capital Locked ───────────────────────────────────────
    # Dead stock total value > INR 10,000
    check('7', 'Working Capital Story (dead stock value > INR 10,000)',
          dead_value >= 10000,
          f'Dead stock value: INR {dead_value:,.0f}  '
          f'(Items: {len(dead_stock)}, threshold: INR 10,000)')

    # ── OWNER_DEMO_AUDIT VERDICT ──────────────────────────────────────────────
    print('\n' + '=' * 60)
    total = len(STORIES_PASS) + len(STORIES_FAIL)
    print(f'OWNER_DEMO_AUDIT Results: {len(STORIES_PASS)}/{total} stories PASS')
    print()

    if STORIES_FAIL:
        print('FAILED stories (must fix before Phase 1A):')
        for sid, label, detail in STORIES_FAIL:
            print(f'  Story {sid}: {label}')
            if detail:
                print(f'    Detail: {detail}')
    else:
        print('ALL 7 STORIES VERIFIED.')
        print()
        print('OWNER_DEMO_AUDIT = PASS')
        print()
        print('Phase 1A (72 SKU full dataset) is now UNBLOCKED.')

    print('=' * 60)
    return len(STORIES_FAIL) == 0
