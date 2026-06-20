# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/cge/service/cge_service.py
# @description: SMRITI CGE service — commission calculation and rule engine.
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

def safe_parse_redis_val(val):
    """Safely decodes and parses Redis string/bytes value to dictionary."""
    if isinstance(val, bytes):
        val = val.decode("utf-8")
    if isinstance(val, str):
        try:
            import json
            val = json.loads(val)
        except Exception:
            try:
                val = frappe.safe_eval(val)
            except Exception:
                import sys
                _frappe = sys.modules.get('frappe')
                if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in cge/service/cge_service.py:35: {sys.exc_info()[1]}")
    return val

def get_active_wallet_balance(customer):
    """Calculates customer's active wallet balance using remaining unconsumed credit balances."""
    if not customer:
        return 0.0
    credits = flt(frappe.db.sql("""
        select sum(balance_remaining)
        from `tabSMRITI Wallet Ledger`
        where customer = %s and transaction_type = 'Credit' 
          and is_expired = 0 and (expiry_date is null or expiry_date >= %s)
    """, (customer, nowdate()))[0][0])
    return credits


def calculate_wallet_expiry_date(posting_date=None):
    """Calculates wallet expiry date based on wallet_validity_days in SMRITI CGE Settings (defaults to 90)."""
    if not posting_date:
        posting_date = nowdate()
    validity_days = frappe.db.get_single_value("SMRITI CGE Settings", "wallet_validity_days")
    if validity_days is None:
        validity_days = 90
    else:
        validity_days = int(validity_days)
    return add_to_date(posting_date, days=validity_days)


def consume_credits(customer, debit_amount):
    """Consumes active unexpired credits in FIFO order (by expiry_date ascending)."""
    debit_amount = flt(debit_amount)
    if debit_amount <= 0:
        return
        
    credits = frappe.get_all(
        "SMRITI Wallet Ledger",
        filters={
            "customer": customer,
            "transaction_type": "Credit",
            "is_expired": 0,
            "balance_remaining": (">", 0)
        },
        fields=["name", "balance_remaining"],
        order_by="expiry_date asc, creation asc"
    )
    
    remaining_to_deduct = debit_amount
    for c in credits:
        bal = flt(c.balance_remaining)
        if bal >= remaining_to_deduct:
            frappe.db.set_value("SMRITI Wallet Ledger", c.name, "balance_remaining", bal - remaining_to_deduct)
            remaining_to_deduct = 0.0
            break
        else:
            frappe.db.set_value("SMRITI Wallet Ledger", c.name, "balance_remaining", 0.0)
            remaining_to_deduct -= bal


