# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/cge/service/cge_service.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/cge/service/cge_service.py
# @description: Core Business Logic and Engine for SMRITI Customer Growth Engine (CGE) v1.0.
# @author: Antigravity AI
# @date: 2026-06-18
#

import frappe
from frappe import _
from frappe.utils import now_datetime, nowdate, add_to_date, flt, getdate
from frappe.model.document import Document

class CGERuleEvaluator:
    def __init__(self, invoice_doc):
        self.invoice = invoice_doc
        self.customer = invoice_doc.customer
        self.items = invoice_doc.items
        self.trace_logs = []

    def evaluate(self):
        """
        Main runner:
        1. Fetch active SMRITI Loyalty Rules.
        2. Resolve tier details and base multipliers.
        3. Match item dimensions (Brand, Group, Style, Season, Store, Customer Group, Tier).
        4. Apply stacking / priority overrides.
        5. Log matching traces into SMRITI Rule Evaluation Log.
        """
        # Resolve customer details
        cust_doc = frappe.get_doc("Customer", self.customer)
        
        # 1. Fetch customer's tier and base multiplier
        tier_info = get_customer_loyalty_tier(self.customer)
        tier_multiplier = flt(tier_info.get("tier_multiplier", 1.0))
        tier_name = tier_info.get("tier_name", "Default")
        
        # 2. Fetch active loyalty rules
        today = getdate(nowdate())
        rules = frappe.get_all("SMRITI Loyalty Rule",
            filters={
                "status": "Active"
            },
            fields=[
                "name", "rule_name", "rule_type", "dimension", 
                "dimension_doctype", "dimension_value", "rule_value", 
                "priority", "allow_stack", "effective_from", "effective_to"
            ]
        )
        
        # Filter rules by date range manually to support open-ended ranges
        active_rules = []
        for r in rules:
            from_date = getdate(r.effective_from) if r.effective_from else None
            to_date = getdate(r.effective_to) if r.effective_to else None
            
            if from_date and today < from_date:
                continue
            if to_date and today > to_date:
                continue
            active_rules.append(r)
            
        evaluation_results = []
        
        # 3. Match rules for each item
        for item in self.items:
            item_rules = []
            
            # Fetch item brand, group, style, season etc.
            item_brand = frappe.db.get_value("Item", item.item_code, "brand")
            item_group = frappe.db.get_value("Item", item.item_code, "item_group")
            item_style = frappe.db.get_value("Item", item.item_code, "custom_style_code") if frappe.db.has_column("Item", "custom_style_code") else None
            item_season = frappe.db.get_value("Item", item.item_code, "custom_season") if frappe.db.has_column("Item", "custom_season") else None
            
            for rule in active_rules:
                matched = False
                dim = rule.dimension
                val = rule.dimension_value
                
                if dim == "Brand" and item_brand == val:
                    matched = True
                elif dim == "Item Group" and item_group == val:
                    matched = True
                elif dim == "Style" and item_style == val:
                    matched = True
                elif dim == "Season" and item_season == val:
                    matched = True
                elif dim == "Store" and (item.warehouse == val or self.invoice.set_warehouse == val):
                    matched = True
                elif dim == "Customer Group" and cust_doc.customer_group == val:
                    matched = True
                elif dim == "Tier" and tier_name == val:
                    matched = True
                    
                if matched:
                    item_rules.append(rule)
                    
            # Apply stacking and overrides
            # Separate by rule type
            multipliers = [r for r in item_rules if r.rule_type == "Multiplier"]
            bonus_points = [r for r in item_rules if r.rule_type == "Bonus Points"]
            caps = [r for r in item_rules if r.rule_type == "Cap"]
            exclusions = [r for r in item_rules if r.rule_type == "Exclusion"]
            
            # Check exclusions first
            is_excluded = len(exclusions) > 0
            if is_excluded:
                # Log exclusions
                for r in exclusions:
                    self.log_trace(rule_name=r.rule_name, rule_type="Loyalty Rule", status="Applied", reason=f"Item excluded by rule {r.rule_name}", multiplier=0)
                evaluation_results.append({
                    "item_code": item.item_code,
                    "multiplier": 0.0,
                    "bonus_points": 0.0,
                    "cap": 0.0,
                    "excluded": True
                })
                continue
                
            # Resolve Multipliers
            effective_mult = 1.0
            applied_mult_rules = []
            if multipliers:
                # Check if any multiplier rule does not allow stacking
                has_non_stack = any(not r.allow_stack for r in multipliers)
                if has_non_stack:
                    # Pick the highest priority rule
                    best_rule = max(multipliers, key=lambda x: (x.priority, x.rule_value))
                    effective_mult = flt(best_rule.rule_value)
                    applied_mult_rules.append(best_rule)
                else:
                    # Stacking allowed: multiply all rule values
                    for r in multipliers:
                        effective_mult *= flt(r.rule_value)
                        applied_mult_rules.append(r)
            
            # Apply customer's tier multiplier
            final_mult = effective_mult * tier_multiplier
            
            # Log trace for applied multipliers
            for r in applied_mult_rules:
                self.log_trace(rule_name=r.rule_name, rule_type="Loyalty Rule", status="Applied", reason=f"Matched brand/group/style with value {r.dimension_value}", multiplier=flt(r.rule_value))
            
            # If no rule matched but tier multiplier is applied
            if not applied_mult_rules and tier_multiplier != 1.0:
                self.log_trace(rule_name=f"{tier_name} Tier Multiplier", rule_type="Loyalty Rule", status="Applied", reason=f"Customer tier {tier_name}", multiplier=tier_multiplier)
                
            # Resolve Bonus Points
            effective_bonus = 0.0
            applied_bonus_rules = []
            if bonus_points:
                has_non_stack = any(not r.allow_stack for r in bonus_points)
                if has_non_stack:
                    best_rule = max(bonus_points, key=lambda x: (x.priority, x.rule_value))
                    effective_bonus = flt(best_rule.rule_value)
                    applied_bonus_rules.append(best_rule)
                else:
                    for r in bonus_points:
                        effective_bonus += flt(r.rule_value)
                        applied_bonus_rules.append(r)
                        
            for r in applied_bonus_rules:
                self.log_trace(rule_name=r.rule_name, rule_type="Loyalty Rule", status="Applied", reason="Bonus points applied", multiplier=flt(r.rule_value))
                
            # Resolve Caps
            final_cap = 0.0
            if caps:
                # Cap is always the minimum of all matching caps
                final_cap = min(flt(r.rule_value) for r in caps)
                for r in caps:
                    self.log_trace(rule_name=r.rule_name, rule_type="Loyalty Rule", status="Applied", reason="Points cap applied", multiplier=flt(r.rule_value))
            
            evaluation_results.append({
                "item_code": item.item_code,
                "multiplier": final_mult,
                "bonus_points": effective_bonus,
                "cap": final_cap,
                "excluded": False
            })
            
        return evaluation_results

    def log_trace(self, rule_name, rule_type, status, reason, multiplier=0.0, discount_amount=0.0):
        """Creates a rule evaluation log entry if tracing is enabled in settings."""
        # Check settings
        enable_trace = frappe.db.get_single_value("SMRITI CGE Settings", "enable_rule_trace")
        if not enable_trace:
            return
            
        log_doc = frappe.get_doc({
            "doctype": "SMRITI Rule Evaluation Log",
            "invoice": self.invoice.name,
            "rule_name": rule_name,
            "rule_type": rule_type,
            "status": status,
            "reason": reason,
            "multiplier": multiplier,
            "discount_amount": discount_amount,
            "timestamp": now_datetime()
        })
        log_doc.insert(ignore_permissions=True, ignore_links=True)
        self.trace_logs.append(log_doc)


