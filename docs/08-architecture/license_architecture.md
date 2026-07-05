---
Document ID: "ARCH-017"
Title: "SMRITI License Architecture v1.0"
Owner: "Architecture Team"
Audience: "Architect"
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

# SMRITI License Architecture v1.0

**Status:** FROZEN
**Version:** 1.0
**Effective:** 2026-06-17
**Modification Policy:** Any schema change requires architecture review.
**Repo Path:** `docs/architecture/licensing/SMRITI_LICENSE_ARCHITECTURE_V1.md`
**Lifecycle:** DRAFT → REVIEW → LOCKED → FROZEN → SUPERSEDED. FROZEN means implementation may begin; no functional changes are allowed; only typo/clarity corrections are permitted; any architecture change requires v1.1.

## 1. Purpose & Scope

This document defines the licensing and registration architecture for SMRITI Retail OS itself — distinct from Customer/Party Registration (retail business customer master data). It governs how a single SMRITI deployment identifies, validates, and enforces its own commercial license, across both On-Premise and future SaaS delivery models.

## 2. Architecture Principle

```
1 Frappe Site
    └── 1 SMRITI License        (Single DocType — exactly one record)
          └── N Companies / Branches
                └── N Users
```

License is stored at system level, never at branch level. This guarantees one license per deployment and eliminates accidental multi-license states. It assumes a one-site-per-client deployment model (each client = a dedicated Frappe site/container) for both On-Prem and future SaaS — this is the foundational assumption the Single DocType decision depends on.

## 3. Schema — SMRITI License (Single DocType)

| Field | Type | Notes |
|---|---|---|
| organization_name, store_name, owner_name | Data | Snapshot, synced from Company master via "Sync from Company" action |
| gstin, pan, business_type | Data | |
| license_key | **Password** | Encrypted at rest, never returned via API |
| license_type | Select: Starter / Professional / Enterprise | |
| license_status | Select: **Unregistered** / Active / Grace Period / Expired / Suspended / Tampered | Single source of truth for business logic |
| license_health | Select: **Unregistered** / Healthy / Warning / Grace Period / Expired / Suspended / Tampered | UI-facing refinement, derived together with license_status in the same function — never set independently |
| grace_reason | Select: Expiry / Offline Too Long / Manual Override | Set whenever license_status = Grace Period |
| activation_date, expiry_date | Date | |
| grace_period_days | Int | Default: 7 |
| warning_threshold_days | Int | Default: 14. Used for `license_health = Warning` derivation (§6) |
| installation_id | Data | `set_only_once`, generated in `before_insert`, immutable forever (see §8) |
| device_id, server_id, site_name, site_url, server_fingerprint | Data | |
| registered_domain, registered_email, registered_mobile, created_on | Data / Datetime | |
| current_plan | Data | |
| user_limit, store_limit | Int | -1 = unlimited |
| customer_id, support_contract_status, amc_status | Data | |
| last_license_validation | Datetime | |
| instance_id, tenant_id | Data | Reserved for Phase-3 multi-tenant SaaS |
| license_signature | **Password** | Phase-2: signed by SMRITI License Server private key — the actual anti-tamper authority |
| activation_token | **Password** | |
| offline_validation_status | Select | |
| last_sync | Datetime | |
| tamper_detected | Check | |
| tamper_reason | Data | |
| last_integrity_check | Datetime | |
| checksum_hash | **Password** | **Integrity check only — NOT a security control.** See §5. |

### Schema Invariant: license_health Write Guard

`license_health` MUST only change when `license_status` is also recalculated in the same operation. The DocType's `validate()` method enforces this:

```python
def validate(self):
    if self.has_value_changed("license_health") and not self.has_value_changed("license_status"):
        frappe.throw("license_health must only change via recalculate_license_state()")
```

This prevents any code path from setting `license_health` directly without going through the centralized state recalculation function.

## 4. Schema — Child Tables

### smriti_license_features

| Field | Type |
|---|---|
| feature_code, feature_name | Data |
| enabled | Check |
| tier_minimum | Select: Starter / Professional / Enterprise |
| restriction_level | Select: NONE / READ_ONLY / BLOCKED |