class CGERuleEvaluator:
    def __init__(self, invoice_doc):
        self.invoice = invoice_doc
        self.customer = invoice_doc.customer
        self.items = invoice_doc.items
        self.trace_logs = []
        # Pre-check columns once in constructor (AUD-18)
        self.has_style_col = frappe.db.has_column("Item", "custom_style_code")
        self.has_season_col = frappe.db.has_column("Item", "custom_season")

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
        
        # Batch pre-fetch item dimensions to avoid N+1 queries inside loop (AUD-10)
        item_codes = list(set([item.item_code for item in self.items]))
        item_dimension_cache = {}
        if item_codes:
            fields = ["name", "brand", "item_group"]
            if self.has_style_col:
                fields.append("custom_style_code")
            if self.has_season_col:
                fields.append("custom_season")
            
            items_info = frappe.get_all("Item", filters={"name": ["in", item_codes]}, fields=fields)
            item_dimension_cache = {d.name: d for d in items_info}
        
        # 3. Match rules for each item
        for item in self.items:
            item_rules = []
            
            # Fetch item brand, group, style, season etc. from batch cache (AUD-10)
            item_info = item_dimension_cache.get(item.item_code) or {}
            item_brand = item_info.get("brand")
            item_group = item_info.get("item_group")
            item_style = item_info.get("custom_style_code")
            item_season = item_info.get("custom_season")
            
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
            
        # Use invoice name if available; invoice may be unsaved in test scenarios
        invoice_name = getattr(self.invoice, "name", None) or ""
        log_doc = frappe.get_doc({
            "doctype": "SMRITI Rule Evaluation Log",
            "invoice": invoice_name,
            "rule_name": rule_name,
            "rule_type": rule_type,
            "status": status,
            "reason": reason,
            "multiplier": multiplier,
            "discount_amount": discount_amount,
            "timestamp": now_datetime()
        })
        log_doc.insert(ignore_permissions=True, ignore_links=True, ignore_mandatory=True)
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
            if isinstance(cache_key, bytes):
                cache_key = cache_key.decode("utf-8")
            val = safe_parse_redis_val(val)
            if not isinstance(val, dict):
                continue
                
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
    def post_transaction(customer, wallet_type, transaction_type, amount, reference_invoice=None, company=None, remarks=None, adjustment_reason_type="POS Transaction"):
        """
        Creates an immutable SMRITI Wallet Ledger entry.
        Generates corresponding double-entry Journal Voucher in ERPNext.
        Enforces deterministic idempotency.
        """
        # Deterministic Idempotency Check
        if reference_invoice:
            duplicate = frappe.db.exists("SMRITI Wallet Ledger", {
                "reference_invoice": reference_invoice,
                "transaction_type": transaction_type,
                "wallet_type": wallet_type,
                "is_reversal": 0
            })
            if duplicate:
                frappe.throw(
                    _("Duplicate transaction detected: wallet entry already posted for invoice {0}.").format(reference_invoice),
                    frappe.DuplicateEntryError
                )

        if not company:
            if reference_invoice:
                if frappe.db.exists("POS Invoice", reference_invoice):
                    company = frappe.db.get_value("POS Invoice", reference_invoice, "company")
                elif frappe.db.exists("Sales Invoice", reference_invoice):
                    company = frappe.db.get_value("Sales Invoice", reference_invoice, "company")
            
            if not company:
                company = frappe.defaults.get_user_default("Company")
                
            if not company:
                company = frappe.db.get_default("company") or frappe.get_all("Company", limit=1)[0].name

        # Wallet negative balance check
        if transaction_type == "Debit":
            active_bal = get_active_wallet_balance(customer)
            if flt(amount) > active_bal:
                frappe.throw(
                    _("Insufficient wallet balance for Customer {0}. Active balance: {1}, requested debit: {2}").format(
                        customer, active_bal, amount
                    ),
                    frappe.ValidationError
                )

        # 1. Generate sequence name via atomic naming series
        from frappe.model.naming import make_autoname
        seq_id = make_autoname("WL-.YYYY.-.#####")
        
        # 2. Expiry & balance_remaining calculation
        expiry_date = None
        balance_remaining = 0.0
        if transaction_type == "Credit":
            expiry_date = calculate_wallet_expiry_date(nowdate())
            balance_remaining = flt(amount)
        
        # 3. Post ledger entry
        ledger_doc = frappe.get_doc({
            "doctype": "SMRITI Wallet Ledger",
            "ledger_sequence": seq_id,
            "customer": customer,
            "company": company,
            "wallet_type": wallet_type,
            "transaction_type": transaction_type,
            "amount": flt(amount),
            "balance_remaining": balance_remaining,
            "reference_invoice": reference_invoice,
            "expiry_date": expiry_date,
            "is_reversal": 0,
            "is_expired": 0,
            "remarks": remarks,
            "adjustment_reason_type": adjustment_reason_type
        })
        
        # 4. Create Journal Entry in ERPNext (propagate exception on failure, no swallowing)
        try:
            je_name = create_double_entry_journal(customer, transaction_type, amount, company, seq_id, reference_invoice=reference_invoice)
            ledger_doc.journal_entry = je_name
        except Exception as e:
            frappe.log_error(title="CGE Wallet Journal Posting Failure", message=frappe.get_traceback())
            raise e
            
        ledger_doc.insert(ignore_permissions=True)
        
        # 5. If Debit, consume credits in FIFO order
        if transaction_type == "Debit":
            consume_credits(customer, amount)
            
        return ledger_doc

    @staticmethod
    def reverse_transaction(ledger_seq, reason):
        """
        Performs reversal. Creates counter debit/credit entry referencing ledger_seq.
        """
        orig_doc = frappe.get_doc("SMRITI Wallet Ledger", ledger_seq)
        
        rev_type = "Debit" if orig_doc.transaction_type == "Credit" else "Credit"
        
        from frappe.model.naming import make_autoname
        seq_id = make_autoname("WL-.YYYY.-.#####")
        
        # Expiry & balance_remaining logic for reversal
        expiry_date = None
        balance_remaining = 0.0
        if rev_type == "Credit":
            expiry_date = orig_doc.expiry_date or calculate_wallet_expiry_date(nowdate())
            balance_remaining = orig_doc.amount

        company = orig_doc.company
        if not company:
            company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name

        rev_doc = frappe.get_doc({
            "doctype": "SMRITI Wallet Ledger",
            "ledger_sequence": seq_id,
            "customer": orig_doc.customer,
            "company": company,
            "wallet_type": orig_doc.wallet_type,
            "transaction_type": rev_type,
            "amount": orig_doc.amount,
            "balance_remaining": balance_remaining,
            "reference_invoice": orig_doc.reference_invoice,
            "expiry_date": expiry_date,
            "is_reversal": 1,
            "is_expired": 0,
            "remarks": reason,
            "adjustment_reason_type": "Reversal"
        })
        
        try:
            je_name = create_double_entry_journal(orig_doc.customer, rev_type, orig_doc.amount, company, seq_id, is_reversal=True, ref_seq=ledger_seq, reference_invoice=orig_doc.reference_invoice)
            rev_doc.journal_entry = je_name
        except Exception as e:
            frappe.log_error(title="CGE Wallet Reversal Journal Posting Failure", message=frappe.get_traceback())
            raise e
            
        rev_doc.insert(ignore_permissions=True)
        
        # If Debit, consume credits in FIFO order
        if rev_type == "Debit":
            consume_credits(orig_doc.customer, orig_doc.amount)
            
        return rev_doc


def reconcile_wallet_liability():
    """
    Daily reconciliation job. Verifies customer wallet balances match ledger records.
    Records reconciliation snapshot and alerts on variance.
    """
    # 1. Calculate sum from ledger using the safer dynamic date filter
    credits = flt(frappe.db.sql("""
        select sum(amount)
        from `tabSMRITI Wallet Ledger`
        where transaction_type = 'Credit' and is_expired = 0 
          and (expiry_date is null or expiry_date >= %s)
    """, (nowdate()))[0][0])
    debits_res = frappe.db.sql("""
        select sum(amount) from `tabSMRITI Wallet Ledger`
        where transaction_type = 'Debit'
    """)
    debits = flt(debits_res[0][0] if debits_res else 0)
    ledger_total = max(0.0, credits - debits)

    # 2. Sum up balances from wallets per customer using grouped queries (AUD-11)
    credits_res = frappe.db.sql("""
        select customer, sum(amount)
        from `tabSMRITI Wallet Ledger`
        where transaction_type = 'Credit' and is_expired = 0 
          and (expiry_date is null or expiry_date >= %s)
        group by customer
    """, (nowdate()))
    
    debits_res = frappe.db.sql("""
        select customer, sum(amount)
        from `tabSMRITI Wallet Ledger`
        where transaction_type = 'Debit'
        group by customer
    """)
    
    credits_map = {r[0]: flt(r[1]) for r in credits_res if r[0]}
    debits_map = {r[0]: flt(r[1]) for r in debits_res if r[0]}
    
    all_customers = set(list(credits_map.keys()) + list(debits_map.keys()))
    wallet_total = 0.0
    for cust in all_customers:
        active_bal = max(0.0, credits_map.get(cust, 0.0) - debits_map.get(cust, 0.0))
        wallet_total += active_bal

    variance = flt(ledger_total - wallet_total)
    status = "Reconciled" if abs(variance) < 0.01 else "Mismatch"

    details_dict = {
        "ledger_total": ledger_total,
        "wallet_total": wallet_total,
        "variance": variance,
        "status": status,
        "checked_customers_count": len(all_customers)
    }
    
    # Save snapshot
    snapshot = frappe.get_doc({
        "doctype": "SMRITI Wallet Reconciliation Snapshot",
        "snapshot_date": nowdate(),
        "wallet_total": wallet_total,
        "ledger_total": ledger_total,
        "variance": variance,
        "status": status,
        "details": json.dumps(details_dict, indent=2)
    })
    
    today_snapshot = frappe.db.exists("SMRITI Wallet Reconciliation Snapshot", {"snapshot_date": nowdate()})
    if today_snapshot:
        frappe.delete_doc("SMRITI Wallet Reconciliation Snapshot", today_snapshot, ignore_permissions=True)
        
    snapshot.insert(ignore_permissions=True)
    frappe.db.commit()

    if status == "Mismatch":
        frappe.log_error(
            title="SMRITI Wallet Reconciliation Mismatch Alert",
            message=f"Reconciliation variance detected on {nowdate()}: Variance = {variance}. Details: {json.dumps(details_dict)}"
        )
    return snapshot


def create_double_entry_journal(customer, transaction_type, amount, company, seq_id, is_reversal=False, ref_seq=None, reference_invoice=None):
    """
    Creates double entry journal.
    Issue Cashback (Credit):
      Dr Promotion Expense
      Cr Cashback Liability
    Redemption (Debit):
      Dr Cashback Liability
      Cr Accounts Receivable (Customer, referencing Sales/POS Invoice)
    """
    liability_account = get_or_create_account("Cashback Liability", "Liability", company)
    
    je = frappe.new_doc("Journal Entry")
    je.company = company
    je.posting_date = nowdate()
    je.voucher_type = "Journal Entry"
    
    remark = f"SMRITI Wallet Ledger {seq_id}"
    if is_reversal:
        remark += f" (Reversal of {ref_seq})"
    je.user_remark = remark
    
    if is_reversal:
        if transaction_type == "Credit":
            # Reversing a Debit (redemption) -> Dr Accounts Receivable, Cr Cashback Liability
            receivable_account = frappe.db.get_value("Party Account", {"parent": customer, "company": company}, "account")
            if not receivable_account:
                receivable_account = frappe.db.get_value("Customer", customer, "receivable_account")
            if not receivable_account:
                receivable_account = frappe.get_cached_value("Company", company, "default_receivable_account")
            if not receivable_account:
                receivable_account = get_or_create_account("Accounts Receivable", "Receivable", company)
                
            debit_row = {
                "account": receivable_account,
                "debit_in_account_currency": flt(amount),
                "credit_in_account_currency": 0.0,
                "party_type": "Customer",
                "party": customer
            }
            if reference_invoice:
                if frappe.db.exists("POS Invoice", reference_invoice):
                    ref_doctype = "POS Invoice"
                else:
                    ref_doctype = "Sales Invoice"
                debit_row["reference_type"] = ref_doctype
                debit_row["reference_name"] = reference_invoice
                
            je.append("accounts", debit_row)
            je.append("accounts", {
                "account": liability_account,
                "debit_in_account_currency": 0.0,
                "credit_in_account_currency": flt(amount)
                # party_type/party NOT set — Liability account type disallows it
            })
        else:
            # Reversing a Credit (cashback issue) -> Dr Cashback Liability, Cr Promotion Expense
            expense_account = get_or_create_account("Promotion Expense", "Expense Account", company)
            je.append("accounts", {
                "account": liability_account,
                "debit_in_account_currency": flt(amount),
                "credit_in_account_currency": 0.0
                # party_type/party NOT set — Liability account type disallows it
            })
            je.append("accounts", {
                "account": expense_account,
                "debit_in_account_currency": 0.0,
                "credit_in_account_currency": flt(amount),
                "cost_center": frappe.get_cached_value("Company", company, "default_cost_center")
            })
    else:
        if transaction_type == "Credit":
            expense_account = get_or_create_account("Promotion Expense", "Expense Account", company)
            je.append("accounts", {
                "account": expense_account,
                "debit_in_account_currency": flt(amount),
                "credit_in_account_currency": 0.0,
                "cost_center": frappe.get_cached_value("Company", company, "default_cost_center")
            })
            je.append("accounts", {
                "account": liability_account,
                "debit_in_account_currency": 0.0,
                "credit_in_account_currency": flt(amount)
                # party_type/party NOT set — Liability account type disallows it
            })
        else:
            # Resolve customer standard Accounts Receivable account
            # ERPNext: customer AR is stored in Party Account child table, not on Customer DocType
            receivable_account = frappe.db.get_value(
                "Party Account",
                {"parent": customer, "company": company, "parenttype": "Customer"},
                "account"
            )
            if not receivable_account:
                receivable_account = frappe.get_cached_value("Company", company, "default_receivable_account")
            if not receivable_account:
                receivable_account = get_or_create_account("Accounts Receivable", "Receivable", company)
                
            je.append("accounts", {
                "account": liability_account,
                "debit_in_account_currency": flt(amount),
                "credit_in_account_currency": 0.0
                # party_type/party NOT set — Liability account type disallows it
            })
            
            credit_row = {
                "account": receivable_account,
                "debit_in_account_currency": 0.0,
                "credit_in_account_currency": flt(amount),
                "party_type": "Customer",
                "party": customer
            }
            if reference_invoice:
                if frappe.db.exists("POS Invoice", reference_invoice):
                    ref_doctype = "POS Invoice"
                else:
                    ref_doctype = "Sales Invoice"
                credit_row["reference_type"] = ref_doctype
                credit_row["reference_name"] = reference_invoice
                
            je.append("accounts", credit_row)
        
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
        
    if account_type in ["Expense", "Expense Account"]:
        search_names = ["Indirect Expenses", "Expenses", "Direct Expenses"]
    elif account_type in ["Asset", "Receivable"]:
        search_names = ["Current Assets", "Assets"]
    else:
        search_names = ["Current Liabilities", "Liabilities"]
        
    abbr = frappe.db.get_value("Company", company, "abbr")
    for name in search_names:
        full_name = f"{name} - {abbr}"
        if frappe.db.exists("Account", full_name):
            return full_name
            
    return frappe.db.get_value("Account", {"company": company, "is_group": 1})


def generate_nightly_liability_snapshot(company=None):
    """Sum active Loyalty points, Cashback ledger balances, and Coupon Campaign budget reservations per company and record snapshot idempotently."""
    today = nowdate()
    
    # 1. Sum remaining points for active Loyalty Point Entries
    if company:
        # Join with Sales Invoice and POS Invoice to filter by company
        loyalty_points_sum = flt(frappe.db.sql("""
            select sum(lpe.remaining_points)
            from `tabLoyalty Point Entry` lpe
            left join `tabSales Invoice` si on lpe.invoice = si.name
            left join `tabPOS Invoice` pi on lpe.invoice = pi.name
            where lpe.expiry_date >= %s
              and (si.company = %s or pi.company = %s)
        """, (today, company, company))[0][0])
    else:
        loyalty_points_sum = flt(frappe.db.sql("""
            select sum(remaining_points)
            from `tabLoyalty Point Entry`
            where expiry_date >= %s
        """, (today,))[0][0])
        
    # 2. Sum Cashback balances from SMRITI Wallet Ledger
    if company:
        credits = flt(frappe.db.sql("""
            select sum(balance_remaining)
            from `tabSMRITI Wallet Ledger`
            where company = %s and transaction_type = 'Credit' and is_expired = 0 
              and (expiry_date is null or expiry_date >= %s)
        """, (company, today))[0][0])
    else:
        credits = flt(frappe.db.sql("""
            select sum(balance_remaining)
            from `tabSMRITI Wallet Ledger`
            where transaction_type = 'Credit' and is_expired = 0 
              and (expiry_date is null or expiry_date >= %s)
        """, (today,))[0][0])
        
    cashback_bal = credits
    
    # 3. Sum Coupon Campaign budget reservations
    has_company_campaign = frappe.db.has_column("SMRITI Coupon Campaign", "company")
    if has_company_campaign and company:
        coupon_reserved_res = frappe.db.sql("""
            select sum(budget_reserved) from `tabSMRITI Coupon Campaign`
            where status = 'Active' and company = %s
        """, (company,))
    else:
        coupon_reserved_res = frappe.db.sql("""
            select sum(budget_reserved) from `tabSMRITI Coupon Campaign`
            where status = 'Active'
        """)
    coupon_reserved = flt(coupon_reserved_res[0][0] if coupon_reserved_res else 0)
    
    # Check if snapshot exists for company and date (Idempotent update-or-create)
    filters = {"snapshot_date": today}
    if company:
        filters["company"] = company
    else:
        filters["company"] = ["is", "not set"]
        
    existing_name = frappe.db.get_value("SMRITI Liability Snapshot", filters, "name")
    
    if existing_name:
        snapshot = frappe.get_doc("SMRITI Liability Snapshot", existing_name)
        snapshot.loyalty_liability = loyalty_points_sum
        snapshot.cashback_liability = cashback_bal
        snapshot.coupon_liability = coupon_reserved
        snapshot.giftcard_liability = 0.0
        snapshot.save(ignore_permissions=True)
    else:
        snapshot = frappe.get_doc({
            "doctype": "SMRITI Liability Snapshot",
            "snapshot_date": today,
            "company": company,
            "loyalty_liability": loyalty_points_sum,
            "cashback_liability": cashback_bal,
            "coupon_liability": coupon_reserved,
            "giftcard_liability": 0.0
        })
        snapshot.insert(ignore_permissions=True)
        
    frappe.db.commit()
    return snapshot


def generate_all_liability_snapshots():
    """Scheduled daily runner to generate liability snapshots for all active companies."""
    companies = frappe.get_all("Company", filters={"is_group": 0}, pluck="name")
    for company in companies:
        generate_nightly_liability_snapshot(company)
    # Generate global snapshot (company = None) for compatibility
    generate_nightly_liability_snapshot(None)


def expire_wallet_credits():
    """Daily scheduler task to mark unconsumed past-due wallet credits as expired."""
    today = nowdate()
    expired_entries = frappe.get_all(
        "SMRITI Wallet Ledger",
        filters={
            "transaction_type": "Credit",
            "is_expired": 0,
            "expiry_date": ("<", today),
            "balance_remaining": (">", 0)
        },
        fields=["name", "customer", "balance_remaining", "company"]
    )
    
    for entry in expired_entries:
        frappe.db.set_value("SMRITI Wallet Ledger", entry.name, {
            "is_expired": 1,
            "balance_remaining": 0.0
        })
        
    frappe.db.commit()


def release_expired_reservations():
    """Wrapper to run CGECampaignManager.release_expired_reservations() from dotted path hook."""
    CGECampaignManager.release_expired_reservations()


