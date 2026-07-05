---
Document ID: "KB-025"
Title: "Support Runbook — License Key Not Activating"
Owner: "Support Team"
Audience: "Support Engineer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# Support Runbook — License Key Not Activating

This runbook helps administrators diagnose and resolve cryptographic license key verification failures during store setup.

## 🚨 Symptom
The administrator enters a license key on the registration tab (`/app/smriti-license`) and receives one of these errors:
- `"Invalid Signature / Signature Mismatch"`
- `"Installation Binding Mismatch"`
- `"Expired Key"`

---

## 🔍 Diagnostics Step-by-Step

### Step 1: Verify Site Config Secret
HMAC signatures depend on the local secret key. Ensure your secret is set:
1. View the site configuration file:
   ```bash
   cat sites/smriti_retail/site_config.json
   ```
2. Verify that `smriti_license_secret` exists and matches the secret used by ERPNBook to sign the key.
3. *Resolution*: If the secret is missing or is using the development fallback key (`SMRITI-DEV-SECRET-...`), update `site_config.json` with your production key and clear the cache:
   ```bash
   bench --site smriti_retail clear-cache
   ```

### Step 2: Validate Installation UUID
License keys are bound to a specific server Installation ID:
1. Query the local installation ID:
   ```bash
   docker exec -it smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.api.licensing.get_installation_id
   ```
2. Compare the output to the `iid` parameter embedded in the license key payload.
3. *Resolution*: If they do not match, request a new license key bound to the correct Installation ID from `support@erpnbook.com`.

### Step 3: Check System Clock
HMAC expiration checks rely on the host system clock:
- Verify that the server timezone and date are set correctly:
  ```bash
  date
  ```
- *Resolution*: Sync the system clock with an NTP server to resolve false expiration errors:
  ```bash
  sudo ntpdate pool.ntp.org
  ```

### Step 4: Unstyled Billing Terminal (Flat Light-Blue/Grey Theme)
*Symptom*: The billing terminal at `/billing` loads with a flat light-blue/grey theme instead of the midnight dark theme, and the CGE features or pricing features are missing or not resolving.
*Diagnosis*: The SMRITI License key is unregistered or missing in the database, causing the UI engine's resolver to fallback to default light configurations.
*Resolution*: Verify if a license exists in the database. If missing, activate a valid Enterprise license key using direct database execution:
```sql
INSERT INTO `tabSMRITI License` (name, status, health, license_type, expiry_date, token) 
VALUES ('27AAXFT2508H1ZR-ENT-2030', 'Active', 'Healthy', 'Enterprise', '2030-01-01', 'mock_token');
```
Commit the changes and clear the cache:
```bash
bench --site smriti_retail clear-cache
```

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.1 | 2026-06-28 | Jawahar R. Mallah | Added unstyled billing terminal license check |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL