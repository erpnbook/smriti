import frappe
import json
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup_smriti_retail_os():
    """
    Initializes custom fields, roles, and workspaces for standard DocTypes
    to extend ERPNext for SMRITI Retail OS.
    """

    # 1. Custom Fields Provisioning
    custom_fields = {
        "User": [
            {
                "fieldname": "custom_is_smriti_user",
                "label": "Is SMRITI User",
                "fieldtype": "Check",
                "insert_after": "role_profile_name",
                "default": "1"
            }
        ],
        "POS Invoice": [
            {
                "fieldname": "custom_is_held",
                "label": "Is Held",
                "fieldtype": "Check",
                "insert_after": "status",
                "read_only": 1,
                "default": "0"
            },
            {
                "fieldname": "custom_held_by",
                "label": "Held By",
                "fieldtype": "Link",
                "options": "User",
                "insert_after": "custom_is_held",
                "read_only": 1
            },
            {
                "fieldname": "custom_hold_time",
                "label": "Hold Time",
                "fieldtype": "Datetime",
                "insert_after": "custom_held_by",
                "read_only": 1
            }
        ],
        "Item": [
            {
                "fieldname": "custom_mrp",
                "label": "MRP (Maximum Retail Price)",
                "fieldtype": "Currency",
                "insert_after": "standard_rate",
                "bold": 1
            },
            {
                "fieldname": "custom_gst_percentage",
                "label": "GST Percentage (%)",
                "fieldtype": "Select",
                "options": "\n0\n5\n12\n18\n28",
                "insert_after": "custom_mrp"
            },
            {
                "fieldname": "custom_is_retail_item",
                "label": "Is Retail Item",
                "fieldtype": "Check",
                "default": "1",
                "insert_after": "custom_gst_percentage"
            },
            {
                "fieldname": "custom_department",
                "label": "Department",
                "fieldtype": "Link",
                "options": "Item Group",
                "insert_after": "custom_is_retail_item"
            },
            {
                "fieldname": "custom_barcode_size",
                "label": "Barcode Size",
                "fieldtype": "Select",
                "options": "\n50x25\n50x30\n75x50\n100x50",
                "insert_after": "custom_department"
            },
            {
                "fieldname": "custom_current_stock_html",
                "label": "Current Stock HTML",
                "fieldtype": "HTML",
                "insert_after": "custom_barcode_size"
            }
        ],
        "Customer": [
            {
                "fieldname": "custom_address_text",
                "label": "Address Text",
                "fieldtype": "Small Text",
                "insert_after": "customer_name"
            },
            {
                "fieldname": "custom_birthday",
                "label": "Birthday",
                "fieldtype": "Date",
                "insert_after": "custom_address_text"
            },
            {
                "fieldname": "custom_anniversary",
                "label": "Anniversary",
                "fieldtype": "Date",
                "insert_after": "custom_birthday"
            }
        ],
        "Supplier": [
            {
                "fieldname": "custom_address_text",
                "label": "Address Text",
                "fieldtype": "Small Text",
                "insert_after": "supplier_name"
            },
            {
                "fieldname": "custom_credit_days",
                "label": "Credit Days",
                "fieldtype": "Int",
                "insert_after": "custom_address_text"
            }
        ]
    }

    create_custom_fields(custom_fields, ignore_validate=True)

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
        {
            "label": "Products",
            "type": "Link",
            "link_type": "DocType",
            "link_to": "Item",
            "label_for_links": "Simplified retail products catalog."
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

    if frappe.db.exists("Workspace", workspace_name):
        ws = frappe.get_doc("Workspace", workspace_name)
        ws.links = []
        for l in required_links:
            ws.append("links", l)
        ws.flags.ignore_links = True
        ws.save(ignore_permissions=True)
        print(f"Updated standard SMRITI Workspace: {workspace_name}")
    else:
        ws = frappe.new_doc("Workspace")
        ws.label = workspace_name
        ws.title = workspace_name
        ws.icon = "shopping-cart"
        ws.public = 1
        ws.is_standard = 1
        ws.module = "Custom"
        for l in required_links:
            ws.append("links", l)
        ws.flags.ignore_links = True
        ws.insert(ignore_permissions=True)
        print(f"Created custom SMRITI Workspace: {workspace_name}")

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
