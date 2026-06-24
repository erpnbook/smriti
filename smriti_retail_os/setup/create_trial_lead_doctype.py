"""
SMRITI Trial Lead DocType Creator
Run: bench --site smriti_retail execute smriti_retail_os.setup.create_trial_lead_doctype.main
"""
import frappe


def main():
    frappe.set_user('Administrator')

    if frappe.db.exists('DocType', 'SMRITI Trial Lead'):
        print('SMRITI Trial Lead DocType already exists. Skipping.')
        return

    doc = frappe.get_doc({
        'doctype':        'DocType',
        'name':           'SMRITI Trial Lead',
        'module':         'Smriti Retail Os',
        'is_single':      0,
        'is_submittable': 0,
        'track_changes':  1,
        'fields': [
            {
                'fieldname': 'store_name', 'label': 'Store Name',
                'fieldtype': 'Data', 'reqd': 1, 'in_list_view': 1,
            },
            {
                'fieldname': 'owner_name', 'label': 'Owner Name',
                'fieldtype': 'Data', 'reqd': 1, 'in_list_view': 1,
            },
            {
                'fieldname': 'mobile', 'label': 'Mobile',
                'fieldtype': 'Data', 'reqd': 1, 'in_list_view': 1,
                'unique': 1,
            },
            {
                'fieldname': 'city', 'label': 'City',
                'fieldtype': 'Data', 'in_list_view': 1,
            },
            {
                'fieldname': 'business_type', 'label': 'Business Type',
                'fieldtype': 'Data',
            },
            {
                'fieldname': 'plan_selected', 'label': 'Plan Selected',
                'fieldtype': 'Select',
                'options':   'starter\ngrowth\npro',
                'in_list_view': 1,
            },
            {
                'fieldname': 'warehouses', 'label': 'Warehouses',
                'fieldtype': 'Int', 'default': '1',
            },
            {
                'fieldname': 'monthly_sales', 'label': 'Monthly Sales (₹)',
                'fieldtype': 'Currency',
            },
            {
                'fieldname': 'source', 'label': 'Source',
                'fieldtype': 'Data', 'default': 'smriti-trial',
            },
            {
                'fieldname': 'status', 'label': 'Status',
                'fieldtype': 'Select',
                'options':   'New\nContacted\nDemo Scheduled\nConverted\nLost',
                'default':   'New', 'in_list_view': 1,
            },
            {
                'fieldname': 'submitted_at', 'label': 'Submitted At',
                'fieldtype': 'Datetime', 'read_only': 1,
            },
            {
                'fieldname': 'notes', 'label': 'Notes',
                'fieldtype': 'Small Text',
            },
        ],
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print('SMRITI Trial Lead DocType created successfully.')
    print('Fields: store_name, owner_name, mobile, city, business_type,')
    print('        plan_selected, warehouses, monthly_sales, source, status,')
    print('        submitted_at, notes')