def cleanup_expired_budget_reservations():
    """
    Daily scheduler task (safety sweeper).
    1. Finds reservations in Redis older than 24 hours.
    2. Checks if corresponding invoice exists/submitted.
    3. If not, releases the budget and deletes the reservation from Redis.
    4. Reconciles all active campaigns' budget_reserved with active Redis reservations to heal from Redis restarts.
    """
    # 1. Clean up Redis reservations older than 24 hours
    reservations = frappe.cache().hgetall("cge_budget_reservations") or {}
    now = now_datetime()
    
    for cache_key, val in reservations.items():
        if isinstance(cache_key, bytes):
            cache_key = cache_key.decode("utf-8")
        val = safe_parse_redis_val(val)
        if not isinstance(val, dict):
            continue
            
        try:
            from frappe.utils import get_datetime
            expires_dt = get_datetime(val.get("expires_at"))
            if (now - expires_dt).total_seconds() > 24 * 3600:
                # Check if invoice exists and is submitted
                invoice_submitted = False
                parts = cache_key.split("_")
                invoice_name = None
                if len(parts) >= 2:
                    session_id = "_".join(parts[:-1])
                    invoice_name = frappe.db.get_value("POS Invoice", {"custom_billing_session_id": session_id}, "name")
                    if not invoice_name:
                        invoice_name = frappe.db.get_value("Sales Invoice", {"custom_billing_session_id": session_id}, "name")
                    if not invoice_name:
                        for p in parts:
                            if p.startswith("ACC-") or p.startswith("SINV-") or p.startswith("PINV-") or "-" in p:
                                invoice_name = p
                                break
                
                if invoice_name:
                    docstatus = frappe.db.get_value("POS Invoice", invoice_name, "docstatus")
                    if docstatus is None:
                        docstatus = frappe.db.get_value("Sales Invoice", invoice_name, "docstatus")
                    if docstatus == 1:
                        invoice_submitted = True
                        
                if not invoice_submitted:
                    campaign_name = val.get("campaign")
                    amount = flt(val.get("amount"))
                    if frappe.db.exists("SMRITI Coupon Campaign", campaign_name):
                        campaign = frappe.get_doc("SMRITI Coupon Campaign", campaign_name)
                        campaign.budget_reserved = max(0.0, flt(campaign.budget_reserved) - amount)
                        campaign.save(ignore_permissions=True)
                    
                    frappe.cache().hdel("cge_budget_reservations", cache_key)
        except Exception as ex:
            frappe.log_error(title="CGE Stale Reservation Cleanup Error", message=frappe.get_traceback())
            
    # 2. Reconcile campaign.budget_reserved with Redis to heal from restarts
    try:
        active_campaigns = frappe.get_all("SMRITI Coupon Campaign", filters={"status": "Active"}, fields=["name", "budget_reserved"])
        redis_reservations = frappe.cache().hgetall("cge_budget_reservations") or {}
        
        campaign_redis_sums = {}
        for cache_key, val in redis_reservations.items():
            if isinstance(cache_key, bytes):
                cache_key = cache_key.decode("utf-8")
            val = safe_parse_redis_val(val)
            if isinstance(val, dict):
                camp = val.get("campaign")
                amt = flt(val.get("amount"))
                if camp:
                    campaign_redis_sums[camp] = campaign_redis_sums.get(camp, 0.0) + amt

                    
        for camp_doc in active_campaigns:
            expected_reserved = campaign_redis_sums.get(camp_doc.name, 0.0)
            if abs(flt(camp_doc.budget_reserved) - expected_reserved) > 0.01:
                frappe.db.set_value("SMRITI Coupon Campaign", camp_doc.name, "budget_reserved", expected_reserved)
                
        frappe.db.commit()
    except Exception as ex:
        frappe.log_error(title="CGE Campaign Budget Reconciliation Error", message=frappe.get_traceback())


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


import hashlib
import json

def validate_coupon_code(coupon_code, customer, docname=None):
    """
    Validates a coupon code against all limits.
    Throws ValidationError if any limits are violated.
    """
    if not customer:
        frappe.throw(_("Customer is required for coupon validation."), frappe.ValidationError)
        
    settings = frappe.get_single("SMRITI CGE Settings")
    if not settings.enable_coupon:
        frappe.throw(_("Coupon Studio is disabled in CGE settings."), frappe.ValidationError)
        
    if not frappe.db.exists("Coupon Code", coupon_code):
        frappe.throw(_("Coupon Code {0} does not exist.").format(coupon_code), frappe.ValidationError)
        
    coupon = frappe.get_doc("Coupon Code", coupon_code)
    today = getdate(nowdate())
    
    # Dates
    if coupon.valid_from and today < getdate(coupon.valid_from):
        frappe.throw(_("Coupon Code {0} is not active yet.").format(coupon_code), frappe.ValidationError)
    if coupon.valid_upto and today > getdate(coupon.valid_upto):
        frappe.throw(_("Coupon Code {0} has expired.").format(coupon_code), frappe.ValidationError)
        
    # Overall Limit
    if coupon.maximum_use and coupon.used >= coupon.maximum_use:
        frappe.throw(_("Coupon Code {0} has reached its maximum usage limit.").format(coupon_code), frappe.ValidationError)
        
    # Customer limit (AUD-02: count across both Sales Invoice and POS Invoice)
    if coupon.custom_max_uses_per_customer:
        total_cust_uses = 0
        for doctype in ["Sales Invoice", "POS Invoice"]:
            res = frappe.db.sql(f"""
                select count(name) from `tab{doctype}`
                where customer = %s and docstatus = 1
                  and coupon_code = %s
                  and name != %s
            """, (customer, coupon_code, docname or ""))
            total_cust_uses += res[0][0] if res else 0
            
        if total_cust_uses >= coupon.custom_max_uses_per_customer:
            frappe.throw(_("Coupon Code {0} has exceeded customer usage limit.").format(coupon_code), frappe.ValidationError)
            
    # Mobile limit (AUD-02: count across both Sales Invoice and POS Invoice)
    if coupon.custom_max_uses_per_mobile:
        mobile = frappe.db.get_value("Customer", customer, "mobile_no")
        if mobile:
            matching_customers = frappe.get_all("Customer", filters={"mobile_no": mobile}, pluck="name")
            if matching_customers:
                total_mobile_uses = 0
                for doctype in ["Sales Invoice", "POS Invoice"]:
                    res = frappe.db.sql(f"""
                        select count(name) from `tab{doctype}`
                        where customer in %s and docstatus = 1
                          and coupon_code = %s
                          and name != %s
                    """, (matching_customers, coupon_code, docname or ""))
                    total_mobile_uses += res[0][0] if res else 0
                    
                if total_mobile_uses >= coupon.custom_max_uses_per_mobile:
                    frappe.throw(_("Coupon Code {0} has exceeded mobile usage limit.").format(coupon_code), frappe.ValidationError)
                    
    # Daily limit (AUD-02: count across both Sales Invoice and POS Invoice)
    if coupon.custom_max_uses_per_day:
        total_daily_uses = 0
        for doctype in ["Sales Invoice", "POS Invoice"]:
            res = frappe.db.sql(f"""
                select count(name) from `tab{doctype}`
                where posting_date = %s and docstatus = 1
                  and coupon_code = %s
                  and name != %s
            """, (nowdate(), coupon_code, docname or ""))
            total_daily_uses += res[0][0] if res else 0
            
        if total_daily_uses >= coupon.custom_max_uses_per_day:
            frappe.throw(_("Coupon Code {0} has exceeded daily usage limit.").format(coupon_code), frappe.ValidationError)
            
    # Campaign budget
    if coupon.custom_campaign:
        campaign = frappe.get_doc("SMRITI Coupon Campaign", coupon.custom_campaign)
        if campaign.status != "Active":
            frappe.throw(_("Campaign {0} linked to Coupon is not Active.").format(campaign.campaign_name), frappe.ValidationError)
        if campaign.start_date and today < getdate(campaign.start_date):
            frappe.throw(_("Campaign {0} is not active yet.").format(campaign.campaign_name), frappe.ValidationError)
        if campaign.end_date and today > getdate(campaign.end_date):
            frappe.throw(_("Campaign {0} has ended.").format(campaign.campaign_name), frappe.ValidationError)
            
    return coupon


