import frappe
import json
from smriti_retail_os.license.key_validator import generate_license_key
from smriti_retail_os.api.license_api import activate_license

def execute():
    frappe.set_user('Administrator')
    doc = frappe.get_single('SMRITI License')
    
    # Generate a valid signed key for Professional tier
    key = generate_license_key('CUST-DEMO-001', 'Professional', '2029-12-31', doc.installation_id or '*')
    print("Generated key:", key)
    
    # Activate
    res = activate_license(
        license_key=key,
        organization_name='SMRITI UAT Footwear Co',
        owner_name='Jawahar R Mallah',
        registered_email='admin@smriti.io',
        registered_mobile='9999999999',
        license_type='Professional'
    )
    print("Activation result:", json.dumps(res, indent=2))

execute()
