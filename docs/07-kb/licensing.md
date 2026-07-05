---
Document ID: "KB-010"
Title: "Frequently Asked Questions — Licensing"
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

# Frequently Asked Questions — Licensing

### Q1: What happens when the SMRITI license expires?
**A**: When the license expires, the system enters a **7-day Grace Period**, displaying an Amber warning banner on all terminals. If a new license key is not activated within these 7 days, the status changes to `Expired`. In this state, checkout registers lock, preventing cashier transactions until a valid license is entered.

### Q2: Can I move SMRITI to another server?
**A**: If your license is bound to a specific **Installation ID** (UUID), moving the system to another server (which generates a new Installation ID) will cause validation checks to fail, flagging the license as `Invalid`. To migrate to a new server, contact `support@erpnbook.com` to revoke your old key and issue a new one bound to the new Installation ID.

### Q3: How do I activate an offline license?
**A**: SMRITI utilizes an offline-first cryptographic signature system:
1. Navigate to `/app/smriti-license` and copy your unique Installation ID.
2. Share the ID with ERPNBook support to receive your signed license key (`SMRT-1-...`).
3. Paste the key into the **Registration** tab and click **Activate**. The validation is executed entirely locally on your server using the shared HMAC secret.

### Q4: Why am I getting an "Invalid Signature" error during activation?
**A**: This error occurs when the HMAC signature suffix of the key does not match the value computed by your server. Ensure that the `smriti_license_secret` parameter in your `sites/smriti_retail/site_config.json` file is correctly configured and matches the secret used during key generation.

### Q5: How do I check if my license is active and healthy?
**A**: Open the Go-Live Readiness dashboard (`/smriti-go-live`) or the License Management page (`/app/smriti-license`). A healthy, active license shows a green `PASS` badge next to the status indicators, listing the tier (Starter/Professional/Enterprise) and expiry date.

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