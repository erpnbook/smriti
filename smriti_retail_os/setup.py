import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup_smriti_retail_os():
    """
    Initializes custom fields, roles, and workspaces for standard DocTypes
    to extend ERPNext for SMRITI Retail OS.
    This function is upgrade-safe, idempotent, and runs during bench migrate.
    """
    # 1. Custom Fields setup
    custom_fields = {
        "Item": [
            {
                "fieldname": "custom_is_retail_item",
                "label": "Is Retail Item",
                "fieldtype": "Check",
                "default": "1",
                "insert_after": "item_name"
            },
            {
                "fieldname": "custom_department",
                "label": "Department",
                "fieldtype": "Link",
                "options": "Item Group",
                "insert_after": "custom_is_retail_item"
            },
            {
                "fieldname": "custom_gst_percentage",
                "label": "GST %",
                "fieldtype": "Select",
                "options": "\n0\n5\n12\n18\n28",
                "insert_after": "custom_department"
            },
            {
                "fieldname": "custom_mrp",
                "label": "MRP",
                "fieldtype": "Currency",
                "insert_after": "custom_gst_percentage"
            },
            {
                "fieldname": "custom_current_stock_html",
                "label": "Current Stock",
                "fieldtype": "HTML",
                "insert_after": "custom_mrp"
            },
            {
                "fieldname": "custom_barcode_size",
                "label": "Barcode Size",
                "fieldtype": "Select",
                "options": "\n50x25\n50x30\n75x50\n100x50",
                "insert_after": "custom_current_stock_html"
            }
        ],
        "Customer": [
            {
                "fieldname": "custom_address_text",
                "label": "Address",
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
                "label": "Address",
                "fieldtype": "Small Text",
                "insert_after": "supplier_name"
            },
            {
                "fieldname": "custom_credit_days",
                "label": "Credit Days",
                "fieldtype": "Int",
                "insert_after": "custom_address_text"
            }
        ],
        "POS Invoice": [
            {
                "fieldname": "custom_is_held",
                "label": "Is Held",
                "fieldtype": "Check",
                "default": "0",
                "insert_after": "customer"
            },
            {
                "fieldname": "custom_held_by",
                "label": "Held By",
                "fieldtype": "Link",
                "options": "User",
                "insert_after": "custom_is_held"
            },
            {
                "fieldname": "custom_hold_time",
                "label": "Hold Time",
                "fieldtype": "Datetime",
                "insert_after": "custom_held_by"
            }
        ],
    }

    create_custom_fields(custom_fields, ignore_validate=True)

    # Clean up custom SMRITI PIN from User DocType if it exists
    if frappe.db.exists("Custom Field", "User-custom_smriti_pin"):
        frappe.delete_doc("Custom Field", "User-custom_smriti_pin", ignore_permissions=True)
        frappe.db.commit()
    
    # 2. Programmatic Role Creation
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
            "label": "Retail Inventory",
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
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1}
        },
        "POS Invoice": {
            "SMRITI Cashier": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "POS Profile": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "Dashboard": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "Dashboard Chart": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "Number Card": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "POS Opening Entry": {
            "SMRITI Cashier": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "POS Closing Entry": {
            "SMRITI Cashier": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "Purchase Receipt": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "Purchase Order": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "Purchase Invoice": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "Stock Entry": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "Stock Reconciliation": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "POS Settings": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1}
        },
        "Warehouse": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1}
        },
        "Mode of Payment": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1}
        },
        "Batch": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1}
        },
        "Bin": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1}
        },
        "Sales Invoice": {
            "SMRITI Cashier": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "SMRITI Store Manager": {"read": 1, "write": 1, "create": 1, "submit": 1}
        },
        "Page": {
            "SMRITI Cashier": {"read": 1},
            "SMRITI Store Manager": {"read": 1}
        }
    }

    for doctype, roles_dict in doctype_permissions.items():
        for role, perms in roles_dict.items():
            dp_name = frappe.db.get_value("Custom DocPerm", {"parent": doctype, "role": role})
            if dp_name:
                dp = frappe.get_doc("Custom DocPerm", dp_name)
            else:
                dp = frappe.new_doc("Custom DocPerm")
                dp.parent = doctype
                dp.parenttype = "DocType"
                dp.parentfield = "permissions"
                dp.role = role

            dp.read = perms.get("read", 0)
            dp.write = perms.get("write", 0)
            dp.create = perms.get("create", 0)
            dp.submit = perms.get("submit", 0)
            dp.save(ignore_permissions=True)
            print(f"Configured SMRITI permissions on {doctype} for {role}")

    # 5. Programmatic Branding setup for SMRITI Retail OS
    # SVG logo path (served by Frappe asset pipeline from public/images/ root)
    SVG_LOGO   = "/assets/smriti_retail_os/images/logo.svg"

    # Website Settings
    if frappe.db.exists("DocType", "Website Settings"):
        web_settings = frappe.get_doc("Website Settings", "Website Settings")
        web_settings.app_name = "SMRITI Retail OS"
        web_settings.app_logo = SVG_LOGO
        web_settings.favicon = SVG_LOGO
        web_settings.splash_image = SVG_LOGO
        web_settings.brand_html = (
            f'<img src="{SVG_LOGO}" alt="SMRITI" '
            f'style="height:28px;width:auto;vertical-align:middle;margin-right:8px;"/>'
            f'<span style="font-weight:700;color:#9e77ed;font-family:Outfit,sans-serif;">SMRITI Retail OS</span>'
        )
        web_settings.save(ignore_permissions=True)
        print("SMRITI Retail OS branding configured in Website Settings")

    # Navbar Settings
    if frappe.db.exists("DocType", "Navbar Settings"):
        nav_settings = frappe.get_doc("Navbar Settings", "Navbar Settings")
        nav_settings.app_logo = SVG_LOGO
        nav_settings.app_title = "SMRITI Retail OS"
        nav_settings.save(ignore_permissions=True)
        print("SMRITI Retail OS branding configured in Navbar Settings")

    # System Settings
    if frappe.db.exists("DocType", "System Settings"):
        sys_settings = frappe.get_doc("System Settings", "System Settings")
        sys_settings.app_name = "SMRITI Retail OS"
        sys_settings.save(ignore_permissions=True)
        print("SMRITI Retail OS branding configured in System Settings")

    frappe.db.commit()
    print("SMRITI Retail OS setup successfully initialized!")

    # 6. Module Profiles
    setup_module_profiles()

    # 7. Role Profiles
    setup_role_profiles()


