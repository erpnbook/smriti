# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/setup.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

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

    # Create SMRITI Print Template DocType specifically
    if not frappe.db.exists("DocType", "SMRITI Print Template"):
        try:
            doc = frappe.new_doc("DocType")
            doc.name = "SMRITI Print Template"
            doc.module = "SMRITI Retail OS"
            doc.custom = 1
            doc.autoname = "field:template_name"
            doc.editable_grid = 1
            doc.quick_entry = 1
            doc.track_changes = 1
            
            doc.append("fields", {
                "fieldname": "template_name",
                "fieldtype": "Data",
                "label": "Template Name",
                "reqd": 1,
                "unique": 1,
                "in_list_view": 1
            })
            
            doc.append("fields", {
                "fieldname": "label_size",
                "fieldtype": "Select",
                "label": "Label Size",
                "options": "\n50x25\n50x30\n75x50\n100x50\n106x55",
                "reqd": 1,
                "in_list_view": 1
            })
            
            doc.append("fields", {
                "fieldname": "printer_language",
                "fieldtype": "Select",
                "label": "Printer Language",
                "options": "\nZPL\nTSPL",
                "reqd": 1,
                "in_list_view": 1
            })
            
            doc.append("fields", {
                "fieldname": "raw_template",
                "fieldtype": "Code",
                "options": "text",
                "label": "Raw PRN Template",
                "reqd": 1
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
            frappe.log_error(f"Error creating custom SMRITI Print Template: {str(e)}")

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
                "template_name": "Zebra 50x25 Standard Label",
                "label_size": "50x25",
                "printer_language": "ZPL",
                "raw_template": "^XA\n^FO20,10^BCN,60,Y,N,N^FD{barcode}^FS\n^FO20,80^ADN,18,10^FD{item_name}^FS\n^FO20,100^ADN,18,10^FDMRP: Rs.{mrp}^FS\n^FO20,120^ADN,14,8^FD{brand} | Size: {size} | Color: {color}^FS\n^XZ"
            },
            {
                "template_name": "TSC 106x55 3-Up Footwear Label",
                "label_size": "106x55",
                "printer_language": "TSPL",
                "raw_template": "SIZE 106.6 mm, 55.4 mm\nGAP 3 mm, 0 mm\nSPEED 4\nDENSITY 14\nDIRECTION 0,0\nREFERENCE 0,0\nOFFSET 0 mm\nSET PEEL OFF\nSET CUTTER OFF\nSET TEAR ON\nCLS\nCODEPAGE 850\nTEXT 820,372,\"2\",180,2,2,\"{color}\"\nTEXT 702,318,\"2\",180,3,3,\"{size}\"\nTEXT 820,428,\"3\",180,2,2,\"{item_code}\"\nTEXT 556,335,\"4\",180,1,1,\"{mrp}/-\"\nTEXT 824,260,\"3\",180,1,1,\"{brand}\"\nTEXT 809,304,\"1\",180,2,2,\"SIZE-\"\nTEXT 475,401,\"1\",180,1,1,\"Footwear\"\nTEXT 596,401,\"1\",180,1,1,\"Commodity :\"\nTEXT 594,381,\"1\",180,1,1,\"Net Contents :\"\nTEXT 448,381,\"1\",180,1,1,\"1 Pair\"\nTEXT 600,301,\"1\",180,1,1,\"(Incl of all Taxes)\"\nTEXT 594,358,\"1\",180,1,1,\"Pkd On :\"\nTEXT 501,358,\"1\",180,1,1,\"{pkd_date}\"\nBARCODE 613,279,\"128\",95,0,180,2,4,\"{barcode}\"\nTEXT 597,176,\"3\",180,1,1,\"{barcode}\"\nPRINT 1,1"
            }
        ]
        for t in default_templates:
            if not frappe.db.exists("SMRITI Print Template", t["template_name"]):
                try:
                    doc = frappe.new_doc("SMRITI Print Template")
                    doc.update(t)
                    doc.insert(ignore_permissions=True)
                except Exception as e:
                    frappe.log_error(f"Error seeding print template {t['template_name']}: {str(e)}")
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
    frappe.db.commit()

def setup_smriti_retail_os():
    """
    Initializes custom fields, roles, and workspaces for standard DocTypes
    to extend ERPNext for SMRITI Retail OS.
    """
    # 0. Provision dynamic attribute Master DocTypes + preserve existing database entries
    create_master_doctypes()
    backup_and_seed_existing_data()
    seed_master_doctypes()

    # 1. Custom Fields Provisioning
    custom_fields = {
        "User": [
            {
                "fieldname": "custom_is_smriti_user",
                "label": "Is SMRITI User",
                "fieldtype": "Check",
                "insert_after": "role_profile_name",
                "default": "1",
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
                "fieldname": "custom_birthday",
                "label": "Birthday",
                "fieldtype": "Date",
                "insert_after": "custom_address_text",
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
                "fieldname": "custom_credit_days",
                "label": "Credit Days",
                "fieldtype": "Int",
                "insert_after": "custom_address_text",
                "module": "SMRITI Retail OS"
            }
        ]
    }

    create_custom_fields(custom_fields, ignore_validate=True)

    # Force sync all existing Custom Fields to SMRITI Retail OS module in the database
    for dt, fields in custom_fields.items():
        for f in fields:
            fieldname = f.get("fieldname")
            custom_field_name = f"{dt}-{fieldname}"
            if frappe.db.exists("Custom Field", custom_field_name):
                frappe.db.set_value("Custom Field", custom_field_name, "module", "SMRITI Retail OS")

    # 2. Role Provisioning
    # Clean up custom SMRITI PIN from User DocType if it exists
    if frappe.db.exists("Custom Field", "User-custom_smriti_pin"):
        frappe.delete_doc("Custom Field", "User-custom_smriti_pin", ignore_permissions=True)

    for role_name in ["SMRITI Cashier", "SMRITI Store Manager"]:
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.desk_access = 1
            role.insert(ignore_permissions=True)
            print(f"Created custom SMRITI role: {role_name}")

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
            "link_to": "smriti-billing",
            "label_for_links": "Keyboard-driven fast point-of-sale checkout."
        },
        {
            "label": "Day Open / Close",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti-shift",
            "label_for_links": "Open and close cashier shifts with denomination count."
        },
        {
            "label": "Inventory",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti-inventory",
            "label_for_links": "Mobile-ready quick scanning barcode inventory."
        },
        {
            "label": "Barcode Printing",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti-barcode",
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
            "link_to": "smriti-item-master",
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
            "link_to": "smriti-loyalty",
            "label_for_links": "Configure customer points tiers and conversion rules."
        },
        {
            "label": "Reports",
            "type": "Link",
            "link_type": "Page",
            "link_to": "smriti-reports",
            "label_for_links": "Visual sales, stock, and outstanding analytics."
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