`restriction_level` replaces a separate `restrict_in_grace` boolean — `NONE` already means "not restricted," so a second boolean field would only create a manual-sync risk between the two. One field, three states.

**Confirmed Feature Mapping (FROZEN):**

| feature_code | feature_name | restriction_level (Grace Period) |
|---|---|---|
| POS_BILLING | POS Billing | NONE |
| CRM | CRM | NONE |
| LOYALTY | Loyalty | NONE |
| ANALYTICS | Analytics | READ_ONLY |
| EXPORT | Export | BLOCKED |
| AI_ASSISTANT | AI Assistant | BLOCKED |
| WHATSAPP_CAMPAIGNS | WhatsApp Campaigns | BLOCKED |

### smriti_license_activity_log

timestamp, action (Activated / Renewed / Changed / Synced / Exported / Support Contacted / Manual Override), performed_by (Link: User), result, remarks

### smriti_license_validation_history

timestamp, validation_type (Online / Offline), result, signature_check_result (Valid / Invalid / Not Checked), remarks

### 4a. Confirmed Defaults (FROZEN)

These values are frozen. Implementation agents must use these exact defaults without reopening discussion:

```
warning_threshold_days  = 14
grace_period_days       = 7
Admin Role              = SMRITI System Admin
Route                   = /app/smriti-license
Hash Algorithm          = HMAC-SHA256 (key = installation_id)
```

## 5. Security Model

| Layer | Rule |
|---|---|
| UI | license_key / signature / token always masked (last 4 characters only) |
| API | Password fieldtype — never serialized in plaintext, even to System Manager |
| DB | Encrypted at rest (Frappe native Password fieldtype) |
| Logs | Never logged in cleartext, anywhere |
| Exports | Never included in Export Registration Certificate or any export |

**checksum_hash vs license_signature — different trust levels:**

`checksum_hash` (Phase-1) detects accidental modification only. A determined attacker with DB access can recompute the hash after editing a field, making tampering invisible:

```
DB access → field modified → checksum recalculated → tamper invisible
```

It is documented and labeled as an **Integrity Check**, not a Security Control.

**Hash algorithm:** `checksum_hash` uses HMAC-SHA256 with `installation_id` as the HMAC key. Input is the concatenation of (`license_key`, `license_type`, `expiry_date`, `user_limit`, `store_limit`, `installation_id`) in canonical (alphabetical) order. This does not change the trust model — it is still not anti-tamper — but it makes casual modification marginally harder since the attacker must know the HMAC key, not just the hash algorithm.

`license_signature` (Phase-2) is the actual anti-tamper authority — signed by the SMRITI License Server's private key, verified locally against an embedded public key:

```
Signed Payload → Public Key Verification → Valid / Invalid
```

This cannot be regenerated by anyone without the private key, including someone with full DB access.

**Known Phase-1 Limitation — System Clock Manipulation:**

On-Prem deployments can manipulate the local system clock to bypass date-based expiry checks. The state machine (§6) relies on `today > expiry_date`, which uses the server's local clock. A client who sets their clock backwards can indefinitely avoid Grace Period or Expired states. This is accepted risk for Phase-1 and is addressed by Phase-2 server-side validation, where the SMRITI License Server maintains its own timestamps and can detect clock drift anomalies during sync.

## 6. State Machine

Priority order (highest wins):

```
0. license_key is empty or null               → Unregistered
1. tamper_detected == true                     → Tampered
2. manually Suspended (admin action)           → Suspended   (persists, skips auto-logic below)
3. today > expiry_date + grace_period_days     → Expired
4. today > expiry_date                         → Grace Period   (grace_reason = Expiry)
5. (now - last_sync) > grace_period_days       → Grace Period   (grace_reason = Offline Too Long)
6. admin manually forces Grace Period          → Grace Period   (grace_reason = Manual Override)
7. else                                        → Active
```

**Unregistered behavior:** A fresh SMRITI installation with no license key starts in Unregistered state. All features are blocked except the License & Registration page. The system displays a registration prompt on every page load. This state can only be exited by entering a valid license key and activating.

`license_health` is derived in the same function, in the same write, never independently:

```
Unregistered                                  → Unregistered
Active + days_to_expiry <= warning_threshold_days → Warning
Active + days_to_expiry  > warning_threshold_days → Healthy
all other states                              → pass through 1:1
```