class CGECampaignManager:
    @staticmethod
    def reserve_budget(coupon_code, estimated_discount, session_id):
        """
        Increments campaign.budget_reserved.
        Sets checkouts reservation_expiry_minutes = 30.
        Throws error if budget_limit is exceeded (if stop_on_limit is active).
        """
        coupon = frappe.get_doc("Coupon Code", coupon_code)
        if not coupon.custom_campaign:
            return
            
        campaign = frappe.get_doc("SMRITI Coupon Campaign", coupon.custom_campaign)
        if campaign.status != "Active":
            frappe.throw(_("Campaign {0} is not active.").format(campaign.campaign_name))
            
        if campaign.stop_on_limit:
            total_reserved = flt(campaign.budget_reserved) + flt(campaign.budget_consumed) + flt(estimated_discount)
            if total_reserved > flt(campaign.budget_limit):
                frappe.throw(_("Campaign budget limit exceeded for campaign {0}.").format(campaign.campaign_name))
                
        # Update campaign reserved budget
        campaign.budget_reserved = flt(campaign.budget_reserved) + flt(estimated_discount)
        campaign.save(ignore_permissions=True)
        
        # Store in cache
        cache_key = f"{session_id}_{coupon_code}"
        expires_at = add_to_date(now_datetime(), minutes=30)
        
        frappe.cache().hset("cge_budget_reservations", cache_key, {
            "amount": flt(estimated_discount),
            "campaign": campaign.name,
            "expires_at": str(expires_at)
        })
        
    @staticmethod
    def commit_budget(coupon_code, final_discount, session_id):
        """
        Decrements campaign.budget_reserved by the original reserved amount.
        Increments campaign.budget_consumed by final_discount.
        """
        coupon = frappe.get_doc("Coupon Code", coupon_code)
        if not coupon.custom_campaign:
            return
            
        campaign = frappe.get_doc("SMRITI Coupon Campaign", coupon.custom_campaign)
        
        cache_key = f"{session_id}_{coupon_code}"
        reservation = frappe.cache().hget("cge_budget_reservations", cache_key)
        
        reserved_amount = 0.0
        if reservation:
            reserved_amount = flt(reservation.get("amount"))
            # remove reservation
            frappe.cache().hdel("cge_budget_reservations", cache_key)
            
        campaign.budget_reserved = max(0.0, flt(campaign.budget_reserved) - reserved_amount)
        campaign.budget_consumed = flt(campaign.budget_consumed) + flt(final_discount)
        campaign.save(ignore_permissions=True)

    @staticmethod
    def release_expired_reservations():
        """
        Cron trigger running every 30 minutes.
        Identifies expired reservations and releases budget_reserved.
        """
        reservations = frappe.cache().hgetall("cge_budget_reservations") or {}
        now = now_datetime()
        
        for cache_key, val in reservations.items():
            try:
                from frappe.utils import get_datetime
                expires_dt = get_datetime(val.get("expires_at"))
            except Exception:
                expires_dt = now
                
            if now > expires_dt:
                campaign_name = val.get("campaign")
                amount = flt(val.get("amount"))
                
                # Release budget
                if frappe.db.exists("SMRITI Coupon Campaign", campaign_name):
                    campaign = frappe.get_doc("SMRITI Coupon Campaign", campaign_name)
                    campaign.budget_reserved = max(0.0, flt(campaign.budget_reserved) - amount)
                    campaign.save(ignore_permissions=True)
                    
                # Delete from cache
                frappe.cache().hdel("cge_budget_reservations", cache_key)


