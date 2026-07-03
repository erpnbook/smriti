import frappe

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Not permitted", frappe.PermissionError)
    context.no_cache = 1
    context.cashier = frappe.session.user
    context.csrf_token = frappe.sessions.get_csrf_token()
    return context