def setup_module_profiles():
    """
    Creates dedicated Frappe Module Profiles for SMRITI roles.

    Module Profile controls which sidebar modules (apps) are visible per user.
    Two profiles are provisioned:
      * SMRITI Cashier Profile        — billing-only, minimal footprint
      * SMRITI Store Manager Profile  — full retail + buying + stock view
    """

    # Modules visible to a Cashier (minimal — only what they need at the POS)
    cashier_modules = [
        "SMRITI Retail OS",
        "Accounts",
        "Selling",
        "Setup",
    ]

    # Modules visible to a Store Manager (broader retail footprint)
    manager_modules = [
        "SMRITI Retail OS",
        "Accounts",
        "Buying",
        "Stock",
        "Selling",
        "Setup",
        "Reports",
        "Integrations",
    ]

    profiles = {
        "SMRITI Cashier Profile": cashier_modules,
        "SMRITI Store Manager Profile": manager_modules,
    }

    for profile_name, allowed_modules in profiles.items():
        if frappe.db.exists("Module Profile", profile_name):
            doc = frappe.get_doc("Module Profile", profile_name)
            doc.block_modules = []
        else:
            doc = frappe.new_doc("Module Profile")
            doc.module_profile_name = profile_name

        # Frappe stores the modules a user CANNOT see as block_modules.
        # Discover all installed modules and block everything not in our allow-list.
        try:
            all_installed = frappe.get_all("Module Def", pluck="name")
        except Exception:
            all_installed = []

        for module in all_installed:
            if module not in allowed_modules:
                doc.append("block_modules", {"module": module})

        try:
            if doc.is_new():
                doc.insert(ignore_permissions=True)
            else:
                doc.save(ignore_permissions=True)
            print(f"[SMRITI] Module Profile created/updated: {profile_name}")
        except Exception as e:
            print(f"[SMRITI] Warning — could not save Module Profile '{profile_name}': {e}")

    frappe.db.commit()


def setup_role_profiles():
    """
    Creates dedicated Frappe Role Profiles for SMRITI roles.

    A Role Profile is a named bundle of roles that can be assigned to a user
    in one click — instead of manually assigning each role individually.

    Two profiles are provisioned:
      * SMRITI Cashier Role Profile       — assigns SMRITI Cashier role
      * SMRITI Store Manager Role Profile — assigns SMRITI Store Manager role
    """

    role_profiles = {
        "SMRITI Cashier Role Profile": [
            "SMRITI Cashier",
        ],
        "SMRITI Store Manager Role Profile": [
            "SMRITI Store Manager",
            "SMRITI Cashier",       # Managers can also operate the POS
        ],
    }

    for profile_name, roles in role_profiles.items():
        if frappe.db.exists("Role Profile", profile_name):
            doc = frappe.get_doc("Role Profile", profile_name)
            doc.roles = []  # Reset roles before re-applying
        else:
            doc = frappe.new_doc("Role Profile")
            doc.role_profile = profile_name

        for role in roles:
            # Only add the role if it actually exists
            if frappe.db.exists("Role", role):
                doc.append("roles", {"role": role})

        try:
            if doc.is_new():
                doc.insert(ignore_permissions=True)
            else:
                doc.save(ignore_permissions=True)
            print(f"[SMRITI] Role Profile created/updated: {profile_name}")
        except Exception as e:
            print(f"[SMRITI] Warning — could not save Role Profile '{profile_name}': {e}")

    frappe.db.commit()


def after_install():
    """Called once immediately after `bench install-app smriti_retail_os`."""
    setup_smriti_retail_os()
