# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/setup.py
# @description: Application install, migrate, and patch hooks for SMRITI Retail OS.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_smriti_company_settings_doctype():
    """Creates the SMRITI Company Settings custom DocType for per-company retail configuration."""
    if frappe.db.exists("DocType", "SMRITI Company Settings"):
        dt = frappe.get_doc("DocType", "SMRITI Company Settings")
        existing_fields = [f.fieldname for f in dt.fields]
        changed = False
        new_fields = [
            {"fieldname": "default_printer_ip", "fieldtype": "Data", "label": "Default Printer IP"},
            {"fieldname": "default_printer_port", "fieldtype": "Int", "label": "Default Printer Port", "default": 9100},
            {"fieldname": "default_printer_lang", "fieldtype": "Select", "options": "ZPL\nTSPL", "label": "Default Printer Language", "default": "ZPL"},
            {"fieldname": "default_label_size", "fieldtype": "Select", "options": "50x25\n50x30\n75x50\n100x50\n106x55", "label": "Default Label Size", "default": "50x25"}
        ]
        for f in new_fields:
            if f["fieldname"] not in existing_fields:
                dt.append("fields", f)
                changed = True
        if changed:
            dt.save(ignore_permissions=True)
            frappe.db.commit()
            print("[SMRITI] Appended printer fields to existing SMRITI Company Settings DocType")
        return
    try:
        doc = frappe.new_doc("DocType")
        doc.name = "SMRITI Company Settings"
        doc.module = "SMRITI Retail OS"
        doc.custom = 1
        doc.autoname = "field:company"
        doc.editable_grid = 0
        doc.quick_entry = 0
        doc.track_changes = 1
        doc.issingle = 0

        fields = [
            {"fieldname": "company", "fieldtype": "Link", "options": "Company", "label": "Company", "reqd": 1, "unique": 1, "in_list_view": 1},
            {"fieldname": "sb_store", "fieldtype": "Section Break", "label": "Store Identity"},
            {"fieldname": "store_trade_name", "fieldtype": "Data", "label": "Store Trade Name", "in_list_view": 1},
            {"fieldname": "store_logo_url", "fieldtype": "Data", "label": "Store Logo URL"},
            {"fieldname": "cb_store", "fieldtype": "Column Break"},
            {"fieldname": "brand_color", "fieldtype": "Color", "label": "Brand Color", "default": "#1a73e8"},
            {"fieldname": "receipt_footer_text", "fieldtype": "Small Text", "label": "Receipt Footer Text", "default": "Thank you for shopping with us!"},
            {"fieldname": "invoice_series_prefix", "fieldtype": "Data", "label": "Invoice Series Prefix", "default": "SINV-"},
            {"fieldname": "sb_defaults", "fieldtype": "Section Break", "label": "Operational Defaults"},
            {"fieldname": "default_warehouse", "fieldtype": "Link", "options": "Warehouse", "label": "Default Warehouse"},
            {"fieldname": "default_pos_profile", "fieldtype": "Link", "options": "POS Profile", "label": "Default POS Profile"},
            {"fieldname": "cb_defaults", "fieldtype": "Column Break"},
            {"fieldname": "default_walk_in_customer", "fieldtype": "Link", "options": "Customer", "label": "Default Walk-in Customer"},
            {"fieldname": "default_intrastate_tax_template", "fieldtype": "Link", "options": "Sales Taxes and Charges Template", "label": "Default Intrastate Tax Template"},
            {"fieldname": "default_interstate_tax_template", "fieldtype": "Link", "options": "Sales Taxes and Charges Template", "label": "Default Interstate Tax Template"},
            {"fieldname": "sb_loyalty", "fieldtype": "Section Break", "label": "Loyalty Program"},
            {"fieldname": "loyalty_enabled", "fieldtype": "Check", "label": "Enable Loyalty Program", "default": "0"},
            {"fieldname": "loyalty_points_per_rupee", "fieldtype": "Float", "label": "Points per Rupee", "default": "1.0"},
            {"fieldname": "sb_cloud_backup", "fieldtype": "Section Break", "label": "Cloud Backup (S3/Rclone)"},
            {"fieldname": "cloud_backup_enabled", "fieldtype": "Check", "label": "Enable Cloud Backup", "default": "0"},
            {"fieldname": "cloud_provider", "fieldtype": "Select", "label": "Cloud Provider", "options": "\nAWS S3\nGoogle Cloud Storage\nAzure Blob\nDigitalOcean Spaces"},
            {"fieldname": "s3_bucket", "fieldtype": "Data", "label": "S3 Bucket Name"},
            {"fieldname": "cb_cloud", "fieldtype": "Column Break"},
            {"fieldname": "s3_access_key", "fieldtype": "Data", "label": "S3 Access Key"},
            {"fieldname": "s3_secret_key", "fieldtype": "Password", "label": "S3 Secret Key"},
            {"fieldname": "s3_region", "fieldtype": "Data", "label": "S3 Region", "default": "ap-south-1"},
            {"fieldname": "sb_advanced", "fieldtype": "Section Break", "label": "Advanced Configuration", "collapsible": 1},
            {"fieldname": "size_groups_json", "fieldtype": "Long Text", "label": "Size Groups JSON", "hidden": 1},
            {"fieldname": "destinationwise_taxes_json", "fieldtype": "Long Text", "label": "Destinationwise Taxes JSON", "hidden": 1},
            {"fieldname": "backup_settings_json", "fieldtype": "Long Text", "label": "Backup Settings JSON", "hidden": 1},
            {"fieldname": "sb_printer", "fieldtype": "Section Break", "label": "Printer Profile"},
            {"fieldname": "default_printer_ip", "fieldtype": "Data", "label": "Default Printer IP"},
            {"fieldname": "default_printer_port", "fieldtype": "Int", "label": "Default Printer Port", "default": 9100},
            {"fieldname": "cb_printer", "fieldtype": "Column Break"},
            {"fieldname": "default_printer_lang", "fieldtype": "Select", "options": "ZPL\nTSPL", "label": "Default Printer Language", "default": "ZPL"},
            {"fieldname": "default_label_size", "fieldtype": "Select", "options": "50x25\n50x30\n75x50\n100x50\n106x55", "label": "Default Label Size", "default": "50x25"}
        ]
        for f in fields:
            doc.append("fields", f)

        doc.append("permissions", {
            "role": "System Manager",
            "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
        })
        doc.append("permissions", {
            "role": "SMRITI Store Manager",
            "read": 1, "write": 1, "create": 1, "delete": 0, "share": 0
        })
        doc.append("permissions", {
            "role": "SMRITI Cashier",
            "read": 1, "write": 0, "create": 0, "delete": 0, "share": 0
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"[SMRITI] Created SMRITI Company Settings DocType")
    except Exception as e:
        frappe.log_error(f"Error creating SMRITI Company Settings DocType: {str(e)}")


def create_reporting_doctypes():
    """Creates the SMRITI Report Role child table, SMRITI Report Template parent table, and SMRITI Saved View parent table."""
    # 1. SMRITI Report Role (Child DocType)
    if not frappe.db.exists("DocType", "SMRITI Report Role"):
        try:
            doc = frappe.new_doc("DocType")
            doc.name = "SMRITI Report Role"
            doc.module = "SMRITI Retail OS"
            doc.custom = 1
            doc.istable = 1
            doc.autoname = "autoincrement"
            doc.editable_grid = 1
            
            fields = [
                {"fieldname": "role", "fieldtype": "Link", "options": "Role", "label": "Role", "reqd": 1, "in_list_view": 1}
            ]
            for f in fields:
                doc.append("fields", f)
            doc.insert(ignore_permissions=True)
            print("[SMRITI] Created SMRITI Report Role Child DocType")
        except Exception as e:
            frappe.log_error(f"Error creating SMRITI Report Role child doctype: {str(e)}")

    # 2. SMRITI Report Template
    if not frappe.db.exists("DocType", "SMRITI Report Template"):
        try:
            doc = frappe.new_doc("DocType")
            doc.name = "SMRITI Report Template"
            doc.module = "SMRITI Retail OS"
            doc.custom = 1
            doc.autoname = "field:report_key"
            doc.editable_grid = 0
            doc.quick_entry = 0
            doc.track_changes = 1
            doc.issingle = 0
            
            fields = [
                {"fieldname": "report_key", "fieldtype": "Data", "label": "Report Key", "reqd": 1, "unique": 1, "in_list_view": 1},
                {"fieldname": "report_name", "fieldtype": "Data", "label": "Report Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "report_category", "fieldtype": "Select", "label": "Report Category", "options": "Sales\nInventory Analytics\nCash\nPurchase\nFinance\nAnalytics\nAccounting\nCustom", "reqd": 1, "in_list_view": 1},
                {"fieldname": "source_doctype", "fieldtype": "Link", "options": "DocType", "label": "Source DocType"},
                {"fieldname": "columns_json", "fieldtype": "Long Text", "label": "Columns JSON"},
                {"fieldname": "filters_json", "fieldtype": "Long Text", "label": "Filters JSON"},
                {"fieldname": "group_by", "fieldtype": "Data", "label": "Group By"},
                {"fieldname": "order_by", "fieldtype": "Data", "label": "Order By"},
                {"fieldname": "branch_restricted", "fieldtype": "Check", "label": "Branch Restricted", "default": "0"},
                {"fieldname": "company_restricted", "fieldtype": "Check", "label": "Company Restricted", "default": "0"},
                {"fieldname": "cache_minutes", "fieldtype": "Int", "label": "Cache Minutes", "default": "0"},
                {"fieldname": "schema_version", "fieldtype": "Int", "label": "Schema Version", "default": "1"},
                {"fieldname": "layout_json", "fieldtype": "Long Text", "label": "Layout JSON", "hidden": 1},
                {"fieldname": "chart_json", "fieldtype": "Long Text", "label": "Chart JSON", "hidden": 1},
                {"fieldname": "pivot_json", "fieldtype": "Long Text", "label": "Pivot JSON", "hidden": 1},
                {"fieldname": "widget_json", "fieldtype": "Long Text", "label": "Widget JSON", "hidden": 1},
                {"fieldname": "is_public", "fieldtype": "Check", "label": "Is Public", "default": "1"},
                {"fieldname": "role_access", "fieldtype": "Table", "options": "SMRITI Report Role", "label": "Role Access"}
            ]
            for f in fields:
                doc.append("fields", f)
                
            doc.append("permissions", {
                "role": "System Manager",
                "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
            })
            doc.append("permissions", {
                "role": "SMRITI Store Manager",
                "read": 1, "write": 1, "create": 1, "delete": 0, "share": 1
            })
            doc.append("permissions", {
                "role": "SMRITI Cashier",
                "read": 1, "write": 0, "create": 0, "delete": 0, "share": 0
            })
            doc.insert(ignore_permissions=True)
            print("[SMRITI] Created SMRITI Report Template DocType")
        except Exception as e:
            frappe.log_error(f"Error creating SMRITI Report Template DocType: {str(e)}")
    else:
        try:
            dt = frappe.get_doc("DocType", "SMRITI Report Template")
            for f in dt.fields:
                if f.fieldname == "report_category":
                    options_list = [opt.strip() for opt in (f.options or "").split("\n") if opt.strip()]
                    if "Accounting" not in options_list or "Inventory Analytics" not in options_list:
                        # Rebuild with standard categories to match new definition
                        f.options = "Sales\nInventory Analytics\nCash\nPurchase\nFinance\nAnalytics\nAccounting\nCustom"
                        dt.save(ignore_permissions=True)
                        frappe.db.commit()
                        print("[SMRITI] Updated SMRITI Report Template report_category options")
                    break
        except Exception as e:
            frappe.log_error(f"Error updating SMRITI Report Template options: {str(e)}")

    # 3. SMRITI Saved View
    if not frappe.db.exists("DocType", "SMRITI Saved View"):
        try:
            doc = frappe.new_doc("DocType")
            doc.name = "SMRITI Saved View"
            doc.module = "SMRITI Retail OS"
            doc.custom = 1
            doc.autoname = "autoincrement"
            doc.editable_grid = 0
            doc.quick_entry = 0
            doc.track_changes = 1
            doc.issingle = 0
            
            fields = [
                {"fieldname": "view_name", "fieldtype": "Data", "label": "View Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "report_template", "fieldtype": "Link", "options": "SMRITI Report Template", "label": "Report Template", "reqd": 1, "in_list_view": 1},
                {"fieldname": "user", "fieldtype": "Link", "options": "User", "label": "User", "reqd": 1, "in_list_view": 1},
                {"fieldname": "applied_filters_json", "fieldtype": "Long Text", "label": "Applied Filters JSON"},
                {"fieldname": "visible_columns_json", "fieldtype": "Long Text", "label": "Visible Columns JSON"},
                {"fieldname": "is_default", "fieldtype": "Check", "label": "Is Default", "default": "0"}
            ]
            for f in fields:
                doc.append("fields", f)
                
            doc.append("permissions", {
                "role": "System Manager",
                "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
            })
            doc.append("permissions", {
                "role": "SMRITI Store Manager",
                "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
            })
            doc.append("permissions", {
                "role": "SMRITI Cashier",
                "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
            })
            doc.insert(ignore_permissions=True)
            print("[SMRITI] Created SMRITI Saved View DocType")
        except Exception as e:
            frappe.log_error(f"Error creating SMRITI Saved View DocType: {str(e)}")


def seed_report_templates():
    """Seeds the standard SMRITI Report Template records."""
    import json
    
    reports = [
        {
            "report_key": "item_wise_sales",
            "report_name": "SMRITI Item-wise Sales Analytics",
            "report_category": "Sales",
            "source_doctype": "POS Invoice",
            "group_by": "items.item_code",
            "order_by": "qty_sold DESC",
            "company_restricted": 1,
            "branch_restricted": 1,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager", "SMRITI Cashier"],
            "columns": [
                {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Link", "options": "Item", "width": 120},
                {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 180},
                {"fieldname": "item_group", "label": "Item Group", "fieldtype": "Link", "options": "Item Group", "width": 120},
                {"fieldname": "brand", "label": "Brand", "fieldtype": "Link", "options": "Brand", "width": 100},
                {"fieldname": "qty_sold", "label": "Qty Sold", "fieldtype": "Float", "width": 100},
                {"fieldname": "taxable_amount", "label": "Taxable Amount", "fieldtype": "Currency", "width": 120},
                {"fieldname": "gross_amount", "label": "Gross Amount", "fieldtype": "Currency", "width": 120}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse"},
                {"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
                {"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"},
                {"fieldname": "item_group", "label": "Item Group", "fieldtype": "Link", "options": "Item Group"},
                {"fieldname": "brand", "label": "Brand", "fieldtype": "Link", "options": "Brand"},
                {"fieldname": "style", "label": "Style / Article", "fieldtype": "Data"},
                {"fieldname": "size", "label": "Size", "fieldtype": "Data"},
                {"fieldname": "color", "label": "Color", "fieldtype": "Data"},
                {"fieldname": "salesperson", "label": "Salesperson", "fieldtype": "Link", "options": "Sales Person"}
            ]
        },
        {
            "report_key": "daily_sales_summary",
            "report_name": "SMRITI Daily Sales Summary",
            "report_category": "Sales",
            "source_doctype": "POS Invoice",
            "group_by": "parent.posting_date",
            "order_by": "parent.posting_date ASC",
            "company_restricted": 1,
            "branch_restricted": 1,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager", "SMRITI Cashier"],
            "columns": [
                {"fieldname": "posting_date", "label": "Date", "fieldtype": "Date", "width": 120},
                {"fieldname": "bills_count", "label": "Bills Count", "fieldtype": "Int", "width": 100},
                {"fieldname": "qty_sold", "label": "Qty Sold", "fieldtype": "Float", "width": 100},
                {"fieldname": "taxable_amount", "label": "Taxable Amount", "fieldtype": "Currency", "width": 120},
                {"fieldname": "tax_amount", "label": "Tax Amount", "fieldtype": "Currency", "width": 120},
                {"fieldname": "discount_amount", "label": "Discount Amount", "fieldtype": "Currency", "width": 120},
                {"fieldname": "grand_total", "label": "Grand Total", "fieldtype": "Currency", "width": 120}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse"},
                {"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
                {"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"}
            ]
        },
        {
            "report_key": "cash_z_report",
            "report_name": "SMRITI Cash Z-Report",
            "report_category": "Cash",
            "source_doctype": "POS Invoice",
            "group_by": "",
            "order_by": "",
            "company_restricted": 1,
            "branch_restricted": 1,
            "cache_minutes": 0,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager", "SMRITI Cashier"],
            "columns": [
                {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 110},
                {"fieldname": "cashier", "label": "Cashier", "fieldtype": "Data", "width": 120},
                {"fieldname": "opening_cash", "label": "Opening Cash", "fieldtype": "Currency", "width": 110},
                {"fieldname": "total_bills", "label": "Total Bills", "fieldtype": "Int", "width": 90},
                {"fieldname": "total_sales", "label": "Total Sales", "fieldtype": "Currency", "width": 110},
                {"fieldname": "total_net", "label": "Total Net", "fieldtype": "Currency", "width": 110},
                {"fieldname": "total_tax", "label": "Total Tax", "fieldtype": "Currency", "width": 100},
                {"fieldname": "total_discount", "label": "Total Discount", "fieldtype": "Currency", "width": 110},
                {"fieldname": "total_refunds", "label": "Total Refunds", "fieldtype": "Currency", "width": 110},
                {"fieldname": "expected_cash_in_drawer", "label": "Expected Cash in Drawer", "fieldtype": "Currency", "width": 140},
                {"fieldname": "payment_modes", "label": "Payment Breakdown", "fieldtype": "Data", "width": 250}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "from_date", "label": "Date", "fieldtype": "Date", "reqd": 1},
                {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse"},
                {"fieldname": "cashier", "label": "Cashier / User", "fieldtype": "Link", "options": "User"}
            ]
        },
        {
            "report_key": "cash_reconciliation",
            "report_name": "SMRITI Cash Reconciliation Report",
            "report_category": "Cash",
            "source_doctype": "POS Closing Entry",
            "group_by": "",
            "order_by": "ce.posting_date DESC",
            "company_restricted": 1,
            "branch_restricted": 1,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "closing_id", "label": "Closing Entry", "fieldtype": "Link", "options": "POS Closing Entry", "width": 130},
                {"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "width": 110},
                {"fieldname": "cashier", "label": "Cashier", "fieldtype": "Link", "options": "User", "width": 120},
                {"fieldname": "pos_profile", "label": "POS Profile", "fieldtype": "Link", "options": "POS Profile", "width": 120},
                {"fieldname": "mode_of_payment", "label": "Mode of Payment", "fieldtype": "Data", "width": 120},
                {"fieldname": "expected_amount", "label": "Expected", "fieldtype": "Currency", "width": 110},
                {"fieldname": "declared_amount", "label": "Declared", "fieldtype": "Currency", "width": 110},
                {"fieldname": "difference", "label": "Difference", "fieldtype": "Currency", "width": 110}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
                {"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"}
            ]
        },
        {
            "report_key": "current_stock_position",
            "report_name": "SMRITI Current Stock Position",
            "report_category": "Inventory Analytics",
            "source_doctype": "Bin",
            "group_by": "",
            "order_by": "b.item_code ASC",
            "company_restricted": 1,
            "branch_restricted": 1,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Link", "options": "Item", "width": 120},
                {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 180},
                {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 120},
                {"fieldname": "actual_qty", "label": "Actual Qty", "fieldtype": "Float", "width": 100},
                {"fieldname": "valuation_rate", "label": "Valuation Rate", "fieldtype": "Currency", "width": 110},
                {"fieldname": "stock_value", "label": "Stock Value", "fieldtype": "Currency", "width": 110},
                {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse"},
                {"fieldname": "item_group", "label": "Item Group", "fieldtype": "Link", "options": "Item Group"},
                {"fieldname": "brand", "label": "Brand", "fieldtype": "Link", "options": "Brand"},
                {"fieldname": "style", "label": "Style / Article", "fieldtype": "Data"},
                {"fieldname": "size", "label": "Size", "fieldtype": "Data"},
                {"fieldname": "color", "label": "Color", "fieldtype": "Data"}
            ]
        },
        {
            "report_key": "style_wise_stock",
            "report_name": "SMRITI Style-wise Stock Position",
            "report_category": "Inventory Analytics",
            "source_doctype": "Bin",
            "group_by": "style_code",
            "order_by": "actual_qty DESC",
            "company_restricted": 1,
            "branch_restricted": 1,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "style_code", "label": "Style / Article Code", "fieldtype": "Data", "width": 130},
                {"fieldname": "style_name", "label": "Style / Article Name", "fieldtype": "Data", "width": 180},
                {"fieldname": "actual_qty", "label": "Actual Qty", "fieldtype": "Float", "width": 100},
                {"fieldname": "stock_value", "label": "Stock Value", "fieldtype": "Currency", "width": 110}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse"},
                {"fieldname": "item_group", "label": "Item Group", "fieldtype": "Link", "options": "Item Group"},
                {"fieldname": "brand", "label": "Brand", "fieldtype": "Link", "options": "Brand"},
                {"fieldname": "style", "label": "Style / Article", "fieldtype": "Data"}
            ]
        },
        {
            "report_key": "size_wise_stock",
            "report_name": "SMRITI Variant Stock Position",
            "report_category": "Inventory Analytics",
            "source_doctype": "Bin",
            "group_by": "style_code, color, size, b.warehouse",
            "order_by": "style_code ASC",
            "company_restricted": 1,
            "branch_restricted": 1,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "style_code", "label": "Style / Article Code", "fieldtype": "Data", "width": 130},
                {"fieldname": "style_name", "label": "Style / Article Name", "fieldtype": "Data", "width": 180},
                {"fieldname": "color", "label": "Color", "fieldtype": "Data", "width": 100},
                {"fieldname": "size", "label": "Size", "fieldtype": "Data", "width": 80},
                {"fieldname": "actual_qty", "label": "Actual Qty", "fieldtype": "Float", "width": 100},
                {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 120}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse"},
                {"fieldname": "item_group", "label": "Item Group", "fieldtype": "Link", "options": "Item Group"},
                {"fieldname": "brand", "label": "Brand", "fieldtype": "Link", "options": "Brand"},
                {"fieldname": "style", "label": "Style / Article", "fieldtype": "Data"},
                {"fieldname": "size", "label": "Size", "fieldtype": "Data"},
                {"fieldname": "color", "label": "Color", "fieldtype": "Data"}
            ]
        },
        {
            "report_key": "payment_mode_summary",
            "report_name": "SMRITI Payment Mode Summary",
            "report_category": "Cash",
            "source_doctype": "POS Invoice",
            "group_by": "p.mode_of_payment",
            "order_by": "total_amount DESC",
            "company_restricted": 1,
            "branch_restricted": 1,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager", "SMRITI Cashier"],
            "columns": [
                {"fieldname": "mode_of_payment", "label": "Mode of Payment", "fieldtype": "Data", "width": 150},
                {"fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Currency", "width": 150}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse"},
                {"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
                {"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"}
            ]
        }
    ]
    
    reports.extend([
        {
            "report_key": "payment_register",
            "report_name": "SMRITI Payment Register",
            "report_category": "Accounting",
            "source_doctype": "Payment Entry",
            "group_by": "",
            "order_by": "posting_date DESC",
            "company_restricted": 1,
            "branch_restricted": 0,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "width": 110},
                {"fieldname": "payment_entry_no", "label": "Payment Entry No", "fieldtype": "Link", "options": "Payment Entry", "width": 140},
                {"fieldname": "party_type", "label": "Party Type", "fieldtype": "Data", "width": 100},
                {"fieldname": "party", "label": "Party Name", "fieldtype": "Data", "width": 150},
                {"fieldname": "payment_type", "label": "Payment Type", "fieldtype": "Data", "width": 110},
                {"fieldname": "mode_of_payment", "label": "Mode of Payment", "fieldtype": "Data", "width": 120},
                {"fieldname": "paid_amount", "label": "Paid Amount", "fieldtype": "Currency", "width": 120},
                {"fieldname": "reference_no", "label": "Reference Number", "fieldtype": "Data", "width": 120},
                {"fieldname": "remarks", "label": "Remarks", "fieldtype": "Data", "width": 200}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
                {"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"},
                {"fieldname": "party", "label": "Party Name", "fieldtype": "Data"},
                {"fieldname": "payment_mode", "label": "Payment Mode", "fieldtype": "Data"}
            ]
        },
        {
            "report_key": "receipt_register",
            "report_name": "SMRITI Receipt Register",
            "report_category": "Accounting",
            "source_doctype": "Payment Entry",
            "group_by": "",
            "order_by": "pe.posting_date DESC",
            "company_restricted": 1,
            "branch_restricted": 0,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "width": 110},
                {"fieldname": "receipt_no", "label": "Receipt No", "fieldtype": "Link", "options": "Payment Entry", "width": 140},
                {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 150},
                {"fieldname": "against_invoice", "label": "Against Invoice", "fieldtype": "Data", "width": 140},
                {"fieldname": "mode_of_payment", "label": "Mode of Payment", "fieldtype": "Data", "width": 120},
                {"fieldname": "amount_received", "label": "Amount Received", "fieldtype": "Currency", "width": 120},
                {"fieldname": "reference_number", "label": "Reference Number", "fieldtype": "Data", "width": 120}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
                {"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"},
                {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer"},
                {"fieldname": "payment_mode", "label": "Payment Mode", "fieldtype": "Data"}
            ]
        },
        {
            "report_key": "cash_book",
            "report_name": "SMRITI Cash Book",
            "report_category": "Accounting",
            "source_doctype": "GL Entry",
            "group_by": "",
            "order_by": "",
            "company_restricted": 1,
            "branch_restricted": 0,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 110},
                {"fieldname": "opening_balance", "label": "Opening Balance", "fieldtype": "Currency", "width": 130},
                {"fieldname": "cash_receipts", "label": "Cash Receipts", "fieldtype": "Currency", "width": 130},
                {"fieldname": "cash_payments", "label": "Cash Payments", "fieldtype": "Currency", "width": 130},
                {"fieldname": "closing_balance", "label": "Closing Balance", "fieldtype": "Currency", "width": 130}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
                {"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"}
            ]
        },
        {
            "report_key": "day_book",
            "report_name": "SMRITI Day Book",
            "report_category": "Accounting",
            "source_doctype": "GL Entry",
            "group_by": "",
            "order_by": "",
            "company_restricted": 1,
            "branch_restricted": 0,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 110},
                {"fieldname": "sales", "label": "Sales", "fieldtype": "Currency", "width": 120},
                {"fieldname": "sales_returns", "label": "Sales Returns", "fieldtype": "Currency", "width": 120},
                {"fieldname": "purchases", "label": "Purchases", "fieldtype": "Currency", "width": 120},
                {"fieldname": "purchase_returns", "label": "Purchase Returns", "fieldtype": "Currency", "width": 120},
                {"fieldname": "receipts", "label": "Receipts", "fieldtype": "Currency", "width": 120},
                {"fieldname": "payments", "label": "Payments", "fieldtype": "Currency", "width": 120},
                {"fieldname": "net_cash_position", "label": "Net Cash Position", "fieldtype": "Currency", "width": 140}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
                {"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"}
            ]
        },
        {
            "report_key": "customer_outstanding",
            "report_name": "SMRITI Customer Outstanding Book",
            "report_category": "Accounting",
            "source_doctype": "Sales Invoice",
            "group_by": "",
            "order_by": "posting_date ASC",
            "company_restricted": 1,
            "branch_restricted": 0,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 180},
                {"fieldname": "invoice", "label": "Invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 140},
                {"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "width": 110},
                {"fieldname": "due_date", "label": "Due Date", "fieldtype": "Date", "width": 110},
                {"fieldname": "outstanding_amount", "label": "Outstanding Amount", "fieldtype": "Currency", "width": 140},
                {"fieldname": "ageing_days", "label": "Ageing Days", "fieldtype": "Int", "width": 100}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer"},
                {"fieldname": "ageing_bucket", "label": "Ageing Bucket", "fieldtype": "Select", "options": "\n1-30\n31-60\n61-90\n90+"}
            ]
        },
        {
            "report_key": "supplier_outstanding",
            "report_name": "SMRITI Supplier Outstanding Book",
            "report_category": "Accounting",
            "source_doctype": "Purchase Invoice",
            "group_by": "",
            "order_by": "posting_date ASC",
            "company_restricted": 1,
            "branch_restricted": 0,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "supplier", "label": "Supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
                {"fieldname": "invoice", "label": "Invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 140},
                {"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "width": 110},
                {"fieldname": "due_date", "label": "Due Date", "fieldtype": "Date", "width": 110},
                {"fieldname": "outstanding_amount", "label": "Outstanding Amount", "fieldtype": "Currency", "width": 140},
                {"fieldname": "ageing_days", "label": "Ageing Days", "fieldtype": "Int", "width": 100}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "supplier", "label": "Supplier", "fieldtype": "Link", "options": "Supplier"},
                {"fieldname": "ageing_bucket", "label": "Ageing Bucket", "fieldtype": "Select", "options": "\n1-30\n31-60\n61-90\n90+"}
            ]
        },
        {
            "report_key": "psv_reorder_report",
            "report_name": "SMRITI PSV Reorder Report",
            "report_category": "Inventory Analytics",
            "source_doctype": "SMRITI Party Stock Account",
            "group_by": "",
            "order_by": "",
            "company_restricted": 1,
            "branch_restricted": 0,
            "cache_minutes": 0,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "location", "label": "Location", "fieldtype": "Link", "options": "SMRITI Party Stock Account", "width": 180},
                {"fieldname": "zone", "label": "Zone", "fieldtype": "Data", "width": 100},
                {"fieldname": "item_code", "label": "Item Variant", "fieldtype": "Link", "options": "Item", "width": 150},
                {"fieldname": "current_balance", "label": "Current Balance", "fieldtype": "Float", "width": 120},
                {"fieldname": "weekly_sale_avg", "label": "Weekly Sale Avg", "fieldtype": "Float", "width": 120},
                {"fieldname": "days_cover", "label": "Days Cover", "fieldtype": "Float", "width": 100},
                {"fieldname": "reorder_level", "label": "Reorder Level", "fieldtype": "Float", "width": 120},
                {"fieldname": "recommended_qty", "label": "Recommended Qty", "fieldtype": "Float", "width": 130},
                {"fieldname": "priority", "label": "Priority", "fieldtype": "Data", "width": 100}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "zone", "label": "Zone", "fieldtype": "Select", "options": "\nNorth\nSouth\nEast\nWest\nCentral"},
                {"fieldname": "priority", "label": "Priority", "fieldtype": "Select", "options": "\nCritical\nHigh\nMedium\nLow"},
                {"fieldname": "show_zero", "label": "Show Zero Recommendations", "fieldtype": "Check"}
            ]
        },
        {
            "report_key": "inventory_productivity",
            "report_name": "SMRITI Inventory Productivity & SKU Rationalization",
            "report_category": "Inventory Analytics",
            "source_doctype": "Bin",
            "group_by": "",
            "order_by": "score DESC",
            "company_restricted": 1,
            "branch_restricted": 0,
            "cache_minutes": 5,
            "schema_version": 1,
            "is_public": 1,
            "roles": ["System Manager", "SMRITI Store Manager"],
            "columns": [
                {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Link", "options": "Item", "width": 120},
                {"fieldname": "sales_qty", "label": "Sales Qty", "fieldtype": "Float", "width": 100},
                {"fieldname": "velocity", "label": "Weekly Velocity", "fieldtype": "Float", "width": 120},
                {"fieldname": "cost", "label": "Landing Cost", "fieldtype": "Currency", "width": 110},
                {"fieldname": "price", "label": "Avg Realized Price", "fieldtype": "Currency", "width": 130},
                {"fieldname": "gross_margin", "label": "Gross Margin", "fieldtype": "Currency", "width": 120},
                {"fieldname": "inventory_value", "label": "Inventory Value", "fieldtype": "Currency", "width": 120},
                {"fieldname": "gmroi", "label": "GMROI", "fieldtype": "Float", "width": 100},
                {"fieldname": "category", "label": "Category", "fieldtype": "Data", "width": 120},
                {"fieldname": "score", "label": "Productivity Score", "fieldtype": "Float", "width": 120},
                {"fieldname": "action", "label": "Action Recommendation", "fieldtype": "Data", "width": 150}
            ],
            "filters": [
                {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "reqd": 1},
                {"fieldname": "timespan_days", "label": "Timespan (Days)", "fieldtype": "Int"}
            ]
        }
    ])
    
    for r in reports:
        key = r["report_key"]
        
        # Check if exists
        if frappe.db.exists("SMRITI Report Template", key):
            doc = frappe.get_doc("SMRITI Report Template", key)
            doc.report_name = r["report_name"]
            doc.report_category = r["report_category"]
            doc.source_doctype = r["source_doctype"]
            doc.columns_json = json.dumps(r["columns"])
            doc.filters_json = json.dumps(r["filters"])
            doc.group_by = r["group_by"]
            doc.order_by = r["order_by"]
            doc.company_restricted = r["company_restricted"]
            doc.branch_restricted = r["branch_restricted"]
            doc.cache_minutes = r["cache_minutes"]
            doc.schema_version = r["schema_version"]
            doc.is_public = r["is_public"]
            
            # Reset role_access child table
            doc.set("role_access", [])
            for role in r["roles"]:
                doc.append("role_access", {"role": role})
                
            doc.save(ignore_permissions=True)
            print(f"[SMRITI] Updated SMRITI Report Template: {key}")
        else:
            doc = frappe.new_doc("SMRITI Report Template")
            doc.report_key = key
            doc.report_name = r["report_name"]
            doc.report_category = r["report_category"]
            doc.source_doctype = r["source_doctype"]
            doc.columns_json = json.dumps(r["columns"])
            doc.filters_json = json.dumps(r["filters"])
            doc.group_by = r["group_by"]
            doc.order_by = r["order_by"]
            doc.company_restricted = r["company_restricted"]
            doc.branch_restricted = r["branch_restricted"]
            doc.cache_minutes = r["cache_minutes"]
            doc.schema_version = r["schema_version"]
            doc.is_public = r["is_public"]
            
            for role in r["roles"]:
                doc.append("role_access", {"role": role})
                
            doc.insert(ignore_permissions=True)
            print(f"[SMRITI] Created SMRITI Report Template: {key}")
            
    frappe.db.commit()


