---
Document ID: "KB-022"
Title: "SMRITI Retail OS — Master Troubleshooting Guide"
Owner: "Support Team"
Audience: "Support Engineer"
Module: "CGE"
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

# SMRITI Retail OS — Master Troubleshooting Guide

> **Author:** Jawahar R. Mallah — Founder & Chief Architect, AITDL
> **Version:** 2.0 (Merged)
> **Last Updated:** June 2026
> **Applies To:** SMRITI Retail OS v1.x on Docker (Windows)

This is the **single authoritative troubleshooting reference** for SMRITI Retail OS. It merges all previously separate guides into one document, organized by domain.

---

## 📋 Quick Diagnostic Toolkit

Run these first before diving into any specific issue:

```powershell
# 1. Container health snapshot
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. Check recent logs of the backend container
docker logs smriti_retail-backend-1 --tail 50

# 3. Check recent logs of the Nginx frontend proxy
docker logs smriti_retail-frontend-1 --tail 50

# 4. Check files inside the backend container mount
docker exec smriti_retail-backend-1 ls -la /home/frappe/frappe-bench/apps/smriti_retail_os/

# 5. Read the Frappe application error log
docker exec smriti_retail-backend-1 tail -100 /home/frappe/frappe-bench/sites/smriti_retail/logs/frappe.log
```

### ✅ Expected Healthy Container State

| Container | Expected Status |
|---|---|
| `smriti_retail-frontend-1` | Up X minutes |
| `smriti_retail-backend-1` | Up X minutes |
| `smriti_retail-scheduler-1` | Up X minutes |
| `smriti_retail-queue-long-1` | Up X minutes |
| `smriti_retail-queue-short-1` | Up X minutes |
| `smriti_retail-websocket-1` | Up X minutes |
| `smriti_retail-redis-queue-1` | Up X minutes |
| `smriti_retail-redis-cache-1` | Up X minutes |
| `smriti_retail-db-1` | Up X minutes **(healthy)** |

> [!IMPORTANT]
> If **any** container shows `Restarting` → run `docker logs <container-name> --tail 30` to find the error before proceeding.

---

## 📂 Volume Mount & Container Name Reference

```
Windows Host (D:\Smriti_Retail_OS\)        →   Inside Container
apps/smriti_retail_os/   (must have files) →   /home/frappe/frappe-bench/apps/smriti_retail_os/
apps/india_compliance/   (must have files) →   /home/frappe/frappe-bench/apps/india_compliance/
```

Container naming follows the **folder name** of `compose.yaml`:

```
Folder: D:\Smriti_Retail_OS\  →  Prefix: smriti_retail
  smriti_retail-backend-1       smriti_retail-frontend-1
  smriti_retail-db-1            smriti_retail-scheduler-1
  smriti_retail-queue-long-1    smriti_retail-queue-short-1
  smriti_retail-websocket-1     smriti_retail-redis-queue-1
  smriti_retail-redis-cache-1
```

> [!TIP]
> Always run <code v-pre>docker ps --format "{{.Names}}"</code> first if unsure about container names.

---

## ⌨️ Quick Bench Command Reference

```bash
docker exec -it smriti_retail-backend-1 bench --site smriti_retail <command>
```

| Goal | Command |
|---|---|
| Run Migrations | `bench --site smriti_retail migrate` |
| Rebuild Assets | `bench build --app smriti_retail_os` |
| Clear Cache | `bench --site smriti_retail clear-cache` |
| Reset Admin Password | `bench --site smriti_retail set-admin-password <password>` |
| Run Tests | `bench --site smriti_retail run-tests --app smriti_retail_os` |
| Maintenance Mode On/Off | `bench --site smriti_retail set-maintenance-mode on/off` |
| Backup | `bench --site smriti_retail backup --with-files` |

---

# 🐳 SECTION 1 — Docker & Container Issues

---

## 🔴 Issue 1: "No such container: demotest-backend-1"

### Symptom
```
Error response from daemon: No such container: demotest-backend-1
```

### Root Cause
Docker Compose names containers using the **parent folder name** of the compose file. If your folder is `Smriti_Retail_OS`, containers are `smriti_retail_os-backend-1`, not `demotest-backend-1`.

### Fix
```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
docker exec -it smriti_retail-backend-1 bench --site smriti_retail migrate
```

---

## 🔴 Issue 2: Backend Keeps Restarting — "neither 'setup.py' nor 'pyproject.toml' found"

