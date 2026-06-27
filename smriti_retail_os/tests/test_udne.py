import unittest
import frappe
from frappe.utils import nowdate
import datetime
from smriti_retail_os.services.udne.interfaces import GenerationContext
from smriti_retail_os.services.udne import generate, explain, metrics, health, gaps, reservations
from smriti_retail_os.services.udne.cache import clear_compiled_template_cache
from smriti_retail_os.services.udne.gap_scanner import scan_gaps
from smriti_retail_os.services.udne.reservation_manager import reserve_range
from smriti_retail_os.services.udne.exceptions import UDNERuleNotFoundError, UDNECollisionError, UDNEExhaustedError

class TestUDNE(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from smriti_retail_os.setup import setup_smriti_retail_os
        setup_smriti_retail_os()
        frappe.db.commit()

    def setUp(self):
        frappe.db.delete("SMRITI Numbering Rule")
        frappe.db.delete("SMRITI Numbering Counter")
        frappe.db.delete("SMRITI Numbering Reserved Range")
        frappe.db.delete("SMRITI Numbering Audit Log")
        frappe.db.delete("POS Invoice")
        frappe.db.delete("Sales Invoice")
        frappe.db.commit()
        clear_compiled_template_cache()
        
    def tearDown(self):
        frappe.db.delete("SMRITI Numbering Rule")
        frappe.db.delete("SMRITI Numbering Counter")
        frappe.db.delete("SMRITI Numbering Reserved Range")
        frappe.db.delete("SMRITI Numbering Audit Log")
        frappe.db.delete("POS Invoice")
        frappe.db.delete("Sales Invoice")
        frappe.db.commit()
        clear_compiled_template_cache()
        
    def test_facade_api(self):
        rule = frappe.get_doc({
            "doctype": "SMRITI Numbering Rule",
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV-{year}-{counter:6}",
            "is_active": 1,
            "reset_rule": "Never"
        })
        rule.insert(ignore_permissions=True)
        frappe.db.commit()
        
        context = GenerationContext(
            company="Test Company",
            branch="Test Branch",
            store="Test Store",
            terminal_id="TERM-01",
            user="Administrator"
        )
        
        result1 = generate("POS Invoice", context)
        self.assertEqual(result1.display_number, f"INV-2026-000001")
        self.assertEqual(result1.counter, 1)
        self.assertTrue(result1.identity.startswith("PI-"))
        
        result2 = generate("POS Invoice", context)
        self.assertEqual(result2.display_number, f"INV-2026-000002")
        self.assertEqual(result2.counter, 2)
        
    def test_priority_resolution(self):
        frappe.get_doc({
            "doctype": "SMRITI Numbering Rule",
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "GLOBAL-{counter}",
            "is_active": 1
        }).insert(ignore_permissions=True)
        
        frappe.get_doc({
            "doctype": "SMRITI Numbering Rule",
            "document_type": "POS Invoice",
            "priority": "Branch",
            "priority_value": "MUMBAI",
            "template": "MUM-{counter}",
            "is_active": 1
        }).insert(ignore_permissions=True)
        
        frappe.get_doc({
            "doctype": "SMRITI Numbering Rule",
            "document_type": "POS Invoice",
            "priority": "Store",
            "priority_value": "MUM-STORE",
            "template": "STORE-{counter}",
            "is_active": 1
        }).insert(ignore_permissions=True)
        
        frappe.db.commit()
        
        ctx_global = GenerationContext(company="Test Company")
        res_global = generate("POS Invoice", ctx_global)
        self.assertEqual(res_global.display_number, "GLOBAL-1")
        
        ctx_branch = GenerationContext(company="Test Company", branch="MUMBAI")
        res_branch = generate("POS Invoice", ctx_branch)
        self.assertEqual(res_branch.display_number, "MUM-1")
        
        ctx_store = GenerationContext(company="Test Company", branch="MUMBAI", store="MUM-STORE")
        res_store = generate("POS Invoice", ctx_store)
        self.assertEqual(res_store.display_number, "STORE-1")
        
    def test_cache_invalidation(self):
        rule = frappe.get_doc({
            "doctype": "SMRITI Numbering Rule",
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "OLD-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        frappe.db.commit()
        
        ctx = GenerationContext(company="Test Company")
        res1 = generate("POS Invoice", ctx)
        self.assertEqual(res1.display_number, "OLD-1")
        
        rule.template = "NEW-{counter}"
        rule.save(ignore_permissions=True)
        frappe.db.commit()
        
        res2 = generate("POS Invoice", ctx)
        self.assertEqual(res2.display_number, "NEW-2")
        
    def test_financial_year_rollover(self):
        rule = frappe.get_doc({
            "doctype": "SMRITI Numbering Rule",
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV/{fy}/{counter:4}",
            "reset_rule": "Financial Year",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        frappe.db.commit()
        
        ctx1 = GenerationContext(company="Test Company", transaction_date=datetime.date(2026, 3, 15))
        res1 = generate("POS Invoice", ctx1)
        self.assertEqual(res1.display_number, "INV/25-26/0001")
        
        ctx2 = GenerationContext(company="Test Company", transaction_date=datetime.date(2026, 4, 1))
        res2 = generate("POS Invoice", ctx2)
        self.assertEqual(res2.display_number, "INV/26-27/0001")
        
    def test_reservation_lifecycle(self):
        rule = frappe.get_doc({
            "doctype": "SMRITI Numbering Rule",
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        frappe.db.commit()
        
        ctx = GenerationContext(company="Test Company")
        
        res_info = reserve_range("POS Invoice", "TERM-01", 10, rule.name, "Never", ctx.as_dict())
        self.assertEqual(res_info["start"], 1)
        self.assertEqual(res_info["end"], 10)
        
        res_online = generate("POS Invoice", ctx)
        self.assertEqual(res_online.counter, 11)
        
        ctx_offline = GenerationContext(
            company="Test Company",
            extra_context={"reservation_id": res_info["reservation_id"]}
        )
        res_off1 = generate("POS Invoice", ctx_offline)
        self.assertEqual(res_off1.counter, 1)
        self.assertEqual(res_off1.display_number, "INV-1")
        
    def test_gap_scanner_classification(self):
        rule = frappe.get_doc({
            "doctype": "SMRITI Numbering Rule",
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        frappe.db.commit()
        
        ctx = GenerationContext(company="Test Company")
        
        res1 = generate("POS Invoice", ctx)
        frappe.db.sql("insert into `tabPOS Invoice` (name, custom_business_display_number, company, docstatus) values (%s, %s, %s, 0)", (res1.identity, res1.display_number, "Test Company"))
        
        reserve_range("POS Invoice", "TERM-02", 2, rule.name, "Never", ctx.as_dict())
        
        res4 = generate("POS Invoice", ctx)
        frappe.db.sql("insert into `tabPOS Invoice` (name, custom_business_display_number, company, docstatus) values (%s, %s, %s, 0)", (res4.identity, res4.display_number, "Test Company"))
        frappe.db.commit()
        
        gaps = scan_gaps("POS Invoice", rule.name)
        self.assertEqual(len(gaps), 2)
        self.assertEqual(gaps[0]["number"], 2)
        self.assertEqual(gaps[0]["status"], "Pending")
        self.assertEqual(gaps[1]["number"], 3)

    def test_explain_generation(self):
        rule = frappe.get_doc({
            "doctype": "SMRITI Numbering Rule",
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        frappe.db.commit()
        
        ctx = GenerationContext(company="Test Company", branch="MUMBAI")
        res = generate("POS Invoice", ctx)
        
        exp = explain(res.identity)
        self.assertTrue(exp["success"])
        self.assertEqual(exp["schema_version"], 1)
        self.assertEqual(exp["evidence"]["generated_number"], "INV-1")
        self.assertEqual(exp["evidence"]["context"]["branch"], "MUMBAI")
        self.assertEqual(exp["metrics"]["explainability_score"], 100)
        self.assertTrue(len(exp["timeline"]) > 3)
        
        # Test look up by business display number too
        exp_by_display = explain("INV-1")
        self.assertTrue(exp_by_display["success"])
        self.assertEqual(exp_by_display["evidence"]["document_name"], res.identity)

    def test_explain_missing_record(self):
        exp = explain("NONEXISTENT-INV-999")
        self.assertFalse(exp["success"])
        self.assertEqual(exp["schema_version"], 1)
        self.assertEqual(exp["confidence"], 0)
        self.assertEqual(exp["metrics"]["explainability_score"], 0)
        self.assertIn("No UDNE audit trace found", exp["summary"])

    def test_explain_invalid_json_context(self):
        # Create a mock audit log with malformed context details
        log = frappe.get_doc({
            "doctype": "SMRITI Numbering Audit Log",
            "document_type": "POS Invoice",
            "document_name": "PI-MALFORMED",
            "generated_number": "INV-MALFORMED",
            "rule_version": 1,
            "context_details": "{invalid-json}",
            "timestamp": datetime.datetime.now()
        })
        log.insert(ignore_permissions=True)
        frappe.db.commit()
        
        exp = explain("PI-MALFORMED")
        self.assertTrue(exp["success"])
        self.assertEqual(exp["evidence"]["context"], {})  # Graceful fallback to empty dict
        self.assertEqual(exp["confidence"], 60)  # Deducted for missing rule reference (20) & missing template (20)

    def test_dashboard_metrics_aggregation(self):
        rule = frappe.get_doc({
            "doctype": "SMRITI Numbering Rule",
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        frappe.db.commit()
        
        ctx = GenerationContext(company="Test Company")
        res1 = generate("POS Invoice", ctx)
        res2 = generate("POS Invoice", ctx)
        
        # Insert generated numbers into the table so gaps() returns 0 unexplained gaps
        frappe.db.sql("insert into `tabPOS Invoice` (name, custom_business_display_number, company, docstatus) values (%s, %s, %s, 0)", (res1.identity, res1.display_number, "Test Company"))
        frappe.db.sql("insert into `tabPOS Invoice` (name, custom_business_display_number, company, docstatus) values (%s, %s, %s, 0)", (res2.identity, res2.display_number, "Test Company"))
        frappe.db.commit()
        
        m = metrics("Today")
        self.assertEqual(m["total_generations"], 2)
        self.assertTrue(m["average_latency_ms"] >= 0.0)
        self.assertTrue(m["p95_latency_ms"] >= 0.0)
        
        h = health()
        self.assertEqual(h["active_rules"], 1)
        self.assertEqual(h["explainability_score"], 100.0)
        
        r = reservations()
        self.assertEqual(len(r), 0)
        
        g = gaps()
        self.assertEqual(len(g), 0)

    def test_before_print_document_hook(self):
        doc = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": frappe.get_all("Company")[0].name,
            "posting_date": nowdate(),
            "customer": "Walk-In Customer",
            "custom_business_display_number": "MUM/FY26/INV/000088"
        })
        
        from smriti_retail_os.services.udne.hooks import before_print_document
        before_print_document(doc)
        
        self.assertEqual(doc.udne_display_number, "MUM/FY26/INV/000088")
        self.assertEqual(doc.udne_print_number, "MUM/FY26/INV/000088")
        self.assertEqual(doc.select_print_heading, "MUM/FY26/INV/000088")
        
        # Verify canonical name is NOT mutated to prevent downstream bugs!
        self.assertNotEqual(doc.name, "MUM/FY26/INV/000088")

    def test_search_by_partial_business_number(self):
        comp = frappe.get_all("Company")[0].name
        doc = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": comp,
            "posting_date": nowdate(),
            "customer": "Walk-In Customer",
            "custom_business_display_number": "MUM/FY26/INV/000099",
            "base_grand_total": 0.0,
            "base_rounded_total": 0.0,
            "grand_total": 0.0,
            "rounded_total": 0.0
        })
        doc.insert(ignore_permissions=True, ignore_mandatory=True)
        frappe.db.commit()
        
        # Verify list query returns match by display number (partial lookups)
        res = frappe.get_list("Sales Invoice", filters={"custom_business_display_number": ["like", "%000099%"]})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].name, doc.name)

    def test_missing_business_number_fallback(self):
        doc = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": frappe.get_all("Company")[0].name,
            "posting_date": nowdate(),
            "customer": "Walk-In Customer"
        })
        
        # Capture current select_print_heading if any
        initial_heading = getattr(doc, "select_print_heading", None)
        
        from smriti_retail_os.services.udne.hooks import before_print_document
        before_print_document(doc)
        
        self.assertIsNone(getattr(doc, "udne_display_number", None))
        self.assertIsNone(getattr(doc, "udne_print_number", None))
        self.assertEqual(getattr(doc, "select_print_heading", None), initial_heading)

