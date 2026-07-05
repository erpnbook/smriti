---
Document ID: "SMRITI-DOC-026"
Title: "SMRITI API Inventory"
Owner: "Release Engineering Team"
Audience: "Support Engineer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "No"
Depends On: ""
Related Modules: ""
Last Updated: "2026-07-04"
Last Reviewed: "2026-07-04"
AI Generated: "No"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Whitelisted API Reference

* **Compiler Version:** 1.1
* **Snapshot Commit:** `f95b4fe91f273f7a6745f2f7d1de4733757db2dd`
* **Compiled At:** 2026-06-25T10:19:35Z

## Whitelisted Methods

### `smriti_retail_os.backup_api.get_settings`
* **Artifact ID:** `ART-API-00194`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.save_settings`
* **Artifact ID:** `ART-API-00195`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** settings
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.get_backup_status`
* **Artifact ID:** `ART-API-00196`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.get_backup_history`
* **Artifact ID:** `ART-API-00197`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.export_site_config`
* **Artifact ID:** `ART-API-00198`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** password
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.run_smtp_password_migration`
* **Artifact ID:** `ART-API-00199`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.verify_custodian_emails`
* **Artifact ID:** `ART-API-00200`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** emails
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.send_recovery_key`
* **Artifact ID:** `ART-API-00201`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** recipient_email
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.get_encryption_status`
* **Artifact ID:** `ART-API-00202`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.confirm_custodian_otp`
* **Artifact ID:** `ART-API-00203`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** email, otp
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.rotate_encryption_key`
* **Artifact ID:** `ART-API-00204`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** new_key
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.take_backup_now`
* **Artifact ID:** `ART-API-00205`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** backup_type
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.delete_backup`
* **Artifact ID:** `ART-API-00206`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** file_name
* **Evidence Type:** `AST`

### `smriti_retail_os.backup_api.restore_backup`
* **Artifact ID:** `ART-API-00207`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/backup_api.py`
* **Arguments:** file_name
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_barcode_filters`
* **Artifact ID:** `ART-API-00101`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** 
* **Database References:** Brand, Department, DocType, Item Group, SMRITI Gender, SMRITI Print Template, Supplier
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_print_templates`
* **Artifact ID:** `ART-API-00102`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** 
* **Database References:** DocType, SMRITI Print Template
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.expand_item_variants`
* **Artifact ID:** `ART-API-00103`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** item_code, default_print_qty
* **Database References:** Item
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_transaction_items_checklist`
* **Artifact ID:** `ART-API-00104`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** source_doctype, source_name
* **Database References:** Item, Item Barcode
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_items_by_range`
* **Artifact ID:** `ART-API-00105`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** from_article, to_article
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_items_for_printing`
* **Artifact ID:** `ART-API-00106`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** filters, source_doctype, source_name
* **Database References:** Item Attribute, Purchase Receipt, Stock Entry
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.generate_prn`
* **Artifact ID:** `ART-API-00107`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** items, template_name
* **Database References:** DocType, Item, SMRITI Print Template
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.send_to_network_printer`
* **Artifact ID:** `ART-API-00108`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** items, template_name, printer_ip, printer_port
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_field_mapping_reference`
* **Artifact ID:** `ART-API-00109`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_recent_transactions`
* **Artifact ID:** `ART-API-00110`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** doctype, limit
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.test_printer_connection`
* **Artifact ID:** `ART-API-00111`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** printer_ip, printer_port
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.print_test_label`
* **Artifact ID:** `ART-API-00112`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** printer_ip, printer_port, printer_language
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.log_print_job`
* **Artifact ID:** `ART-API-00113`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** template_name, printer_ip, labels_count, success, error_message, print_profile, details
* **Database References:** Activity Log, Company
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_print_analytics`
* **Artifact ID:** `ART-API-00114`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_template_usage_stats`
* **Artifact ID:** `ART-API-00115`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_print_profiles`
* **Artifact ID:** `ART-API-00116`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** 
* **Database References:** SMRITI Company Settings
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.save_print_profile`
* **Artifact ID:** `ART-API-00117`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** profile_name, template_name, printer_ip, printer_port, dpi, copies, label_size, is_default
* **Database References:** Company, SMRITI Company Settings
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.delete_print_profile`
* **Artifact ID:** `ART-API-00118`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** profile_name
* **Database References:** SMRITI Company Settings
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.save_print_template`
* **Artifact ID:** `ART-API-00119`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** template_name, label_size, printer_language, raw_template, field_mappings_json, printer_family, custom_active, custom_is_default, custom_version, custom_visual_layout_json, version_label
* **Database References:** DocType, SMRITI Print Template
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.delete_print_template`
* **Artifact ID:** `ART-API-00120`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** name_id
* **Database References:** DocType, SMRITI Print Template
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.search_barcode_items`
* **Artifact ID:** `ART-API-00121`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** txt
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.enqueue_print_job`
* **Artifact ID:** `ART-API-00122`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** template_name, printer_ip, printer_port, payload, print_qty, labels_count, item_code, barcode
* **Database References:** SMRITI Print Job
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api._process_print_job`
* **Artifact ID:** `ART-API-00123`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** job_id, print_job_id
* **Database References:** SMRITI Print Job
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_print_job_status`
* **Artifact ID:** `ART-API-00124`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** job_id
* **Database References:** SMRITI Print Job
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.retry_print_job`
* **Artifact ID:** `ART-API-00125`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** job_id
* **Database References:** SMRITI Print Job
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_recent_print_jobs`
* **Artifact ID:** `ART-API-00126`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** limit
* **Database References:** SMRITI Print Job
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_print_template_versions`
* **Artifact ID:** `ART-API-00127`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** template_name
* **Database References:** SMRITI Print Template, SMRITI Print Template Version
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.restore_print_template_version`
* **Artifact ID:** `ART-API-00128`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** template_name, version_number, expected_checksum
* **Database References:** SMRITI Print Template, SMRITI Print Template Version
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.validate_layout_diagnostics`
* **Artifact ID:** `ART-API-00129`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** layout_json, label_size, item_data
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.cleanup_old_print_jobs`
* **Artifact ID:** `ART-API-00130`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** 
* **Database References:** SMRITI Print Job
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.get_barcode_feature_flags`
* **Artifact ID:** `ART-API-00131`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** 
* **Database References:** DocType, SMRITI Barcode Settings
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.log_barcode_scan_event`
* **Artifact ID:** `ART-API-00132`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** event_uuid, template_id, barcode_family, printer_profile, scan_method, scan_attempts, scan_success, first_pass_success, store_id, pos_invoice, pos_invoice_item
* **Database References:** SMRITI Barcode Scan Event, Warehouse
* **Evidence Type:** `AST`

### `smriti_retail_os.barcode_api.aggregate_scan_telemetry`
* **Artifact ID:** `ART-API-00133`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/barcode_api.py`
* **Arguments:** period, target_date
* **Database References:** SMRITI Barcode Telemetry Snapshot
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.add_item_by_barcode`
* **Artifact ID:** `ART-API-00208`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** barcode, price_list
* **Database References:** Item, Item Barcode, Item Price
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.search_customer`
* **Artifact ID:** `ART-API-00209`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** query
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.hold_bill`
* **Artifact ID:** `ART-API-00210`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** cashier, customer, items, remarks, sales_staff
* **Database References:** Company, POS Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.recall_bill`
* **Artifact ID:** `ART-API-00211`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** cashier
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.submit_bill`
* **Artifact ID:** `ART-API-00212`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** cashier, customer, items, payments, loyalty_points, invoice_name, remarks, sales_staff, on_credit, tax_override, billing_address, shipping_address, billing_session_id
* **Database References:** Address, Company, Cost Center, Customer, Mode of Payment Account, POS Invoice, POS Opening Entry, Sales Invoice, Sales Taxes and Charges Template, Warehouse
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.search_items`
* **Artifact ID:** `ART-API-00213`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** query, price_list
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.load_held_invoice`
* **Artifact ID:** `ART-API-00214`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** invoice_name
* **Database References:** Item Price, POS Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.validate_manager_override`
* **Artifact ID:** `ART-API-00215`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** pin, action_type, invoice_name
* **Database References:** User
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.generate_mock_eway_bill`
* **Artifact ID:** `ART-API-00216`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** invoice_name, vehicle_no, distance, mode_of_transport, gst_vehicle_type, transporter_name
* **Database References:** Sales Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.create_return_invoice`
* **Artifact ID:** `ART-API-00217`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** invoice_name
* **Database References:** POS Invoice, Sales Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.create_custom_sales_return`
* **Artifact ID:** `ART-API-00218`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** customer, items, return_against_invoice, remarks, company, draft
* **Database References:** Company, Cost Center, Sales Invoice, Sales Taxes and Charges Template, Warehouse
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.update_sales_return`
* **Artifact ID:** `ART-API-00219`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** name, items, remarks, draft
* **Database References:** Company, Cost Center, Sales Invoice, Warehouse
* **Evidence Type:** `AST`

