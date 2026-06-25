#!/bin/bash
cd /home/frappe/frappe-bench
echo "=============================="
echo "PHASE 1A.2: Customer Segmentation"
echo "=============================="
bench --site smriti_retail execute smriti_retail_os.demo_phase1a.phase1a_2
echo ""
echo "=============================="
echo "PHASE 1A.3: Transactions (230 SI + 35 PI)"
echo "=============================="
bench --site smriti_retail execute smriti_retail_os.demo_phase1a.phase1a_3
echo ""
echo "=============================="
echo "FINAL AUDIT: OWNER_DEMO_AUDIT + HEALTH_SCORE"
echo "=============================="
bench --site smriti_retail execute smriti_retail_os.demo_verify.verify
