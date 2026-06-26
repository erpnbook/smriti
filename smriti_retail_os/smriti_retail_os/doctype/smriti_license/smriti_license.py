# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_license/smriti_license.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_license/smriti_license.py
# @description: SMRITI License DocType controller.
#               Enforces architecture invariants: installation_id immutability,
#               license_health write guard, auto state recalculation on save.
# @authority: docs/architecture/licensing/SMRITI_LICENSE_ARCHITECTURE_V1.md
# @version: 1.0.0
#

import frappe
import uuid
from frappe.model.document import Document
from frappe import _


class SMRITILicense(Document):

    # ── Lifecycle hooks ───────────────────────────────────────────────────────

    def before_insert(self):
        """Generate installation_id once, on first insert only."""
        if not self.installation_id:
            self.installation_id = str(uuid.uuid4())
        if not self.created_on:
            from frappe.utils import now_datetime
            self.created_on = now_datetime()

    def validate(self):
        self._guard_installation_id()
        # NOTE: _recalculate_license_state runs BEFORE _guard_license_health_write.
        # The guard checks whether health changed WITHOUT status also changing.
        # Running recalculate first means the guard sees the post-recalculation state,
        # which always changes health+status together — so the guard never fires on
        # legitimate recalculation, only on direct rogue writes.
        self._recalculate_license_state()
        self._recompute_checksum()
        self._guard_license_health_write()

    def after_insert(self):
        self._seed_default_features()
        self._log_activity("Activated", "Initial install record created")

    # ── Installation ID guard ─────────────────────────────────────────────────

    def _guard_installation_id(self):
        """
        Blocks any attempt to change installation_id after it has been set.
        set_only_once in the JSON handles UI/API; this guard handles .save() patches.
        """
        if not self.is_new():
            original = frappe.db.get_value("SMRITI License", self.name, "installation_id")
            if original and self.installation_id != original:
                frappe.throw(
                    _("installation_id is immutable. It cannot be changed after initial creation."),
                    frappe.PermissionError
                )

    # ── license_health write guard ────────────────────────────────────────────

    def _guard_license_health_write(self):
        """
        Architecture §3 invariant: license_health must only change when
        license_status is also changing in the same save operation.
        Prevents any code path setting license_health directly.
        """
        if self.is_new():
            return
        original_health  = frappe.db.get_value("SMRITI License", self.name, "license_health")
        original_status  = frappe.db.get_value("SMRITI License", self.name, "license_status")
        health_changed   = self.license_health != original_health
        status_unchanged = self.license_status == original_status
        if health_changed and status_unchanged:
            frappe.throw(
                _("license_health must only change via recalculate_license_state(). "
                  "Do not set it directly."),
                frappe.ValidationError
            )

    # ── State recalculation ───────────────────────────────────────────────────

    def _recalculate_license_state(self):
        """
        Single authority for license_status + license_health.
        Architecture §6 state machine — priority order enforced.
        """
        from frappe.utils import getdate, date_diff, now_datetime, nowdate
        from frappe.utils import cint

        today = getdate(nowdate())

        # Priority 0 — Unregistered
        if not self.license_key:
            self.license_status = "Unregistered"
            self.license_health = "Unregistered"
            return

        # Priority 1 — Tampered
        if self.tamper_detected:
            self.license_status = "Tampered"
            self.license_health = "Tampered"
            return

        # Priority 2 — Suspended (persists, never auto-cleared)
        if self.license_status == "Suspended":
            self.license_health = "Suspended"
            return

        grace_days = cint(self.grace_period_days) or 7
        warn_days  = cint(self.warning_threshold_days) or 14

        # Priority 3 — Expired (past grace)
        if self.expiry_date:
            days_since_expiry = date_diff(today, getdate(self.expiry_date))
            if days_since_expiry > grace_days:
                self.license_status = "Expired"
                self.license_health = "Expired"
                return

            # Priority 4 — Grace Period (expiry breach)
            if days_since_expiry > 0:
                self.license_status = "Grace Period"
                self.license_health = "Grace Period"
                if not self.grace_reason:
                    self.grace_reason = "Expiry"
                return

        # Priority 5 — Grace Period (offline too long)
        if self.last_sync and self.grace_period_days:
            from frappe.utils import get_datetime
            offline_days = date_diff(now_datetime(), get_datetime(self.last_sync))
            if offline_days > grace_days:
                self.license_status = "Grace Period"
                self.license_health = "Grace Period"
                self.grace_reason = "Offline Too Long"
                return

        # Priority 7 — Active: derive license_health
        self.license_status = "Active"
        if self.expiry_date:
            days_remaining = date_diff(getdate(self.expiry_date), today)
            if days_remaining <= warn_days:
                self.license_health = "Warning"
            else:
                self.license_health = "Healthy"
        else:
            self.license_health = "Healthy"

    # ── Checksum ──────────────────────────────────────────────────────────────

    def _recompute_checksum(self):
        """
        HMAC-SHA256 integrity check (NOT anti-tamper).
        Key = installation_id. Input = canonical concat of key fields.
        Architecture §5.
        """
        import hmac
        import hashlib

        key = (self.installation_id or "").encode("utf-8")
        payload = "|".join([
            str(self.expiry_date or ""),
            str(self.installation_id or ""),
            str(self.license_key or ""),
            str(self.license_type or ""),
            str(self.store_limit or ""),
            str(self.user_limit or ""),
        ]).encode("utf-8")

        self.checksum_hash = hmac.new(key, payload, hashlib.sha256).hexdigest()

    # ── Default Feature Seeding ───────────────────────────────────────────────

    def _seed_default_features(self):
        """
        On first insert, populate the features child table with the
        confirmed v1 feature mapping from architecture §4a.
        Uses frappe.get_doc().db_insert() to bypass hooks and avoid recursive validate().
        """
        DEFAULT_FEATURES = [
            {"feature_code": "POS_BILLING",        "feature_name": "POS Billing",        "enabled": 1, "tier_minimum": "Starter",      "restriction_level": "NONE"},
            {"feature_code": "CRM",                "feature_name": "CRM",                "enabled": 1, "tier_minimum": "Professional",  "restriction_level": "NONE"},
            {"feature_code": "LOYALTY",            "feature_name": "Loyalty",            "enabled": 1, "tier_minimum": "Professional",  "restriction_level": "NONE"},
            {"feature_code": "ANALYTICS",          "feature_name": "Analytics",          "enabled": 1, "tier_minimum": "Professional",  "restriction_level": "READ_ONLY"},
            {"feature_code": "EXPORT",             "feature_name": "Export",             "enabled": 1, "tier_minimum": "Enterprise",    "restriction_level": "BLOCKED"},
            {"feature_code": "AI_ASSISTANT",       "feature_name": "AI Assistant",       "enabled": 1, "tier_minimum": "Enterprise",    "restriction_level": "BLOCKED"},
            {"feature_code": "WHATSAPP_CAMPAIGNS", "feature_name": "WhatsApp Campaigns", "enabled": 1, "tier_minimum": "Enterprise",    "restriction_level": "BLOCKED"},
        ]
        for idx, f in enumerate(DEFAULT_FEATURES, start=1):
            child = frappe.get_doc({
                "doctype":     "SMRITI License Features",
                "parenttype":  "SMRITI License",
                "parentfield": "features",
                "parent":      self.name,
                "idx":         idx,
                **f
            })
            child.db_insert()
        frappe.db.commit()

    # ── Activity logging ──────────────────────────────────────────────────────

    def _log_activity(self, action, remarks="", result="Success"):
        """Inserts activity log row via db_insert() to bypass hooks and avoid recursive validate()."""
        from frappe.utils import now_datetime
        child = frappe.get_doc({
            "doctype":      "SMRITI License Activity Log",
            "parenttype":   "SMRITI License",
            "parentfield":  "activity_log",
            "parent":       self.name,
            "idx":          (frappe.db.count("SMRITI License Activity Log", {"parent": self.name}) or 0) + 1,
            "timestamp":    now_datetime(),
            "action":       action,
            "performed_by": frappe.session.user,
            "result":       result,
            "remarks":      remarks,
        })
        child.db_insert()
        frappe.db.commit()

    def _log_validation(self, validation_type, result, sig_result="Not Checked", remarks=""):
        """Inserts validation history row via db_insert() to bypass hooks and avoid recursive validate()."""
        from frappe.utils import now_datetime
        child = frappe.get_doc({
            "doctype":               "SMRITI License Validation History",
            "parenttype":            "SMRITI License",
            "parentfield":           "validation_history",
            "parent":                self.name,
            "idx":                   (frappe.db.count("SMRITI License Validation History", {"parent": self.name}) or 0) + 1,
            "timestamp":             now_datetime(),
            "validation_type":       validation_type,
            "result":                result,
            "signature_check_result": sig_result,
            "remarks":               remarks,
        })
        child.db_insert()
        frappe.db.commit()