### Symptom
```
smriti_retail-backend-1  Restarting (1) 58 seconds ago
ERROR: ../../apps/smriti_retail_os does not appear to be a Python project
```

### Root Cause
The `apps/smriti_retail_os/` directory on the Windows host is **empty**. Volume mount puts an empty folder in the container; pip cannot install the app.

### Fix
```powershell
Get-ChildItem D:\Smriti_Retail_OS\apps\smriti_retail_os

# If empty — copy from workspace
Copy-Item -Path "D:\Smriti_Retail_OS\apps\smriti_retail_os\*" `
          -Destination "D:\demotest\apps\smriti_retail_os\" `
          -Recurse -Force

docker compose restart backend scheduler queue-long queue-short
```

---

## 🔴 Issue 3: "wait-for-it: waiting 120 seconds for db:3306"

### Root Cause
MariaDB takes 30–90 seconds to initialize on first launch. **This is normal.**

### Fix
Wait. If it times out after 2 minutes:
```powershell
docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String "db"
docker logs smriti_retail-db-1 --tail 30
Get-PSDrive C | Select-Object Used, Free   # Check disk space
```

---

## 🔴 Issue 4: "ERPNEXT_VERSION variable is not set"

### Root Cause
The `.env` file is missing or the variable is unset.

### Fix
```powershell
Copy-Item example.env .env
notepad .env   # Set ERPNEXT_VERSION=version-15
```

> [!NOTE]
> This is a cosmetic warning and does not crash anything.

---

## 🔴 Issue 5: "Site Already Exists" / create-site Fails

### Root Cause
1. Previously initialized site (usually safe — just wait for healthy status).
2. Half-initialized volumes from a failed previous run.
3. Docker OOM — ERPNext creates 1000+ tables; insufficient RAM crashes the DB.

### Fix — Safe Reset (destroys data)
```powershell
docker compose -f pwd.yml down -v
docker compose -f pwd.yml up -d
```

### Fix — WSL2 Memory
Add to `%USERPROFILE%\.wslconfig`:
```ini
[wsl2]
memory=8GB
```
Then run: `wsl --shutdown`

---

## 🔴 Issue 6: Nginx "502 Bad Gateway"

### Root Cause
Nginx cached the backend's old container IP after a restart.

### Fix
```powershell
docker restart smriti_retail-frontend-1
```

---

## 🔴 Issue 7: Socket.IO "Invalid Origin" Error

### Fix
```bash
docker exec smriti_retail-backend-1 bench config set-common-config -c allow_cors_origin "http://localhost:8765"
docker compose restart websocket
```

---

## 🔴 Issue 8: ModuleNotFoundError: 'erpnextindia_compliance'

### Root Cause
`apps.txt` is corrupted — `erpnext` and `india_compliance` lines merged into one.

### Verify
```powershell
docker exec smriti_retail-backend-1 cat /home/frappe/frappe-bench/sites/apps.txt
# BAD:  erpnextindia_compliance   ← merged!
```

### Fix
```powershell
docker exec smriti_retail-backend-1 bash -c "printf 'frappe\nerpnext\nindia_compliance\nsmriti_retail_os\n' > /home/frappe/frappe-bench/sites/apps.txt"
docker compose restart scheduler queue-long queue-short
```

> [!WARNING]
> Order matters: `frappe` first, then `erpnext`, then dependent apps. One app per line.

---

## 🔴 Issue 9: "404 Not Found: smriti_retail does not exist" — Site Never Created

### Fix — Step 1: Set Common Config (if `common_site_config.json` is empty `{}`)
```powershell
docker exec smriti_retail-backend-1 bash -c "
  bench set-config -g db_host db &&
  bench set-config -gp db_port 3306 &&
  bench set-config -g redis_cache 'redis://redis-cache:6379' &&
  bench set-config -g redis_queue 'redis://redis-queue:6379' &&
  bench set-config -g redis_socketio 'redis://redis-queue:6379' &&
  bench set-config -gp socketio_port 9000
"
```

### Fix — Step 2: Create Site
```powershell
docker exec smriti_retail-backend-1 bench new-site `
  --mariadb-user-host-login-scope='%' `
  --admin-password=admin `
  --db-root-username=root `
  --db-root-password=admin `
  --install-app erpnext `
  --install-app india_compliance `
  --install-app smriti_retail_os `
  --set-default smriti_retail