### `smriti_retail_os.billing_api.delete_sales_return`
* **Artifact ID:** `ART-API-00220`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/billing_api.py`
* **Arguments:** name, manager_pin
* **Database References:** Sales Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.boot.get_smriti_session_info`
* **Artifact ID:** `ART-API-00221`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/boot.py`
* **Arguments:** 
* **Database References:** User
* **Evidence Type:** `AST`

### `smriti_retail_os.boot.health_check`
* **Artifact ID:** `ART-API-00222`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/boot.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.branding_api.get_versions`
* **Artifact ID:** `ART-API-00223`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/branding_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.get_business_type`
* **Artifact ID:** `ART-API-00224`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** 
* **Database References:** Company, SMRITI Company Settings
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.list_companies`
* **Artifact ID:** `ART-API-00225`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** 
* **Database References:** Company
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.get_company_settings`
* **Artifact ID:** `ART-API-00226`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** company
* **Database References:** Company
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.save_company_settings`
* **Artifact ID:** `ART-API-00227`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** company, settings
* **Database References:** Company
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.get_store_address`
* **Artifact ID:** `ART-API-00228`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** company
* **Database References:** Address, Dynamic Link
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.save_store_address`
* **Artifact ID:** `ART-API-00229`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** company, address_data
* **Database References:** Address, Company, Dynamic Link
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.create_company`
* **Artifact ID:** `ART-API-00230`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** company_name, abbr, country, default_currency, gstin
* **Database References:** Company
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.update_company`
* **Artifact ID:** `ART-API-00231`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** company, company_name, gstin, default_currency
* **Database References:** Company
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.delete_company`
* **Artifact ID:** `ART-API-00232`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** company
* **Database References:** Company
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.get_item_attributes`
* **Artifact ID:** `ART-API-00233`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** company
* **Database References:** DocType, SMRITI Attribute Layout, SMRITI Custom Attribute
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.save_item_attributes`
* **Artifact ID:** `ART-API-00234`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** company, attributes
* **Database References:** SMRITI Attribute Layout, SMRITI Audit Event
* **Evidence Type:** `AST`

### `smriti_retail_os.company_api.reset_item_attributes`
* **Artifact ID:** `ART-API-00235`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/company_api.py`
* **Arguments:** company
* **Database References:** SMRITI Attribute Layout, SMRITI Audit Event
* **Evidence Type:** `AST`

### `smriti_retail_os.inventory_api.scan_item_for_inventory`
* **Artifact ID:** `ART-API-00236`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/inventory_api.py`
* **Arguments:** barcode, warehouse
* **Database References:** Company, Global Defaults, Item, Item Barcode
* **Evidence Type:** `AST`

### `smriti_retail_os.inventory_api.create_grn`
* **Artifact ID:** `ART-API-00237`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/inventory_api.py`
* **Arguments:** supplier, invoice_no, items, warehouse
* **Database References:** Company, Global Defaults, Item, Purchase Receipt
* **Evidence Type:** `AST`

### `smriti_retail_os.inventory_api.create_stock_transfer`
* **Artifact ID:** `ART-API-00238`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/inventory_api.py`
* **Arguments:** from_warehouse, to_warehouse, items
* **Database References:** Company, Item, Stock Entry
* **Evidence Type:** `AST`

### `smriti_retail_os.inventory_api.create_stock_adjustment`
* **Artifact ID:** `ART-API-00239`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/inventory_api.py`
* **Arguments:** items, reason
* **Database References:** Account, Company, Item, Stock Entry
* **Evidence Type:** `AST`

### `smriti_retail_os.inventory_api.create_stock_audit`
* **Artifact ID:** `ART-API-00240`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/inventory_api.py`
* **Arguments:** items
* **Database References:** Account, Company, Item, Stock Reconciliation
* **Evidence Type:** `AST`

### `smriti_retail_os.inventory_api.get_stock_summary`
* **Artifact ID:** `ART-API-00241`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/inventory_api.py`
* **Arguments:** warehouse
* **Database References:** Item
* **Evidence Type:** `AST`

### `smriti_retail_os.inventory_api.reset_db`
* **Artifact ID:** `ART-API-00242`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/inventory_api.py`
* **Arguments:** confirmation_token
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.get_import_column_defs`
* **Artifact ID:** `ART-API-00243`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.get_import_template_headers`
* **Artifact ID:** `ART-API-00244`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.get_hsn_gst_rate`
* **Artifact ID:** `ART-API-00245`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** hsn_code
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.validate_import_rows`
* **Artifact ID:** `ART-API-00246`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** rows_json
* **Database References:** Company
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.import_item_master`
* **Artifact ID:** `ART-API-00247`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** rows_json
* **Database References:** Company, Item, Item Barcode, Item Group
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.generate_ean13_barcode`
* **Artifact ID:** `ART-API-00248`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** 
* **Database References:** Item, Item Barcode
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.get_style_details`
* **Artifact ID:** `ART-API-00249`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** article_no
* **Database References:** Item, Item Barcode, Item Supplier, Item Variant Attribute
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.create_style_with_variants`
* **Artifact ID:** `ART-API-00250`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** base_details, sizes_config
* **Database References:** Company, Item, Item Barcode
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.delete_size_variant`
* **Artifact ID:** `ART-API-00251`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** variant_code
* **Database References:** Item
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.delete_style_and_variants`
* **Artifact ID:** `ART-API-00252`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** style_code
* **Database References:** Item
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.validate_pivot_values`
* **Artifact ID:** `ART-API-00253`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** styles_json
* **Database References:** DocType, Item Attribute
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.import_pivot_item_master`
* **Artifact ID:** `ART-API-00254`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** styles_json
* **Database References:** Company, Item, Item Barcode, Item Group
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.reset_all_transactions`
* **Artifact ID:** `ART-API-00255`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.reset_all_items`
* **Artifact ID:** `ART-API-00256`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.item_master_api.get_items_missing_barcodes`
* **Artifact ID:** `ART-API-00257`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/item_master_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.loyalty_api.get_loyalty_details`
* **Artifact ID:** `ART-API-00258`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/loyalty_api.py`
* **Arguments:** customer
* **Database References:** Customer
* **Evidence Type:** `AST`

### `smriti_retail_os.loyalty_api.get_loyalty_schemes`
* **Artifact ID:** `ART-API-00259`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/loyalty_api.py`
* **Arguments:** 
* **Database References:** Loyalty Program, Loyalty Program Collection
* **Evidence Type:** `AST`

### `smriti_retail_os.loyalty_api.save_loyalty_scheme`
* **Artifact ID:** `ART-API-00260`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/loyalty_api.py`
* **Arguments:** doc_name, loyalty_program_name, conversion_factor, auto_opt_in, min_spent, collection_factor, tier_name
* **Database References:** Account, Company, Cost Center, Loyalty Program
* **Evidence Type:** `AST`

