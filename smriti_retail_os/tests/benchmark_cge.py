# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/benchmark_cge.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/benchmark_cge.py
# @description: Performance scaling curve benchmark script for SMRITI Customer Growth Engine (CGE).
# @author: Antigravity AI
# @date: 2026-06-19
#

import time
import os
import frappe
from frappe.utils import nowdate, add_to_date, flt
from smriti_retail_os.cge.service.cge_service import (
    CGERuleEvaluator,
    validate_checkout_rules
)

try:
    import psutil
    def get_memory_usage():
        process = psutil.Process()
        return process.memory_info().rss / (1024.0 * 1024.0) # Convert to MB
except ImportError:
    def get_memory_usage():
        return 0.0

def run_benchmark():
    """
    Executes the CGE performance scale-curve benchmark.
    Asserts performance targets under varying rule sizes (100, 500, 1000, 5000).
    """
    print("==========================================================")
    print("SMRITI CGE PERFORMANCE SCALE-CURVE BENCHMARK ENGINE")
    print("==========================================================")
    
    # 1. Setup mock load data
    customer_name = "_Test Bench Customer"
    if not frappe.db.exists("Customer", customer_name):
        cust = frappe.new_doc("Customer")
        cust.customer_name = customer_name
        cust.customer_group = "Individual"
        cust.insert(ignore_permissions=True)

    brand_name = "Raymond Bench"
    if not frappe.db.exists("Brand", brand_name):
        b = frappe.new_doc("Brand")
        b.brand = brand_name
        b.insert(ignore_permissions=True)

    item_code = "_Test Bench Item"
    if not frappe.db.exists("Item", item_code):
        item = frappe.new_doc("Item")
        item.item_code = item_code
        item.item_name = item_code
        item.item_group = "All Item Groups"
        item.brand = brand_name
        item.gst_hsn_code = "999900"
        item.insert(ignore_permissions=True)

    # Setup standard tier
    frappe.db.delete("SMRITI Loyalty Tier")
    tier = frappe.new_doc("SMRITI Loyalty Tier")
    tier.tier_name = "Platinum Tier"
    tier.min_points = 0.0
    tier.tier_multiplier = 2.0
    tier.active = 1
    tier.insert(ignore_permissions=True)
    
    frappe.db.commit()

    # Create mockup invoice
    invoice_doc = frappe.new_doc("Sales Invoice")
    invoice_doc.customer = customer_name
    invoice_doc.company = frappe.get_all("Company", limit=1)[0].name
    invoice_doc.posting_date = nowdate()
    invoice_doc.append("items", {
        "item_code": item_code,
        "qty": 2,
        "rate": 2500.0,
        "warehouse": "Stores - TDP"
    })

    # Scale tiers to test
    scale_tiers = [100, 500, 1000, 5000]
    results = {}

    for size in scale_tiers:
        print(f"\nPopulating database with {size} active loyalty rules...")
        frappe.db.delete("SMRITI Loyalty Rule")
        
        # Generate rules in bulk for faster insertion
        for i in range(size):
            rule = frappe.new_doc("SMRITI Loyalty Rule")
            rule.rule_name = f"Bench Rule {i+1}"
            rule.rule_type = "Multiplier"
            rule.dimension = "Brand"
            rule.dimension_value = brand_name
            rule.rule_value = 1.01 + (i * 0.0001)
            rule.priority = i
            rule.allow_stack = 1
            rule.status = "Active"
            rule.insert(ignore_permissions=True)
            
            # Commit periodically to keep transactions light
            if i % 1000 == 0:
                frappe.db.commit()
                
        frappe.db.commit()
        
        print(f"Executing load loops for {size} rules...")
        
        # Warmup round
        evaluator = CGERuleEvaluator(invoice_doc)
        evaluator.evaluate()

        # Benchmark iterations (adjust loops based on size to keep runtime sane)
        loops = 50 if size < 1000 else 15
        
        mem_before = get_memory_usage()
        start_time = time.perf_counter()
        
        for _ in range(loops):
            eval = CGERuleEvaluator(invoice_doc)
            eval.evaluate()
            
        end_time = time.perf_counter()
        mem_after = get_memory_usage()
        
        avg_latency_ms = ((end_time - start_time) / loops) * 1000.0
        mem_delta = max(0.0, mem_after - mem_before)
        
        results[size] = {
            "latency_ms": avg_latency_ms,
            "memory_mb": mem_after,
            "memory_delta_mb": mem_delta
        }
        
        print(f"-> Size {size}: Avg Latency = {avg_latency_ms:.2f} ms | RSS Memory = {mem_after:.2f} MB")

    # Print Summary Report Table
    print("\n==========================================================")
    print("                CGE SCALING CURVE REPORT")
    print("==========================================================")
    print(" Rules Count | Avg Latency (ms) | Memory delta (MB) ")
    print("-------------|------------------|-------------------")
    for size in scale_tiers:
        lat = results[size]["latency_ms"]
        mdelta = results[size]["memory_delta_mb"]
        print(f" {size:<11} | {lat:<16.2f} | {mdelta:<17.2f} ")
    print("==========================================================")

    # Scale curves latency assertions
    # Latency grows with rule count, but matches standard search boundaries
    assert results[100]["latency_ms"] < 50.0, f"100 rules exceeded 50ms target: {results[100]['latency_ms']:.2f}ms"
    assert results[500]["latency_ms"] < 100.0, f"500 rules exceeded 100ms target: {results[500]['latency_ms']:.2f}ms"
    assert results[1000]["latency_ms"] < 150.0, f"1000 rules exceeded 150ms target: {results[1000]['latency_ms']:.2f}ms"
    assert results[5000]["latency_ms"] < 400.0, f"5000 rules exceeded 400ms target: {results[5000]['latency_ms']:.2f}ms"

    print("Success: Performance curves satisfy all scaling targets!")
    print("==========================================================")

    # Cleanup
    frappe.db.delete("SMRITI Loyalty Rule")
    frappe.db.delete("SMRITI Loyalty Tier")
    frappe.db.delete("Customer", {"name": customer_name})
    frappe.db.delete("Item", {"name": item_code})
    frappe.db.delete("Brand", {"name": brand_name})
    frappe.db.commit()

if __name__ == "__main__":
    run_benchmark()