```

---

# 🐍 SECTION 2 — Python & Migration Issues

---

## 🔴 Issue 10: bench migrate Fails — `AttributeError: module 'smriti_retail_os.setup' has no attribute 'setup_smriti_retail_os'`

### Symptom
```
Executing `after_migrate` hooks...
AttributeError: module 'smriti_retail_os.setup' has no attribute 'setup_smriti_retail_os'
```

### Root Cause
A **directory named `setup/`** exists alongside `setup.py`. Python resolves **packages over modules** of the same name — `smriti_retail_os.setup` resolves to `setup/__init__.py` (empty) instead of `setup.py`.

```
smriti_retail_os/
  setup.py      ← has setup_smriti_retail_os()  ✅
  setup/        ← empty __init__.py              ❌ SHADOWS setup.py
    __init__.py
```

### Diagnose
```powershell
docker exec smriti_retail-backend-1 bash -c "cd /home/frappe/frappe-bench && env/bin/python3 -c 'import smriti_retail_os.setup; print(smriti_retail_os.setup.__file__)'"
# BAD:  .../setup/__init__.py
# GOOD: .../setup.py
```

### Fix
```powershell
# Rename on Windows host (propagates via volume mount)
Rename-Item "d:\Smriti_Retail_OS\apps\smriti_retail_os\smriti_retail_os\setup" "setup_scripts"

# Rename inside container (for immediate effect)
docker exec smriti_retail-backend-1 bash -c "mv .../smriti_retail_os/setup .../smriti_retail_os/setup_scripts"

# Re-run
docker exec smriti_retail-backend-1 bench --site smriti_retail migrate
```

> [!WARNING]
> **Never name a directory the same as an existing `.py` module in the same package.** Risky names: `setup/`, `hooks/`, `boot/`, `utils/` (if `utils.py` also exists).

---

## 🟡 Issue 11: Running Migrations After Code Changes

### When to Run
After pulling new code, adding DocTypes/fields, or updating app version.

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"   # Confirm backend is UP
docker exec smriti_retail-backend-1 bench --site smriti_retail migrate
```

### If Migration Fails
```powershell
docker exec smriti_retail-backend-1 tail -100 /home/frappe/frappe-bench/sites/smriti_retail/logs/frappe.log
```

---

# 🎨 SECTION 3 — UI, Templates & Assets

---

## 🔴 Issue 12: `/smriti` Returns 500 — `RecursionError: maximum recursion depth exceeded`

### Symptom
```
RecursionError: maximum recursion depth exceeded
  File "smriti_token_loader.html", line 6
    @usage: {%- include "smriti_retail_os/templates/includes/smriti_token_loader.html" -%}
  [Previous line repeated 972 more times]
```

### Root Cause
A `{%- include -%}` Jinja tag was placed inside an HTML `<!-- comment -->` block as a usage example. **Jinja2 does NOT suppress tag execution inside HTML comments.** When `smriti-home.html` uses `{% extends %}`, the tag executes and the file includes itself infinitely.

### Affected Pattern (remove `{%- ... -%}` from comment)
```html
<!-- WRONG — Jinja executes this even inside a comment -->
<!-- @usage: {%- include "smriti_retail_os/templates/includes/smriti_token_loader.html" -%} -->

<!-- CORRECT — plain text, safe -->
<!-- @usage: include smriti_retail_os/templates/includes/smriti_token_loader.html -->
```

### Fix
Edit all three affected include files and remove the Jinja delimiters from the `@usage` line:
- `templates/includes/smriti_token_loader.html`
- `templates/includes/smriti_topbar.html`
- `templates/includes/smriti_sidebar.html`

Then clear template cache:
```powershell
docker exec smriti_retail-backend-1 bench --site smriti_retail clear-cache
# If error persists — gunicorn holds old compiled cache in memory:
docker restart smriti_retail-backend-1
```

> [!IMPORTANT]
> **Rule:** Never put `{% %}`, `{{ }}`, or `{%- -%}` Jinja tags inside HTML `<!-- -->` comments. Use Jinja comments `{# ... #}` to suppress execution.

> [!NOTE]
> `bench clear-cache` clears Redis/DB cache but does NOT flush gunicorn's in-process Jinja compiled templates. A container restart is needed to fully reload from disk.

---

## 🔴 Issue 13: Blank or Unstyled UI (CSS/JS MIME-type Errors)

### Symptom
```
Refused to apply style because its MIME type ('text/html') is not a supported stylesheet MIME type.
```

### Fix
```bash
docker exec smriti_retail-backend-1 bench build --app smriti_retail_os
docker exec smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.sync_assets.sync_assets
docker restart smriti_retail-frontend-1
```