@frappe.whitelist()
def validate_checkout_rules(invoice_data):
    """
    POS Checkout Rule Pipeline calculation endpoint.
    Calculates loyalty points earned, coupon discounts, wallet deductions, and net total.
    """
    if isinstance(invoice_data, str):
        invoice_data = json.loads(invoice_data)
        
    customer = invoice_data.get("customer")
    items = invoice_data.get("items") or []
    coupon_code = invoice_data.get("coupon_code")
    use_wallet_balance = flt(invoice_data.get("use_wallet_balance", 0))
    session_id = invoice_data.get("session_id")
    company = invoice_data.get("company") or frappe.db.get_default("company") or frappe.get_all("Company", limit=1)[0].name
    
    settings = frappe.get_doc("SMRITI CGE Settings")
    
    # Create Sales Invoice mockup in-memory for CGERuleEvaluator
    invoice_doc = frappe.new_doc("Sales Invoice")
    invoice_doc.customer = customer
    invoice_doc.company = company
    invoice_doc.posting_date = nowdate()
    for item in items:
        invoice_doc.append("items", {
            "item_code": item.get("item_code"),
            "qty": flt(item.get("qty", 1)),
            "rate": flt(item.get("rate", 0)),
            "warehouse": item.get("warehouse")
        })
        
    loyalty_points_earned = 0.0
    loyalty_tier = "Default"
    item_results = []
    
    # 1. Loyalty Resolution
    if settings.enable_loyalty and customer:
        evaluator = CGERuleEvaluator(invoice_doc)
        item_results = evaluator.evaluate()
        
        # Get standard points collection factor
        loyalty_program = frappe.db.get_value("Customer", customer, "loyalty_program")
        collection_factor = 0.0
        if loyalty_program:
            collection_rules = frappe.get_all("Loyalty Program Collection",
                filters={"parent": loyalty_program},
                fields=["collection_factor"]
            )
            if collection_rules:
                collection_factor = flt(collection_rules[0].collection_factor)
                
        # Calculate points for each item
        for i, res in enumerate(item_results):
            item = items[i]
            qty = flt(item.get("qty", 1))
            rate = flt(item.get("rate", 0))
            if res.get("excluded"):
                points = 0.0
            else:
                multiplier = flt(res.get("multiplier", 1.0))
                bonus = flt(res.get("bonus_points", 0.0))
                cap = flt(res.get("cap", 0.0))
                
                points = (rate * qty * collection_factor * multiplier) + bonus
                if cap > 0.0:
                    points = min(points, cap)
            
            res["points_earned"] = flt(points)
            loyalty_points_earned += points
            
        tier_info = get_customer_loyalty_tier(customer)
        loyalty_tier = tier_info.get("tier_name", "Default")
        
    # 2. Coupon Validation
    coupon_discount = 0.0
    if coupon_code:
        coupon = validate_coupon_code(coupon_code, customer)
        
        # Calculate discount using Pricing Rule
        if not coupon.pricing_rule:
            frappe.throw(_("No Pricing Rule linked to Coupon {0}.").format(coupon_code), frappe.ValidationError)
            
        pr = frappe.get_doc("Pricing Rule", coupon.pricing_rule)
        cart_total = sum(flt(item.get("qty", 1)) * flt(item.get("rate", 0)) for item in items)
        
        matched_items = []
        scope = coupon.custom_coupon_scope or "Invoice"
        
        for item in items:
            item_code = item.get("item_code")
            item_brand = frappe.db.get_value("Item", item_code, "brand")
            item_group = frappe.db.get_value("Item", item_code, "item_group")
            
            is_matched = False
            if scope == "Invoice":
                is_matched = True
            elif scope == "Item" and item_code == pr.item_code:
                is_matched = True
            elif scope == "Brand" and item_brand == pr.brand:
                is_matched = True
            elif scope == "Item Group" and item_group == pr.item_group:
                is_matched = True
            elif scope == "Store" and (item.get("warehouse") == pr.warehouse or invoice_doc.set_warehouse == pr.warehouse):
                is_matched = True
            elif scope == "Customer" and customer == pr.customer:
                is_matched = True
            elif scope == "Customer Group":
                cust_group = frappe.db.get_value("Customer", customer, "customer_group")
                if cust_group == pr.customer_group:
                    is_matched = True
                    
            if is_matched:
                matched_items.append(item)
                
        if matched_items:
            matched_total = sum(flt(item.get("qty", 1)) * flt(item.get("rate", 0)) for item in matched_items)
            if pr.rate_or_discount == "Discount Percentage":
                coupon_discount = matched_total * (flt(pr.discount_percentage) / 100.0)
            elif pr.rate_or_discount == "Discount Amount":
                coupon_discount = min(flt(pr.discount_amount), matched_total)
            elif pr.rate_or_discount == "Rate":
                orig_total = sum(flt(item.get("qty", 1)) * flt(item.get("rate", 0)) for item in matched_items)
                new_total = sum(flt(item.get("qty", 1)) * flt(pr.rate) for item in matched_items)
                coupon_discount = max(0.0, orig_total - new_total)
                
            if coupon.custom_max_discount_cap and coupon_discount > flt(coupon.custom_max_discount_cap):
                coupon_discount = flt(coupon.custom_max_discount_cap)
                
        # Check campaign budget limits
        if coupon.custom_campaign and settings.enable_campaign_budget:
            campaign = frappe.get_doc("SMRITI Coupon Campaign", coupon.custom_campaign)
            if campaign.stop_on_limit:
                total_exposure = flt(campaign.budget_consumed) + flt(campaign.budget_reserved) + coupon_discount
                if total_exposure > flt(campaign.budget_limit):
                    frappe.throw(_("Campaign budget limit exceeded for campaign {0}.").format(campaign.campaign_name), frappe.ValidationError)
                    
        # Reserve campaign budget if session_id is provided
        if session_id and coupon.custom_campaign and coupon_discount > 0:
            CGECampaignManager.reserve_budget(coupon_code, coupon_discount, session_id)
            
    # 3. Wallet Deduction
    wallet_deduction = 0.0
    cart_total = sum(flt(item.get("qty", 1)) * flt(item.get("rate", 0)) for item in items)
    net_total = max(0.0, cart_total - coupon_discount)
    
    if use_wallet_balance > 0 and customer:
        if not settings.enable_cashback:
            frappe.throw(_("Cashback Wallet is disabled in CGE settings."), frappe.ValidationError)
            
        active_bal = get_active_wallet_balance(customer)
        
        if use_wallet_balance > active_bal:
            frappe.throw(_("Requested wallet deduction {0} exceeds active cashback balance {1}.").format(use_wallet_balance, active_bal), frappe.ValidationError)
            
        wallet_deduction = min(use_wallet_balance, net_total)
        net_total = max(0.0, net_total - wallet_deduction)
        
    return {
        "loyalty_points_earned": flt(loyalty_points_earned),
        "loyalty_tier": loyalty_tier,
        "coupon_discount": flt(coupon_discount),
        "wallet_deduction": flt(wallet_deduction),
        "net_total": flt(net_total),
        "items": item_results
    }


