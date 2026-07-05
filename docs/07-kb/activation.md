---
Document ID: "KB-001"
Title: "SMRITI License Activation Guide"
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

# SMRITI License Activation Guide

This guide details how to activate SMRITI Retail OS, retrieve offline cryptographic keys, and manage license tier limits.

## 🔑 License Key Structure

SMRITI utilizes cryptographically signed, offline-verifiable keys to eliminate external server dependencies during activation. The format of the key is:

```text
SMRT-{VERSION}-{PAYLOAD}-{SIGNATURE}
```

- **SMRT**: Standard prefix.
- **VERSION**: Numerical key version (e.g. `1`).
- **PAYLOAD**: Base64URL-encoded JSON containing customer metadata:
  ```json
  {
    "cid": "cust_12345",
    "tier": "Enterprise",
    "exp": "2028-12-31",
    "iid": "installation_uuid",
    "iss": "ERPNBOOK"
  }
  ```
- **SIGNATURE**: First 16 hex digits of a HMAC-SHA256 signature calculated using the secret defined in `site_config.json`.

---

## 🚀 Step-by-Step Activation Protocol

To activate a new site license:

1. **Get Installation ID**: Navigate to the SMRITI License page (`/app/smriti-license`) and copy the unique **Installation ID** (UUID format).
2. **Request License Key**: Send your Installation ID and corporate registration details to `support@erpnbook.com` to receive a signed license key.
3. **Register the Key**:
   - Open the **Registration** tab on the license page.
   - Paste the received key into the input field.
   - Click the `🔑 Activate License` button.
4. **Validation Check**: SMRITI verifies the HMAC signature, matches the installation UUID, validates the expiration window, and updates the local state to `Active`.

---

## 📊 Subscription Tiers & Scale Limits

SMRITI enforces structural limits based on the active license tier:

| Parameter | Starter | Professional | Enterprise |
| :--- | :---: | :---: | :---: |
| **Max Store Warehouses** | 2 | 10 | Unlimited |
| **Active Cashiers** | 1 | 5 | Unlimited |
| **Pricing Schemes** | Standard Only | Advanced | Custom Scripts |
| **Offline Validation** | Yes | Yes | Yes |
| **API Support** | None | Standard Rest | Direct Sync |

---

## ⚠️ Troubleshooting Grace Periods

If a license expires or signature verification fails:
- The system enters a **7-day Grace Period**, showing an Amber warning banner on all terminals.
- After 7 days, the status shifts to `Expired`. The billing terminal locks, preventing cashier invoices until a new key is activated.
- If signature check fails with `Invalid Signature`, ensure the `smriti_license_secret` key in `site_config.json` matches the value used during key issuance.

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
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