---

## 🔴 Issue 14: Frontend Shows Old Code — Changes Not Reflected

```powershell
docker exec smriti_retail-backend-1 bench --site smriti_retail clear-cache
docker exec smriti_retail-backend-1 bench build --app smriti_retail_os
docker restart smriti_retail-backend-1   # Flush in-memory compiled templates
```

---

## 🔴 Issue 15: Frappe Jinja `UndefinedError: 'context' is undefined`

### Root Cause
Frappe **automatically unpacks** the `get_context()` return dict into the Jinja namespace. `context` itself does not exist in templates — only its keys do.

```html
<!-- ❌ WRONG -->
<h1>{{ context.company }}</h1>

<!-- ✅ CORRECT -->
<h1>{{ company }}</h1>
<div>{{ user_name or 'Guest' }}</div>
```

---

## 🔴 Issue 16: Stale Redis Cache After Config / Company Changes

```bash
docker exec smriti_retail-backend-1 bench --site smriti_retail clear-cache
```

---

# 🔑 SECTION 4 — Authentication & Database

---

## 🔴 Issue 17: "Invalid credentials" / Lost Admin Password

```bash
docker exec smriti_retail-backend-1 bench --site smriti_retail set-admin-password "YourNewSecurePassword"
```

---

## 🔴 Issue 18: CSRF Token Errors on Standalone SMRITI Pages

### Symptom
```
Failed to load data: {"message":"Invalid Request"...}
```

### Fix — Page Controller (`page.py`)
```python
def get_context(context):
    context.no_cache = 1
    context.csrf_token = frappe.sessions.get_csrf_token()
```

### Fix — JavaScript
```javascript
const headers = { 'Content-Type': 'application/json' };
if (window.csrf_token) headers['X-Frappe-CSRF-Token'] = window.csrf_token;
fetch('/api/method/...', { method: 'POST', headers, body: JSON.stringify(data) });
```

---

# 🧪 SECTION 5 — Unit Tests

---

## 🔴 Issue 19: "LinkValidationError: Transit not found in Warehouse Type"

### Fix
```python
frappe.get_doc({"doctype": "Warehouse Type", "name": "Transit"}).insert(ignore_if_duplicate=True)
```

---

## 🔴 Issue 20: "MandatoryError: cost_center" on Invoice Saves

### Fix
```python
company = frappe.defaults.get_defaults().get("company")
cc = frappe.get_value("Company", company, "cost_center")
for item in invoice.items:
    item.cost_center = cc
```

---

# 🏪 SECTION 6 — Business Module Issues

---

## 🔴 Issue 21: CGE — Campaign Budget Limit Exceeded

### Symptom
```
Campaign budget limit exceeded for campaign [Campaign Name].
```

### Fix
1. Increase `budget_limit` at `/app/smriti-coupon-campaign`.
2. Release stale cart reservations:
```bash
bench --site smriti_retail execute smriti_retail_os.cge.service.cge_service.CGECampaignManager.release_expired_reservations
```

---

## 🔴 Issue 22: CGE — "Error posting CGE Journal Entry: Account not found"

### Fix
Manually create missing accounts in ERPNext Chart of Accounts:
- **Cashback Liability** → Parent: `Current Liabilities` → Type: `Liability`
- **Promotion Expense** → Parent: `Indirect Expenses` → Type: `Expense`

---

## 🔴 Issue 23: CGE — LinkValidationError on Rule Trace Logs

### Fix
```python
log_doc.insert(ignore_permissions=True, ignore_links=True)
```

---

## 🔴 Issue 24: SFC — Commission Missing or Incorrect

### Diagnostics Checklist
1. **Customer Ownership**: `posting_date` within `start_date`/`end_date`, `is_active = 1`.
2. **Target Split**: `primary_split_pct + secondary_split_pct = 100`.
3. **Rule Precedence**: Employee-level (highest) → Company-level → Settings fallback.
4. **Revenue Threshold**: If `Attributed Revenue < min_revenue_threshold`, commission = `0.0` is correct.

### Escalation
- L1: Store Manager — manual adjustment lines in Settlement.
- L2: `support@erpnbook.com` with invoice ID + employee code.

---

## 🔴 Issue 25: Go-Live Checklist Shows FAIL / WARN

**CSRF on page load** → Add `context.csrf_token = frappe.sessions.get_csrf_token()` to controller.