class CGEWalletLedger:
    @staticmethod
    def post_transaction(customer, wallet_type, transaction_type, amount, reference_invoice=None, company=None):
        """
        Creates an immutable SMRITI Wallet Ledger entry.
        Generates corresponding double-entry Journal Voucher in ERPNext.
        """
        if not company:
            company = frappe.db.get_default("company") or frappe.get_all("Company", limit=1)[0].name
            
        # 1. Generate sequence name
        year = now_datetime().year
        count = frappe.db.count("SMRITI Wallet Ledger", {"creation": (">=", f"{year}-01-01 00:00:00")}) + 1
        seq_id = f"WL-{year}-{count:06d}"
        
        # 2. Post ledger entry
        ledger_doc = frappe.get_doc({
            "doctype": "SMRITI Wallet Ledger",
            "ledger_sequence": seq_id,
            "customer": customer,
            "wallet_type": wallet_type,
            "transaction_type": transaction_type,
            "amount": flt(amount),
            "reference_invoice": reference_invoice,
            "is_reversal": 0,
            "is_expired": 0
        })
        
        # 3. Create Journal Entry in ERPNext
        je_name = None
        try:
            je_name = create_double_entry_journal(customer, transaction_type, amount, company, seq_id)
            ledger_doc.journal_entry = je_name
        except Exception as e:
            frappe.log_error(f"Error posting CGE Journal Entry: {str(e)}")
            
        ledger_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return ledger_doc

    @staticmethod
    def reverse_transaction(ledger_seq, reason):
        """
        Performs reversal. Creates counter debit/credit entry referencing ledger_seq.
        """
        orig_doc = frappe.get_doc("SMRITI Wallet Ledger", ledger_seq)
        
        rev_type = "Debit" if orig_doc.transaction_type == "Credit" else "Credit"
        
        year = now_datetime().year
        count = frappe.db.count("SMRITI Wallet Ledger", {"creation": (">=", f"{year}-01-01 00:00:00")}) + 1
        seq_id = f"WL-{year}-{count:06d}"
        
        rev_doc = frappe.get_doc({
            "doctype": "SMRITI Wallet Ledger",
            "ledger_sequence": seq_id,
            "customer": orig_doc.customer,
            "wallet_type": orig_doc.wallet_type,
            "transaction_type": rev_type,
            "amount": orig_doc.amount,
            "reference_invoice": orig_doc.reference_invoice,
            "is_reversal": 1,
            "is_expired": 0
        })
        
        company = frappe.db.get_default("company") or frappe.get_all("Company", limit=1)[0].name
        try:
            je_name = create_double_entry_journal(orig_doc.customer, rev_type, orig_doc.amount, company, seq_id, is_reversal=True, ref_seq=ledger_seq)
            rev_doc.journal_entry = je_name
        except Exception as e:
            frappe.log_error(f"Error reversing CGE Journal Entry: {str(e)}")
            
        rev_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return rev_doc


