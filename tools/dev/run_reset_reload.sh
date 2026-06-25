#!/bin/bash
cd /home/frappe/frappe-bench
echo "=== Step 1: Reset existing SIs ==="
bench --site smriti_retail execute smriti_retail_os.demo_reset_si.reset_sales
echo ""
echo "=== Step 2: Reload Phase 0 (items/suppliers/stock already exist — will SKIP) ==="
bench --site smriti_retail execute smriti_retail_os.demo_phase0.main
echo ""
echo "=== Step 3: OWNER_DEMO_AUDIT ==="
bench --site smriti_retail execute smriti_retail_os.demo_verify.verify