def execute_non_critical(operation_name, fn):
    """
    Wraps non-critical transaction hooks in protected execution handlers to log errors 
    without aborting the cashier's main checkout submission (AUD-08).
    """
    try:
        fn()
    except Exception as e:
        frappe.log_error(
            title=f"CGE Non-Critical Hook Error: {operation_name}",
            message=frappe.get_traceback()
        )


def process_invoice_submit(doc, method=None):
    """
    Hook handler on POS/Sales Invoice submit.
    Commits coupon budget, posts wallet ledger entries, and writes loyalty points.
    """
    settings = frappe.get_doc("SMRITI CGE Settings")
    
    # 1. Wallet Deduction (Critical)
    wallet_ded_amt = flt(doc.get("custom_wallet_deduction"))
    if wallet_ded_amt > 0.0 and settings.enable_cashback:
        exists = frappe.db.exists("SMRITI Wallet Ledger", {"reference_invoice": doc.name, "transaction_type": "Debit"})
        if not exists:
            CGEWalletLedger.post_transaction(
                customer=doc.customer,
                wallet_type="Promo Cashback",
                transaction_type="Debit",
                amount=wallet_ded_amt,
                reference_invoice=doc.name,
                company=doc.company
            )
            
    # 2. Coupon Campaign Budget Commit (Non-Critical)
    coupon_code = doc.get("coupon_code") or doc.get("custom_coupon_code")
    coupon_disc_amt = flt(doc.get("custom_coupon_discount") or doc.get("discount_amount"))
    
    if coupon_code and settings.enable_coupon:
        if frappe.db.exists("Coupon Code", coupon_code):
            coupon = frappe.get_doc("Coupon Code", coupon_code)
            if coupon.custom_campaign:
                session_id = doc.get("custom_billing_session_id") or f"pos_{doc.name}"
                execute_non_critical(
                    "Coupon Campaign Budget Commit",
                    lambda: CGECampaignManager.commit_budget(coupon_code, coupon_disc_amt, session_id)
                )
                
    # 3. Loyalty Points Entry update (Non-Critical)
    pts_earned = flt(doc.get("custom_loyalty_points_earned"))
    if pts_earned > 0.0 and settings.enable_loyalty:
        def update_loyalty():
            lpe = frappe.db.get_value("Loyalty Point Entry", {"invoice": doc.name}, "name")
            if lpe:
                frappe.db.set_value("Loyalty Point Entry", lpe, "loyalty_points", pts_earned)
                frappe.db.set_value("Loyalty Point Entry", lpe, "remaining_points", pts_earned)
            else:
                lpe_doc = frappe.get_doc({
                    "doctype": "Loyalty Point Entry",
                    "customer": doc.customer,
                    "loyalty_program": doc.loyalty_program or frappe.db.get_value("Customer", doc.customer, "loyalty_program"),
                    "invoice": doc.name,
                    "loyalty_points": pts_earned,
                    "remaining_points": pts_earned,
                    "posting_date": doc.posting_date or nowdate(),
                    "expiry_date": add_to_date(doc.posting_date or nowdate(), months=12)
                })
                lpe_doc.insert(ignore_permissions=True)
        execute_non_critical("Loyalty Points Entry Update", update_loyalty)


def process_invoice_cancel(doc, method=None):
    """
    Hook handler on POS/Sales Invoice cancel.
    Reverses wallet deductions and reverts coupon campaigns budget.
    """
    settings = frappe.get_doc("SMRITI CGE Settings")
    
    # 1. Wallet Reversal (Critical)
    wallet_ded_amt = flt(doc.get("custom_wallet_deduction"))
    if wallet_ded_amt > 0.0 and settings.enable_cashback:
        ledger_seq = frappe.db.get_value("SMRITI Wallet Ledger", {"reference_invoice": doc.name, "transaction_type": "Debit"}, "name")
        if ledger_seq:
            already_reversed = frappe.db.exists("SMRITI Wallet Ledger", {"reference_invoice": doc.name, "transaction_type": "Credit", "is_reversal": 1})
            if not already_reversed:
                CGEWalletLedger.reverse_transaction(ledger_seq, reason=f"Invoice {doc.name} Cancelled")
                
    # 2. Coupon Campaign Revert (Non-Critical)
    coupon_code = doc.get("coupon_code") or doc.get("custom_coupon_code")
    coupon_disc_amt = flt(doc.get("custom_coupon_discount") or doc.get("discount_amount"))
    
    if coupon_code and settings.enable_coupon:
        if frappe.db.exists("Coupon Code", coupon_code):
            coupon = frappe.get_doc("Coupon Code", coupon_code)
            if coupon.custom_campaign:
                def revert_budget():
                    campaign = frappe.get_doc("SMRITI Coupon Campaign", coupon.custom_campaign)
                    campaign.budget_consumed = max(0.0, flt(campaign.budget_consumed) - coupon_disc_amt)
                    campaign.save(ignore_permissions=True)
                execute_non_critical("Coupon Campaign Revert", revert_budget)


