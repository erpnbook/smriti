#!/bin/bash
cd /home/frappe/frappe-bench
echo "=============================="
echo "Phase 1A Post-Fix: Founder Spec Alignment"
echo "=============================="
bench --site smriti_retail execute smriti_retail_os.demo_phase1a_fix.main
echo ""
echo "=============================="
echo "FINAL AUDIT: OWNER_DEMO_AUDIT + HEALTH_SCORE"
echo "=============================="
bench --site smriti_retail execute smriti_retail_os.demo_verify.verify
