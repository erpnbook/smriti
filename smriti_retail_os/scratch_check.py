import frappe

def run():
    print("--- RECENT ERROR LOGS ---")
    logs = frappe.get_all("Error Log", fields=["name", "creation", "method", "error"], order_by="creation desc", limit=10)
    for log in logs:
        print(f"Log: {log.name} | Created: {log.creation} | Method: {log.method}")
        print(log.error)
        print("-" * 50)