**Catalog FAIL** → Check:
```sql
SELECT count(*) FROM `tabItem` WHERE disabled=0 AND is_sales_item=1 AND maintain_stock=1;
-- Must be ≥ 5
```

**POS / Warehouse mismatch** → Verify POS Profiles are linked to active warehouses and company has at least one active cost center.

---

## 🔴 Issue 26: Backup — GPG Decryption Failed

```bash
gpg --verbose --decrypt --passphrase "full_merged_key" --output test.sql.gz smriti_backup-v1.enc
```
Fragments must be merged in order: Fragment 01 + Fragment 02.

---

## 🔴 Issue 27: Backup — Table Locked During Extraction

```bash
bench --site smriti_retail backup --with-files --skip-lock-tables
```

---

## 🔴 Issue 28: Restore — SQL Constraint Violations

```bash
bench --site smriti_retail set-maintenance-mode on
bench --site smriti_retail restore decrypted_backup.sql.gz --force --db-root-username root --db-root-password admin
bench --site smriti_retail set-maintenance-mode off
```

---

## 🔴 Issue 39: Platform Center Backup Fails with "new_backup() got an unexpected keyword argument 'with_files'"

### Symptom
When triggering a manual backup from the SMRITI Platform Center admin console, the backup fails immediately with the traceback showing:
`TypeError: new_backup() got an unexpected keyword argument 'with_files'`

### Root Cause
In Frappe v15 and v16, the deprecated `with_files` argument has been completely removed from `new_backup()`. Calling it with this parameter raises a python `TypeError`.

### Fix
Update the `new_backup()` calls to use the newer `ignore_files` parameter:
1. Replace `new_backup(with_files=True)` with `new_backup(ignore_files=False, force=True)`.
2. Replace `new_backup(with_files=False)` with `new_backup(ignore_files=True, force=True)`.
3. Construct and return a JSON-serializable `data` dict from the resulting `BackupGenerator` instance attributes (like `backup_path_db` and `backup_path_files`).
This is fully resolved in the core SMRITI `platform_api.py` module.

---

# ⚙️ SECTION 7 — Setup Wizard & Configure Portal

---

## 🔴 Issue 29: "Cannot select a Group type Customer Group"

### Fix
```python
is_group = frappe.db.get_value("Customer Group", customer_group, "is_group")
if is_group:
    leaf_group = "Individual - " + company_abbr
    if not frappe.db.exists("Customer Group", leaf_group):
        cg = frappe.new_doc("Customer Group")
        cg.customer_group_name = leaf_group
        cg.parent_customer_group = customer_group
        cg.is_group = 0
        cg.insert(ignore_permissions=True)
    customer_group = leaf_group
```

---

## 🔴 Issue 30: "Please set default Cash or Bank account in Mode of Payments"

### Fix
```python
def link_mode_of_payment_account(mode_of_payment, company, account):
    doc = frappe.get_doc("Mode of Payment", mode_of_payment)
    if not any(r.company == company for r in doc.accounts):
        doc.append("accounts", {"company": company, "default_account": account})
        doc.save(ignore_permissions=True)
        frappe.db.commit()
```

---

## 🔴 Issue 31: POS Profile Creation Fails — write_off_account Mandatory

### Fix
```python
write_off_account = frappe.db.get_value("Account", {"account_type": "Write Off", "company": company_name}, "name")
cost_center = frappe.db.get_value("Cost Center", {"is_group": 0, "company": company_name}, "name")
pos_profile.write_off_account = write_off_account
pos_profile.write_off_cost_center = cost_center
pos_profile.insert(ignore_permissions=True)
```

---

## 🔴 Issue 32: Company Creation — "LinkValidationError: Transit not found in Warehouse Type"

### Root Cause
ERPNext auto-creates warehouses when saving a Company. On clean DBs (setup wizard bypassed), `Warehouse Type` records don't exist.

### Fix — Pre-seed Warehouse Types
```python
for wt_name in ["All", "Transit", "Bonded", "Consignment", "Spares", "Work In Progress"]:
    if not frappe.db.exists("Warehouse Type", wt_name):
        wt = frappe.new_doc("Warehouse Type")
        wt.name = wt_name
        wt.warehouse_type = wt_name
        wt.insert(ignore_permissions=True)
frappe.db.commit()
```

---

## 🔴 Issue 33: Bank Account Duplication / Idempotency Failure

### Root Cause
`Bank Account` is autonamed from `bank_account_no`, not a custom name.

