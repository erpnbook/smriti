"""
OWNER-DEMO-001 — verify_stories.py
OWNER_DEMO_AUDIT + OWNER_DEMO_HEALTH_SCORE

Verifies all 7 business stories. Returns PASS/FAIL per story plus a Health Score.
Phase 1A expansion continues regardless of score — score tracks richness.

Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
"""

import frappe
from datetime import date, timedelta

COMPANY   = 'SMRITI UAT Footwear Co'
WAREHOUSE = 'Stores - SUFC'
TODAY     = date.today()
D60 = (TODAY - timedelta(days=60)).strftime('%Y-%m-%d')
D90 = (TODAY - timedelta(days=90)).strftime('%Y-%m-%d')

STORIES_PASS   = []
STORIES_FAIL   = []
STORY_SCORES   = {}   # story_id -> score 0-100

def check(story_id, label, result, detail='', score=None):
    status = 'PASS' if result else 'FAIL'
    symbol = 'OK' if result else 'XX'
    score_str = f'  [{score:3d}/100]' if score is not None else ''
    line = f'  [{symbol}]{score_str} Story {story_id}: {label}'
    if detail:
        line += f'\n       {detail}'
    print(line)
    if result:
        STORIES_PASS.append(story_id)
    else:
        STORIES_FAIL.append((story_id, label, detail))
    if score is not None:
        STORY_SCORES[story_id] = score

def _score(value, bands):
    """bands = [(threshold, score),...]. Returns score for the highest threshold met."""
    for threshold, score in sorted(bands, reverse=True):
        if value >= threshold:
            return score
    return 0

