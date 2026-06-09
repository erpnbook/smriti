# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_psv_transaction/smriti_psv_transaction.py
# @description: DocType controller for SMRITI PSV Transaction.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>

import frappe
from frappe.model.document import Document
from smriti_retail_os.ledger_engine import make_ledger_entry, log_activity

class SMRITIPSVTransaction(Document):
    def validate(self):
        self.validate_tracking_mode()
        self.generate_fingerprint()

    def validate_tracking_mode(self):
        """Ensures the transaction type is allowed by the PSA's tracking mode."""
        psa_doc = frappe.get_cached_doc("SMRITI Party Stock Account", self.party_stock_account)
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

    def update_ledger(self, cancel=False):
        multiplier = -1 if cancel else 1
        
        for item in self.items:
            qty = item.qty * multiplier
            
            # Reversals logic: If it's a deduction (Sales, Transfer Out), we pass negative qty to ledger
            if self.transaction_type in ("SALES_UPLOAD", "POS_SALE", "TRANSFER_OUT", "AUDIT_ADJUSTMENT"):
                 if self.transaction_type == "AUDIT_ADJUSTMENT":
                     # Audit adjustment qty is the variance.
                     # If variance is -5 (missing stock), we want to deduct 5. Ledger expects -5.
                     # If variance is +5 (extra stock), we want to add 5. Ledger expects +5.
                     pass # Qty is already correctly signed in the item row based on variance
                 elif self.transaction_type == "RETURN":
                     # Return is an addition back to stock
                     pass
                 else:
                     # Normal sales/outbound are deductions
                     qty = -qty
            
            make_ledger_entry(
                party_stock_account=self.party_stock_account,
                item_code=item.item_code,
                qty=qty,
                voucher_type="PSV Transaction",
                voucher_no=self.name,
                company=self.company,
                posting_datetime=self.posting_date
            )
            
        action = "Cancelled" if cancel else "Submitted"
        log_activity(
            action_type=f"Transaction {action}",
            party_stock_account=self.party_stock_account,
            reference_doctype="SMRITI PSV Transaction",
            reference_name=self.name,
            details=f"{action} {self.transaction_type} for {len(self.items)} items."
        )
