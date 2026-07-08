# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/purchase_studio/service/purchase_settings_service.py
# @desc:    Reads and writes SMRITI Purchase Settings, integrating with the SMRITI Foundation SDK.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 3 (Settings Service)
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from frappe.utils import flt

# smriti_foundation is not a deployed package — provide silent no-op stubs so
# that the existing try/except Exception: pass call-sites degrade gracefully.
try:
	from smriti_foundation.common import SmritiRegistry
	from smriti_foundation.configuration import IConfigurationProvider
	from smriti_foundation.policy import IPolicyProvider
except ImportError:
	# Stubs — all SDK usage sites already use try/except so they will fall through
	# to the Frappe DocType fallback path automatically.
	class _NoOpProvider:
		"""Null provider that raises AttributeError on any attribute access."""
		pass
	class SmritiRegistry:
		@staticmethod
		def resolve(iface):
			raise RuntimeError("smriti_foundation not installed")
	IConfigurationProvider = _NoOpProvider
	IPolicyProvider = _NoOpProvider

SETTINGS_DOCTYPE = "SMRITI Purchase Settings"
VALID_POLICIES   = {"grn_only", "standalone", "both"}
VALID_LC_RULES   = {"manual", "proportional", "disabled"}


# ─────────────────────────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────────────────────────

def get_settings():
	"""
	Returns all SMRITI Purchase Settings as a plain dict.
	Attempts to load from the SMRITI Configuration Provider first, falling back to DocType records.
	"""
	try:
		config = SmritiRegistry.resolve(IConfigurationProvider)
		
		# Resolve keys from SDK Configuration Provider
		policy_val = config.get_config("purchase_invoice_policy")
		threshold_val = config.get_config("approval_threshold")
		grn_mand = config.get_config("grn_mandatory")
		over_rec = config.get_config("allow_over_receipt")
		auto_itm = config.get_config("auto_create_items")
		def_wh = config.get_config("default_warehouse")
		tol_pct = config.get_config("tolerance_percent")
		lc_rule = config.get_config("landed_cost_rule")
		
		# If configuration keys are present, return the resolved set
		if policy_val is not None:
			return {
				"purchase_invoice_policy":             policy_val or "both",
				"approval_threshold":                  flt(threshold_val or 0.0),
				# Issue #5: True = threshold is compared against GST-inclusive grand_total;
				# False (default) = compared against pre-GST net_total (line totals before tax)
				"approval_threshold_inclusive_of_tax": bool(config.get_config("approval_threshold_inclusive_of_tax")),
				"grn_mandatory":                       bool(grn_mand),
				"allow_over_receipt":                  bool(over_rec),
				"auto_create_items":                   bool(auto_itm),
				"default_warehouse":                   def_wh or "",
				"tolerance_percent":                   flt(tol_pct or 0.0),
				"landed_cost_rule":                    lc_rule or "manual"
			}
	except Exception:
		pass

	# Fallback to single DocType lookup
	try:
		s = frappe.get_single(SETTINGS_DOCTYPE)
		return {
			"purchase_invoice_policy":             s.purchase_invoice_policy or "both",
			"approval_threshold":                  flt(s.approval_threshold),
			"approval_threshold_inclusive_of_tax": bool(getattr(s, "approval_threshold_inclusive_of_tax", False)),
			"grn_mandatory":                       bool(s.grn_mandatory),
			"allow_over_receipt":                  bool(s.allow_over_receipt),
			"auto_create_items":                   bool(s.auto_create_items),
			"default_warehouse":                   s.default_warehouse or "",
			"tolerance_percent":                   flt(s.tolerance_percent),
			"landed_cost_rule":                    s.landed_cost_rule or "manual"
		}
	except Exception:
		# Settings not yet created — return safe defaults
		return {
			"purchase_invoice_policy":             "both",
			"approval_threshold":                  0.0,
			"approval_threshold_inclusive_of_tax": False,
			"grn_mandatory":                       False,
			"allow_over_receipt":                  False,
			"auto_create_items":                   True,
			"default_warehouse":                   "",
			"tolerance_percent":                   0.0,
			"landed_cost_rule":                    "manual"
		}


def check_invoice_policy():
	"""
	Returns the current Purchase Invoice Policy: "grn_only" | "standalone" | "both"
	"""
	return get_settings().get("purchase_invoice_policy", "both")