@frappe.whitelist()
def get_offline_cache():
    """
    Serializes active loyalty rules, loyalty tiers, coupon campaigns, and coupons
    for offline POS caching. Generates an MD5 checksum version.
    """
    import hashlib
    
    # 1. Read from Redis cache first if enabled (AUD-13)
    settings = frappe.get_doc("SMRITI CGE Settings")
    if settings.enable_offline_cache:
        cached = frappe.cache().hget("cge_offline_cache", "latest")
        if cached:
            return cached

    # 2. Fetch active loyalty tiers
    tiers = frappe.get_all("SMRITI Loyalty Tier",
        filters={"active": 1},
        fields=["name", "tier_name", "min_points", "tier_multiplier", "validity_months", "active"]
    )
    
    # 3. Fetch active loyalty rules
    rules = frappe.get_all("SMRITI Loyalty Rule",
        filters={"status": "Active"},
        fields=[
            "name", "rule_name", "version", "status", "effective_from", "effective_to",
            "rule_type", "dimension", "dimension_doctype", "dimension_value",
            "rule_value", "priority", "allow_stack"
        ]
    )
    
    # 4. Fetch active coupon campaigns
    campaigns = frappe.get_all("SMRITI Coupon Campaign",
        filters={"status": "Active"},
        fields=[
            "name", "campaign_name", "campaign_type", "start_date", "end_date",
            "budget_limit", "budget_reserved", "budget_consumed", "stop_on_limit", "status"
        ]
    )
    
    # 5. Fetch active, non-personalized, non-exhausted coupons (AUD-12)
    coupons = []
    if campaigns:
        campaign_names = [c.campaign_name for c in campaigns]
        today = nowdate()
        # Fetch maximum 1000 active, non-personalized, non-exhausted coupons
        coupons = frappe.db.sql("""
            select name, coupon_code, coupon_name, coupon_type, valid_from, valid_upto,
                   used, maximum_use, pricing_rule,
                   custom_coupon_scope, custom_campaign, custom_max_uses_per_customer,
                   custom_max_uses_per_mobile, custom_max_uses_per_day, custom_max_discount_cap
            from `tabCoupon Code`
            where custom_campaign in %s
              and (customer is null or customer = '')
              and (valid_upto is null or valid_upto >= %s)
              and (maximum_use = 0 or used < maximum_use)
            order by modified desc
            limit 1000
        """, (campaign_names, today), as_dict=True)
    
    # Compile data dictionary
    data = {
        "tiers": tiers,
        "rules": rules,
        "campaigns": campaigns,
        "coupons": coupons
    }
    
    # Serialize data consistently
    serialized_data = json.dumps(data, sort_keys=True, default=str)
    
    # Byte size guard (AUD-12)
    CACHE_MAX_BYTES = 5 * 1024 * 1024
    if len(serialized_data.encode("utf-8")) > CACHE_MAX_BYTES:
        # Prune coupons list to stay under safe size limit
        while len(serialized_data.encode("utf-8")) > CACHE_MAX_BYTES and coupons:
            coupons.pop()
            data["coupons"] = coupons
            serialized_data = json.dumps(data, sort_keys=True, default=str)
            
        if len(serialized_data.encode("utf-8")) > CACHE_MAX_BYTES:
            frappe.throw(_("Offline cache payload size exceeds the 5MB memory guard threshold after pruning."))
    
    # Compute MD5 checksum
    checksum = hashlib.md5(serialized_data.encode("utf-8")).hexdigest()
    
    result_dict = {
        "checksum": checksum,
        "data": data
    }
    
    # Cache in Redis if offline cache is enabled
    if settings.enable_offline_cache:
        frappe.cache().hset("cge_offline_cache", "latest", result_dict)
        
    return result_dict


def get_cge_generic_fields_meta(doctype):
    """
    Returns field metadata for CGE DocType to render form fields dynamically in the UI.
    """
    import json
    meta = frappe.get_meta(doctype)
    fields = []
    for f in meta.fields:
        if not f.hidden and f.fieldtype not in ['Section Break', 'Column Break']:
            fields.append({
                "fieldname": f.fieldname,
                "label": f.label,
                "fieldtype": f.fieldtype,
                "reqd": f.reqd,
                "options": f.options,
                "default": f.default
            })
    return fields


def save_cge_generic_doc_service(doctype, doc_data):
    """
    Saves (inserts or updates) a SMRITI CGE document.
    """
    import json
    if isinstance(doc_data, str):
        doc_data = json.loads(doc_data)

    name = doc_data.get("name")
    if name and frappe.db.exists(doctype, name):
        doc = frappe.get_doc(doctype, name)
    else:
        doc = frappe.new_doc(doctype)

    # Set fields
    meta = frappe.get_meta(doctype)
    for f in meta.fields:
        if f.fieldname == "name":
            continue
        if f.fieldtype == "Table":
            # Handle child table (sequence_details, etc.)
            child_rows = doc_data.get(f.fieldname) or []
            doc.set(f.fieldname, [])
            for row in child_rows:
                # Remove temporary properties
                row.pop("name", None)
                row.pop("parent", None)
                row.pop("parentfield", None)
                row.pop("parenttype", None)
                doc.append(f.fieldname, row)
        elif f.fieldname in doc_data:
            doc.set(f.fieldname, doc_data[f.fieldname])

    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return doc.name


def delete_cge_generic_doc_service(doctype, name):
    """
    Deletes a SMRITI CGE document.
    """
    if not frappe.db.exists(doctype, name):
        frappe.throw(_("Document {0} of type {1} not found.").format(name, doctype))

    frappe.delete_doc(doctype, name, ignore_permissions=True)
    frappe.db.commit()
    return True