### Fix
```python
existing = frappe.db.get_value("Bank Account", {"bank_account_no": bank_account_no}, "name")
if not existing:
    ba = frappe.new_doc("Bank Account")
    # ... set fields
    ba.insert(ignore_permissions=True)
else:
    ba = frappe.get_doc("Bank Account", existing)
    ba.branch_code = info.get("branch_code")
    ba.save(ignore_permissions=True)
frappe.db.commit()
```

---

## 🔴 Issue 40: Category Master Fails on Fresh Install with LinkValidationError: "Could not find Parent Item Group: All Item Groups"

### Symptom
When creating a category from the SMRITI Category Master page on a fresh installation, the insertion fails with:
`LinkValidationError: Could not find Parent Item Group: All Item Groups`

### Root Cause
SMRITI bypasses the default Frappe Setup Wizard to present a unified SMRITI portal. As a result, standard ERPNext seeding of the root `Item Group` named `All Item Groups` is skipped. When creating a new category, SMRITI attempts to set the parent to `All Item Groups` which is missing from the database.

### Fix
1. **Setup-time Seeding:** A seeding hook has been added to `setup_smriti_retail_os` in `setup.py` that automatically creates the root `Item Group` if it is missing:
   ```python
   if not frappe.db.exists("Item Group", "All Item Groups"):
       frappe.get_doc({
           "doctype": "Item Group",
           "item_group_name": "All Item Groups",
           "is_group": 1,
           "parent_item_group": ""
       }).insert(ignore_permissions=True)
   ```
2. **Runtime Guard:** A runtime safety check `_ensure_root_item_group()` has been added to `create_category` in `category_api.py` to create the root group on-demand:
   ```python
   def _ensure_root_item_group():
       if not frappe.db.exists("Item Group", "All Item Groups"):
           root = frappe.get_doc({
               "doctype": "Item Group",
               "item_group_name": "All Item Groups",
               "is_group": 1,
               "parent_item_group": ""
           })
           root.insert(ignore_permissions=True)
           frappe.db.commit()
   ```

---

# 🖨️ SECTION 8 — Peripherals & Label Printing

---

## 🔴 Issue 34: QZ Tray Not Connected

1. Download & install QZ Tray on the client computer.
2. Launch QZ Tray — verify system tray icon appears.
3. Open `https://localhost:8182` → **Advanced → Proceed to localhost (unsafe)** to whitelist the cert.
4. Refresh SMRITI Label Studio (`/barcode`).

---

## 🔴 Issue 35: USB Label Printer Not Detected

1. Ensure printer is powered on and USB connected.
2. Install manufacturer driver (Zebra / TSC / etc.).
3. Verify printer appears in Windows **Settings → Printers & Scanners**.
4. Click **Refresh Printers** in Label Studio.

---

# ⚠️ SECTION 9 — Windows Execution Policy

---

## 🔴 Issue 36: "SecurityError: Running scripts is disabled on this system"

```powershell
PowerShell -ExecutionPolicy Bypass -File .\install.ps1
```

---

# 💣 SECTION 10 — Full Stack Reset (Nuclear Option)

> [!CAUTION]
> This permanently deletes all local database records and file attachments. **Development only.**

```powershell
cd D:\Smriti_Retail_OS

# 1. Destroy all containers and volumes
docker compose -f pwd.yml down -v

# 2. Re-start stack (triggers fresh site creation ~3–5 min)
docker compose -f pwd.yml up -d

# 3. Monitor creation
docker compose logs -f backend

# 4. After site is up — rebuild assets
docker exec smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.sync_assets.sync_assets
docker restart smriti_retail-frontend-1
```

---

# 🧭 SECTION 11 — SMRITI Navigation Manager (SNM)

---

## 🔴 Issue 37: Custom Navigation Changes Do Not Appear in Sidebar

### Symptom
An administrator changes a menu setting (e.g. hides or re-labels an item) in the Navigation Override DocType, but users still see the old static layout.

### Root Cause
1. **Redis Caching:** SMRITI caches resolved navigation trees per user/company context in Redis for optimal performance.
2. **Missing Assignment:** The user has not been correctly mapped to the updated Navigation Profile via the `SMRITI Navigation Assignment` DocType.

### Fix
1. Clear the navigation cache manually inside the container:
   ```bash
   docker exec -it smriti_retail-backend-1 bench --site smriti_retail execute smriti_retail_os.navigation.navigation_service.invalidate_navigation_cache
   ```