def create_double_entry_journal(customer, transaction_type, amount, company, seq_id, is_reversal=False, ref_seq=None):
    """
    Creates double entry journal.
    Issue Cashback (Credit):
      Dr Promotion Expense
      Cr Cashback Liability
    Redemption (Debit):
      Dr Cashback Liability
      Cr Sales Invoice Adjustment
    """
    liability_account = get_or_create_account("Cashback Liability", "Liability", company)
    expense_account = get_or_create_account("Promotion Expense", "Expense", company)
    
    je = frappe.new_doc("Journal Entry")
    je.company = company
    je.posting_date = nowdate()
    je.voucher_type = "Journal Entry"
    
    remark = f"SMRITI Wallet Ledger {seq_id}"
    if is_reversal:
        remark += f" (Reversal of {ref_seq})"
    je.user_remark = remark
    
    if transaction_type == "Credit":
        je.append("accounts", {
            "account": expense_account,
            "debit_in_account_currency": flt(amount),
            "credit_in_account_currency": 0.0,
            "cost_center": frappe.get_cached_value("Company", company, "default_cost_center")
        })
        je.append("accounts", {
            "account": liability_account,
            "debit_in_account_currency": 0.0,
            "credit_in_account_currency": flt(amount),
            "party_type": "Customer",
            "party": customer
        })
    else:
        je.append("accounts", {
            "account": liability_account,
            "debit_in_account_currency": flt(amount),
            "credit_in_account_currency": 0.0,
            "party_type": "Customer",
            "party": customer
        })
        je.append("accounts", {
            "account": expense_account,
            "debit_in_account_currency": 0.0,
            "credit_in_account_currency": flt(amount),
            "cost_center": frappe.get_cached_value("Company", company, "default_cost_center")
        })
        
    je.insert(ignore_permissions=True)
    je.submit()
    return je.name


def get_customer_loyalty_points(customer):
    """Calculates active remaining loyalty points for the customer."""
    points = frappe.db.sql("""
        select sum(loyalty_points)
        from `tabLoyalty Point Entry`
        where customer = %s and expiry_date >= %s
    """, (customer, nowdate()))
    return flt(points[0][0]) if points else 0.0


