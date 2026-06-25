#!/bin/bash
cd /home/frappe/frappe-bench
echo "=== Running OWNER_DEMO_AUDIT (data already loaded) ==="
bench --site smriti_retail execute smriti_retail_os.demo_verify.verify