2. Verify profile assignments:
   - Check the `SMRITI Navigation Assignment` list view.
   - Verify the priority values: Assignments resolve sorted by priority (e.g., User = 50, Role = 30, Company = 20, Global = 10). If a lower-priority profile matches, make sure it is not overriding your settings.

---

## 🔴 Issue 38: Command Error "SQL functions are not allowed as strings in SELECT: max(modified)"

### Symptom
The resolver crashes with a ValidationError pointing to select function constraints.

### Root Cause
SQL aggregation functions in select strings are blocked in newer versioned query builders.

### Fix
Use order-by arrays instead of raw select strings to retrieve the latest entry. This has been fully resolved inside the core `navigation_service.py` module.

---

## 🔴 Issue 41: Barcode Center Console Error — "SyntaxError: Unexpected token '<'" & Favicon 404

### Symptom
The browser console on the Barcode Center / Label Studio page shows:
- `barcode-center:6 Uncaught SyntaxError: Unexpected token '<'`
- `favicon.ico:1 Failed to load resource: the server responded with a status of 404 (Not Found)`

### Root Cause
1. **SyntaxError:** Internal scripts (e.g. `smriti_sidebar_standalone.js`, `smriti_ui_resolver.js`) were loaded using version-pinned query parameters (like `?v=2.0.7`, `?v=2.0.9`). If `bench build` was not executed or after version upgrades, these scripts fail to load, causing the server to return the HTML 404/redirect page. The browser attempts to parse the HTML string as JavaScript, raising the `<` SyntaxError.
2. **Favicon 404:** The `favicon.ico` was missing from individual templates, causing browser diagnostic requests to fail.

### Fix
1. **Remove Version Query Strings:** All hardcoded version strings (`?v=2.0.7`, etc.) pointing to local SMRITI assets have been stripped from the `www/*.html` templates.
2. **Global Favicon:** Added the favicon link tag globally inside `smriti_token_loader.html`:
   ```html
   <link rel="icon" href="/assets/smriti_retail_os/images/icon-192.png" type="image/png">
   ```
3. **Rebuild Assets:** Run esbuild inside the backend container to package the linked assets:
   ```powershell
   docker compose -f pwd.yml exec backend bench build --app smriti_retail_os
   docker compose -f pwd.yml restart backend
   ```

---

*Last Updated: June 2026 | SMRITI Retail OS Master Troubleshooting Guide v2.3*
*Author: Jawahar R. Mallah — Founder & Chief Architect, AITDL*


## Revision History

| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |
| 1.1.0 | 2026-06-28 | Jawahar R. Mallah | Added Section 11 for SMRITI Navigation Manager (SNM) |
| 1.2.0 | 2026-06-29 | Jawahar R. Mallah | Added Issues 39, 40, and 41 (Backup/Seeding/SyntaxError fixes) |
| 1.3.0 | 2026-06-30 | Jawahar R. Mallah | Added Issue 42 (Style/Article No 4-step resolution + prnContent dict extraction fix) |
| 1.4.0 | 2026-06-30 | Jawahar R. Mallah | Added Issue 43 (Barcode Studio navigation group consolidation — Barcode Center retired) |

---

## Issue 42 — Style / Article No Not Printing Correctly in PRN Labels

**Symptom:** `{style}` token on variant items prints the full SKU code (e.g., `BBM-0001-6`) instead of the parent template / Article No. `{style_code}` and `{variant_template}` tokens show blank even when configured in the print template mapping.

**Root Cause (3-part):**

### Gap 1 — `{style}` resolution was SKU-split only (Step 4 only)
`get_item_print_details()` in `barcode_api.py` resolved `style` with a single line:
```python
style = item_code.split("-")[0] if "-" in item_code else item_code
```
This only performed Step 4 (SKU prefix split). For variant items like `BBM-0001-6`, the parent template (`BBM-0001`) is stored in `item_doc.variant_of` — but the code never checked it. Result: `{style}` printed `BBM`, not `BBM-0001`.

### Gap 2 — `{style_code}` token did not exist
The return dict from `get_item_print_details()` had no `"style_code"` key. Any template using `{style_code}` printed blank.

### Gap 3 — `{variant_template}` token did not exist
Same as above — `"variant_template"` key was absent from the return dict.

**Fix Applied — `barcode_api.py` (commit `efcd7e5`):**