### `smriti_retail_os.loyalty_api.enroll_customer`
* **Artifact ID:** `ART-API-00261`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/loyalty_api.py`
* **Arguments:** customer, program_name
* **Database References:** Customer, Loyalty Program
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.quick_create_item`
* **Artifact ID:** `ART-API-00262`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** item_name, barcode, rate, mrp, gst_percentage, style_code
* **Database References:** GST HSN Code, Item, Item Tax Template
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.quick_create_customer`
* **Artifact ID:** `ART-API-00263`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** customer_name, mobile_no
* **Database References:** Customer, Customer Group, Territory
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.quick_create_supplier`
* **Artifact ID:** `ART-API-00264`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** supplier_name, mobile_no
* **Database References:** Supplier, Supplier Group
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.save_supplier_on_fly`
* **Artifact ID:** `ART-API-00265`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** supplier_name, supplier_group, supplier_type, name
* **Database References:** Supplier, Supplier Group
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.get_customer_detail`
* **Artifact ID:** `ART-API-00266`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** name
* **Database References:** Customer
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.get_supplier_detail`
* **Artifact ID:** `ART-API-00267`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** name
* **Database References:** Contact, Dynamic Link, Supplier
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.save_supplier_detail`
* **Artifact ID:** `ART-API-00268`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** 
* **Database References:** Contact, Dynamic Link, Supplier, Supplier Group
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.save_customer_detail`
* **Artifact ID:** `ART-API-00269`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** customer_name, customer_type, customer_group, territory, mobile_no, email_id, tax_id, gst_category, pan, custom_address_text, custom_shipping_address_text, custom_tax_inclusive_override, name
* **Database References:** Customer, Customer Group, Territory
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.get_size_groups`
* **Artifact ID:** `ART-API-00270`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.save_size_groups`
* **Artifact ID:** `ART-API-00271`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** size_groups
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.get_destinationwise_taxes`
* **Artifact ID:** `ART-API-00272`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.save_destinationwise_taxes`
* **Artifact ID:** `ART-API-00273`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** mappings
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.get_item_tax_templates`
* **Artifact ID:** `ART-API-00274`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** 
* **Database References:** Item Tax Template, Item Tax Template Detail
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.create_item_tax_template`
* **Artifact ID:** `ART-API-00275`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** title, gst_rate, taxes
* **Database References:** Account, Item Tax Template
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.get_brands`
* **Artifact ID:** `ART-API-00276`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** 
* **Database References:** Brand
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.create_brand`
* **Artifact ID:** `ART-API-00277`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** brand_name, brand_description
* **Database References:** Brand
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.delete_brand`
* **Artifact ID:** `ART-API-00278`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** brand_name
* **Database References:** Brand
* **Evidence Type:** `AST`

### `smriti_retail_os.master_api.get_tax_accounts`
* **Artifact ID:** `ART-API-00279`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/master_api.py`
* **Arguments:** 
* **Database References:** Account
* **Evidence Type:** `AST`

### `smriti_retail_os.platform_api.get_system_health`
* **Artifact ID:** `ART-API-00280`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/platform_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.platform_api.get_backup_history`
* **Artifact ID:** `ART-API-00281`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/platform_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.platform_api.trigger_backup`
* **Artifact ID:** `ART-API-00282`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/platform_api.py`
* **Arguments:** backup_type
* **Evidence Type:** `AST`

### `smriti_retail_os.platform_api.run_migration_action`
* **Artifact ID:** `ART-API-00283`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/platform_api.py`
* **Arguments:** action
* **Evidence Type:** `AST`

### `smriti_retail_os.platform_api.get_diagnostics`
* **Artifact ID:** `ART-API-00284`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/platform_api.py`
* **Arguments:** log_type, limit
* **Evidence Type:** `AST`

### `smriti_retail_os.platform_api.run_repair`
* **Artifact ID:** `ART-API-00285`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/platform_api.py`
* **Arguments:** tool, dry_run
* **Database References:** Account, Company
* **Evidence Type:** `AST`

### `smriti_retail_os.platform_api.toggle_maintenance_mode`
* **Artifact ID:** `ART-API-00286`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/platform_api.py`
* **Arguments:** enable
* **Evidence Type:** `AST`

### `smriti_retail_os.platform_api.get_backup_summary`
* **Artifact ID:** `ART-API-00287`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/platform_api.py`
* **Arguments:** file_name
* **Evidence Type:** `AST`

### `smriti_retail_os.platform_api.execute_restore`
* **Artifact ID:** `ART-API-00288`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/platform_api.py`
* **Arguments:** file_name, confirm_text, password
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_analytics_service.get_redistribution_suggestions`
* **Artifact ID:** `ART-API-00289`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_analytics_service.py`
* **Arguments:** company
* **Database References:** PSV Channel Partner, SMRITI Party Stock Account
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_analytics_service.get_channel_health_score`
* **Artifact ID:** `ART-API-00290`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_analytics_service.py`
* **Arguments:** channel_partner, from_date, to_date
* **Database References:** PSV System Settings
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_analytics_service.get_sellin_sellout_summary`
* **Artifact ID:** `ART-API-00291`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_analytics_service.py`
* **Arguments:** company, channel_partner
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_analytics_service.get_stock_cover_risks`
* **Artifact ID:** `ART-API-00292`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_analytics_service.py`
* **Arguments:** company
* **Database References:** PSV Channel Partner, PSV Ledger Entry, SMRITI Party Stock Account
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_analytics_service.get_channel_stock_trend`
* **Artifact ID:** `ART-API-00293`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_analytics_service.py`
* **Arguments:** company
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_analytics_service.get_inventory_productivity_metrics`
* **Artifact ID:** `ART-API-00294`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_analytics_service.py`
* **Arguments:** company, timespan_days
* **Database References:** PSV Ledger Entry, PSV System Settings
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_analytics_service.get_inventory_productivity_methodology`
* **Artifact ID:** `ART-API-00295`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_analytics_service.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_api.get_dashboard_summary`
* **Artifact ID:** `ART-API-00296`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_api.py`
* **Arguments:** company
* **Database References:** PSV Ledger Entry
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_api.get_party_balance_detail`
* **Artifact ID:** `ART-API-00297`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_api.py`
* **Arguments:** company, party_stock_account
* **Database References:** PSV Ledger Entry
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_api.get_reorder_dashboard_data`
* **Artifact ID:** `ART-API-00298`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_api.py`
* **Arguments:** company
* **Database References:** PSV Channel Partner, PSV Ledger Entry, SMRITI Party Stock Account
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_api.create_psa`
* **Artifact ID:** `ART-API-00299`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_api.py`
* **Arguments:** company, customer, location_name, zone, region, area_manager, contact_person, mobile, email, active
* **Database References:** SMRITI Party Stock Account
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_api.update_psa`
* **Artifact ID:** `ART-API-00300`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_api.py`
* **Arguments:** name, zone, region, area_manager, contact_person, mobile, email, active
* **Database References:** SMRITI Party Stock Account
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_api.get_psa`
* **Artifact ID:** `ART-API-00301`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_api.py`
* **Arguments:** name
* **Database References:** SMRITI Party Stock Account
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_api.list_psas`
* **Artifact ID:** `ART-API-00302`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_api.py`
* **Arguments:** company, active
* **Database References:** SMRITI Party Stock Account
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_api.upload_sell_through`
* **Artifact ID:** `ART-API-00303`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_api.py`
* **Arguments:** upload_doc_name
* **Database References:** PSV Sell-Through Upload
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_api.fetch_channel_balance`
* **Artifact ID:** `ART-API-00304`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_api.py`
* **Arguments:** customer, item_code
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_api.get_psv_health`
* **Artifact ID:** `ART-API-00305`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_api.py`
* **Arguments:** 
* **Database References:** Delivery Note, DocType, SMRITI PSV Exception Record, Stock Entry
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_migration_service.create_reversal_entry`
* **Artifact ID:** `ART-API-00306`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_migration_service.py`
* **Arguments:** original_name, reason
* **Database References:** PSV Ledger Entry
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_migration_service.migrate_to_new_psv_partner`
* **Artifact ID:** `ART-API-00307`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_migration_service.py`
* **Arguments:** dry_run
* **Database References:** Company, Customer, Fiscal Year, PSV Channel Partner, PSV Ledger Entry, SMRITI Party Stock Account, SMRITI Party Stock Ledger Entry, Territory
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_service.process_opening_balance`
* **Artifact ID:** `ART-API-00308`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_service.py`
* **Arguments:** company, party_stock_account, items
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_snapshot_service.get_landing_cost`
* **Artifact ID:** `ART-API-00309`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_snapshot_service.py`
* **Arguments:** variant
* **Evidence Type:** `AST`

### `smriti_retail_os.psv_snapshot_service.generate_snapshots`
* **Artifact ID:** `ART-API-00310`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/psv_snapshot_service.py`
* **Arguments:** 
* **Database References:** Item, PSV Channel Partner, SMRITI Party Stock Account
* **Evidence Type:** `AST`