A pure offline on-prem client (no expiry breach, just stale sync) caps out at Grace Period — it cannot auto-escalate to Expired from staleness alone. Only an actual expiry_date breach (past grace_period_days) produces Expired. This protects legitimate air-gapped deployments from being hard-locked purely for not phoning home.

### 6a. Evaluation Triggers

`license_status` is re-evaluated at these points:

```
A. Daily Scheduler Job
   smriti_retail_os.license.tasks.evaluate_license_status
   → Full evaluation, writes license_status + license_health to DocType
   → Logs result to smriti_license_validation_history

B. On DocType Save
   → Triggers recalculate_license_state() in validate()
   → Covers: Activate, Renew, Sync License, any admin edit

C. Inside check_feature() — Lightweight Date Check
   → Compares cached expiry_date against now()
   → Does NOT write to DB (no save, no commit)
   → If stale state detected, returns the correct enforcement
     but does not persist — scheduler or next save will persist
   → Guarantees real-time enforcement even if scheduler hasn't run
```

This hybrid approach ensures:
- Enforcement is always real-time (via C)
- Persisted state is always current within 24 hours (via A)
- User actions immediately reflect (via B)

## 7. Enforcement Layer

All feature gating goes through one centralized function. No module checks `license_status` directly.

```python
# smriti_retail_os/license/manager.py

def check_feature(feature_code: str) -> dict:
    """
    Single source of truth for feature gating.

    Returns:
        allowed: bool        — can the user proceed?
        mode: str            — "none" | "read_only" | "blocked"
        reason: str | None   — human-readable explanation for UI display
        status: str          — current license_status (for UI badge rendering)
        days_remaining: int  — days until expiry (-N if expired, None if Unregistered)
    """
```

Forbidden pattern:

```python
if license_status == "Active":   # scattered, unmaintainable — never do this
```

Required pattern:

```python
from smriti_retail_os.license.manager import check_feature
check_feature("AI_ASSISTANT")
```

`restriction_level` in `smriti_license_features` governs per-feature behavior **only while in Grace Period**. Unregistered / Expired / Suspended / Tampered are system-wide locks, more severe than any per-feature setting:

| Status | System Behavior |
|---|---|
| Unregistered | Full system blocked except License & Registration page (force registration) |
| Expired | Full system blocked except License & Registration page (force renewal) |
| Suspended | Full system blocked except License & Registration + Contact Support |
| Tampered | Full system blocked, Sync License disabled (channel itself may be compromised), Contact Support mandatory |

**Universal exception:** the License & Registration page and its Activate / Renew / Contact Support actions must always remain accessible, regardless of license_status — otherwise a locked-out client has no way to self-recover.

## 8. Installation Identity

`installation_id` is generated once in `before_insert` and locked via Frappe's `set_only_once` DocField property plus a `validate()` guard that throws if the value differs from the original. This blocks edits through the UI, API, and standard `.save()` patches.

Caveat: `set_only_once` is enforced by the document controller — a raw `frappe.db.set_value()` call from a bench console bypasses it entirely. True tamper-resistance for this field, like for license dates, ultimately depends on the Phase-2 signature/integrity layer (§5), not on the field property alone.

## 9. UI Structure

Single dedicated SMRITI page at **`/app/smriti-license`** (accessible via Settings → License & Registration), per the standing rule that every module gets one SMRITI UI wrapper, never raw Frappe Desk. Internal tabs:

```
License & Registration
 ├── Overview
 ├── Registration Details
 ├── Feature Entitlements
 ├── Validation History
 ├── Activity Log
 └── Support Information
```

Route name is frozen as `smriti-license`. Navigation uses:

```javascript
frappe.set_route("smriti-license");
```

## 10. Implementation File Structure

```
smriti_retail_os/
├── license/
│   ├── __init__.py
│   ├── manager.py              ← LicenseManager + check_feature()
│   └── tasks.py                ← Daily scheduler: evaluate_license_status
├── api/
│   └── license_api.py          ← Whitelisted API endpoints
├── www/
│   ├── smriti-license.html     ← UI page
│   └── smriti-license.py       ← Auth context
└── smriti_retail_os/
    └── doctype/
        ├── smriti_license/
        │   ├── smriti_license.json
        │   └── smriti_license.py
        ├── smriti_license_features/
        │   └── smriti_license_features.json
        ├── smriti_license_activity_log/
        │   └── smriti_license_activity_log.json
        └── smriti_license_validation_history/
            └── smriti_license_validation_history.json
```