def get_customer_loyalty_tier(customer):
    """Finds matching loyalty tier based on active points."""
    points = get_customer_loyalty_points(customer)
    tiers = frappe.get_all("SMRITI Loyalty Tier",
        filters={"active": 1, "min_points": ("<=", points)},
        fields=["tier_name", "tier_multiplier"],
        order_by="min_points desc",
        limit=1
    )
    if tiers:
        return tiers[0]
    return {"tier_name": "Default", "tier_multiplier": 1.0}


def get_or_create_account(account_name, account_type, company):
    """Gets or creates the account with company suffix matching standard chart of accounts."""
    abbr = frappe.db.get_value("Company", company, "abbr")
    full_name = f"{account_name} - {abbr}"
    if frappe.db.exists("Account", full_name):
        return full_name
        
    parent_account = get_parent_account(company, account_type)
    
    doc = frappe.new_doc("Account")
    doc.account_name = account_name
    doc.account_type = account_type
    doc.parent_account = parent_account
    doc.company = company
    doc.insert(ignore_permissions=True)
    return doc.name


def get_parent_account(company, account_type):
    """Finds a group account of specified type to act as parent."""
    parent = frappe.db.get_value("Account", {"company": company, "is_group": 1, "account_type": account_type})
    if parent:
        return parent
        
    if account_type == "Expense":
        search_names = ["Indirect Expenses", "Expenses", "Direct Expenses"]
    else:
        search_names = ["Current Liabilities", "Liabilities"]
        
    abbr = frappe.db.get_value("Company", company, "abbr")
    for name in search_names:
        full_name = f"{name} - {abbr}"
        if frappe.db.exists("Account", full_name):
            return full_name
            
    return frappe.db.get_value("Account", {"company": company, "is_group": 1})


def generate_nightly_liability_snapshot():
    """Sum active Loyalty points and Cashback ledger balances and record snapshot."""
    loyalty_points_sum = frappe.db.sql("""
        select sum(loyalty_points)
        from `tabLoyalty Point Entry`
        where expiry_date >= %s
    """, (nowdate()))[0][0] or 0.0
    
    credits = flt(frappe.db.get_value("SMRITI Wallet Ledger", {"transaction_type": "Credit", "is_expired": 0}, "sum(amount)"))
    debits = flt(frappe.db.get_value("SMRITI Wallet Ledger", {"transaction_type": "Debit"}, "sum(amount)"))
    cashback_bal = max(0.0, credits - debits)
    
    coupon_reserved = flt(frappe.db.get_value("SMRITI Coupon Campaign", {"status": "Active"}, "sum(budget_reserved)"))
    
    snapshot = frappe.get_doc({
        "doctype": "SMRITI Liability Snapshot",
        "snapshot_date": nowdate(),
        "loyalty_liability": loyalty_points_sum,
        "cashback_liability": cashback_bal,
        "coupon_liability": coupon_reserved,
        "giftcard_liability": 0.0
    })
    snapshot.insert(ignore_permissions=True)
    frappe.db.commit()
    return snapshot


def execute_snapshot_cleanup():
    """Deletes daily snapshots older than 90 days, keeping monthly ones up to 5 years."""
    cutoff_90_days = add_to_date(nowdate(), days=-90)
    
    old_snapshots = frappe.get_all("SMRITI Liability Snapshot",
        filters={"snapshot_date": ("<", cutoff_90_days)},
        fields=["name", "snapshot_date"]
    )
    
    for s in old_snapshots:
        s_date = getdate(s.snapshot_date)
        if s_date.day == 1:
            cutoff_5_years = add_to_date(nowdate(), years=-5)
            if s_date < cutoff_5_years:
                frappe.delete_doc("SMRITI Liability Snapshot", s.name, ignore_permissions=True)
        else:
            frappe.delete_doc("SMRITI Liability Snapshot", s.name, ignore_permissions=True)
            
    frappe.db.commit()