### `smriti_retail_os.purchase_api.get_open_purchase_orders`
* **Artifact ID:** `ART-API-00311`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/purchase_api.py`
* **Arguments:** supplier
* **Database References:** Purchase Order
* **Evidence Type:** `AST`

### `smriti_retail_os.purchase_api.get_po_details`
* **Artifact ID:** `ART-API-00312`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/purchase_api.py`
* **Arguments:** po_name
* **Database References:** Item, Purchase Order
* **Evidence Type:** `AST`

### `smriti_retail_os.purchase_api.create_purchase_order`
* **Artifact ID:** `ART-API-00313`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/purchase_api.py`
* **Arguments:** supplier, items, schedule_date, remarks, image_base64, image_filename, warehouse
* **Database References:** Company, GST HSN Code, Global Defaults, Item, Item Group, Item Price, Item Tax Template, Purchase Order
* **Evidence Type:** `AST`

### `smriti_retail_os.purchase_api.create_purchase_receipt`
* **Artifact ID:** `ART-API-00314`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/purchase_api.py`
* **Arguments:** supplier, items, po_name, warehouse
* **Database References:** Company, Global Defaults, Purchase Order, Purchase Receipt
* **Evidence Type:** `AST`

### `smriti_retail_os.purchase_api.create_purchase_return`
* **Artifact ID:** `ART-API-00315`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/purchase_api.py`
* **Arguments:** receipt_name
* **Database References:** Purchase Receipt
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_sales_report`
* **Artifact ID:** `ART-API-00316`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** from_date, to_date, granularity
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_stock_report`
* **Artifact ID:** `ART-API-00317`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** warehouse, item_group, show_zero
* **Database References:** Bin, Item
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_gst_report`
* **Artifact ID:** `ART-API-00318`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** from_date, to_date
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_outstanding_report`
* **Artifact ID:** `ART-API-00319`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** customer, days_overdue
* **Database References:** Sales Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_quick_stats`
* **Artifact ID:** `ART-API-00320`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_sales_return_register`
* **Artifact ID:** `ART-API-00321`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** from_date, to_date
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_purchase_return_register`
* **Artifact ID:** `ART-API-00322`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** from_date, to_date
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_gstr1_9b_report`
* **Artifact ID:** `ART-API-00323`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** from_date, to_date
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_deadline_alerts`
* **Artifact ID:** `ART-API-00324`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_smriti_report_data`
* **Artifact ID:** `ART-API-00325`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** report_key, filters
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.save_smriti_saved_view`
* **Artifact ID:** `ART-API-00326`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** view_name, report_key, applied_filters_json, visible_columns_json, is_default
* **Database References:** SMRITI Saved View
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_smriti_saved_views`
* **Artifact ID:** `ART-API-00327`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** report_key
* **Database References:** SMRITI Saved View
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.delete_smriti_saved_view`
* **Artifact ID:** `ART-API-00328`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** view_name
* **Database References:** SMRITI Saved View
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_smriti_reports_list`
* **Artifact ID:** `ART-API-00329`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** 
* **Database References:** SMRITI Report Template
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_smriti_warehouses`
* **Artifact ID:** `ART-API-00330`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** 
* **Database References:** Warehouse
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_smriti_item_groups`
* **Artifact ID:** `ART-API-00331`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** 
* **Database References:** Item Group
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_smriti_brands`
* **Artifact ID:** `ART-API-00332`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** 
* **Database References:** Brand
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_smriti_salespersons`
* **Artifact ID:** `ART-API-00333`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** 
* **Database References:** Sales Person
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_smriti_cashiers`
* **Artifact ID:** `ART-API-00334`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.export_smriti_report`
* **Artifact ID:** `ART-API-00335`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** report_key, filters, format_type
* **Evidence Type:** `AST`

### `smriti_retail_os.reports_api.get_report_glossary`
* **Artifact ID:** `ART-API-00336`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/reports_api.py`
* **Arguments:** report_key
* **Database References:** SMRITI Business Term, SMRITI Formula Definition, SMRITI Report Template
* **Evidence Type:** `AST`

### `smriti_retail_os.sales_order_api.get_open_sales_orders`
* **Artifact ID:** `ART-API-00337`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sales_order_api.py`
* **Arguments:** customer
* **Database References:** Sales Order
* **Evidence Type:** `AST`

### `smriti_retail_os.sales_order_api.get_so_details`
* **Artifact ID:** `ART-API-00338`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sales_order_api.py`
* **Arguments:** so_name
* **Database References:** Sales Order
* **Evidence Type:** `AST`

### `smriti_retail_os.sales_order_api.create_sales_order`
* **Artifact ID:** `ART-API-00339`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sales_order_api.py`
* **Arguments:** customer, items, delivery_date, remarks
* **Database References:** Company, Global Defaults, Item, Item Reorder, Sales Order, Warehouse
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.list_users`
* **Artifact ID:** `ART-API-00340`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** 
* **Database References:** Has Role, User
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.save_user`
* **Artifact ID:** `ART-API-00341`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** email, first_name, last_name, roles, role_profile
* **Database References:** User
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.set_user_status`
* **Artifact ID:** `ART-API-00342`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** email, enabled
* **Database References:** User
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.reset_user_password`
* **Artifact ID:** `ART-API-00343`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** email, password
* **Database References:** Role, User
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.set_user_pin`
* **Artifact ID:** `ART-API-00344`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** email, pin
* **Database References:** User
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.clear_user_pin`
* **Artifact ID:** `ART-API-00345`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** email
* **Database References:** User
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.get_user_metrics`
* **Artifact ID:** `ART-API-00346`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** 
* **Database References:** Has Role, User
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.list_roles`
* **Artifact ID:** `ART-API-00347`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** 
* **Database References:** Role
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.create_role`
* **Artifact ID:** `ART-API-00348`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** role_name
* **Database References:** Role
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.delete_role`
* **Artifact ID:** `ART-API-00349`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** role_name
* **Database References:** Role
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.list_role_profiles`
* **Artifact ID:** `ART-API-00350`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** 
* **Database References:** Has Role, Role Profile
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.save_role_profile`
* **Artifact ID:** `ART-API-00351`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** name, roles
* **Database References:** Role Profile
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.delete_role_profile`
* **Artifact ID:** `ART-API-00352`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** name
* **Database References:** Role Profile
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.list_user_permissions`
* **Artifact ID:** `ART-API-00353`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** user
* **Database References:** User, User Permission
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.add_user_permission`
* **Artifact ID:** `ART-API-00354`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** user, doctype, docname, is_default
* **Database References:** User
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.remove_user_permission`
* **Artifact ID:** `ART-API-00355`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** name
* **Database References:** User
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.list_workflows`
* **Artifact ID:** `ART-API-00356`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** 
* **Database References:** Workflow
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.get_workflow_details`
* **Artifact ID:** `ART-API-00357`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** workflow_name
* **Database References:** Workflow
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.save_workflow`
* **Artifact ID:** `ART-API-00358`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** name, document_type, is_active, states, transitions
* **Database References:** Workflow
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.delete_workflow`
* **Artifact ID:** `ART-API-00359`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** name
* **Database References:** Workflow
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.list_workflow_states`
* **Artifact ID:** `ART-API-00360`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** 
* **Database References:** Workflow State
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.save_workflow_state`
* **Artifact ID:** `ART-API-00361`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** name, style
* **Database References:** Workflow State
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.get_pending_approvals`
* **Artifact ID:** `ART-API-00362`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** 
* **Database References:** Workflow
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.apply_workflow_action`
* **Artifact ID:** `ART-API-00363`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** doctype, docname, action
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.verify_user_password`
* **Artifact ID:** `ART-API-00364`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** password
* **Evidence Type:** `AST`

