#!/bin/bash
cd /home/frappe/frappe-bench
echo "=============================="
echo "PHASE 1A.1: Items + Suppliers + Opening Stock"
echo "=============================="
bench --site smriti_retail execute smriti_retail_os.demo_phase1a.phase1a_1
echo ""
echo "=============================="
echo "AUDIT after Phase 1A.1"
echo "=============================="
bench --site smriti_retail execute smriti_retail_os.demo_verify.verify