def create_audit_log_doctype():
    """Creates the SMRITI Address Audit Log custom DocType for store address change tracking."""
    if frappe.db.exists("DocType", "SMRITI Address Audit Log"):
        return
    try:
        doc = frappe.new_doc("DocType")
        doc.name = "SMRITI Address Audit Log"
        doc.module = "SMRITI Retail OS"
        doc.custom = 1
        doc.autoname = "autoincrement"
        doc.editable_grid = 0
        doc.quick_entry = 0
        doc.track_changes = 0
        doc.issingle = 0

        fields = [
            {"fieldname": "changed_by", "fieldtype": "Link", "options": "User", "label": "Changed By", "in_list_view": 1},
            {"fieldname": "changed_at", "fieldtype": "Datetime", "label": "Changed At", "in_list_view": 1},
            {"fieldname": "field_name", "fieldtype": "Data", "label": "Field Name", "in_list_view": 1},
            {"fieldname": "old_value", "fieldtype": "Small Text", "label": "Old Value"},
            {"fieldname": "new_value", "fieldtype": "Small Text", "label": "New Value"},
            {"fieldname": "company", "fieldtype": "Link", "options": "Company", "label": "Company", "in_list_view": 1},
        ]
        for f in fields:
            doc.append("fields", f)

        doc.append("permissions", {
            "role": "System Manager",
            "read": 1, "write": 0, "create": 0, "delete": 0, "share": 0
        })
        doc.append("permissions", {
            "role": "SMRITI Store Manager",
            "read": 1, "write": 0, "create": 0, "delete": 0, "share": 0
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"[SMRITI] Created SMRITI Address Audit Log DocType")
    except Exception as e:
        frappe.log_error(f"Error creating SMRITI Address Audit Log DocType: {str(e)}")



def create_master_doctypes():
    masters = [
        ("SMRITI Heel Type", "Heel Type"),
        ("SMRITI Outsole", "Outsole"),
        ("SMRITI Upper Material", "Upper Material"),
        ("SMRITI Gender", "Gender"),
        ("SMRITI Purchase Class", "Purchase Class"),
        ("SMRITI Merchandise Category", "Merchandise Category"),
        ("SMRITI Sub Category", "Sub Category")
    ]
    for doctype_name, label in masters:
        if not frappe.db.exists("DocType", doctype_name):
            try:
                doc = frappe.new_doc("DocType")
                doc.name = doctype_name
                doc.module = "SMRITI Retail OS"
                doc.custom = 1
                doc.autoname = "field:attribute_value"
                doc.editable_grid = 1
                doc.quick_entry = 1
                doc.track_changes = 1
                
                doc.append("fields", {
                    "fieldname": "attribute_value",
                    "fieldtype": "Data",
                    "label": "Value",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1
                })
                
                doc.append("permissions", {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
                })
                
                doc.append("permissions", {
                    "role": "SMRITI Store Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
                })
                
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(f"Error creating custom Master DocType {doctype_name}: {str(e)}")


def seed_master_doctypes():
    seeds = {
        "SMRITI Gender": ["MENS", "LADIES", "BOYS", "GIRLS", "UNISEX", "KIDS"],
        "SMRITI Purchase Class": ["FW", "MFW", "LFW", "BFW", "GFW", "KFW", "ASSTED", "SPORTS", "ACC", "BAG", "FORMAL", "CASUAL"],
        "SMRITI Heel Type": ["FLAT", "BLOCK", "WEDGE", "PENCIL", "PLATFORM"],
        "SMRITI Outsole": ["EVA", "TPR", "PU", "RUBBER", "PVC"],
        "SMRITI Upper Material": ["SYNTHETIC", "LEATHER", "MESH", "CANVAS", "KNITTED"]
    }
    for doctype_name, values in seeds.items():
        if frappe.db.exists("DocType", doctype_name):
            for val in values:
                if not frappe.db.exists(doctype_name, val):
                    try:
                        doc = frappe.new_doc(doctype_name)
                        doc.attribute_value = val
                        doc.insert(ignore_permissions=True)
                    except Exception as e:
                        frappe.log_error(f"Error seeding {val} to {doctype_name}: {str(e)}")

    # Seed default Print Templates
    if frappe.db.exists("DocType", "SMRITI Print Template"):
        default_templates = [
            {
                "name": "ZEBRA_50X25_STANDARD",
                "template_title": "Zebra 50x25 Standard Label",
                "label_size": "50x25",
                "printer_language": "ZPL",
                "printer_family": "ZPL",
                "raw_template": "^XA\n^FO20,10^BCN,60,Y,N,N^FD{barcode}^FS\n^FO20,80^ADN,18,10^FD{item_name}^FS\n^FO20,100^ADN,18,10^FDMRP: Rs.{mrp}^FS\n^FO20,120^ADN,14,8^FD{brand} | Size: {size} | Color: {color}^FS\n^XZ"
            },
            {
                "name": "TSC_106X55_3UP_FOOTWEAR",
                "template_title": "TSC 106x55 3-Up Footwear Label",
                "label_size": "106x55",
                "printer_language": "TSPL",
                "printer_family": "TSPL",
                "raw_template": "SIZE 106.6 mm, 55.4 mm\nGAP 3 mm, 0 mm\nSPEED 4\nDENSITY 14\nDIRECTION 0,0\nREFERENCE 0,0\nOFFSET 0 mm\nSET PEEL OFF\nSET CUTTER OFF\nSET TEAR ON\nCLS\nCODEPAGE 850\nTEXT 820,372,\"2\",180,2,2,\"{color}\"\nTEXT 702,318,\"2\",180,3,3,\"{size}\"\nTEXT 820,428,\"3\",180,2,2,\"{item_code}\"\nTEXT 556,335,\"4\",180,1,1,\"{mrp}/-\"\nTEXT 824,260,\"3\",180,1,1,\"{brand}\"\nTEXT 809,304,\"1\",180,2,2,\"SIZE-\"\nTEXT 475,401,\"1\",180,1,1,\"Footwear\"\nTEXT 596,401,\"1\",180,1,1,\"Commodity :\"\nTEXT 594,381,\"1\",180,1,1,\"Net Contents :\"\nTEXT 448,381,\"1\",180,1,1,\"1 Pair\"\nTEXT 600,301,\"1\",180,1,1,\"(Incl of all Taxes)\"\nTEXT 594,358,\"1\",180,1,1,\"Pkd On :\"\nTEXT 501,358,\"1\",180,1,1,\"{pkd_date}\"\nBARCODE 613,279,\"128\",95,0,180,2,4,\"{barcode}\"\nTEXT 597,176,\"3\",180,1,1,\"{barcode}\"\nPRINT 1,1"
            },
            {
                "name": "IMPACT_HONEYWELL_IH2_ZPL",
                "template_title": "IMPACT by Honeywell IH-2 (ZPL)",
                "label_size": "100x50",
                "printer_language": "ZPL",
                "printer_family": "ZPL",
                "raw_template": (
                    "^XA\n"
                    "^SZ2^JMA\n"
                    "^MCY^PMN\n"
                    "^PW804\n"
                    "^JZY\n"
                    "^LH0,0^LRN\n"
                    "^XZ\n"
                    "^XA\n"
                    "^FO706,47\n"
                    "^BY3^BCB,50,N,N^FD{barcode}^FS\n"
                    "^FT781,340\n"
                    "^CI0\n"
                    "^AAB,27,15^FD{barcode}^FS\n"
                    "^FT345,53\n"
                    "^A0N,34,46^FD{brand}^FS\n"
                    "^FT335,340\n"
                    "^A0N,17,23^FDMKTD.By:{brand}^FS\n"
                    "^FT335,351\n"
                    "^ABN,11,7^FD81,Umerkhadi,Mumbai,400003^FS\n"
                    "^FO615,135\n"
                    "^GB76,80,76^FS\n"
                    "^FT615,198\n"
                    "^A0N,79,77^FR^FD{size}^FS\n"
                    "^FT400,182\n"
                    "^A0N,37,49^FD{color}^FS\n"
                    "^FO410,86\n"
                    "^GB277,46,46^FS\n"
                    "^FT410,124\n"
                    "^A0N,45,43^FR^FD{item_code}^FS\n"
                    "^FO327,84\n"
                    "^GB367,129,3^FS\n"
                    "^FO329,128\n"
                    "^GB337,0,3^FS\n"
                    "^FT536,274\n"
                    "^A0N,17,23^FD(Incl of all taxes)^FS\n"
                    "^FT493,251\n"
                    "^A0N,42,56^FD{mrp}/-^FS\n"
                    "^FT410,246\n"
                    "^A0N,28,38^FDMRP:^FS\n"
                    "^FT327,274\n"
                    "^A0N,17,23^FDMFG.Dt.: {pkd_date}^FS\n"
                    "^FT327,290\n"
                    "^ABN,11,7^FDNET CONTENTS:1 Pair Footwear^FS\n"
                    "^FT335,113\n"
                    "^A0N,17,23^FDArt.No.^FS\n"
                    "^FT335,175\n"
                    "^A0N,17,23^FDColor:^FS\n"
                    "^FT335,386\n"
                    "^ABN,11,7^FDcontact@yourstore.com^FS\n"
                    "^FO34,125\n"
                    "^BY2^BCN,30,N,N^FD{barcode}^FS\n"
                    "^FT46,181\n"
                    "^A0N,25,34^FD{barcode}^FS\n"
                    "^FO37,60\n"
                    "^GB70,67,67^FS\n"
                    "^FT37,114\n"
                    "^A0N,65,72^FR^FD{size}^FS\n"
                    "^FO116,50\n"
                    "^GB101,30,30^FS\n"
                    "^FT116,76\n"
                    "^A0N,28,38^FR^FD{color}^FS\n"
                    "^FT37,47\n"
                    "^A0N,28,27^FD{item_code}^FS\n"
                    "^FT17,159\n"
                    "^ABB,11,7^FD{brand}^FS\n"
                    "^FT116,97\n"
                    "^A0N,20,27^FDMRP:{mrp}/-^FS\n"
                    "^FT116,114\n"
                    "^A0N,17,23^FD(Incl of all taxes)^FS\n"
                    "^FO33,338\n"
                    "^BCN,30,N,N^FD{barcode}^FS\n"
                    "^FT45,394\n"
                    "^A0N,25,34^FD{barcode}^FS\n"
                    "^FO33,275\n"
                    "^GB70,65,65^FS\n"
                    "^FT33,327\n"
                    "^A0N,62,70^FR^FD{size}^FS\n"
                    "^FO116,263\n"
                    "^GB101,30,30^FS\n"
                    "^FT116,289\n"
                    "^A0N,28,38^FR^FD{color}^FS\n"
                    "^FT33,260\n"
                    "^A0N,28,27^FD{item_code}^FS\n"
                    "^FT16,372\n"
                    "^ABB,11,7^FD{brand}^FS\n"
                    "^FT116,310\n"
                    "^A0N,20,27^FDMRP:{mrp}/-^FS\n"
                    "^FT116,327\n"
                    "^A0N,17,23^FD(Incl of all taxes)^FS\n"
                    "^FO328,308\n"
                    "^GB367,0,3^FS\n"
                    "^FO328,365\n"
                    "^GB367,0,3^FS\n"
                    "^PQ1,0,1,Y\n"
                    "^XZ"
                )
            }
        ]
        for t in default_templates:
            if frappe.db.exists("SMRITI Print Template", t["name"]):
                try:
                    # Update path to refresh missing or updated fields on existing template
                    doc = frappe.get_doc("SMRITI Print Template", t["name"])
                    updated = False
                    for key in ["template_title", "label_size", "printer_language", "printer_family", "raw_template"]:
                        if doc.get(key) != t.get(key):
                            doc.set(key, t.get(key))
                            updated = True
                    if updated:
                        doc.save(ignore_permissions=True)
                except Exception as e:
                    frappe.log_error(f"Error updating print template {t['name']}: {str(e)}")
            else:
                try:
                    doc = frappe.new_doc("SMRITI Print Template")
                    doc.name = t["name"]
                    doc.update(t)
                    doc.insert(ignore_permissions=True)
                except Exception as e:
                    frappe.log_error(f"Error seeding print template {t['name']}: {str(e)}")
    frappe.db.commit()

def backup_and_seed_existing_data():
    field_to_doctype = {
        "custom_heel_type": "SMRITI Heel Type",
        "custom_outsole": "SMRITI Outsole",
        "custom_upper_material": "SMRITI Upper Material",
        "custom_gender": "SMRITI Gender",
        "custom_sub_category": "SMRITI Sub Category",
        "custom_merchandise_category": "SMRITI Merchandise Category",
        "custom_purchase_class": "SMRITI Purchase Class"
    }
    for field, dt in field_to_doctype.items():
        if frappe.db.exists("DocType", dt) and frappe.db.has_column("Item", field):
            try:
                unique_vals = frappe.db.sql(f"select distinct `{field}` from `tabItem` where `{field}` is not null and `{field}` != ''", as_list=True)
                for (val,) in unique_vals:
                    val_clean = str(val).strip()
                    if val_clean and not frappe.db.exists(dt, val_clean):
                        try:
                            doc = frappe.new_doc(dt)
                            doc.attribute_value = val_clean
                            doc.insert(ignore_permissions=True)
                        except Exception as e:
                            frappe.log_error(f"Error backing up {val_clean} to {dt}: {str(e)}")
            except Exception as e:
                frappe.log_error(f"Error reading column {field} from Item: {str(e)}")
def setup_activity_log_options():
    """Adds SMRITI custom operations to Activity Log's operation Select field options."""
    try:
        from frappe.custom.doctype.property_setter.property_setter import make_property_setter
        options = (
            "\nLogin"
            "\nLogout"
            "\nImpersonate"
            "\nBlocked Download Attempt"
            "\nConfig Exported"
            "\nCustodian Verified"
            "\nRecovery Fragments Sent"
            "\nPrint Job Cleanup"
            "\nBackup Encryption Enabled"
            "\nBackup Encryption Disabled"
            "\nGPG Executable Missing"
            "\nBackup Created"
            "\nBackup Restored"
            "\nDatabase Restore"
            "\nSMRITI Visual Template Saved"
            "\nSMRITI Visual Template Compilation Failed"
            "\nSMRITI Print Template Version Created"
            "\nSMRITI Print Template Version Restored"
            "\nSMRITI Print Job Queued"
            "\nSMRITI Print Job Sending"
            "\nSMRITI Print Job Success"
            "\nSMRITI Print Job Failed"
            "\nSMRITI Print Job Cleanup"
            "\nSMRITI Label Studio Print Run"
            "\nSMRITI PSV Activity Log"
        )
        # Delete existing first to force update
        frappe.db.delete("Property Setter", {"doc_type": "Activity Log", "field_name": "operation", "property": "options"})
        make_property_setter(
            doctype="Activity Log",
            fieldname="operation",
            property="options",
            value=options,
            property_type="Select",
            validate_fields_for_doctype=False
        )
        frappe.db.commit()
        frappe.clear_cache(doctype="Activity Log")
        print("[SMRITI] Updated Activity Log operation field options")
    except Exception as e:
        frappe.log_error(f"Error updating Activity Log options: {str(e)}")


def create_smriti_key_custodian_doctype():
    """Creates the SMRITI Key Custodian custom DocType for metadata-only custodian storage."""
    if frappe.db.exists("DocType", "SMRITI Key Custodian"):
        return
    try:
        doc = frappe.new_doc("DocType")
        doc.name = "SMRITI Key Custodian"
        doc.module = "SMRITI Retail OS"
        doc.custom = 1
        doc.autoname = "field:email"
        doc.editable_grid = 0
        doc.quick_entry = 0
        doc.track_changes = 1
        doc.issingle = 0

        fields = [
            {"fieldname": "custodian_name", "fieldtype": "Data", "label": "Custodian Name", "reqd": 1, "in_list_view": 1},
            {"fieldname": "email", "fieldtype": "Data", "label": "Email", "reqd": 1, "unique": 1, "in_list_view": 1},
            {"fieldname": "verified", "fieldtype": "Check", "label": "Verified", "default": "0", "read_only": 1, "in_list_view": 1},
            {"fieldname": "verification_date", "fieldtype": "Datetime", "label": "Verification Date", "read_only": 1},
            {"fieldname": "last_recovery_sent", "fieldtype": "Datetime", "label": "Last Recovery Sent", "read_only": 1},
            {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Pending\nVerified\nRevoked", "default": "Pending", "in_list_view": 1},
            {"fieldname": "otp_hash", "fieldtype": "Data", "label": "OTP Hash", "hidden": 1, "read_only": 1},
            {"fieldname": "otp_expiry", "fieldtype": "Datetime", "label": "OTP Expiry", "hidden": 1, "read_only": 1}
        ]
        for f in fields:
            doc.append("fields", f)

        # Do NOT assign default permissions to standard roles (restricted to programmatic access)
        doc.append("permissions", {
            "role": "Administrator",
            "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
        })
        doc.append("permissions", {
            "role": "System Manager",
            "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("[SMRITI] Created SMRITI Key Custodian DocType")
    except Exception as e:
        frappe.log_error(f"Error creating SMRITI Key Custodian DocType: {str(e)}")


def ensure_print_job_directory():
    import os
    path = frappe.get_site_path("private", "print_jobs")
    os.makedirs(path, exist_ok=True)
    test_file = os.path.join(path, ".healthcheck")
    try:
        with open(test_file, "w") as f:
            f.write("ok")
        os.unlink(test_file)
    except Exception:
        raise RuntimeError("SMRITI print_jobs directory is not writable.")


def create_smriti_print_job_doctype():
    """Creates the SMRITI Print Job custom DocType for asynchronous print tracking."""
    try:
        if frappe.db.exists("DocType", "SMRITI Print Job"):
            frappe.delete_doc("DocType", "SMRITI Print Job", ignore_missing=True, force=True)
            frappe.db.commit()

        doc = frappe.new_doc("DocType")
        doc.name = "SMRITI Print Job"
        doc.module = "SMRITI Retail OS"
        doc.custom = 1
        doc.autoname = "field:job_id"
        doc.editable_grid = 0
        doc.quick_entry = 0
        doc.track_changes = 1
        doc.issingle = 0

        fields = [
            {"fieldname": "job_id", "fieldtype": "Data", "label": "Job ID", "read_only": 1, "unique": 1, "in_list_view": 1},
            {"fieldname": "item_code", "fieldtype": "Link", "options": "Item", "label": "Item Code", "in_list_view": 1},
            {"fieldname": "barcode", "fieldtype": "Data", "label": "Barcode", "in_list_view": 1},
            {"fieldname": "template_name", "fieldtype": "Data", "label": "Template Name", "in_list_view": 1},
            {"fieldname": "printer_ip", "fieldtype": "Data", "label": "Printer IP", "in_list_view": 1},
            {"fieldname": "printer_port", "fieldtype": "Int", "label": "Printer Port", "default": 9100},
            {"fieldname": "print_qty", "fieldtype": "Int", "label": "Print Qty", "in_list_view": 1},
            {"fieldname": "payload_hash", "fieldtype": "Data", "label": "Payload Hash", "read_only": 1},
            {"fieldname": "payload_preview", "fieldtype": "Data", "label": "Payload Preview", "read_only": 1},
            {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Queued\nSending\nSuccess\nFailed", "default": "Queued", "in_list_view": 1},
            {"fieldname": "error_message", "fieldtype": "Text", "label": "Error Message", "read_only": 1},
            {"fieldname": "created_by", "fieldtype": "Data", "label": "Created By", "read_only": 1},
            {"fieldname": "created_on", "fieldtype": "Datetime", "label": "Created On", "read_only": 1},
            {"fieldname": "completed_on", "fieldtype": "Datetime", "label": "Completed On", "read_only": 1}
        ]
        for f in fields:
            doc.append("fields", f)

        doc.append("permissions", {
            "role": "Administrator",
            "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
        })
        doc.append("permissions", {
            "role": "System Manager",
            "read": 1, "write": 1, "create": 1, "delete": 1, "share": 1
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("[SMRITI] Created SMRITI Print Job DocType")
    except Exception as e:
        frappe.log_error(f"Error creating SMRITI Print Job DocType: {str(e)}")


def setup_smriti_retail_os():
    """
    Initializes custom fields, roles, and workspaces for standard DocTypes
    to extend ERPNext for SMRITI Retail OS.
    """
    # 00. Provision SMRITI roles first to prevent dependency issues in custom DocTypes
    for role_name in ["SMRITI Cashier", "SMRITI Store Manager"]:
        if not frappe.db.exists("Role", role_name):
            try:
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.desk_access = 1
                role.insert(ignore_permissions=True)
                frappe.db.commit()
                print(f"Created custom SMRITI role: {role_name}")
            except Exception as e:
                frappe.log_error(f"Error creating role {role_name}: {str(e)}")

    # 0. Provision SMRITI Company Settings DocType
    create_smriti_company_settings_doctype()

    # 0a. Provision SMRITI Address Audit Log DocType
    create_audit_log_doctype()

    # 0b. Provision SMRITI Key Custodian DocType (v1.8.3)
    create_smriti_key_custodian_doctype()

    # 0e. Provision SMRITI Print Job DocType (V2.1)
    create_smriti_print_job_doctype()
    ensure_print_job_directory()

    # 0c. Provision SMRITI Reporting DocTypes
    create_reporting_doctypes()
    seed_report_templates()

    # 0d. Update Activity Log operation options
    setup_activity_log_options()


    # 0b. Provision dynamic attribute Master DocTypes + preserve existing database entries
    create_master_doctypes()
    backup_and_seed_existing_data()
    seed_master_doctypes()
    seed_retail_defaults()

    # 1. Custom Fields Provisioning
    custom_fields = {}


    if frappe.db.exists("DocType", "SMRITI Company Settings"):
        custom_fields["SMRITI Company Settings"] = [
            {
                "fieldname": "custom_business_type",
                "label": "Business Type",
                "fieldtype": "Select",
                "options": "Footwear\nFMCG\nGarments\nPharma\nCosmetics\nGeneral Retail",
                "default": "Footwear",
                "insert_after": "company",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_print_profiles_json",
                "label": "Print Profiles JSON",
                "fieldtype": "Long Text",
                "insert_after": "backup_settings_json",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "default_printer_ip",
                "label": "Default Printer IP",
                "fieldtype": "Data",
                "insert_after": "custom_print_profiles_json",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "default_printer_port",
                "label": "Default Printer Port",
                "fieldtype": "Int",
                "default": "9100",
                "insert_after": "default_printer_ip",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "default_printer_lang",
                "label": "Default Printer Language",
                "fieldtype": "Select",
                "options": "ZPL\nTSPL",
                "default": "ZPL",
                "insert_after": "default_printer_port",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "default_label_size",
                "label": "Default Label Size",
                "fieldtype": "Select",
                "options": "50x25\n50x30\n75x50\n100x50\n106x55",
                "default": "50x25",
                "insert_after": "default_printer_lang",
                "module": "SMRITI Retail OS"
            }
        ]

    custom_fields.update({
        "User": [
            {
                "fieldname": "custom_is_smriti_user",
                "label": "Is SMRITI User",
                "fieldtype": "Check",
                "insert_after": "role_profile_name",
                "default": "1",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_smriti_pin",
                "label": "SMRITI POS PIN",
                "fieldtype": "Password",
                "insert_after": "custom_is_smriti_user",
                "module": "SMRITI Retail OS"
            }
        ],
        "POS Invoice": [
            {
                "fieldname": "custom_is_held",
                "label": "Is Held",
                "fieldtype": "Check",
                "insert_after": "status",
                "read_only": 1,
                "default": "0",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_held_by",
                "label": "Held By",
                "fieldtype": "Link",
                "options": "User",
                "insert_after": "custom_is_held",
                "read_only": 1,
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_hold_time",
                "label": "Hold Time",
                "fieldtype": "Datetime",
                "insert_after": "custom_held_by",
                "read_only": 1,
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_billing_session_id",
                "label": "Billing Session ID",
                "fieldtype": "Data",
                "insert_after": "custom_hold_time",
                "read_only": 1,
                "unique": 1,
                "module": "SMRITI Retail OS"
            }
        ],
        "Item": [
            {
                "fieldname": "custom_mrp",
                "label": "MRP (Maximum Retail Price)",
                "fieldtype": "Currency",
                "insert_after": "standard_rate",
                "bold": 1,
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_gst_percentage",
                "label": "GST Percentage (%)",
                "fieldtype": "Select",
                "options": "\n0\n5\n12\n18\n28",
                "insert_after": "custom_mrp",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_is_retail_item",
                "label": "Is Retail Item",
                "fieldtype": "Check",
                "default": "1",
                "insert_after": "custom_gst_percentage",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_department",
                "label": "Department",
                "fieldtype": "Link",
                "options": "Item Group",
                "insert_after": "custom_is_retail_item",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_barcode_size",
                "label": "Barcode Size",
                "fieldtype": "Select",
                "options": "\n50x25\n50x30\n75x50\n100x50",
                "insert_after": "custom_department",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_current_stock_html",
                "label": "Current Stock HTML",
                "fieldtype": "HTML",
                "insert_after": "custom_barcode_size",
                "module": "SMRITI Retail OS"
            },
            # ── Fashion / Footwear attributes ─────────────────────────────
            {
                "fieldname": "custom_purchase_class",
                "label": "Purchase Class",
                "fieldtype": "Link",
                "options": "SMRITI Purchase Class",
                "insert_after": "custom_current_stock_html",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_merchandise_category",
                "label": "Merchandise Category",
                "fieldtype": "Link",
                "options": "SMRITI Merchandise Category",
                "insert_after": "custom_purchase_class",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_sub_category",
                "label": "Sub Category",
                "fieldtype": "Link",
                "options": "SMRITI Sub Category",
                "insert_after": "custom_merchandise_category",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_gender",
                "label": "Gender",
                "fieldtype": "Link",
                "options": "SMRITI Gender",
                "insert_after": "custom_sub_category",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_upper_material",
                "label": "Upper Material",
                "fieldtype": "Link",
                "options": "SMRITI Upper Material",
                "insert_after": "custom_gender",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_outsole",
                "label": "Outsole",
                "fieldtype": "Link",
                "options": "SMRITI Outsole",
                "insert_after": "custom_upper_material",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_heel_type",
                "label": "Heel Type",
                "fieldtype": "Link",
                "options": "SMRITI Heel Type",
                "insert_after": "custom_outsole",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_style_code",
                "label": "Style / Article No",
                "fieldtype": "Data",
                "insert_after": "custom_heel_type",
                "in_list_view": 1,
                "bold": 1,
                "module": "SMRITI Retail OS"
            }
        ],
        "Customer": [
            {
                "fieldname": "custom_address_text",
                "label": "Address Text",
                "fieldtype": "Small Text",
                "insert_after": "customer_name",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_shipping_address_text",
                "label": "Shipping Address Text",
                "fieldtype": "Small Text",
                "insert_after": "custom_address_text",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_tax_inclusive_override",
                "label": "Tax Inclusive Override",
                "fieldtype": "Select",
                "options": "Default\nInclusive\nExclusive",
                "default": "Default",
                "insert_after": "custom_shipping_address_text",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_birthday",
                "label": "Birthday",
                "fieldtype": "Date",
                "insert_after": "custom_tax_inclusive_override",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_anniversary",
                "label": "Anniversary",
                "fieldtype": "Date",
                "insert_after": "custom_birthday",
                "module": "SMRITI Retail OS"
            }
        ],
        "Supplier": [
            {
                "fieldname": "custom_address_text",
                "label": "Address Text",
                "fieldtype": "Small Text",
                "insert_after": "supplier_name",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_shipping_address_text",
                "label": "Shipping Address Text",
                "fieldtype": "Small Text",
                "insert_after": "custom_address_text",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_credit_days",
                "label": "Credit Days",
                "fieldtype": "Int",
                "insert_after": "custom_shipping_address_text",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_vendor_code",
                "label": "Vendor Code",
                "fieldtype": "Data",
                "insert_after": "custom_credit_days",
                "unique": 1,
                "module": "SMRITI Retail OS"
            }
        ],
        "Sales Invoice": [
            {
                "fieldname": "custom_sizewise_json",
                "label": "Sizewise Matrix JSON",
                "fieldtype": "Long Text",
                "insert_after": "remarks",
                "hidden": 1,
                "no_copy": 1,
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_billing_session_id",
                "label": "Billing Session ID",
                "fieldtype": "Data",
                "insert_after": "custom_sizewise_json",
                "read_only": 1,
                "unique": 1,
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_party_stock_account",
                "label": "Party Stock Account",
                "fieldtype": "Link",
                "options": "SMRITI Party Stock Account",
                "insert_after": "custom_billing_session_id",
                "module": "SMRITI Retail OS"
            }
        ],
        "Company": [
            {
                "fieldname": "custom_smriti_store_type",
                "label": "SMRITI Store Type",
                "fieldtype": "Select",
                "options": "\nRetail\nB2B Distributor\nWholesale",
                "insert_after": "company_name",
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_smriti_gstin_state",
                "label": "SMRITI GSTIN State Code",
                "fieldtype": "Data",
                "insert_after": "custom_smriti_store_type",
                "read_only": 1,
                "module": "SMRITI Retail OS"
            },
            {
                "fieldname": "custom_smriti_settings_configured",
                "label": "SMRITI Settings Configured",
                "fieldtype": "Check",
                "insert_after": "custom_smriti_gstin_state",
                "read_only": 1,
                "default": "0",
                "module": "SMRITI Retail OS"
            }
        ],
        "Item Barcode": [
            {
                "fieldname": "custom_is_primary",
                "label": "Is Primary",
                "fieldtype": "Check",
                "default": "0",
                "in_list_view": 1,
                "module": "SMRITI Retail OS"
            }
        ]
    })

    create_custom_fields(custom_fields, ignore_validate=True)

    # Force sync all existing Custom Fields to SMRITI Retail OS module in the database
    for dt, fields in custom_fields.items():
        for f in fields:
            fieldname = f.get("fieldname")
            custom_field_name = f"{dt}-{fieldname}"
            if frappe.db.exists("Custom Field", custom_field_name):
                frappe.db.set_value("Custom Field", custom_field_name, "module", "SMRITI Retail OS")

    # 2. Role Provisioning (Note: provisioned at start of setup to prevent DocPerm insert errors)

    # 3. Programmatic Workspace Provisioning
    workspace_name = "SMRITI Retail OS"
    required_links = [
        # Card 1: Quick Access
        {
            "label": "Quick Access",
            "type": "Card Break",
            "icon": "desktop"
        },
        {
            "label": "Retail Billing",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti_billing",
            "label_for_links": "Keyboard-driven fast point-of-sale checkout."
        },
        {
            "label": "Day Open / Close",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti_shift",
            "label_for_links": "Open and close cashier shifts with denomination count."
        },
        {
            "label": "Inventory",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti_inventory",
            "label_for_links": "Mobile-ready quick scanning barcode inventory."
        },
        {
            "label": "Barcode Printing",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti_barcode",
            "label_for_links": "Transaction-based or bulk label printing."
        },

        # Card 2: Master Data
        {
            "label": "Master Data",
            "type": "Card Break",
            "icon": "database"
        },
        {
            "label": "Products",
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Item",
            "label_for_links": "Simplified retail products catalog."
        },
        {
            "label": "Item Master Import",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti_item_master",
            "label_for_links": "Paste from Excel or upload CSV to bulk-create items with variants."
        },
        {
            "label": "Customers",
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Customer",
            "label_for_links": "Cashier-friendly quick customer onboarding."
        },
        {
            "label": "Party Stock Accounts",
            "type": "Link",
            "link_type": "DocType",
            "link_to": "SMRITI Party Stock Account",
            "label_for_links": "Manage third-party stock locations for customers."
        },
        {
            "label": "Suppliers",
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Supplier",
            "label_for_links": "Simplified supplier credit terms tracker."
        },

        # Card 3: Operations & Marketing
        {
            "label": "Operations & Marketing",
            "type": "Card Break",
            "icon": "settings"
        },
        {
            "label": "Loyalty & Promotions",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti_loyalty",
            "label_for_links": "Configure customer points tiers and conversion rules."
        },
        {
            "label": "Reports",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti_reports",
            "label_for_links": "Visual sales, stock, and outstanding analytics."
        },
        {
            "label": "Party Sales Uploads",
            "type": "Link",
            "link_type": "DocType",
            "link_to": "SMRITI Party Sales Upload",
            "label_for_links": "Upload weekly distributor sales spreadsheets."
        },
        {
            "label": "Party Stock Audits",
            "type": "Link",
            "link_type": "DocType",
            "link_to": "SMRITI Party Physical Snapshot",
            "label_for_links": "Verify physical stock and reconcile variances."
        },

        # Card 4: Settings & Configuration
        {
            "label": "Settings & Configuration",
            "type": "Card Break",
            "icon": "settings"
        },
        {
            "label": "Company Settings",
            "type": "Link",
            "link_type": "Page",
            "link_to": "configure",
            "label_for_links": "Configure store identity, defaults, loyalty, and tax mappings."
        },
        {
            "label": "POS Profiles",
            "type": "Link",
            "link_type": "DocType",
            "link_to": "POS Profile",
            "label_for_links": "Manage point-of-sale configurations, warehouses, and cashier access."
        }
    ]

    blocks = [
        {
            "id": "hdr_smriti",
            "type": "header",
            "data": {
                "text": "<span class=\"h4\"><b>SMRITI Retail Operations</b></span>",
                "col": 12
            }
        },
        {
            "id": "card_quick_access",
            "type": "card",
            "data": {
                "card_name": "Quick Access",
                "col": 4
            }
        },
        {
            "id": "card_master_data",
            "type": "card",
            "data": {
                "card_name": "Master Data",
                "col": 4
            }
        },
        {
            "id": "card_ops_marketing",
            "type": "card",
            "data": {
                "card_name": "Operations & Marketing",
                "col": 4
            }
        }
    ]
    workspace_content = json.dumps(blocks)

    if frappe.db.exists("Workspace", workspace_name):
        ws = frappe.get_doc("Workspace", workspace_name)
        ws.links = []
        for l in required_links:
            ws.append("links", l)
        ws.module = "Selling"
        ws.content = workspace_content
        ws.public = 1
        ws.flags.ignore_links = True
        ws.save(ignore_permissions=True)
        print(f"Updated SMRITI Workspace: {workspace_name}")
    else:
        ws = frappe.new_doc("Workspace")
        ws.label = workspace_name
        ws.title = workspace_name
        ws.icon = "shopping-cart"
        ws.public = 1
        ws.module = "Selling"
        for l in required_links:
            ws.append("links", l)
        ws.content = workspace_content
        ws.flags.ignore_links = True
        ws.insert(ignore_permissions=True)
        print(f"Created custom SMRITI Workspace: {workspace_name}")

    frappe.db.set_value("Workspace", workspace_name, "module", "Selling")
    frappe.db.set_value("Workspace", workspace_name, "public", 1)

    # 4. Programmatic Role Permissions setup
    doctype_permissions = {
        "Item": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1}
        },
        "Customer": {
            "SMRITI Cashier": {"read": 1, "write": 1, "create": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1}
        },
        "Supplier": {
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1}
        },
        "Sales Invoice": {
            "SMRITI Cashier": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1}
        },
        "POS Invoice": {
            "SMRITI Cashier": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1}
        },
        "POS Opening Entry": {
            "SMRITI Cashier": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1}
        },
        "POS Closing Entry": {
            "SMRITI Cashier": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1}
        },
        "Purchase Order": {
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "Purchase Receipt": {
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "Bin": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "Stock Ledger Entry": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "Number Card": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "Dashboard": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "POS Profile": {
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "delete": 1}
        },
        "SMRITI Party Stock Account": {
             "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "delete": 1}
        },
        "SMRITI Party Sales Upload": {
             "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1}
        },
        "SMRITI Party Physical Snapshot": {
             "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1}
        },
        "SMRITI PSV Exception Record": {
             "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "SMRITI PSV Settings": {
             "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "SMRITI Party Stock Ledger Entry": {
             "SMRITI Store Manager": {"read": 1}
        },
        "SMRITI PSV Activity Log": {
             "SMRITI Store Manager": {"read": 1}
        }
    }

    for dt, roles in doctype_permissions.items():
        for role, perm in roles.items():
            if not frappe.db.exists("Custom DocPerm", {"parent": dt, "role": role}):
                p = frappe.get_doc({
                    "doctype": "Custom DocPerm",
                    "parent": dt,
                    "parenttype": "DocType",
                    "parentfield": "permissions",
                    "role": role,
                    "read": perm.get("read", 0),
                    "write": perm.get("write", 0),
                    "create": perm.get("create", 0),
                    "submit": perm.get("submit", 0),
                    "cancel": perm.get("cancel", 0),
                    "amend": perm.get("amend", 0),
                    "export": perm.get("export", 0),
                    "print": perm.get("print", 0),
                    "email": perm.get("email", 0),
                    "report": 1,
                    "idx": 0
                })
                p.insert(ignore_permissions=True)
                print(f"Set custom permissions for {dt} -> {role}")

    # 5. Create Block Module Profiles for simplified Desk experience
    # Note: These are linked to SMRITI Roles via Role Profile or manual assignment
    _setup_module_profiles()

    # 6. Hide all non-retail modules system-wide by default
    hide_non_retail_modules()
    
    # 7. Provision default Admin (Business Owner) account
    create_default_admin_account()

    frappe.db.commit()


def _setup_module_profiles():
    """Restricts visible modules for SMRITI users to keep the Desk uncluttered."""
    profiles = {
        "SMRITI Cashier Profile": [
            "Accounts", "Stock", "Buying", "Selling", "CRM", "HR", "Projects", 
            "Support", "Asset", "Quality Management", "Agriculture", "Education", 
            "Manufacturing", "Retail", "Ecommerce"
        ],
        "SMRITI Store Manager Profile": [
            "CRM", "HR", "Projects", "Support", "Asset", "Quality Management", 
            "Agriculture", "Education", "Manufacturing", "Ecommerce"
        ]
    }

    for profile_name, blocked in profiles.items():
        if not frappe.db.exists("Module Profile", profile_name):
            doc = frappe.new_doc("Module Profile")
            doc.module_profile_name = profile_name
            for m in blocked:
                doc.append("block_modules", {"module": m})
            doc.insert(ignore_permissions=True)
            print(f"[SMRITI] Module Profile created/updated: {profile_name}")

    # Create Role Profiles to bundle SMRITI roles
    role_profiles = {
        "SMRITI Cashier Role Profile": [
            "SMRITI Cashier", 
            "Desk User"
        ],
        "SMRITI Store Manager Role Profile": [
            "SMRITI Store Manager",
            "SMRITI Cashier",       # Managers can also operate the POS
            "Desk User",
            "Stock Manager",
            "Sales Manager",
            "Purchase Manager"
        ]
    }

    for profile_name, roles in role_profiles.items():
        if not frappe.db.exists("Role Profile", profile_name):
            doc = frappe.new_doc("Role Profile")
            doc.role_profile = profile_name
            for r in roles:
                doc.append("roles", {"role": r})
            try:
                doc.insert(ignore_permissions=True)
                print(f"[SMRITI] Role Profile created/updated: {profile_name}")
            except Exception as e:
                print(f"[SMRITI] Warning — could not save Role Profile '{profile_name}': {e}")

    frappe.db.commit()


def hide_non_retail_modules():
    """
    Hides all ERPNext modules and Workspaces that are irrelevant to a Retail Store
    or B2B Distributor — system-wide for all users by default.

    Modules kept visible (Retail / B2B relevant):
      Accounts, Buying, Selling, Stock, HR (basic), CRM,
      SMRITI Retail OS, India Compliance

    Modules hidden:
      Manufacturing, Projects, Agriculture, Education, Healthcare,
      Non Profit, Quality Management, Assets, Hospitality, Payroll,
      Loans, Support, E-commerce, ERPNext Integrations
    """

    # ── 1. System-wide global hide via Frappe Defaults ───────────────────────
    # These are stored in tabDefaultValue with parent="__default".
    # Frappe reads them via frappe.get_default("hide_modules") to build the Desk.
    NON_RETAIL_MODULES = [
        "Manufacturing",
        "Projects",
        "Agriculture",
        "Education",
        "Healthcare",
        "Non Profit",
        "Quality Management",
        "Assets",
        "Hospitality",
        "Payroll",
        "Loans",
        "Support",
        "E-commerce",
        "ERPNext Integrations",
        "Integrations",
    ]

    # Read existing hidden list so we don't overwrite manual changes
    existing_hidden_raw = frappe.db.get_default("hide_modules") or "[]"
    try:
        existing_hidden = json.loads(existing_hidden_raw)
    except Exception:
        existing_hidden = []

    merged = list(set(existing_hidden) | set(NON_RETAIL_MODULES))
    frappe.db.set_default("hide_modules", json.dumps(merged))
    print(f"[SMRITI] Hidden {len(merged)} non-retail modules globally.")

    # ── 2. Mark matching Workspaces as hidden ────────────────────────────────
    # Workspace.is_hidden = 1 removes the sidebar entry for all users.
    NON_RETAIL_WORKSPACES = [
        # ERPNext Workspaces
        "Manufacturing",
        "Project",
        "Agriculture",
        "Education",
        "Healthcare",
        "Non Profit",
        "Quality Management",
        "Asset",
        "Hospitality",
        "Payroll",
        "Loans",
        "Support",
        "E-Commerce",
        "ERPNext Integrations",
        "Integrations",
        # Specific DocType-level workspaces irrelevant to retail
        "Timesheet",
        "Delivery Note",
        "Contract",
        "Driver",
        "Fleet Management",
        "Maintenance",
    ]

    hidden_ws_count = 0
    for ws_name in NON_RETAIL_WORKSPACES:
        if frappe.db.exists("Workspace", ws_name):
            frappe.db.set_value(
                "Workspace", ws_name, "is_hidden", 1,
                update_modified=False
            )
            hidden_ws_count += 1

    if hidden_ws_count:
        print(f"[SMRITI] Hid {hidden_ws_count} non-retail Workspaces.")

    frappe.db.commit()


def after_install():
    """Called once immediately after `bench install-app smriti_retail_os`."""
    setup_smriti_retail_os()
    # Sync branding assets into the shared sites/assets volume
    from smriti_retail_os.sync_assets import sync_assets
    sync_assets()


def patch_company_tax_invoice(print_format_name=None):
    """
    Patches a company Tax Invoice Print Format in the database.
    Injects E-way Bill and Vehicle Number rendering inside the Invoice Details header block.
    If no print_format_name is given, searches for the first custom Sales Invoice print format.
    """
    import frappe
    if not print_format_name:
        # Auto-detect the first custom Sales Invoice print format
        pf_name = frappe.db.get_value(
            "Print Format",
            {"doc_type": "Sales Invoice", "standard": "No"},
            "name"
        )
        if pf_name:
            print_format_name = pf_name
        else:
            print("[SMRITI] No custom Sales Invoice Print Format found to patch.")
            return

    print(f"[SMRITI] Patching custom Print Format '{print_format_name}'...")
    if not frappe.db.exists("Print Format", print_format_name):
        print(f"[SMRITI] Error: Print Format '{print_format_name}' does not exist!")
        return
        
    pf = frappe.get_doc("Print Format", print_format_name)
    
    target = """                    <tr>
                        <td class="bold" style="padding: 2px 0;">Place of Supply:</td>
                        <td style="padding: 2px 0;">37-Andhra Pradesh</td>
                    </tr>"""
                    
    replacement = """                    <tr>
                        <td class="bold" style="padding: 2px 0;">Place of Supply:</td>
                        <td style="padding: 2px 0;">37-Andhra Pradesh</td>
                    </tr>
                    {% if doc.ewaybill %}
                    <tr>
                        <td class="bold" style="padding: 2px 0;">E-Way Bill No.:</td>
                        <td style="padding: 2px 0; color: #2e7d32; font-weight: bold;">{{ doc.ewaybill }}</td>
                    </tr>
                    {% endif %}
                    {% if doc.vehicle_no %}
                    <tr>
                        <td class="bold" style="padding: 2px 0;">Vehicle No.:</td>
                        <td style="padding: 2px 0; text-transform: uppercase;">{{ doc.vehicle_no }}</td>
                    </tr>
                    {% endif %}"""
                    
    if target in pf.html:
        pf.html = pf.html.replace(target, replacement)
        pf.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"[SMRITI] Success! Print Format '{print_format_name}' updated in database.")
    elif "{% if doc.ewaybill %}" in pf.html:
        print(f"[SMRITI] Print Format '{print_format_name}' is already patched and up to date.")
    else:
        print(f"[SMRITI] Error: Place of supply target layout block not found in '{print_format_name}' HTML!")