### `smriti_retail_os.security_api.get_managers_list`
* **Artifact ID:** `ART-API-00365`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/security_api.py`
* **Arguments:** 
* **Database References:** User
* **Evidence Type:** `AST`

### `smriti_retail_os.setup_wizard_api.get_setup_wizard_initial_data`
* **Artifact ID:** `ART-API-00366`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/setup_wizard_api.py`
* **Arguments:** 
* **Database References:** Company, User
* **Evidence Type:** `AST`

### `smriti_retail_os.setup_wizard_api.run_setup_wizard`
* **Artifact ID:** `ART-API-00367`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/setup_wizard_api.py`
* **Arguments:** setup_data
* **Database References:** Account, Address, Company, Cost Center, Customer, Customer Group, Mode of Payment, POS Profile, SMRITI Company Settings, Sales Taxes and Charges Template, Territory, User, Warehouse, Warehouse Type
* **Evidence Type:** `AST`

### `smriti_retail_os.shift_api.open_shift`
* **Artifact ID:** `ART-API-00368`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/shift_api.py`
* **Arguments:** cashier, pos_profile, opening_entries
* **Database References:** Company, POS Opening Entry, POS Profile
* **Evidence Type:** `AST`

### `smriti_retail_os.shift_api.get_active_shift`
* **Artifact ID:** `ART-API-00369`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/shift_api.py`
* **Arguments:** cashier, pos_profile
* **Evidence Type:** `AST`

### `smriti_retail_os.shift_api.get_shift_summary`
* **Artifact ID:** `ART-API-00370`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/shift_api.py`
* **Arguments:** opening_entry_name
* **Database References:** POS Opening Entry
* **Evidence Type:** `AST`

### `smriti_retail_os.shift_api.close_shift`
* **Artifact ID:** `ART-API-00371`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/shift_api.py`
* **Arguments:** opening_entry_name, closing_entries, manager_pin, notes
* **Database References:** POS Closing Entry, POS Opening Entry, POS Settings
* **Evidence Type:** `AST`

### `smriti_retail_os.shift_api.get_pos_profiles`
* **Artifact ID:** `ART-API-00372`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/shift_api.py`
* **Arguments:** 
* **Database References:** POS Profile
* **Evidence Type:** `AST`

### `smriti_retail_os.shift_api.get_payment_modes`
* **Artifact ID:** `ART-API-00373`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/shift_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.shift_api.get_shift_status`
* **Artifact ID:** `ART-API-00374`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/shift_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.get_company_details`
* **Artifact ID:** `ART-API-00375`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** company
* **Database References:** Address, Bank Account, Company, Dynamic Link, Global Defaults
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.get_customer_details`
* **Artifact ID:** `ART-API-00376`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** customer
* **Database References:** Address, Customer, Dynamic Link
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.search_customers`
* **Artifact ID:** `ART-API-00377`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** query
* **Database References:** Customer
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.search_items`
* **Artifact ID:** `ART-API-00378`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** query
* **Database References:** Item
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.resolve_barcode`
* **Artifact ID:** `ART-API-00379`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** barcode
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.get_item_details_by_article`
* **Artifact ID:** `ART-API-00380`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** article, color
* **Database References:** Item
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.get_states_list`
* **Artifact ID:** `ART-API-00381`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.save_sizewise_invoice`
* **Artifact ID:** `ART-API-00382`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** payload
* **Database References:** Address, Company, SMRITI Party Stock Account, Sales Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.submit_sizewise_invoice`
* **Artifact ID:** `ART-API-00383`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** invoice_name
* **Database References:** Sales Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.get_sizewise_invoice`
* **Artifact ID:** `ART-API-00384`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** invoice_name
* **Database References:** Sales Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.list_sizewise_invoices`
* **Artifact ID:** `ART-API-00385`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** customer, limit
* **Database References:** Sales Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.cancel_sizewise_invoice`
* **Artifact ID:** `ART-API-00386`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** invoice_name
* **Database References:** Sales Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.get_admin_session_for_pdf`
* **Artifact ID:** `ART-API-00387`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.get_pdt_column_map`
* **Artifact ID:** `ART-API-00388`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** file_content, file_type
* **Evidence Type:** `AST`

### `smriti_retail_os.sizewise_invoice_api.preview_pdt_import`
* **Artifact ID:** `ART-API-00389`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sizewise_invoice_api.py`
* **Arguments:** file_content, file_type, mapping, price_type, supplier
* **Evidence Type:** `AST`

### `smriti_retail_os.transaction_kernel.execute_smriti_transaction`
* **Artifact ID:** `ART-API-00390`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/transaction_kernel.py`
* **Arguments:** doctype, payload, action
* **Evidence Type:** `AST`

### `smriti_retail_os.transaction_kernel.resolve_identifiers`
* **Artifact ID:** `ART-API-00391`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/transaction_kernel.py`
* **Arguments:** identifiers, company
* **Database References:** Item
* **Evidence Type:** `AST`

### `smriti_retail_os.transaction_kernel.apply_pricing_rules`
* **Artifact ID:** `ART-API-00392`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/transaction_kernel.py`
* **Arguments:** doctype, payload, company
* **Evidence Type:** `AST`

### `smriti_retail_os.transaction_kernel.get_doctype_schema`
* **Artifact ID:** `ART-API-00393`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/transaction_kernel.py`
* **Arguments:** doctype
* **Evidence Type:** `AST`

### `smriti_retail_os.api.analytics_api.get_dashboard_kpis`
* **Artifact ID:** `ART-API-00394`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/analytics_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.analytics_api.get_sales_trend`
* **Artifact ID:** `ART-API-00395`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/analytics_api.py`
* **Arguments:** days
* **Evidence Type:** `AST`

### `smriti_retail_os.api.analytics_api.get_payment_mix`
* **Artifact ID:** `ART-API-00396`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/analytics_api.py`
* **Arguments:** days
* **Evidence Type:** `AST`

### `smriti_retail_os.api.analytics_api.get_top_items`
* **Artifact ID:** `ART-API-00397`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/analytics_api.py`
* **Arguments:** days, limit
* **Evidence Type:** `AST`

### `smriti_retail_os.api.analytics_api.get_cashier_performance`
* **Artifact ID:** `ART-API-00398`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/analytics_api.py`
* **Arguments:** days
* **Evidence Type:** `AST`

### `smriti_retail_os.api.analytics_api.get_outstanding_aging`
* **Artifact ID:** `ART-API-00399`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/analytics_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.audit_log_api.get_security_events`
* **Artifact ID:** `ART-API-00400`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/audit_log_api.py`
* **Arguments:** page, page_size, operation_filter
* **Database References:** Activity Log
* **Evidence Type:** `AST`

### `smriti_retail_os.api.audit_log_api.get_event_detail`
* **Artifact ID:** `ART-API-00401`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/audit_log_api.py`
* **Arguments:** event_name
* **Database References:** Activity Log
* **Evidence Type:** `AST`