def verify():
    frappe.set_user('Administrator')
    STORIES_PASS.clear(); STORIES_FAIL.clear(); STORY_SCORES.clear()

    print('=' * 60)
    print('OWNER_DEMO_AUDIT + OWNER_DEMO_HEALTH_SCORE')
    print(f'Company : {COMPANY}')
    print(f'Date    : {TODAY}')
    print('=' * 60)

    # Story 1: Fast Movers
    fast_movers = frappe.db.sql("""
        SELECT sii.item_code, SUM(sii.qty) as total_qty
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.company = %s AND si.docstatus = 1
          AND si.posting_date >= %s
        GROUP BY sii.item_code
        HAVING total_qty >= 5
        ORDER BY total_qty DESC
    """, (COMPANY, D90), as_dict=True)
    fm_score = _score(len(fast_movers), [(10,100),(6,95),(4,90),(2,75),(1,50)])
    check('1', 'Fast Movers',
          len(fast_movers) >= 2,
          f'{len(fast_movers)} items: ' + ', '.join(f"{r.item_code}({int(r.total_qty)}u)" for r in fast_movers[:5]),
          score=fm_score)

    # Story 2: Dead Stock
    all_stock = frappe.db.sql("""
        SELECT item_code, SUM(actual_qty) as qty FROM `tabBin`
        WHERE warehouse = %s AND actual_qty > 0 GROUP BY item_code
    """, WAREHOUSE, as_dict=True)
    sold_60 = frappe.db.sql("""
        SELECT DISTINCT sii.item_code
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.company = %s AND si.docstatus = 1 AND si.posting_date >= %s
    """, (COMPANY, D60), as_dict=True)
    sold_60_codes = {r.item_code for r in sold_60}
    dead_stock = [r for r in all_stock
                  if r.item_code not in sold_60_codes and r.qty > 0
                  and r.item_code.startswith('DEMO-')]
    dead_value = sum((r.qty * (frappe.db.get_value('Item', r.item_code, 'standard_rate') or 0))
                     for r in dead_stock)
    ds_score = _score(dead_value, [(200000,100),(100000,95),(50000,85),(20000,70),(10000,50)])
    check('2', 'Dead Stock',
          len(dead_stock) >= 2,
          f'{len(dead_stock)} items | INR {dead_value:,.0f} locked | ' + ', '.join(r.item_code for r in dead_stock[:5]),
          score=ds_score)

    # Story 3: Low Stock
    low_stock = frappe.db.sql("""
        SELECT b.item_code, b.actual_qty FROM `tabBin` b
        WHERE b.warehouse = %s AND b.actual_qty > 0 AND b.actual_qty < 5
          AND b.item_code LIKE 'DEMO-%%'
    """, WAREHOUSE, as_dict=True)
    ls_score = _score(len(low_stock), [(5,100),(3,90),(2,80),(1,60)])
    check('3', 'Low Stock Alerts',
          len(low_stock) >= 1,
          ', '.join(f"{r.item_code}(qty={r.actual_qty})" for r in low_stock),
          score=ls_score)

    # Story 4: Loyal Customers
    loyal = frappe.db.sql("""
        SELECT customer, COUNT(name) as visit_count, SUM(grand_total) as total_spent
        FROM `tabSales Invoice`
        WHERE company = %s AND docstatus = 1 AND posting_date >= %s
        GROUP BY customer HAVING visit_count >= 4 ORDER BY visit_count DESC
    """, (COMPANY, D90), as_dict=True)
    loy_score = _score(len(loyal), [(8,100),(5,95),(3,85),(1,65)])
    check('4', 'Loyal Customers',
          len(loyal) >= 1,
          f'{len(loyal)} customers: ' + ', '.join(f"{r.customer[:18]}({r.visit_count}v)" for r in loyal[:4]),
          score=loy_score)

    # Story 5: Lapsed Customers
    lapsed_rows = frappe.db.sql("""
        SELECT customer, MAX(posting_date) as last_purchase
        FROM `tabSales Invoice`
        WHERE company = %s AND docstatus = 1
        GROUP BY customer HAVING last_purchase < %s
    """, (COMPANY, D60), as_dict=True)
    lapsed = {r.customer: str(r.last_purchase) for r in lapsed_rows}
    lap_score = _score(len(lapsed), [(12,100),(8,95),(5,85),(2,65)])
    check('5', 'Lapsed Customers',
          len(lapsed) >= 2,
          f'{len(lapsed)} lapsed: ' + ', '.join(f"{c[:18]}({d})" for c, d in list(lapsed.items())[:4]),
          score=lap_score)

    # Story 6: Reorder Opportunity
    fast_codes = {r.item_code for r in fast_movers}
    reorder_rows = frappe.db.sql("""
        SELECT b.item_code, b.actual_qty FROM `tabBin` b
        WHERE b.warehouse = %s AND b.actual_qty > 0 AND b.actual_qty < 15
          AND b.item_code LIKE 'DEMO-%%'
    """, WAREHOUSE, as_dict=True)
    reorder_opp = fast_codes & {r.item_code for r in reorder_rows}
    ro_score = _score(len(reorder_opp), [(6,100),(4,95),(2,85),(1,65)])
    check('6', 'Reorder Opportunity',
          len(reorder_opp) >= 1,
          ', '.join(f"{r.item_code}(qty={r.actual_qty})"
                    for r in reorder_rows if r.item_code in fast_codes) or 'None',
          score=ro_score)

    # Story 7: Working Capital
    wc_score = _score(dead_value, [(300000,100),(150000,95),(75000,85),(10000,60)])
    check('7', 'Working Capital Locked',
          dead_value >= 10000,
          f'INR {dead_value:,.0f} in {len(dead_stock)} dead items',
          score=wc_score)

    # OWNER_DEMO_AUDIT verdict
    total = len(STORIES_PASS) + len(STORIES_FAIL)
    print('\n' + '=' * 60)
    print(f'OWNER_DEMO_AUDIT : {len(STORIES_PASS)}/{total} PASS')
    if STORIES_FAIL:
        for sid, label, _ in STORIES_FAIL:
            print(f'  FAIL  Story {sid}: {label}')
    else:
        print('OWNER_DEMO_AUDIT = PASS')

    # OWNER_DEMO_HEALTH_SCORE
    labels = {'1':'Fast Movers','2':'Dead Stock','3':'Low Stock Alert',
              '4':'Loyal Customers','5':'Lapsed Customers',
              '6':'Reorder Opportunity','7':'Working Capital'}
    if STORY_SCORES:
        overall = round(sum(STORY_SCORES.values()) / len(STORY_SCORES))
        grade   = ('EXCELLENT' if overall >= 95 else
                   'GOOD'      if overall >= 85 else
                   'ADEQUATE'  if overall >= 70 else 'NEEDS WORK')
        print()
        print('OWNER_DEMO_HEALTH_SCORE')
        print('-' * 60)
        for sid in sorted(STORY_SCORES):
            s   = STORY_SCORES[sid]
            bar = '#' * (s // 10) + '-' * (10 - s // 10)
            print(f'  Story {sid}  {labels.get(sid,""):<22}  [{bar}]  {s:3}/100')
        print()
        print(f'  Overall Score  : {overall}/100')
        print(f'  Grade          : {grade}')
        print()
        if overall >= 90:
            print('  OWNER DEMO READY')
        else:
            print(f'  Target: 90+ | Gap: {90-overall} points | Run Phase 1A')
    print('=' * 60)
    return len(STORIES_FAIL) == 0