Replaced single-step SKU split with 4-step priority resolution:
```python
# Step 1: variant_of (ERP Variant parent template — most authoritative for variant items)
style = item_doc.get("variant_of") or ""

# Step 2: Explicit custom_style_code field
if not style:
    if item_doc.meta.has_field("custom_style_code"):
        style = item_doc.get("custom_style_code") or ""

# Step 3: Explicit style_no field
if not style:
    if item_doc.meta.has_field("style_no"):
        style = item_doc.get("style_no") or ""

# Step 4: SKU parsing — last resort
if not style:
    style = item_code.split("-")[0] if "-" in item_code else item_code
```

Added two new keys to the return dict:
```python
"style_code": item_doc.get("custom_style_code") or item_doc.get("style_no") or "",
"variant_template": item_doc.get("variant_of") or "",
```

**Verification Commands:**
```bash
# 1. Confirm syntax
python -m py_compile smriti_retail_os/barcode_api.py

# 2. Confirm keys present in return dict
grep -n "style_code\|variant_template\|variant_of" smriti_retail_os/barcode_api.py | grep -E "398|402|415|416|417|422|423|445|446"

# 3. Confirm prnContent correctly extracted in all 3 flows
grep -n "prnContent" smriti_retail_os/www/barcode.html | grep -v "const prnContent\|!prnContent\|//"
# Must show .prn || prnContent at lines ~4414, ~4566, ~4621
```

**Available PRN Template Tokens After Fix:**

| Token | Resolution |
|---|---|
| `{style}` | variant_of → custom_style_code → style_no → SKU split |
| `{style_code}` | custom_style_code or style_no (stored field, no chain) |
| `{variant_template}` | item_doc.variant_of (direct ERP parent template ID) |
| `{item_code}` | Full SKU code |
| `{item_name}` | Item name |

**Files Modified:**
- `smriti_retail_os/barcode_api.py` — lines 397–446 (`get_item_print_details`)
- `smriti_retail_os/www/barcode.html` — lines 4414, 4566, 4621 (`prnContent.prn || prnContent`)

**Commit:** `efcd7e5` — pushed to `origin/main`

---

## Issue 43 — "Barcode Center" Menu Item Not Found / Relocated to Barcode Studio

**Symptom:** Users who bookmarked the old "Barcode Center" link or who navigate to the Inventory sidebar group can no longer find the Barcode Center, Print Templates, Sizewise Item CRUD, or Sizewise Invoice entries in their previous locations.

**Root Cause:**
As part of SMRITI Navigation Consolidation (commit `3355e12`), all barcode-related sidebar links were moved from scattered groups into a new dedicated **Barcode Studio** group:
- **Removed from Inventory**: `Barcode Center` (renamed → `Label Studio`) and `Print Templates`
- **Removed from Masters**: `Sizewise Item CRUD`
- **Removed from Sales**: `Sizewise Invoice`

A new sidebar section `Barcode Studio` was inserted between `Inventory` and `Finance` containing all four items under their new labels.

**Fix / Navigation Guide:**
The menu items have not been deleted — they have been consolidated:

| Old Location | Old Label | New Location | New Label | Route |
|---|---|---|---|---|
| Inventory → Barcode Center | Barcode Center | Barcode Studio → Label Studio | Label Studio | `/barcode` |
| Inventory → Print Templates | Print Templates | Barcode Studio → Print Templates | Print Templates | `/print-templates` |
| Masters → Sizewise Item CRUD | Sizewise Item CRUD | Barcode Studio → Sizewise Item CRUD | Sizewise Item CRUD | `/sizewise_item` |
| Sales → Sizewise Invoice | Sizewise Invoice | Barcode Studio → Sizewise Invoice | Sizewise Invoice | `/sizewise_invoice` |

**Note:** The legacy route `/barcode-center` still redirects to `/barcode` (via `hooks.py` `website_route_rules`) for backward compatibility with saved bookmarks.

**Files Modified (commit `3355e12`):**
- `smriti_retail_os/public/js/smriti_nav_config.js` — client-side sidebar navigation
- `smriti_retail_os/navigation/navigation_service.py` — server-side `CANONICAL_NAV` dictionary

**Verification Commands:**
```bash
# Confirm barcode_studio exists in both nav files
grep -n "barcode_studio" smriti_retail_os/public/js/smriti_nav_config.js smriti_retail_os/navigation/navigation_service.py

# Confirm barcode_center fully removed from nav files
grep -n "barcode_center" smriti_retail_os/public/js/smriti_nav_config.js smriti_retail_os/navigation/navigation_service.py
# Expected: zero results
```