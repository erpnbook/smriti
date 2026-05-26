import frappe

def create_smriti_workspace():
    """
    Creates a dedicated SMRITI Retail OS Workspace in the sidebar.
    This serves as the 'Module Profile' for all retail operations.
    """
    workspace_name = "SMRITI Retail OS"
    
    if frappe.db.exists("Workspace", workspace_name):
        return

    doc = frappe.new_doc("Workspace")
    doc.label = workspace_name
    doc.title = workspace_name
    doc.icon = "shop" # Standard Lucide icon
    doc.module = "SMRITI Retail OS"
    doc.is_standard = 1
    doc.public = 1
    doc.sequence_id = 1
    
    # 1. Quick Access Links
    doc.append("links", {
        "label": "Retail Terminal",
        "type": "Link",
        "link_type": "Page",
        "link_to": "smriti-billing",
        "onboard": 1
    })
    doc.append("links", {
        "label": "Control Center",
        "type": "Link",
        "link_type": "Page",
        "link_to": "smriti-desk",
        "onboard": 1
    })
    doc.append("links", {
        "label": "Shift Manager",
        "type": "Link",
        "link_type": "Page",
        "link_to": "smriti-shift",
        "onboard": 0
    })

    # 2. Master Data Links
    doc.append("links", {
        "label": "Masters",
        "type": "Card Break",
        "onboard": 0
    })
    doc.append("links", {
        "label": "Quick Product Add",
        "type": "Link",
        "link_type": "DocType",
        "link_to": "Item",
        "dependencies": "Masters"
    })
    doc.append("links", {
        "label": "Customers",
        "type": "Link",
        "link_type": "DocType",
        "link_to": "Customer",
        "dependencies": "Masters"
    })

    # 3. Operations Links
    doc.append("links", {
        "label": "Operations",
        "type": "Card Break",
        "onboard": 0
    })
    doc.append("links", {
        "label": "Purchases (GRN)",
        "type": "Link",
        "link_type": "Page",
        "link_to": "smriti-purchase",
        "dependencies": "Operations"
    })
    doc.append("links", {
        "label": "Inventory Audit",
        "type": "Link",
        "link_type": "Page",
        "link_to": "smriti-inventory",
        "dependencies": "Operations"
    })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"Workspace '{workspace_name}' created successfully.")

if __name__ == "__main__":
    create_smriti_workspace()
