import unittest
import frappe
from smriti_retail_os import smriti
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
        smriti.db.commit()

    def setUp(self):
        smriti.db.delete("SMRITI Numbering Rule")
        smriti.db.delete("SMRITI Numbering Counter")
        smriti.db.delete("SMRITI Numbering Reserved Range")
        smriti.db.delete("SMRITI Numbering Audit Log")
        smriti.db.delete("POS Invoice")
        smriti.db.delete("Sales Invoice")
        smriti.db.commit()
        clear_compiled_template_cache()
        
    def tearDown(self):
        smriti.db.delete("SMRITI Numbering Rule")
        smriti.db.delete("SMRITI Numbering Counter")
        smriti.db.delete("SMRITI Numbering Reserved Range")
        smriti.db.delete("SMRITI Numbering Audit Log")
        smriti.db.delete("POS Invoice")
        smriti.db.delete("Sales Invoice")
        smriti.db.commit()
        clear_compiled_template_cache()
        
    def test_facade_api(self):
        rule = smriti.documents.new("NumberingRule")
        rule.update({
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV-{year}-{counter:6}",
            "is_active": 1,
            "reset_rule": "Never"
        })
        rule.insert(ignore_permissions=True)
        smriti.db.commit()
        
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
        smriti.documents.new("NumberingRule").update({
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "GLOBAL-{counter}",
            "is_active": 1
        }).insert(ignore_permissions=True)
        
        smriti.documents.new("NumberingRule").update({
            "document_type": "POS Invoice",
            "priority": "Branch",
            "priority_value": "MUMBAI",
            "template": "MUM-{counter}",
            "is_active": 1
        }).insert(ignore_permissions=True)
        
        smriti.documents.new("NumberingRule").update({
            "document_type": "POS Invoice",
            "priority": "Store",
            "priority_value": "MUM-STORE",
            "template": "STORE-{counter}",
            "is_active": 1
        }).insert(ignore_permissions=True)
        
        smriti.db.commit()
        
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
        rule = smriti.documents.new("NumberingRule")
        rule.update({
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "OLD-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        smriti.db.commit()
        
        ctx = GenerationContext(company="Test Company")
        res1 = generate("POS Invoice", ctx)
        self.assertEqual(res1.display_number, "OLD-1")
        
        rule.template = "NEW-{counter}"
        rule.save(ignore_permissions=True)
        smriti.db.commit()
        
        res2 = generate("POS Invoice", ctx)
        self.assertEqual(res2.display_number, "NEW-2")
        
    def test_financial_year_rollover(self):
        rule = smriti.documents.new("NumberingRule")
        rule.update({
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV/{fy}/{counter:4}",
            "reset_rule": "Financial Year",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        smriti.db.commit()
        
        ctx1 = GenerationContext(company="Test Company", transaction_date=datetime.date(2026, 3, 15))
        res1 = generate("POS Invoice", ctx1)
        self.assertEqual(res1.display_number, "INV/25-26/0001")
        
        ctx2 = GenerationContext(company="Test Company", transaction_date=datetime.date(2026, 4, 1))
        res2 = generate("POS Invoice", ctx2)
        self.assertEqual(res2.display_number, "INV/26-27/0001")
        
    def test_reservation_lifecycle(self):
        rule = smriti.documents.new("NumberingRule")
        rule.update({
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        smriti.db.commit()
        
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
        rule = smriti.documents.new("NumberingRule")
        rule.update({
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        smriti.db.commit()
        
        ctx = GenerationContext(company="Test Company")
        
        res1 = generate("POS Invoice", ctx)
        smriti.db.sql("insert into `tabPOS Invoice` (name, custom_business_display_number, company, docstatus) values (%s, %s, %s, 0)", (res1.identity, res1.display_number, "Test Company"))
        
        reserve_range("POS Invoice", "TERM-02", 2, rule.name, "Never", ctx.as_dict())
        
        res4 = generate("POS Invoice", ctx)
        smriti.db.sql("insert into `tabPOS Invoice` (name, custom_business_display_number, company, docstatus) values (%s, %s, %s, 0)", (res4.identity, res4.display_number, "Test Company"))
        smriti.db.commit()
        
        gaps = scan_gaps("POS Invoice", rule.name)
        self.assertEqual(len(gaps), 2)
        self.assertEqual(gaps[0]["number"], 2)
        self.assertEqual(gaps[0]["status"], "Pending")
        self.assertEqual(gaps[1]["number"], 3)

    def test_explain_generation(self):
        rule = smriti.documents.new("NumberingRule")
        rule.update({
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        smriti.db.commit()
        
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
        log = smriti.documents.new("NumberingAuditLog")
        log.update({
            "document_type": "POS Invoice",
            "document_name": "PI-MALFORMED",
            "generated_number": "INV-MALFORMED",
            "rule_version": 1,
            "context_details": "{invalid-json}",
            "timestamp": datetime.datetime.now()
        })
        log.insert(ignore_permissions=True)
        smriti.db.commit()
        
        exp = explain("PI-MALFORMED")
        self.assertTrue(exp["success"])
        self.assertEqual(exp["evidence"]["context"], {})  # Graceful fallback to empty dict
        self.assertEqual(exp["confidence"], 60)  # Deducted for missing rule reference (20) & missing template (20)

    def test_dashboard_metrics_aggregation(self):
        rule = smriti.documents.new("NumberingRule")
        rule.update({
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "INV-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        smriti.db.commit()
        
        ctx = GenerationContext(company="Test Company")
        res1 = generate("POS Invoice", ctx)
        res2 = generate("POS Invoice", ctx)
        
        # Insert generated numbers into the table so gaps() returns 0 unexplained gaps
        smriti.db.sql("insert into `tabPOS Invoice` (name, custom_business_display_number, company, docstatus) values (%s, %s, %s, 0)", (res1.identity, res1.display_number, "Test Company"))
        smriti.db.sql("insert into `tabPOS Invoice` (name, custom_business_display_number, company, docstatus) values (%s, %s, %s, 0)", (res2.identity, res2.display_number, "Test Company"))
        smriti.db.commit()
        
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
        doc = smriti.documents.new("SalesInvoice")
        doc.update({
            "company": smriti.db.get_list("Company")[0].name,
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
        comp = smriti.db.get_list("Company")[0].name
        doc = smriti.documents.new("SalesInvoice")
        doc.update({
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
        smriti.db.commit()
        
        # Verify list query returns match by display number (partial lookups)
        res = frappe.get_list("Sales Invoice", filters={"custom_business_display_number": ["like", "%000099%"]})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].name, doc.name)

    def test_missing_business_number_fallback(self):
        doc = smriti.documents.new("SalesInvoice")
        doc.update({
            "company": smriti.db.get_list("Company")[0].name,
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

    def test_rule_loader_getdate(self):
        # Create a rule with validity period in the future
        future_from = frappe.utils.add_to_date(frappe.utils.nowdate(), days=5)
        rule = smriti.documents.new("NumberingRule")
        rule.update({
            "document_type": "POS Invoice",
            "priority": "Global",
            "template": "FUTURE-{counter}",
            "is_active": 1,
            "effective_from": future_from
        })
        rule.insert(ignore_permissions=True)
        smriti.db.commit()
        
        from smriti_retail_os.services.udne.rule_loader import load_active_rule
        # Verify it raises UDNERuleNotFoundError because the future rule is not yet valid
        with self.assertRaises(UDNERuleNotFoundError):
            load_active_rule("POS Invoice", {"company": "Test Company"})

    def test_autoname_transaction_date(self):
        # Verify that autoname hook resolves posting_date, transaction_date, and None safely
        comp = smriti.db.get_list("Company")[0].name
        
        # 1. Posting date present
        doc1 = smriti.documents.new("SalesInvoice")
        doc1.update({
            "company": comp,
            "posting_date": nowdate(),
            "customer": "Walk-In Customer"
        })
        
        # 2. Transaction date present (no posting date)
        doc2 = smriti.documents.new("SalesInvoice")
        doc2.update({
            "company": comp,
            "transaction_date": nowdate(),
            "customer": "Walk-In Customer"
        })
        
        # 3. Neither present
        doc3 = smriti.documents.new("SalesInvoice")
        doc3.update({
            "company": comp,
            "customer": "Walk-In Customer"
        })
        
        from smriti_retail_os.services.udne.hooks import autoname_document
        
        # Create a numbering rule first to trigger the hook logic
        rule = smriti.documents.new("NumberingRule")
        rule.update({
            "document_type": "Sales Invoice",
            "priority": "Global",
            "template": "INV-{year}-{counter}",
            "is_active": 1
        })
        rule.insert(ignore_permissions=True)
        smriti.db.commit()
        
        # Test them, verifying that they all run autoname successfully without AttributeError
        autoname_document(doc1)
        self.assertTrue(doc1.name.startswith("SI-"))
        self.assertTrue(doc1.custom_business_display_number.startswith("INV-2026-"))
        
        autoname_document(doc2)
        self.assertTrue(doc2.name.startswith("SI-"))
        self.assertTrue(doc2.custom_business_display_number.startswith("INV-2026-"))
        
        autoname_document(doc3)
        self.assertTrue(doc3.name.startswith("SI-"))
        self.assertTrue(doc3.custom_business_display_number.startswith("INV-2026-"))

