#!/bin/bash
cd /home/frappe/frappe-bench
echo "=== Running OWNER-DEMO-001 Phase 0 ==="
bench --site smriti_retail execute smriti_retail_os.demo_phase0.main
echo ""
echo "=== Running OWNER_DEMO_AUDIT ==="
bench --site smriti_retail execute smriti_retail_os.demo_verify.verify
