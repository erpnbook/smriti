# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_psv_transaction/smriti_psv_transaction.py
# @description: DocType controller for SMRITI PSV Transaction.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.model.document import Document
from smriti_retail_os.ledger_engine import make_ledger_entry, log_activity

class SMRITIPSVTransaction(Document):
    def validate(self):
        self.validate_tracking_mode()
        self.generate_fingerprint()

    def validate_tracking_mode(self):
        """Ensures the transaction type is allowed by the PSA's tracking mode."""
        psa_doc = smriti.documents.get("SMRITI Party Stock Account", self.party_stock_account)
        mode = psa_doc.tracking_mode or "Hybrid"
        
        # OPENING, TRANSFER_IN, TRANSFER_OUT, MANUAL_ADJUSTMENT are generally always allowed as admin actions
        if self.transaction_type in ("POS_SALE", "RETURN"):
            if mode == "Sales Upload":
                frappe.throw(f"Transaction Type {self.transaction_type} is blocked for PSA '{self.party_stock_account}' because its Tracking Mode is set to 'Sales Upload'.")
        elif self.transaction_type == "SALES_UPLOAD":
            if mode == "POS Integrated":
                frappe.throw(f"Transaction Type SALES_UPLOAD is blocked for PSA '{self.party_stock_account}' because its Tracking Mode is set to 'POS Integrated'.")

    def generate_fingerprint(self):
        """Generates a human-readable unique key to prevent duplicate processing."""
        if not self.mapping_fingerprint and self.reference_doctype and self.reference_name:
            # We don't hash the item_code here because one transaction can have multiple items.
            # The fingerprint is at the transaction level.
            self.mapping_fingerprint = f"{self.transaction_type}::{self.reference_doctype}::{self.reference_name}"

    def on_submit(self):
        self.status = "Submitted"
        self.update_ledger(cancel=False)

    def on_cancel(self):
        self.status = "Cancelled"
        self.update_ledger(cancel=True)
        self.check_and_log_negative_balances()

    def check_and_log_negative_balances(self):
        from smriti_retail_os.balance_engine import get_party_balance
        for item in self.items:
            bal = get_party_balance(self.party_stock_account, item.item_code)
            if bal < 0:
                # Set PSA status to Pending Reconciliation
                smriti.db.set_value("SMRITI Party Stock Account", self.party_stock_account, "status", "Pending Reconciliation")
                
                # Create exception record
                sales_invoice = self.reference_name if self.reference_doctype == "Sales Invoice" else None
                from smriti_retail_os.psv_service import create_or_update_alert
                create_or_update_alert(
                    party_stock_account=self.party_stock_account,
                    alert_type="Negative Balance",
                    severity="Critical",
                    details=f"Critical: Negative shadow balance ({bal} units) detected on cancellation of {self.reference_doctype} {self.reference_name}.",
                    item_code=item.item_code,
                    sales_invoice=sales_invoice,
                    missing_qty=abs(bal)
                )

    def update_ledger(self, cancel=False):
        multiplier = -1 if cancel else 1

        for item in self.items:
            qty = item.qty * multiplier

            # Sign logic (from the PSA / channel perspective):
            # ─────────────────────────────────────────────────────────────────
            # SALES_UPLOAD, POS_SALE — stock sold by channel → outflow (negative)
            # RETURN           — sold goods returned to channel → inflow (positive)
            # TRANSFER_OUT     — company dispatches stock TO channel → inflow (positive)
            # TRANSFER_IN      — stock coming back FROM channel TO company → outflow (negative)
            # AUDIT_ADJUSTMENT — variance already signed in the item qty field
            # OPENING          — initial stock → inflow (positive)
            # MANUAL_ADJUSTMENT— signed explicitly in item qty field
            # ─────────────────────────────────────────────────────────────────
            if self.transaction_type in ("SALES_UPLOAD", "POS_SALE", "TRANSFER_IN"):
                qty = -qty

            # BUG-003 FIX: Map every transaction type to its ledger voucher_type.
            # Old code defaulted TRANSFER_IN and MANUAL_ADJUSTMENT to 'Adjustment',
            # making them indistinguishable in reports and reorder intelligence.
            v_type_map = {
                "SALES_UPLOAD":       "Sales",
                "POS_SALE":           "Sales",
                "RETURN":             "Return",
                "TRANSFER_OUT":       "Dispatch",
                "TRANSFER_IN":        "Transfer",   # BUG-003: was 'Adjustment'
                "OPENING":            "Opening",
                "AUDIT_ADJUSTMENT":   "Adjustment",
                "MANUAL_ADJUSTMENT":  "Adjustment",
            }
            v_type = v_type_map.get(self.transaction_type, "Adjustment")

            make_ledger_entry(
                party_stock_account=self.party_stock_account,
                item_code=item.item_code,
                qty=qty,
                voucher_type=v_type,
                voucher_no=f"VOID-{self.name}" if cancel else self.name,
                company=self.company,
                posting_datetime=self.posting_date
            )
            
        # Map to allowed select options in SMRITI PSV Activity Log
        if cancel:
            act_type = "Cancel Dispatch"
        else:
            if self.transaction_type == "SALES_UPLOAD":
                act_type = "Upload Sales"
            elif self.transaction_type == "AUDIT_ADJUSTMENT":
                act_type = "Approve Snapshot"
            elif self.transaction_type == "OPENING":
                act_type = "Opening Balance Import"
            else:
                act_type = "Submit Dispatch"

        action_label = "Cancelled" if cancel else "Submitted"
        log_activity(
            action_type=act_type,
            party_stock_account=self.party_stock_account,
            reference_doctype="SMRITI PSV Transaction",
            reference_name=self.name,
            details=f"{action_label} {self.transaction_type} for {len(self.items)} items."
        )