## 11. Phase Roadmap

**Phase 1 (MVP):** Single DocType, license_key, Unregistered/Activation/Expiry/Grace Period states, Activity Log, Validation History, Feature Entitlements, license_health + warning_threshold_days, checksum_hash (HMAC-SHA256, integrity only), daily scheduler evaluation, check_feature() enforcement

**Phase 2:** license_signature + activation_token via PKI, real offline validation, real tamper detection, License Server Sync, clock drift detection

**Phase 3:** Multi-tenant SaaS licensing, billing integration, auto-renewal, customer portal

## 12. Sign-off

| Item | Status |
|---|---|
| Single DocType | ✅ Approved |
| Feature Entitlements (child table) | ✅ Approved |
| Grace Period Logic (OR trigger, soft restriction) | ✅ Approved |
| Activity Log + Validation History (separate tables) | ✅ Approved |
| Offline On-Prem Support | ✅ Approved |
| SaaS Compatibility | ✅ Approved |
| checksum_hash reclassified as Integrity Check, not Security Control | ✅ Applied |
| restrict_in_grace boolean merged into restriction_level | ✅ Applied |
| Unregistered state added to license_status and license_health | ✅ Applied (review fix) |
| warning_threshold_days added to schema | ✅ Applied (review fix) |
| HMAC-SHA256 specified for checksum_hash | ✅ Applied (review suggestion) |
| Evaluation triggers documented (§6a) | ✅ Applied (review suggestion) |
| Clock manipulation documented as Phase-1 limitation | ✅ Applied (review suggestion) |
| license_health write guard added to §3 | ✅ Applied (review suggestion) |
| check_feature() return contract expanded with days_remaining | ✅ Applied (review suggestion) |
| Route name frozen as /app/smriti-license | ✅ Applied (review suggestion) |
| Implementation file structure added (§10) | ✅ Applied (review suggestion) |

## 13. Non-Goals

This architecture does NOT:

- Store branch-level or user-level licenses — licensing is system-level only (§2)
- Depend on permanent internet connectivity — offline / on-prem operation is a first-class requirement (§6)
- Allow any feature module to bypass `LicenseManager.check_feature()` — no scattered `license_status` checks anywhere in the codebase (§7)
- Expose raw Frappe Single DocType forms to end users — access only through the dedicated SMRITI UI wrapper at `/app/smriti-license` (§9)
- Support multiple companies/clients sharing one license on a single Frappe site — one site, one license, one client (§2)
- Treat `checksum_hash` as a security or anti-tamper guarantee in Phase-1 — it is an integrity check only (§5)
- Auto-escalate a license to Expired purely from stale `last_sync` — only an actual `expiry_date` breach can produce Expired (§6)
- Define per-feature billing or metering — that is Phase-3 scope, not part of this architecture
- Defend against system clock manipulation in Phase-1 — this is a known limitation addressed in Phase-2 (§5)

Any future requirement that conflicts with the list above is a scope change, not a bug fix, and requires architecture review per the Modification Policy stated at the top of this document.

## 14. Final Verdict

```
SMRITI License Architecture v1.0

Architecture Status : PASSED
Review Status       : PASSED (all findings applied)
Governance Status   : PASSED
Security Review     : PASSED (Phase-1)
Implementation Gate : OPEN

Ready For:
✓ DocType Creation
✓ Child Tables
✓ API Layer (license_api.py)
✓ LicenseManager (manager.py + check_feature)
✓ Scheduler Task (tasks.py)
✓ UI Wrapper (smriti-license.html)
✓ Phase-1 Build
```

Governance directive for any AI assistant or automated development tool touching licensing code:

```
Licensing-related development MUST comply with
docs/architecture/licensing/SMRITI_LICENSE_ARCHITECTURE_V1.md.

Any deviation requires explicit architecture review,
not silent reinterpretation during implementation.
```


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