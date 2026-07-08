# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_cge_v2_constraints.py
# @description: CGE v2 constraint tests — data integrity and rule validation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/tests/test_cge_v2_constraints.py
# @description: Database index and integrity constraint tests for CGE v2.
# @author: SMRITI Architect / USER & AITDL
# @date: 2026-06-19
#

import frappe
from smriti_retail_os import smriti
import unittest

class TestCGEV2Constraints(unittest.TestCase):
    def setUp(self):
        # Create missing indexes for CGE v2 testing
        from smriti_retail_os.create_indexes import run as create_db_indexes
        create_db_indexes()

        # We check if CGE v2 tables exist before running database tests
        self.wallet_table = "SMRITI Benefit Wallet"
        self.ledger_table = "SMRITI Benefit Ledger"
        
    def test_01_wallet_composite_unique_index_exists(self):
        """Verify uq_wallet_cust_comp_inst unique index exists on SMRITI Benefit Wallet table."""
        if not frappe.db.table_exists(self.wallet_table):
            self.skipTest(f"Table for {self.wallet_table} does not exist in DB yet.")
            
        table_name = f"tab{self.wallet_table}"
        idx_rows = smriti.db.sql(
            f"SHOW INDEX FROM `{table_name}` WHERE Key_name = 'uq_wallet_cust_comp_inst'",
            as_dict=True
        )
        
        self.assertTrue(len(idx_rows) > 0, "Index 'uq_wallet_cust_comp_inst' is missing at the database level!")
        
        # Verify columns covered and uniqueness
        db_cols = []
        for r in idx_rows:
            non_unique = r.get("Non_unique") if r.get("Non_unique") is not None else r.get("non_unique")
            self.assertEqual(int(non_unique), 0, "Index is not unique!")
            db_cols.append(r.get("Column_name") or r.get("column_name"))
            
        self.assertEqual(
            set(db_cols),
            {"customer", "company", "benefit_instrument"},
            f"Index covers {db_cols} instead of ('customer', 'company', 'benefit_instrument')!"
        )

    def test_02_ledger_query_index_exists(self):
        """Verify idx_ledger_cust_inst_date index exists on SMRITI Benefit Ledger table."""
        if not frappe.db.table_exists(self.ledger_table):
            self.skipTest(f"Table for {self.ledger_table} does not exist in DB yet.")
            
        table_name = f"tab{self.ledger_table}"
        idx_rows = smriti.db.sql(
            f"SHOW INDEX FROM `{table_name}` WHERE Key_name = 'idx_ledger_cust_inst_date'",
            as_dict=True
        )
        
        self.assertTrue(len(idx_rows) > 0, "Index 'idx_ledger_cust_inst_date' is missing at the database level!")
        
        db_cols = [r.get("Column_name") or r.get("column_name") for r in idx_rows]
        self.assertEqual(
            set(db_cols),
            {"customer", "benefit_instrument", "posting_date"},
            f"Index covers {db_cols} instead of ('customer', 'benefit_instrument', 'posting_date')!"
        )

    def test_03_ledger_ref_index_exists(self):
        """Verify idx_ledger_ref index exists on SMRITI Benefit Ledger table."""
        if not frappe.db.table_exists(self.ledger_table):
            self.skipTest(f"Table for {self.ledger_table} does not exist in DB yet.")
            
        table_name = f"tab{self.ledger_table}"
        idx_rows = smriti.db.sql(
            f"SHOW INDEX FROM `{table_name}` WHERE Key_name = 'idx_ledger_ref'",
            as_dict=True
        )
        
        self.assertTrue(len(idx_rows) > 0, "Index 'idx_ledger_ref' is missing at the database level!")
        
        db_cols = [r.get("Column_name") or r.get("column_name") for r in idx_rows]
        self.assertEqual(
            set(db_cols),
            {"reference_doctype", "reference_name"},
            f"Index covers {db_cols} instead of ('reference_doctype', 'reference_name')!"
        )

    def test_04_wallet_duplicate_prevention(self):
        """Verify controller-level and database-level duplicate prevention for SMRITI Benefit Wallet."""
        if not frappe.db.table_exists(self.wallet_table):
            self.skipTest(f"Table for {self.wallet_table} does not exist in DB yet.")
            
        # Ensure we have a clean state for test data
        test_cust = "_Test Hardening Customer"
        test_comp = smriti.db.get_list("Company", limit=1)[0].name
        test_inst = "_Test Hardening Instrument"
        
        # Seed test customer if missing
        if not smriti.db.exists("Customer", test_cust):
            cust_doc = smriti.documents.new("Customer")
            cust_doc.update({
                "customer_name": test_cust,
                "customer_group": "Individual"
            })
            cust_doc.insert(ignore_permissions=True)

        # Seed test instrument type if missing (Phase 4C Fix)
        if not smriti.db.exists("SMRITI Benefit Instrument Type", "CASHBACK"):
            type_doc = smriti.documents.new("BenefitInstrumentType")
            type_doc.update({
                "type_name": "CASHBACK",
                "description": "Cashback Benefit Classification"
            })
            type_doc.insert(ignore_permissions=True)
            
        # Seed test instrument if missing
        if not smriti.db.exists("SMRITI Benefit Instrument", test_inst):
            inst_doc = smriti.documents.new("BenefitInstrument")
            inst_doc.update({
                "instrument_name": test_inst,
                "instrument_type": "CASHBACK",
                "validity_days": 90,
                "allow_negative_balance": 0
            })
            inst_doc.insert(ignore_permissions=True)

        # Clear existing wallet for this combo if any (to make test reproducible)
        smriti.db.delete("SMRITI Benefit Wallet", {
            "customer": test_cust,
            "company": test_comp,
            "benefit_instrument": test_inst
        })
        smriti.db.commit()

        # 1. Create first wallet
        wallet1 = smriti.documents.new("BenefitWallet")
        wallet1.update({
            "customer": test_cust,
            "company": test_comp,
            "benefit_instrument": test_inst,
            "balance": 100.0
        })
        wallet1.insert(ignore_permissions=True)
        smriti.db.commit()

        # 2. Attempt to create second wallet with identical key combo (expect ValidationError)
        wallet2 = smriti.documents.new("BenefitWallet")
        wallet2.update({
            "customer": test_cust,
            "company": test_comp,
            "benefit_instrument": test_inst,
            "balance": 200.0
        })
        
        self.assertRaises(frappe.ValidationError, wallet2.insert, ignore_permissions=True)
        
        # Clean up
        smriti.db.delete("SMRITI Benefit Wallet", {"customer": test_cust})
        smriti.db.delete("SMRITI Benefit Instrument", {"name": test_inst})
        smriti.db.delete("Customer", {"name": test_cust})
        smriti.db.commit()
