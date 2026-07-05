# -*- coding: utf-8 -*-
# SMRITI Matrix Platform Subsystem Unit Tests
import frappe
import unittest
from smriti_retail_os.item_studio.service.variant_lifecycle_service import VariantLifecycleService
from smriti_retail_os.matrix_engine.service.matrix_service import MatrixService
from smriti_retail_os.purchase_studio.adapter.purchase_matrix_adapter import PurchaseMatrixAdapter

class TestPurchaseMatrix(unittest.TestCase):
    def setUp(self):
        self.article_code = "TST-SHIRT-TMP"
        self.variant_code = "TST-SHIRT-TMP-RED-M"
        
        # Ensure valid HSN code
        self.hsn_code = frappe.db.get_value("GST HSN Code", {}, "name")
        if not self.hsn_code:
            self.hsn_code = "99990000"
            if not frappe.db.exists("GST HSN Code", self.hsn_code):
                hsn = frappe.new_doc("GST HSN Code")
                hsn.name = self.hsn_code
                hsn.hsn_code = self.hsn_code
                hsn.description = "Test HSN Code"
                hsn.insert(ignore_permissions=True)
                frappe.db.commit()

        # Cleanup
        self.cleanup()

    def tearDown(self):
        self.cleanup()

    def cleanup(self):
        # Delete prices, barcodes, and items
        for item in [self.variant_code, self.article_code]:
            if frappe.db.exists("Item", item):
                frappe.db.delete("Item Price", {"item_code": item})
                frappe.db.delete("Item Barcode", {"parent": item})
                frappe.delete_doc("Item", item, force=1)
        frappe.db.commit()

    def test_matrix_subsystem_flow(self):
        # 1. Create Article template
        article_name = VariantLifecycleService.create_article_template(
            article_code=self.article_code,
            item_name="Test Template Shirt",
            hsn_code=self.hsn_code,
            attributes=["Color", "Size"]
        )
        self.assertEqual(article_name, self.article_code)
        self.assertTrue(frappe.db.get_value("Item", self.article_code, "has_variants"))

        # 2. Resolve or Create Variant
        attributes = {"Color": "Red", "Size": "M"}
        variant_code = VariantLifecycleService.resolve_or_create_variant(self.article_code, attributes)
        self.assertTrue(frappe.db.exists("Item", variant_code))

        # Check barcode assignment
        barcode = frappe.db.get_value("Item Barcode", {"parent": variant_code, "custom_is_primary": 1}, "barcode")
        self.assertTrue(barcode)

        # 3. Test Build Session DTO
        session = MatrixService.build_session(self.article_code)
        self.assertEqual(session.article, self.article_code)
        resolved_color = next((c for c in session.colors if c.lower() == "red"), "Red")
        resolved_size = next((s for s in session.sizes if s.lower() == "m"), "M")
        self.assertIn(resolved_color, session.colors)
        self.assertIn(resolved_size, session.sizes)

        # 4. Test Adapter Mapping
        cells = [{
            "x_val": resolved_size,
            "y_val": resolved_color,
            "qty": 10,
            "article": self.article_code,
            "variant": {
                "item_code": variant_code,
                "item_name": "Test Template Shirt (Red / M)",
                "rate": 150.0,
                "barcode": barcode,
                "uom": "Nos"
            }
        }]
        po_items = PurchaseMatrixAdapter.cells_to_po_items(cells, warehouse="Stores")
        self.assertEqual(len(po_items), 1)
        self.assertEqual(po_items[0]["item_code"], variant_code)
        self.assertEqual(po_items[0]["qty"], 10)
        self.assertEqual(po_items[0]["article"], self.article_code)
        self.assertEqual(po_items[0]["barcode"], barcode)


def run_tests():
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPurchaseMatrix)
    runner = unittest.TextTestRunner()
    runner.run(suite)