### `smriti_retail_os.api.audit_log_api.get_stats`
* **Artifact ID:** `ART-API-00402`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/audit_log_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.brand_api.get_brands`
* **Artifact ID:** `ART-API-00403`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/brand_api.py`
* **Arguments:** search_txt
* **Database References:** Brand
* **Evidence Type:** `AST`

### `smriti_retail_os.api.brand_api.create_brand`
* **Artifact ID:** `ART-API-00404`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/brand_api.py`
* **Arguments:** brand_name, description
* **Database References:** Brand
* **Evidence Type:** `AST`

### `smriti_retail_os.api.brand_api.update_brand`
* **Artifact ID:** `ART-API-00405`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/brand_api.py`
* **Arguments:** brand_name, description
* **Database References:** Brand
* **Evidence Type:** `AST`

### `smriti_retail_os.api.brand_api.delete_brand`
* **Artifact ID:** `ART-API-00406`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/brand_api.py`
* **Arguments:** brand_name
* **Database References:** Brand, Item
* **Evidence Type:** `AST`

### `smriti_retail_os.api.category_api.get_categories`
* **Artifact ID:** `ART-API-00407`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/category_api.py`
* **Arguments:** search_txt
* **Database References:** Item Group
* **Evidence Type:** `AST`

### `smriti_retail_os.api.category_api.create_category`
* **Artifact ID:** `ART-API-00408`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/category_api.py`
* **Arguments:** category_name, parent_category, is_group
* **Database References:** Item Group
* **Evidence Type:** `AST`

### `smriti_retail_os.api.category_api.update_category`
* **Artifact ID:** `ART-API-00409`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/category_api.py`
* **Arguments:** category_name, parent_category
* **Database References:** Item Group
* **Evidence Type:** `AST`

### `smriti_retail_os.api.category_api.delete_category`
* **Artifact ID:** `ART-API-00410`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/category_api.py`
* **Arguments:** category_name
* **Database References:** Item, Item Group
* **Evidence Type:** `AST`

### `smriti_retail_os.api.coming_soon_api.get_feature_info`
* **Artifact ID:** `ART-API-00411`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/coming_soon_api.py`
* **Arguments:** feature_key
* **Evidence Type:** `AST`

### `smriti_retail_os.api.coming_soon_api.get_all_coming_soon`
* **Artifact ID:** `ART-API-00412`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/coming_soon_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.dictionary_api.get_active_terms`
* **Artifact ID:** `ART-API-00413`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/dictionary_api.py`
* **Arguments:** category
* **Evidence Type:** `AST`

### `smriti_retail_os.api.dictionary_api.get_term_detail`
* **Artifact ID:** `ART-API-00414`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/dictionary_api.py`
* **Arguments:** term_id, version
* **Evidence Type:** `AST`

### `smriti_retail_os.api.explain_api.get_explain_payload`
* **Artifact ID:** `ART-API-00415`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/explain_api.py`
* **Arguments:** formula_id, version
* **Evidence Type:** `AST`

### `smriti_retail_os.api.formula_api.get_active_formulas`
* **Artifact ID:** `ART-API-00416`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/formula_api.py`
* **Arguments:** category
* **Evidence Type:** `AST`

### `smriti_retail_os.api.formula_api.get_formula_detail`
* **Artifact ID:** `ART-API-00417`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/formula_api.py`
* **Arguments:** formula_id, version
* **Evidence Type:** `AST`

### `smriti_retail_os.api.golive_api.get_checklist`
* **Artifact ID:** `ART-API-00418`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/golive_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.get_help_article`
* **Artifact ID:** `ART-API-00419`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** article_key
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.get_help_toc`
* **Artifact ID:** `ART-API-00420`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.search_knowledge`
* **Artifact ID:** `ART-API-00421`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** query
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.rebuild_index_cache`
* **Artifact ID:** `ART-API-00422`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.get_governance_data`
* **Artifact ID:** `ART-API-00423`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.get_document_registry`
* **Artifact ID:** `ART-API-00424`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.get_manual_html`
* **Artifact ID:** `ART-API-00425`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** volume_name
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.get_knowledge_assets`
* **Artifact ID:** `ART-API-00426`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** 
* **Database References:** SMRITI Business Term, SMRITI Formula Definition, SMRITI Related Formula, SMRITI Related Term
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.start_psv_exam`
* **Artifact ID:** `ART-API-00427`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** exam_id
* **Database References:** SMRITI Certification Exam, SMRITI PSV Exam Attempt
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.submit_psv_exam`
* **Artifact ID:** `ART-API-00428`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** attempt_id, answers_json
* **Database References:** SMRITI Certification Exam, SMRITI PSV Exam Attempt
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.get_psv_exam_status`
* **Artifact ID:** `ART-API-00429`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** exam_id
* **Database References:** SMRITI Certification Exam, SMRITI PSV Exam Attempt
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.get_certified_registry`
* **Artifact ID:** `ART-API-00430`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** 
* **Database References:** SMRITI Certification Exam, SMRITI PSV Exam Attempt, User
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.download_psv_certificate`
* **Artifact ID:** `ART-API-00431`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** attempt_id
* **Database References:** SMRITI Certification Exam, SMRITI PSV Exam Attempt, User
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.verify_psv_certificate`
* **Artifact ID:** `ART-API-00432`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** certificate_hash
* **Database References:** SMRITI Certification Exam, SMRITI PSV Exam Attempt, User
* **Evidence Type:** `AST`

### `smriti_retail_os.api.help_api.download_enablement_file`
* **Artifact ID:** `ART-API-00433`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/help_api.py`
* **Arguments:** file_key
* **Evidence Type:** `AST`

### `smriti_retail_os.api.knowledge_studio_api.query_ske`
* **Artifact ID:** `ART-API-00607`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/knowledge_studio_api.py`
* **Arguments:** query
* **Evidence Type:** `AST`

### `smriti_retail_os.api.knowledge_studio_api.get_knowledge_studio_counts`
* **Artifact ID:** `ART-API-00608`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/knowledge_studio_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.knowledge_studio_api.explain_screen_by_route`
* **Artifact ID:** `ART-API-00609`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/knowledge_studio_api.py`
* **Arguments:** route_path
* **Evidence Type:** `AST`

### `smriti_retail_os.api.knowledge_studio_api.get_ske_meta`
* **Artifact ID:** `ART-API-00610`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/knowledge_studio_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.license_api.get_license_status`
* **Artifact ID:** `ART-API-00434`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/license_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.license_api.activate_license`
* **Artifact ID:** `ART-API-00435`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/license_api.py`
* **Arguments:** license_key, organization_name, owner_name, registered_email, registered_mobile, license_type
* **Evidence Type:** `AST`

### `smriti_retail_os.api.license_api.sync_from_company`
* **Artifact ID:** `ART-API-00436`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/license_api.py`
* **Arguments:** 
* **Database References:** Company
* **Evidence Type:** `AST`

### `smriti_retail_os.api.license_api.get_feature_entitlements`
* **Artifact ID:** `ART-API-00437`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/license_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.license_api.get_activity_log`
* **Artifact ID:** `ART-API-00438`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/license_api.py`
* **Arguments:** limit
* **Evidence Type:** `AST`

### `smriti_retail_os.api.license_api.get_validation_history`
* **Artifact ID:** `ART-API-00439`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/license_api.py`
* **Arguments:** limit
* **Evidence Type:** `AST`

### `smriti_retail_os.api.license_api.check_feature_access`
* **Artifact ID:** `ART-API-00440`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/license_api.py`
* **Arguments:** feature_code
* **Evidence Type:** `AST`

