# Technical Debt & Risk Report: SMRITI Retail OS

## 1. Architectural Debt

### 1.1 Non-Standard Schema Definition
- **Issue**: Custom DocTypes and fields are defined in Python (`setup.py`) instead of standard Frappe JSON manifests.
- **Impact**: Bypasses the Frappe migration engine. Schema changes are not easily tracked in Git, and manual database cleanups may be required if migrations fail.
- **Reference**: `apps/smriti_retail_os/smriti_retail_os/setup.py`

### 1.2 Configuration via JSON Blobs
- **Issue**: `SMRITI Company Settings` stores complex configuration (e.g., `size_groups_json`) as hidden `Long Text` fields.
- **Impact**: Prevents standard ERPNext reporting, prevents field-level validation, and makes data migration/syncing between sites difficult.
- **Reference**: `SMRITI Company Settings` fields in `setup.py`

### 1.3 Hardcoded Role Dependencies
- **Issue**: Role names like `SMRITI Cashier` and `SMRITI Store Manager` are hardcoded in `hooks.py`, `setup.py`, and `security_api.py`.
- **Impact**: Rigid permission model. Renaming roles or adding intermediate roles requires code changes.

## 2. Security Risks

### 2.1 Plain-Text Credentials in Orchestration
- **Issue**: `pwd.yml` and `install.ps1` contain hardcoded database passwords (e.g., `123`).
- **Impact**: High risk of credential exposure if these files are committed or shared.
- **Reference**: `pwd.yml`, `example.env`

### 2.2 Insecure Manager Overrides — RESOLVED (verify before closing)
- **Original issue**: `validate_manager_override` in `billing_api.py` used the full ERPNext
  login password as a PIN.
- **Current state (as of this audit)**: `billing_api.py::validate_manager_override` now checks
  a dedicated `custom_smriti_pin` field with no fallback to the login password, and applies a
  Redis-backed rate limit (5 attempts / 10 min). This appears fixed in code.
- **Action before marking closed**: (1) confirm `custom_smriti_pin` is stored hashed, not
  plaintext, via `frappe.utils.password.check_password`; (2) add/confirm a regression test that
  asserts login-password fallback is impossible; (3) update this report's status once verified,
  since it was found stale relative to the code during a third-party audit.
- **Reference**: `billing_api.py:789`

### 2.3 Role-Based Access Control (RBAC) Bypass
- **Issue**: `billing_api.py` uses `ignore_permissions=True` in several `@frappe.whitelist()` functions.
- **Impact**: Potential for unauthorized data access if API endpoints are called directly by authenticated but low-permission users.

## 3. Performance Bottlenecks

### 3.1 Unoptimized Stock Queries
- **Issue**: `add_item_by_barcode` uses raw SQL queries on `tabBin` for stock lookups.
- **Impact**: As the `Bin` table grows to millions of rows, POS item lookup will become significantly slower.
- **Reference**: `billing_api.py:52`

### 3.2 Synchronous Asset Sync
- **Issue**: `sync_assets.py` performs physical file copies of all assets during every `after_migrate` and container boot.
- **Impact**: Increases system downtime during updates and slows down container restart times.

## 4. Stability & Testing

### 4.1 Missing Backend Test Coverage
- **Issue**: While the project has a `tests/` directory, core custom APIs in `billing_api.py` and `inventory_api.py` lack comprehensive unit tests.
- **Impact**: High risk of regressions when upgrading Frappe or ERPNext core versions.

---
*Evidence Reference: `billing_api.py`, `setup.py`, `pwd.yml`, `sync_assets.py`, `security_api.py`*
