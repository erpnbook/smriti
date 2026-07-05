---
Document ID: "KB-026"
Title: "Support Runbook — POS Terminal Not Loading"
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

# Support Runbook — POS Terminal Not Loading

> **Author:** Jawahar R Mallah (<jawahar.mallah@gmail.com>)  
> **Last Updated:** 2026-06-18  

This runbook guides support engineers in diagnosing and resolving POS register loading failures at store checkout lanes.

## 🚨 Symptom
The cashier opens the register page `/app/barcode#pos-dark` or `/app/billing` and encounters:
- A blank white screen.
- An infinite loading spinner.
- An "Access Denied" error overlay.

---

## 🔍 Diagnostics Step-by-Step

### Step 1: Check Browser Console Logs
1. Press `F12` to open Developer Tools.
2. Check the Console tab for red errors:
   - If `403 (Forbidden)` appears on api requests, the cashier does not have the **SMRITI Cashier** role assigned.
   - If `CSRFTokenError` is shown, the session token cookie is expired or mismatched.

### Step 2: Validate Cashier Role Mapping
Ensure the cashier's user profile is correctly configured:
```bash
docker exec -it smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.api.golive_api.get_cashier_roles --args '["cashier_username"]'
```
*Resolution*: If the role is missing, assign `SMRITI Cashier` via the User settings list.

### Step 3: Check Active POS Shift Logs
POS terminals require an active shift to initialize the register:
- Open the POS Opening Entry list.
- Verify if the cashier has an open shift for the selected POS profile.
- *Resolution*: If a shift is stuck in draft or mapped to a different cashier, cancel the draft and open a new shift.

### Step 4: Verify Progressive Web App (PWA) & Service Worker Registration
If the billing terminal fails to load assets offline or throws security/MIME-type errors:
1. Open Developer Tools (`F12`) and navigate to the **Application** (or **Service Workers**) panel.
2. Verify that `sw.js` is registered with the correct root scope `/` (e.g. `http://localhost:8765/`).
3. If a MIME-type error (`text/html`) is reported:
   - Check if `/sw.js` is being intercepted at the `before_request` hook in `boot.py` and returned as `application/javascript`.
   - Verify that Gunicorn has been restarted (`docker restart smriti_retail-backend-1`) to reload the python process.
4. If styling or JS assets are missing offline:
   - Check the `sw.js` precache cache list (`STATIC_ASSETS`) and ensure it contains `/assets/smriti_retail_os/css/smriti_tokens.css` and `/assets/smriti_retail_os/js/smriti_sidebar_standalone.js`.
   - Clear browser site data (Application -> Clear site data) and reload the page to trigger a fresh service worker cache pull.

### Step 5: Switcher Pill Truncation & Label Cutoffs
*Symptom*: Bottom-left theme selection switcher shows labels cut off (e.g., "Hybric" instead of "Hybrid", "Minima" instead of "Minimal").
*Diagnosis*: CSS flex wrap layout wraps items and cuts off text due to width constraints of the container.
*Resolution*: Modify `.smriti-standalone-theme-bar` inside `smriti_sidebar_standalone.css` to use CSS grid reordering instead of flex wrap:
```css
.smriti-standalone-theme-bar {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
}
```

### Step 6: Thin Wrapper Interception Page Loading Issues
*Symptom*: Accessing legacy Desk routes (e.g. `/app/smriti-barcode`, `/app/smriti-shift`, `/app/smriti-desk`) loads native Frappe desk screens or gives 404/500 errors.
*Diagnosis*: Interceptor helper missing, or fallback route mapping missing in `boot.py` for `/desk/setup-wizard`.
*Resolution*: Verify `boot.py` interceptor:
```python
def _map_smriti_path(path):
    # maps hyphenated paths to canonical standalone routes
```
Restart Gunicorn after updates (`docker restart smriti_retail-backend-1`).

---

## 🛠️ Escalation Matrix

If the POS screen still fails to load after completing the steps above:
1. **Level 1**: Contact the local Store Manager to verify POS Profile mappings.
2. **Level 2**: File a ticket with the SMRITI IT Support Desk (`support@erpnbook.com`) attaching console logs and the target Cashier username.

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.1 | 2026-06-28 | Jawahar R. Mallah | Added theme switcher grid layout & thin wrapper updates |
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