### `smriti_retail_os.api.license_api.generate_test_key`
* **Artifact ID:** `ART-API-00441`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/license_api.py`
* **Arguments:** customer_id, tier, expiry_date, installation_id
* **Evidence Type:** `AST`

### `smriti_retail_os.api.payment_api.get_payments`
* **Artifact ID:** `ART-API-00442`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/payment_api.py`
* **Arguments:** payment_type, search, date_from, date_to, limit
* **Evidence Type:** `AST`

### `smriti_retail_os.api.payment_api.get_payment_detail`
* **Artifact ID:** `ART-API-00443`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/payment_api.py`
* **Arguments:** name
* **Database References:** Payment Entry
* **Evidence Type:** `AST`

### `smriti_retail_os.api.payment_api.create_payment`
* **Artifact ID:** `ART-API-00444`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/payment_api.py`
* **Arguments:** payment_type, party_type, party, amount, mode_of_payment, posting_date, reference_no, reference_date, remarks, allocate_to
* **Database References:** Company
* **Evidence Type:** `AST`

### `smriti_retail_os.api.payment_api.get_outstanding_invoices`
* **Artifact ID:** `ART-API-00445`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/payment_api.py`
* **Arguments:** party_type, party
* **Evidence Type:** `AST`

### `smriti_retail_os.api.payment_api.get_parties`
* **Artifact ID:** `ART-API-00446`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/payment_api.py`
* **Arguments:** party_type, search
* **Evidence Type:** `AST`

### `smriti_retail_os.api.payment_api.get_modes_of_payment`
* **Artifact ID:** `ART-API-00447`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/payment_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pdt_api.get_twin_status`
* **Artifact ID:** `ART-API-00448`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pdt_api.py`
* **Arguments:** party_stock_account, item_code
* **Database References:** SMRITI Party Stock Account, SMRITI SKU Twin
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pdt_api.trigger_rebuild`
* **Artifact ID:** `ART-API-00449`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pdt_api.py`
* **Arguments:** party_stock_account, item_code
* **Database References:** SMRITI Party Stock Account
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pdt_api.run_simulation`
* **Artifact ID:** `ART-API-00450`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pdt_api.py`
* **Arguments:** simulation_config
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pdt_api.get_pdt_dashboard_list`
* **Artifact ID:** `ART-API-00451`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pdt_api.py`
* **Arguments:** filters
* **Database References:** SMRITI Party Stock Account, SMRITI SKU Twin
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pos_profile_api.get_profiles`
* **Artifact ID:** `ART-API-00452`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pos_profile_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pos_profile_api.get_details`
* **Artifact ID:** `ART-API-00453`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pos_profile_api.py`
* **Arguments:** name
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pos_profile_api.save_profile`
* **Artifact ID:** `ART-API-00454`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pos_profile_api.py`
* **Arguments:** doc_data
* **Database References:** POS Profile
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pos_profile_api.clone_profile`
* **Artifact ID:** `ART-API-00455`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pos_profile_api.py`
* **Arguments:** source_name, target_name
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pos_profile_api.archive_profile`
* **Artifact ID:** `ART-API-00456`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pos_profile_api.py`
* **Arguments:** name
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pos_profile_api.get_dropdowns`
* **Artifact ID:** `ART-API-00457`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pos_profile_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.pos_profile_api.validate_profile`
* **Artifact ID:** `ART-API-00458`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/pos_profile_api.py`
* **Arguments:** name
* **Evidence Type:** `AST`

### `smriti_retail_os.api.scheme_api.get_schemes`
* **Artifact ID:** `ART-API-00459`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/scheme_api.py`
* **Arguments:** search_txt
* **Database References:** Pricing Rule
* **Evidence Type:** `AST`

### `smriti_retail_os.api.scheme_api.create_scheme`
* **Artifact ID:** `ART-API-00460`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/scheme_api.py`
* **Arguments:** title, apply_on, applied_to, discount_type, value, valid_from, valid_upto, company, min_qty, free_qty, same_item, free_item
* **Database References:** Company, Item
* **Evidence Type:** `AST`

### `smriti_retail_os.api.scheme_api.update_scheme`
* **Artifact ID:** `ART-API-00461`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/scheme_api.py`
* **Arguments:** name, title, apply_on, applied_to, discount_type, value, valid_from, valid_upto, min_qty, free_qty, same_item, free_item
* **Database References:** Item, Pricing Rule
* **Evidence Type:** `AST`

### `smriti_retail_os.api.scheme_api.delete_scheme`
* **Artifact ID:** `ART-API-00462`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/scheme_api.py`
* **Arguments:** name
* **Database References:** Pricing Rule
* **Evidence Type:** `AST`

### `smriti_retail_os.api.supplier_returns_api.get_submitted_receipts`
* **Artifact ID:** `ART-API-00463`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/supplier_returns_api.py`
* **Arguments:** query
* **Evidence Type:** `AST`

### `smriti_retail_os.api.supplier_returns_api.get_receipt_details`
* **Artifact ID:** `ART-API-00464`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/supplier_returns_api.py`
* **Arguments:** receipt_name
* **Database References:** Purchase Receipt
* **Evidence Type:** `AST`

### `smriti_retail_os.api.supplier_returns_api.submit_supplier_return`
* **Artifact ID:** `ART-API-00465`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/supplier_returns_api.py`
* **Arguments:** receipt_name, return_items, remarks, manager_pin
* **Database References:** Purchase Receipt
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.get_converted_leads`
* **Artifact ID:** `ART-API-00466`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** 
* **Database References:** SMRITI Trial Activation, SMRITI Trial Lead
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.create_activation`
* **Artifact ID:** `ART-API-00467`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** lead_name, activation_type, trial_days
* **Database References:** SMRITI Trial Activation, SMRITI Trial Lead
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.activate_account`
* **Artifact ID:** `ART-API-00468`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** activation_name, company_name, trial_days
* **Database References:** SMRITI Trial Activation
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.retry_provision`
* **Artifact ID:** `ART-API-00469`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** activation_name, company_name, trial_days
* **Database References:** SMRITI Trial Activation
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.suspend_activation`
* **Artifact ID:** `ART-API-00470`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** activation_name, reason
* **Database References:** SMRITI Trial Activation
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.extend_trial`
* **Artifact ID:** `ART-API-00471`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** activation_name, additional_days, reason
* **Database References:** SMRITI Trial Activation
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.mark_converted_to_paid`
* **Artifact ID:** `ART-API-00472`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** activation_name
* **Database References:** SMRITI Trial Activation
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.get_activations`
* **Artifact ID:** `ART-API-00473`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** status, limit
* **Database References:** SMRITI Trial Activation
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.get_provision_logs`
* **Artifact ID:** `ART-API-00474`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** activation_name, run_id
* **Database References:** SMRITI Provision Log
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.get_activation_dashboard`
* **Artifact ID:** `ART-API-00475`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.get_trial_health_snapshots`
* **Artifact ID:** `ART-API-00476`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** limit
* **Database References:** SMRITI Trial Health Snapshot
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_activation_api.trigger_trial_health_snapshot`
* **Artifact ID:** `ART-API-00477`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_activation_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_api.submit_trial_lead`
* **Artifact ID:** `ART-API-00478`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_api.py`
* **Arguments:** store_name, owner_name, mobile, city, business_type, plan, warehouses, monthly_sales, source
* **Database References:** SMRITI Trial Lead
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_api.get_trial_leads`
* **Artifact ID:** `ART-API-00479`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_api.py`
* **Arguments:** status, limit
* **Database References:** SMRITI Trial Lead
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_api.update_lead_status`
* **Artifact ID:** `ART-API-00480`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_api.py`
* **Arguments:** lead_name, new_status, notes
* **Database References:** SMRITI Trial Lead
* **Evidence Type:** `AST`

### `smriti_retail_os.api.trial_api.get_lead_counts`
* **Artifact ID:** `ART-API-00481`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/trial_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.api.__init__.get_item_stock`
* **Artifact ID:** `ART-API-00482`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/api/__init__.py`
* **Arguments:** item_code, warehouse
* **Database References:** Bin
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.validate_checkout_rules`
* **Artifact ID:** `ART-API-00483`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** invoice_data
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.get_offline_cache`
* **Artifact ID:** `ART-API-00484`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.get_wallet_ledger`
* **Artifact ID:** `ART-API-00485`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** customer, transaction_type, limit
* **Database References:** SMRITI Wallet Ledger
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.post_wallet_adjustment`
* **Artifact ID:** `ART-API-00486`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** customer, wallet_type, transaction_type, amount, remarks, adjustment_reason_type, company
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.reverse_wallet_transaction`
* **Artifact ID:** `ART-API-00487`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** ledger_seq, reason
* **Database References:** SMRITI Wallet Ledger
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.get_cge_liability_metrics`
* **Artifact ID:** `ART-API-00488`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** 
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.get_campaigns_with_utilization`
* **Artifact ID:** `ART-API-00489`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** 
* **Database References:** SMRITI Coupon Campaign
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.save_coupon_campaign`
* **Artifact ID:** `ART-API-00490`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** campaign_data
* **Database References:** SMRITI Coupon Campaign
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.save_loyalty_rule`
* **Artifact ID:** `ART-API-00491`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** rule_data
* **Database References:** SMRITI Loyalty Rule
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.save_loyalty_tier`
* **Artifact ID:** `ART-API-00492`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** tier_data
* **Database References:** SMRITI Loyalty Tier
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.get_cge_generic_fields`
* **Artifact ID:** `ART-API-00493`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** doctype
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.get_cge_generic_list`
* **Artifact ID:** `ART-API-00494`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** doctype, filters, limit
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.get_cge_generic_doc`
* **Artifact ID:** `ART-API-00495`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** doctype, name
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.save_cge_generic_doc`
* **Artifact ID:** `ART-API-00496`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** doctype, doc_data
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.api.cge_api.delete_cge_generic_doc`
* **Artifact ID:** `ART-API-00497`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/api/cge_api.py`
* **Arguments:** doctype, name
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.service.cge_service.validate_checkout_rules`
* **Artifact ID:** `ART-API-00498`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py`
* **Arguments:** invoice_data
* **Database References:** Company, Customer, Item, Loyalty Program Collection, Pricing Rule, SMRITI CGE Settings, SMRITI Coupon Campaign, Sales Invoice
* **Evidence Type:** `AST`

### `smriti_retail_os.cge.service.cge_service.get_offline_cache`
* **Artifact ID:** `ART-API-00499`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/cge/service/cge_service.py`
* **Arguments:** 
* **Database References:** SMRITI CGE Settings, SMRITI Coupon Campaign, SMRITI Loyalty Rule, SMRITI Loyalty Tier
* **Evidence Type:** `AST`

