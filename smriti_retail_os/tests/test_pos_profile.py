# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_pos_profile.py
# @description: Unit tests for SMRITI POS Profile Management APIs, service layers,
#               shift lock rules, and clone utilities.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-25
# @version: 1.8.6
# @sprint: 3C — POS Profile Custom Manager
# @authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
#

import frappe
from smriti_retail_os import smriti
import unittest
from smriti_retail_os.api.pos_profile_api import (
    get_profiles,
    get_details,
    save_profile,
    clone_profile,
    archive_profile,
    get_dropdowns,
    validate_profile
)

class TestPOSProfileManagement(unittest.TestCase):
    def setUp(self):
        self.original_user = frappe.session.user
        frappe.set_user("Administrator")

        # Provision test Company and Warehouse if they don't exist
        self.company = "Test SMRITI Company"
        if not smriti.db.exists("Company", self.company):
            comp = smriti.documents.new("Company")
            comp.company_name = self.company
            comp.default_currency = "INR"
            comp.country = "India"
            comp.insert(ignore_permissions=True)
            smriti.db.commit()

        # Get a valid Cash account from the Chart of Accounts of this company
        self.cash_account = smriti.db.get("Account", {"company": self.company, "account_type": "Cash"}, "name")
        if not self.cash_account:
            self.cash_account = smriti.db.get("Account", {"company": self.company, "is_group": 0}, "name")

        self.warehouse = "Test POS WH - TSC"
        if not smriti.db.exists("Warehouse", self.warehouse):
            wh = smriti.documents.new("Warehouse")
            wh.warehouse_name = "Test POS WH"
            wh.company = self.company
            wh.insert(ignore_permissions=True)
            smriti.db.commit()

        self.price_list = "Test POS Price List"
        if not smriti.db.exists("Price List", self.price_list):
            pl = smriti.documents.new("Price List")
            pl.price_list_name = self.price_list
            pl.enabled = 1
            pl.selling = 1
            pl.insert(ignore_permissions=True)
            smriti.db.commit()

        # Mode of Payment
        self.mop = "Test Cash Mode"
        if not smriti.db.exists("Mode of Payment", self.mop):
            mop_doc = smriti.documents.new("Mode of Payment")
            mop_doc.mode_of_payment = self.mop
            mop_doc.type = "Cash"
            mop_doc.append("accounts", {
                "company": self.company,
                "default_account": self.cash_account
            })
            mop_doc.insert(ignore_permissions=True)
            smriti.db.commit()
        else:
            mop_doc = smriti.documents.get("Mode of Payment", self.mop)
            if not any(a.company == self.company for a in mop_doc.accounts):
                mop_doc.append("accounts", {
                    "company": self.company,
                    "default_account": self.cash_account
                })
                mop_doc.save(ignore_permissions=True)
                smriti.db.commit()

        self.write_off_account = "Write Off - TSC"
        self.cost_center = "Main - TSC"

        # Cleanup existing test profiles
        self.source_profile = "Test Source Terminal"
        self.clone_profile_name = "Test Cloned Terminal"
        
        shift_names = smriti.db.get_list("POS Opening Entry", {"pos_profile": ["in", [self.source_profile, self.clone_profile_name]]}, pluck="name")
        if shift_names:
            smriti.db.delete("POS Opening Entry Detail", {"parent": ["in", shift_names]})
            smriti.db.delete("POS Opening Entry", {"name": ["in", shift_names]})
        smriti.db.delete("POS Payment Method", {"parent": ["in", [self.source_profile, self.clone_profile_name]]})
        smriti.db.delete("POS Profile User", {"parent": ["in", [self.source_profile, self.clone_profile_name]]})
        smriti.db.delete("POS Profile", {"name": ["in", [self.source_profile, self.clone_profile_name]]})
        smriti.db.commit()

    def tearDown(self):
        frappe.set_user("Administrator")
        shift_names = smriti.db.get_list("POS Opening Entry", {"pos_profile": ["in", [self.source_profile, self.clone_profile_name]]}, pluck="name")
        if shift_names:
            smriti.db.delete("POS Opening Entry Detail", {"parent": ["in", shift_names]})
            smriti.db.delete("POS Opening Entry", {"name": ["in", shift_names]})
        smriti.db.delete("POS Payment Method", {"parent": ["in", [self.source_profile, self.clone_profile_name]]})
        smriti.db.delete("POS Profile User", {"parent": ["in", [self.source_profile, self.clone_profile_name]]})
        smriti.db.delete("POS Profile", {"name": ["in", [self.source_profile, self.clone_profile_name]]})
        frappe.set_user(self.original_user)
        smriti.db.commit()

    def test_permission_guards(self):
        # 1. Test Guest access block
        frappe.set_user("Guest")
        with self.assertRaises(frappe.AuthenticationError):
            get_profiles()

        # 2. Test ordinary cashier access block
        test_email = "cashier.test@smriti.local"
        if not smriti.db.exists("User", test_email):
            u = smriti.documents.new("User")
            u.update({
                "email": test_email,
                "first_name": "Test Cashier",
                "roles": [{"role": "SMRITI Cashier"}]
            })
            u.insert(ignore_permissions=True)
            smriti.db.commit()

        frappe.set_user(test_email)
        with self.assertRaises(frappe.PermissionError):
            get_profiles()

        # Clean up
        frappe.set_user("Administrator")
        smriti.db.delete("User", {"email": test_email})
        smriti.db.commit()

    def test_save_and_retrieve_profile(self):
        profile_data = {
            "name": self.source_profile,
            "company": self.company,
            "warehouse": self.warehouse,
            "selling_price_list": self.price_list,
            "currency": "INR",
            "disabled": 0,
            "write_off_account": self.write_off_account,
            "write_off_cost_center": self.cost_center,
            "payments": [
                {"mode_of_payment": self.mop, "default_account": self.cash_account, "default": 1}
            ],
            "applicable_for_users": [
                {"user": "Administrator"}
            ]
        }

        # Save profile
        saved_name = save_profile(profile_data)
        self.assertEqual(saved_name, self.source_profile)

        # Retrieve details
        details = get_details(self.source_profile)
        self.assertEqual(details["company"], self.company)
        self.assertEqual(details["warehouse"], self.warehouse)
        self.assertEqual(len(details["payments"]), 1)
        self.assertEqual(details["payments"][0]["mode_of_payment"], self.mop)
        self.assertEqual(len(details["applicable_for_users"]), 1)

    def test_cloning_profile(self):
        # Setup source profile first
        profile_data = {
            "name": self.source_profile,
            "company": self.company,
            "warehouse": self.warehouse,
            "selling_price_list": self.price_list,
            "currency": "INR",
            "write_off_account": self.write_off_account,
            "write_off_cost_center": self.cost_center,
            "payments": [
                {"mode_of_payment": self.mop, "default_account": self.cash_account, "default": 1}
            ],
            "applicable_for_users": [
                {"user": "Administrator"}
            ]
        }
        save_profile(profile_data)

        # Clone it
        cloned_name = clone_profile(self.source_profile, self.clone_profile_name)
        self.assertEqual(cloned_name, self.clone_profile_name)

        # Verify cloned values
        cloned_details = get_details(self.clone_profile_name)
        self.assertEqual(cloned_details["company"], self.company)
        self.assertEqual(cloned_details["warehouse"], self.warehouse)
        self.assertEqual(len(cloned_details["payments"]), 1)
        self.assertEqual(cloned_details["payments"][0]["mode_of_payment"], self.mop)

    def test_shift_lock_validation_guards(self):
        # Setup profile
        profile_data = {
            "name": self.source_profile,
            "company": self.company,
            "warehouse": self.warehouse,
            "selling_price_list": self.price_list,
            "currency": "INR",
            "write_off_account": self.write_off_account,
            "write_off_cost_center": self.cost_center,
            "payments": [
                {"mode_of_payment": self.mop, "default_account": self.cash_account, "default": 1}
            ],
            "applicable_for_users": [
                {"user": "Administrator"}
            ]
        }
        save_profile(profile_data)

        # Open an active shift (POS Opening Entry)
        shift = smriti.documents.new("POSOpeningEntry")
        shift.update({
            "user": "Administrator",
            "pos_profile": self.source_profile,
            "company": self.company,
            "posting_date": frappe.utils.nowdate(),
            "period_start_date": frappe.utils.now_datetime(),
            "status": "Open",
            "docstatus": 1,
            "balance_details": [
                {
                    "mode_of_payment": self.mop,
                    "opening_amount": 0
                }
            ]
        })
        shift.insert(ignore_permissions=True)
        smriti.db.commit()

        # Try to modify Warehouse while shift is active
        modified_data = profile_data.copy()
        modified_data["warehouse"] = "Another Warehouse - TSC"
        
        with self.assertRaises(frappe.ValidationError):
            save_profile(modified_data)

        # Try to archive/disable while shift is active
        with self.assertRaises(frappe.ValidationError):
            archive_profile(self.source_profile)

        # Verify profile validate API endpoint returns correct locks
        status_check = validate_profile(self.source_profile)
        self.assertTrue(status_check["is_locked"])
        self.assertEqual(status_check["active_shift"]["name"], shift.name)

    def test_soft_delete_archiving(self):
        # Setup profile
        profile_data = {
            "name": self.source_profile,
            "company": self.company,
            "warehouse": self.warehouse,
            "selling_price_list": self.price_list,
            "currency": "INR",
            "write_off_account": self.write_off_account,
            "write_off_cost_center": self.cost_center,
            "payments": [
                {"mode_of_payment": self.mop, "default_account": self.cash_account, "default": 1}
            ],
            "applicable_for_users": []
        }
        save_profile(profile_data)

        # Disable / Archive
        archive_profile(self.source_profile)
        
        # Verify disabled flag set to 1 in DB
        disabled_val = smriti.db.get("POS Profile", self.source_profile, "disabled")
        self.assertEqual(disabled_val, 1)