def check_approval_required(grand_total, net_total=None):
	"""
	Returns True if the relevant PO total exceeds the approval threshold.

	- When settings.approval_threshold_inclusive_of_tax is True:
	    compare grand_total (GST-inclusive) against threshold.
	- When False (default — pre-GST basis):
	    compare net_total against threshold if provided, else fall back to grand_total.

	Queries the SDK Policy Engine to support tenant/department specific thresholds.
	"""
	try:
		policy_engine = SmritiRegistry.resolve(IPolicyProvider)
		context = {
			"company": frappe.defaults.get_user_default("company") or "",
			"user": frappe.session.user or "Guest"
		}
		threshold = flt(policy_engine.get_policy("approval_threshold", context))
		inclusive = bool(policy_engine.get_policy("approval_threshold_inclusive_of_tax", context))
	except Exception:
		s = get_settings()
		threshold = flt(s.get("approval_threshold", 0))
		inclusive = bool(s.get("approval_threshold_inclusive_of_tax", False))

	if threshold <= 0:
		return False

	# Issue #5: choose the correct total for comparison
	if inclusive:
		comparison_total = flt(grand_total)
	else:
		# Pre-GST basis: prefer net_total (line-item subtotal before tax)
		comparison_total = flt(net_total) if net_total is not None else flt(grand_total)

	return comparison_total > threshold


def is_grn_mandatory():
	"""
	Returns True if GRN is mandatory for all Purchase Invoices regardless of policy.
	"""
	try:
		policy_engine = SmritiRegistry.resolve(IPolicyProvider)
		context = {
			"company": frappe.defaults.get_user_default("company") or "",
			"user": frappe.session.user or "Guest"
		}
		return bool(policy_engine.get_policy("grn_mandatory", context))
	except Exception:
		return bool(get_settings().get("grn_mandatory", False))


def is_over_receipt_allowed():
	"""Returns True if receiving more than PO qty is permitted."""
	try:
		policy_engine = SmritiRegistry.resolve(IPolicyProvider)
		context = {
			"company": frappe.defaults.get_user_default("company") or "",
			"user": frappe.session.user or "Guest"
		}
		return bool(policy_engine.get_policy("allow_over_receipt", context))
	except Exception:
		return bool(get_settings().get("allow_over_receipt", False))


def is_auto_create_items():
	"""Returns True if items should be auto-created when not found in PO."""
	return bool(get_settings().get("auto_create_items", True))


def get_default_warehouse_setting():
	"""Returns the configured default warehouse (may be empty string)."""
	return get_settings().get("default_warehouse", "")


# ─────────────────────────────────────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────────────────────────────────────

def save_settings(fields):
	"""
	Validates and saves SMRITI Purchase Settings.
	Writes a SETTINGS_CHANGED audit entry with before/after snapshots.
	"""
	_validate_settings(fields)

	# Capture before snapshot
	before = get_settings()

	# Apply changes
	s = frappe.get_single(SETTINGS_DOCTYPE)

	if "purchase_invoice_policy" in fields:
		s.purchase_invoice_policy = fields["purchase_invoice_policy"]
	if "approval_threshold" in fields:
		s.approval_threshold = flt(fields["approval_threshold"])
	if "grn_mandatory" in fields:
		s.grn_mandatory = int(bool(fields["grn_mandatory"]))
	if "allow_over_receipt" in fields:
		s.allow_over_receipt = int(bool(fields["allow_over_receipt"]))
	if "auto_create_items" in fields:
		s.auto_create_items = int(bool(fields["auto_create_items"]))
	if "default_warehouse" in fields:
		s.default_warehouse = fields["default_warehouse"] or ""
	if "tolerance_percent" in fields:
		s.tolerance_percent = flt(fields["tolerance_percent"])
	if "landed_cost_rule" in fields:
		s.landed_cost_rule = fields["landed_cost_rule"]

	s.save(ignore_permissions=True)
	smriti.db.commit()

	# Capture after snapshot
	after = get_settings()

	# Write audit trail
	from smriti_retail_os.purchase_studio.service.audit_service import log, SETTINGS_CHANGED
	log(
		event_type=SETTINGS_CHANGED,
		payload={"doctype": SETTINGS_DOCTYPE, "name": SETTINGS_DOCTYPE},
		before=before,
		after=after
	)


def _validate_settings(fields):
	"""Internal validation for save_settings input."""
	if "purchase_invoice_policy" in fields:
		if fields["purchase_invoice_policy"] not in VALID_POLICIES:
			frappe.throw(_(
				"Invalid Purchase Invoice Policy '{0}'. "
				"Must be one of: grn_only, standalone, both."
			).format(fields["purchase_invoice_policy"]))

	if "approval_threshold" in fields:
		if flt(fields["approval_threshold"]) < 0:
			frappe.throw(_("Approval Threshold cannot be negative."))

	if "tolerance_percent" in fields:
		tp = flt(fields["tolerance_percent"])
		if tp < 0 or tp > 100:
			frappe.throw(_("Tolerance % must be between 0 and 100."))

	if "landed_cost_rule" in fields:
		if fields["landed_cost_rule"] not in VALID_LC_RULES:
			frappe.throw(_(
				"Invalid Landed Cost Rule '{0}'. "
				"Must be one of: manual, proportional, disabled."
			).format(fields["landed_cost_rule"]))

	if "default_warehouse" in fields and fields["default_warehouse"]:
		if not smriti.db.exists("Warehouse", fields["default_warehouse"]):
			frappe.throw(_(
				"Warehouse '{0}' does not exist."
			).format(fields["default_warehouse"]))