### `smriti_retail_os.clienteling.api.clienteling_api.get_customer_profile`
* **Artifact ID:** `ART-API-00500`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/clienteling/api/clienteling_api.py`
* **Arguments:** customer
* **Database References:** Customer, SMRITI Customer Intelligence Graph, SMRITI Customer Profile, SMRITI Formula Definition
* **Evidence Type:** `AST`

### `smriti_retail_os.clienteling.api.clienteling_api.log_customer_interaction`
* **Artifact ID:** `ART-API-00501`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/clienteling/api/clienteling_api.py`
* **Arguments:** customer, interaction_type, employee, interaction_outcome, store, channel, details
* **Database References:** SMRITI Customer Interaction
* **Evidence Type:** `AST`

### `smriti_retail_os.clienteling.api.clienteling_api.register_walk_in`
* **Artifact ID:** `ART-API-00502`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/clienteling/api/clienteling_api.py`
* **Arguments:** store, phone, customer, status
* **Evidence Type:** `AST`

### `smriti_retail_os.clienteling.api.clienteling_api.update_walk_in_visit`
* **Artifact ID:** `ART-API-00503`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/clienteling/api/clienteling_api.py`
* **Arguments:** visit_id, status, reason, invoice_type, invoice_id, duration
* **Evidence Type:** `AST`

### `smriti_retail_os.clienteling.api.clienteling_api.get_store_walk_in_analytics`
* **Artifact ID:** `ART-API-00504`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/clienteling/api/clienteling_api.py`
* **Arguments:** store, date
* **Database References:** SMRITI Walk In Analytics
* **Evidence Type:** `AST`

### `smriti_retail_os.clienteling.api.clienteling_api.log_explain_audit`
* **Artifact ID:** `ART-API-00505`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/clienteling/api/clienteling_api.py`
* **Arguments:** metric, customer, formula_id, session_id, source_screen
* **Database References:** SMRITI Explain Audit Event, SMRITI Formula Definition
* **Evidence Type:** `AST`

### `smriti_retail_os.services.formula_service.get_active_formulas`
* **Artifact ID:** `ART-API-00506`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/services/formula_service.py`
* **Arguments:** category
* **Database References:** SMRITI Formula Definition
* **Evidence Type:** `AST`

### `smriti_retail_os.services.formula_service.get_formula_detail`
* **Artifact ID:** `ART-API-00507`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/services/formula_service.py`
* **Arguments:** formula_id, version
* **Database References:** SMRITI Formula Definition
* **Evidence Type:** `AST`

### `smriti_retail_os.services.knowledge_service.get_asset_by_uri`
* **Artifact ID:** `ART-API-00508`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/services/knowledge_service.py`
* **Arguments:** uri
* **Database References:** SMRITI Knowledge Asset
* **Evidence Type:** `AST`

### `smriti_retail_os.services.knowledge_service.resolve_relations`
* **Artifact ID:** `ART-API-00509`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/services/knowledge_service.py`
* **Arguments:** asset_id, tenant_context, max_depth
* **Evidence Type:** `AST`

### `smriti_retail_os.services.knowledge_service.search_assets`
* **Artifact ID:** `ART-API-00510`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/services/knowledge_service.py`
* **Arguments:** query, asset_type
* **Database References:** SMRITI Knowledge Asset
* **Evidence Type:** `AST`

### `smriti_retail_os.sfm.api.sfc_api.run_monthly_calculation`
* **Artifact ID:** `ART-API-00511`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sfm/api/sfc_api.py`
* **Arguments:** company, fiscal_year, month
* **Evidence Type:** `AST`

### `smriti_retail_os.sfm.api.sfc_api.get_monthly_commissions`
* **Artifact ID:** `ART-API-00512`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sfm/api/sfc_api.py`
* **Arguments:** company, fiscal_year, month
* **Database References:** Employee, SMRITI Commission Settlement
* **Evidence Type:** `AST`

### `smriti_retail_os.sfm.api.sfm_api.get_sfm_leaderboard`
* **Artifact ID:** `ART-API-00513`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sfm/api/sfm_api.py`
* **Arguments:** company, fiscal_year, month, store
* **Database References:** Employee, SMRITI Sales KPI Snapshot
* **Evidence Type:** `AST`

### `smriti_retail_os.sfm.api.sfm_api.get_employee_summary`
* **Artifact ID:** `ART-API-00514`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sfm/api/sfm_api.py`
* **Arguments:** employee, fiscal_year, month, company
* **Database References:** Employee, SMRITI Sales KPI Snapshot
* **Evidence Type:** `AST`

### `smriti_retail_os.sfm.api.sfm_api.get_store_performance_center`
* **Artifact ID:** `ART-API-00515`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/sfm/api/sfm_api.py`
* **Arguments:** company, fiscal_year, month, store
* **Database References:** SMRITI Sales KPI Snapshot, SMRITI Sales Target
* **Evidence Type:** `AST`

### `smriti_retail_os.utils.opening_balance.parse_opening_excel`
* **Artifact ID:** `ART-API-00516`
* **Source Reference:** `apps/smriti_retail_os/smriti_retail_os/utils/opening_balance.py`
* **Arguments:** file_url
* **Database References:** File, Item
* **Evidence Type:** `AST`
