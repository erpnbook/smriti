import frappe
from smriti_retail_os.notification_studio.service.notification_service import create_notification

def run():
    # Clear existing notifications
    frappe.db.delete("SMRITI Notification Log")
    frappe.db.commit()

    # Create realistic notifications
    notifs = [
        ("Administrator", "purchase_approval", "Purchase Order Approved: PO-2026-00004", "Purchase Order PO-2026-00004 for Supplier Nike India Pvt Ltd has been approved.", "Purchase Order", "PO-2026-00004", "smriti-purchase"),
        ("Administrator", "grn_received", "GRN Received: GRN-2026-00124", "Goods Receipt Note GRN-2026-00124 has been received for Supplier Adidas Group.", "Purchase Receipt", "GRN-2026-00124", "smriti-purchase"),
        ("Administrator", "low_stock", "Low Stock Alert: Nike Pegasus 39 Running Shoes (Size 10)", "Nike Pegasus 39 Running Shoes (Size 10) in Main Warehouse is at 2 units (Reorder level: 5).", "Item", "NIKE-PEG-39-10", "stock-center"),
        ("Administrator", "invoice_due", "Sales Invoice Overdue: PINV-2026-015", "POS Invoice PINV-2026-015 for walk-in customer is overdue by 5 days.", "Sales Invoice", "PINV-2026-015", "billing-center"),
        ("Administrator", "sales", "New POS Invoice Submitted: POS-INV-2026-0428", "POS Invoice POS-INV-2026-0428 of amount INR 4,500.00 has been submitted.", "POS Invoice", "POS-INV-2026-0428", "billing-center"),
        ("Administrator", "system", "System Health: Database backup completed", "Scheduled backup process completed successfully. File size: 145 MB.", None, None, "smriti-dashboard")
    ]

    for args in notifs:
        create_notification(args[0], args[1], args[2], args[3], args[4], args[5], args[6])

    print("Successfully populated 6 notifications.")

if __name__ == '__main__':
    run()