def create_default_admin_account():
    """Creates the default Admin (Business Owner) account if it does not exist.
    Uses admin email from site_config or falls back to 'admin@<site_name>'."""
    email = frappe.conf.get("smriti_admin_email") or f"admin@{frappe.local.site}"
    if not frappe.db.exists("User", email):
        try:
            import secrets
            doc = frappe.new_doc("User")
            doc.email = email
            doc.first_name = "Admin"
            doc.username = "Admin"
            doc.send_welcome_email = 0
            # C-06 FIX: Never hardcode passwords in source code.
            # Force the user to set their own password on first login.
            doc.reset_password_key = secrets.token_urlsafe(32)
            doc.append("roles", {"role": "SMRITI Store Manager"})
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.logger().info(f"[SMRITI] Created default Admin (Business Owner) account: {email}. Password reset required on first login.")
        except Exception as e:
            frappe.log_error(f"Error creating default Admin account: {str(e)}", "SMRITI Setup Error")


def seed_retail_defaults():
    """Seeds standard defaults for SMRITI Retail OS: Walk-In Customer and UPI Mode of Payment."""
    # 0. Ensure all Companies have a default Address (mandatory for Indian GST transactions)
    for comp in frappe.get_all("Company", pluck="name"):
        has_address = frappe.db.exists("Address", {"links.link_doctype": "Company", "links.link_name": comp})
        if not has_address:
            try:
                abbr = frappe.db.get_value("Company", comp, "abbr") or "CO"
                addr_name = f"{comp}-Registered"
                
                if not frappe.db.exists("Address", addr_name):
                    addr = frappe.new_doc("Address")
                    addr.address_title = comp
                    addr.address_type = "Office"
                    addr.address_line1 = "Primary Office Location"
                    addr.city = "Mumbai"
                    addr.state = "Maharashtra"
                    addr.country = "India"
                    addr.pincode = "400001"
                    addr.is_primary_address = 1
                    addr.is_shipping_address = 1
                    addr.is_your_company_address = 1
                    
                    gstin = frappe.db.get_value("Company", comp, "gstin")
                    if gstin:
                        addr.gstin = gstin
                        addr.gst_category = "Registered"
                    else:
                        addr.gst_category = "Unregistered"
                        
                    addr.append("links", {"link_doctype": "Company", "link_name": comp})
                    addr.insert(ignore_permissions=True)
                    print(f"[SMRITI] Created default Registered Address for Company {comp}")
            except Exception as e:
                frappe.log_error(f"Error seeding default Address for Company {comp}: {str(e)}", "SMRITI Setup Error")

    # 1. Walk-In Customer
    if not frappe.db.exists("Customer", "Walk-In Customer"):
        try:
            # Resolve non-group Customer Group
            cg = frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
            if not cg:
                if not frappe.db.exists("Customer Group", "All Customer Groups"):
                    cg_parent = frappe.new_doc("Customer Group")
                    cg_parent.customer_group_name = "All Customer Groups"
                    cg_parent.is_group = 1
                    cg_parent.insert(ignore_permissions=True)
                cg_doc = frappe.new_doc("Customer Group")
                cg_doc.customer_group_name = "Individual"
                cg_doc.parent_customer_group = "All Customer Groups"
                cg_doc.is_group = 0
                cg_doc.insert(ignore_permissions=True)
                cg = cg_doc.name
            
            # Resolve non-group Territory
            terr = frappe.db.get_value("Territory", {"is_group": 0}, "name")
            if not terr:
                if not frappe.db.exists("Territory", "All Territories"):
                    terr_parent = frappe.new_doc("Territory")
                    terr_parent.territory_name = "All Territories"
                    terr_parent.is_group = 1
                    terr_parent.insert(ignore_permissions=True)
                terr_doc = frappe.new_doc("Territory")
                terr_doc.territory_name = "India"
                terr_doc.parent_territory = "All Territories"
                terr_doc.is_group = 0
                terr_doc.insert(ignore_permissions=True)
                terr = terr_doc.name

            cust = frappe.new_doc("Customer")
            cust.customer_name = "Walk-In Customer"
            cust.customer_type = "Individual"
            cust.customer_group = cg
            cust.territory = terr
            cust.insert(ignore_permissions=True)
            print("[SMRITI] Seeded Walk-In Customer")
        except Exception as e:
            frappe.log_error(f"Error seeding Walk-In Customer: {str(e)}", "SMRITI Setup Error")

    # 2. UPI and other payment modes
    mops = ["Cash", "Bank", "UPI", "Card"]
    for mop in mops:
        if not frappe.db.exists("Mode of Payment", mop):
            try:
                doc = frappe.new_doc("Mode of Payment")
                doc.mode_of_payment = mop
                doc.insert(ignore_permissions=True)
                print(f"[SMRITI] Created Mode of Payment: {mop}")
            except Exception as e:
                frappe.log_error(f"Error creating Mode of Payment {mop}: {str(e)}", "SMRITI Setup Error")

        # Map accounts for each active company
        try:
            mop_doc = frappe.get_doc("Mode of Payment", mop)
            for comp in frappe.get_all("Company", pluck="name"):
                # Check if mapping already exists
                has_mapping = False
                for acc in mop_doc.accounts:
                    if str(acc.company).strip().upper() == str(comp).strip().upper():
                        has_mapping = True
                        break
                
                if not has_mapping:
                    # Resolve appropriate ledger
                    ledger = None
                    if mop == "Cash":
                        ledger = f"Cash - {frappe.db.get_value('Company', comp, 'abbr')}"
                        if not frappe.db.exists("Account", ledger):
                            ledger = frappe.db.get_value("Account", {"account_name": "Cash", "company": comp})
                    else:
                        ledger = f"Bank - {frappe.db.get_value('Company', comp, 'abbr')}"
                        if not frappe.db.exists("Account", ledger):
                            ledger = frappe.db.get_value("Account", {"account_type": "Bank", "company": comp})
                            if not ledger:
                                ledger = frappe.db.get_value("Account", {"account_name": ["like", "%Bank%"], "company": comp, "is_group": 0})
                    
                    if ledger:
                        mop_doc.append("accounts", {
                            "company": comp,
                            "default_account": ledger
                        })
            
            # Clean up accounts child table (deduplicate and remove orphaned deleted companies)
            seen_companies = set()
            clean_accounts = []
            for acc in mop_doc.accounts:
                comp_key = str(acc.company).strip().upper()
                if comp_key not in seen_companies and frappe.db.exists("Company", acc.company):
                    seen_companies.add(comp_key)
                    clean_accounts.append(acc)
            
            mop_doc.accounts = clean_accounts
            mop_doc.flags.ignore_links = True
            mop_doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Error mapping accounts for Mode of Payment {mop}: {str(e)}", "SMRITI Setup Error")

    frappe.db.commit()



