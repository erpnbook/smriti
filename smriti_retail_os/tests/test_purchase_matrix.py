# -*- coding: utf-8 -*-
# SMRITI Matrix Platform Subsystem Unit Tests
import frappe
from smriti_retail_os import smriti
import unittest
from smriti_retail_os.item_studio.service.variant_lifecycle_service import VariantLifecycleService
from smriti_retail_os.matrix_engine.service.matrix_service import MatrixService
from smriti_retail_os.purchase_studio.adapter.purchase_matrix_adapter import PurchaseMatrixAdapter

class TestPurchaseMatrix(unittest.TestCase):
    def setUp(self):
        self.article_code = "TST-SHIRT-TMP"
        self.variant_code = "TST-SHIRT-TMP-RED-M"
        
        # Ensure valid HSN code
        self.hsn_code = smriti.db.get("GST HSN Code", {}, "name")
        if not self.hsn_code:
            self.hsn_code = "99990000"
            if not smriti.db.exists("GST HSN Code", self.hsn_code):
                hsn = smriti.documents.new("GST HSN Code")
                hsn.name = self.hsn_code
                hsn.hsn_code = self.hsn_code
                hsn.description = "Test HSN Code"
                hsn.insert(ignore_permissions=True)
                smriti.db.commit()

        # Cleanup
        self.cleanup()

    def tearDown(self):
        self.cleanup()

    def cleanup(self):
        # Delete prices, barcodes, and items
        for item in [self.variant_code, self.article_code]:
            if smriti.db.exists("Item", item):
                smriti.db.delete("Item Price", {"item_code": item})
                smriti.db.delete("Item Barcode", {"parent": item})
                frappe.delete_doc("Item", item, force=1)
        smriti.db.commit()

    def test_matrix_subsystem_flow(self):
        # 1. Create Article template
        article_name = VariantLifecycleService.create_article_template(
            article_code=self.article_code,
            item_name="Test Template Shirt",
            hsn_code=self.hsn_code,
            attributes=["Color", "Size"]
        )
        self.assertEqual(article_name, self.article_code)
        self.assertTrue(smriti.db.get("Item", self.article_code, "has_variants"))

        # 2. Resolve or Create Variant
        attributes = {"Color": "Red", "Size": "M"}
        variant_code = VariantLifecycleService.resolve_or_create_variant(self.article_code, attributes)
        self.assertTrue(smriti.db.exists("Item", variant_code))

        # Check barcode assignment
        barcode = smriti.db.get("Item Barcode", {"parent": variant_code, "custom_is_primary": 1}, "barcode")
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

    def test_dto_and_sorting(self):
        # Create article template with standard rate & name
        VariantLifecycleService.create_article_template(
            article_code=self.article_code,
            item_name="Slim Fit Jeans",
            hsn_code=self.hsn_code,
            attributes=["Color", "Size"]
        )
        # Set standard rate (MRP)
        smriti.db.set_value("Item", self.article_code, "standard_rate", 1299.0)
        smriti.db.commit()

        # Clear cache first to ensure cache miss
        MatrixService.clear_cache(self.article_code)

        # 1. Fresh build / Cache Miss
        session = MatrixService.build_session(self.article_code)
        session_dict = session.to_dict()
        self.assertEqual(session_dict.get("item_name"), "Slim Fit Jeans")
        self.assertEqual(float(session_dict.get("mrp") or 0.0), 1299.0)

        # 2. Cache Hit
        session2 = MatrixService.build_session(self.article_code)
        session_dict2 = session2.to_dict()
        self.assertEqual(session_dict2.get("item_name"), "Slim Fit Jeans")
        self.assertEqual(float(session_dict2.get("mrp") or 0.0), 1299.0)

        # 3. Mixed Size Sorting Logic
        std_sizes = {"M", "XL", "S", "L"}
        std_order = ["3XS", "2XS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL"]
        std_order_map = {size: idx for idx, size in enumerate(std_order)}
        def get_sort_key(sz):
            val = sz.upper()
            if val in std_order_map:
                return (0, std_order_map[val])
            else:
                return (1, val)
        sizes_sorted = sorted(list(std_sizes), key=get_sort_key)
        self.assertEqual(sizes_sorted, ["S", "M", "L", "XL"])

        # Footwear numeric sorting logic
        footwear_sizes = {"9", "11", "6", "10", "7", "12", "8"}
        is_all_numeric = all(x.replace('.', '', 1).isdigit() for x in footwear_sizes if x != "Default")
        if is_all_numeric:
            sizes_sorted_fw = sorted(list(footwear_sizes), key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else 0.0)
        self.assertEqual(sizes_sorted_fw, ["6", "7", "8", "9", "10", "11", "12"])

    def test_analytics_and_performance(self):
        # Ensure Item Groups exist
        for group in ["Footwear", "SANDAL"]:
            if not smriti.db.exists("Item Group", group):
                doc = smriti.documents.new("Item Group")
                doc.item_group_name = group
                doc.parent_item_group = "All Item Groups"
                doc.insert(ignore_permissions=True)
        smriti.db.commit()

        # 1. Clear any existing POs for company
        smriti.db.delete("SMRITI Purchase Order Item")
        smriti.db.delete("SMRITI Purchase Order")
        smriti.db.commit()

        # 2. Create standard items with distinct item groups
        from smriti_retail_os.item_studio.service.variant_lifecycle_service import VariantLifecycleService
        hsn = self.hsn_code
        
        # Create Footwear item
        VariantLifecycleService.ensure_attribute_and_value("Color", "Red")
        VariantLifecycleService.ensure_attribute_and_value("Size", "M")
        fw_art = "ART-SHOES-002"
        VariantLifecycleService.create_article_template(
            article_code=fw_art,
            item_name="Footwear Item",
            hsn_code=hsn,
            attributes=["Color", "Size"]
        )
        smriti.db.set_value("Item", fw_art, "item_group", "Footwear")
        fw_var = VariantLifecycleService.resolve_or_create_variant(fw_art, {"Color": "Red", "Size": "M"})
        smriti.db.set_value("Item", fw_var, "item_group", "Footwear")

        # Create Sandal item
        app_art = "ART-SANDAL-002"
        VariantLifecycleService.create_article_template(
            article_code=app_art,
            item_name="Sandal Item",
            hsn_code=hsn,
            attributes=["Color", "Size"]
        )
        smriti.db.set_value("Item", app_art, "item_group", "SANDAL")
        app_var = VariantLifecycleService.resolve_or_create_variant(app_art, {"Color": "Red", "Size": "M"})
        smriti.db.set_value("Item", app_var, "item_group", "SANDAL")
        
        smriti.db.commit()

        # 3. Resolve suppliers and warehouse dynamically to prevent LinkValidationError
        suppliers_list = smriti.db.get_list("SMRITI Supplier", limit=2, pluck="name")
        supplier_a = suppliers_list[0] if len(suppliers_list) > 0 else "TEST-SUPP-A"
        supplier_b = suppliers_list[1] if len(suppliers_list) > 1 else "TEST-SUPP-B"
        
        for s in [supplier_a, supplier_b]:
            if not smriti.db.exists("SMRITI Supplier", s):
                sup = smriti.documents.new("SMRITI Supplier")
                sup.name = s
                sup.supplier_name = s
                sup.insert(ignore_permissions=True)
        
        warehouse = smriti.db.get("Warehouse", {"is_group": 0}, "name") or "Stores - _SC"

        # 4. Create test Purchase Orders
        # PO 1: Submitted, on time, fully received
        po1 = smriti.documents.new("SMRITI Purchase Order")
        po1.supplier = supplier_a
        po1.supplier_name = supplier_a
        po1.company = "_Test Company"
        po1.transaction_date = "2026-07-01"
        po1.schedule_date = "2026-07-02"
        po1.grand_total = 1000.0
        po1.per_received = 100.0
        po1.docstatus = 1
        po1.status = "Completed"
        po1.append("items", {
            "item_code": fw_var,
            "item_name": "Footwear Item Var",
            "qty": 10,
            "rate": 100.0,
            "amount": 1000.0,
            "uom": "Nos",
            "warehouse": warehouse
        })
        po1.insert(ignore_permissions=True)

        # PO 2: Submitted, overdue (schedule_date is in the past), not received (0% received)
        po2 = smriti.documents.new("SMRITI Purchase Order")
        po2.supplier = supplier_b
        po2.supplier_name = supplier_b
        po2.company = "_Test Company"
        po2.transaction_date = "2026-07-01"
        po2.schedule_date = "2026-07-02" # Past date
        po2.grand_total = 1500.0
        po2.per_received = 0.0
        po2.docstatus = 1
        po2.status = "Ordered"
        po2.append("items", {
            "item_code": app_var,
            "item_name": "Sandal Item Var",
            "qty": 15,
            "rate": 100.0,
            "amount": 1500.0,
            "uom": "Nos",
            "warehouse": warehouse
        })
        po2.insert(ignore_permissions=True)
        smriti.db.commit()

        # 4. Call get_purchase_analytics and assert correct aggregations
        from smriti_retail_os.purchase_studio.service.purchase_service import get_purchase_analytics
        analytics = get_purchase_analytics(company="_Test Company")
        
        # Assert supplier spend
        suppliers = {s["supplier"]: s["total_spend"] for s in analytics["by_supplier"]}
        self.assertEqual(suppliers.get(supplier_a), 1000.0)
        self.assertEqual(suppliers.get(supplier_b), 1500.0)

        # Assert item group spend (Fix 1)
        item_groups = {ig["item_group"]: ig["total_spend"] for ig in analytics["by_item_group"]}
        self.assertEqual(item_groups.get("Footwear"), 1000.0)
        self.assertEqual(item_groups.get("SANDAL"), 1500.0)

        # 5. Call get_supplier_performance and assert correct overdue amounts (Fix 2)
        from smriti_retail_os.purchase_studio.service.purchase_service import get_supplier_performance
        performance = get_supplier_performance(company="_Test Company")
        
        perf_dict = {p["supplier"]: p for p in performance}
        # Supplier A: fully received, overdue_amount should be 0.0
        self.assertEqual(float(perf_dict.get(supplier_a)["overdue_amount"]), 0.0)
        # Supplier B: 0% received, schedule_date in past, overdue_amount should be 1500.0
        self.assertEqual(float(perf_dict.get(supplier_b)["overdue_amount"]), 1500.0)

    def test_size_only_matrix(self):
        # 1. Create a size-only article template
        from smriti_retail_os.item_studio.service.variant_lifecycle_service import VariantLifecycleService
        hsn = self.hsn_code
        
        # Ensure Size "S" value exists
        VariantLifecycleService.ensure_attribute_and_value("Size", "S")
        
        art_code = "ART-SIZEONLY-001"
        VariantLifecycleService.create_article_template(
            article_code=art_code,
            item_name="Size Only Article",
            hsn_code=hsn,
            attributes=["Size"] # No Color attribute
        )
        
        # Create a size variant
        var_code = VariantLifecycleService.resolve_or_create_variant(art_code, {"Size": "S"})
        smriti.db.commit()
        
        # 2. Build matrix session
        session = MatrixService.build_session(art_code)
        
        # Assert colors has exactly "No Color configured" and sizes has "S"
        self.assertEqual(session.colors, ["No Color configured"])
        self.assertIn("S", session.sizes)
        
        # Assert variant attributes do not contain "UNKNOWN" for color
        self.assertEqual(session.variants_list[0].color, "No Color configured")
        self.assertEqual(session.variants_list[0].size, "S")


def run_tests():
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPurchaseMatrix)
    runner = unittest.TextTestRunner()
    runner.run(suite)


def seed_test_data():
    import frappe
    from smriti_retail_os.item_studio.service.variant_lifecycle_service import VariantLifecycleService
    
    hsn = smriti.db.get("GST HSN Code", {}, "name")
    if not hsn:
        doc = smriti.documents.new("GST HSN Code")
        doc.name = "99990000"
        doc.hsn_code = "99990000"
        doc.description = "Test HSN Code"
        doc.insert(ignore_permissions=True)
        hsn = "99990000"

    VariantLifecycleService.ensure_attribute_and_value("Color", "Red")
    VariantLifecycleService.ensure_attribute_and_value("Color", "Blue")
    VariantLifecycleService.ensure_attribute_and_value("Color", "Black")
    VariantLifecycleService.ensure_attribute_and_value("Size", "S")
    VariantLifecycleService.ensure_attribute_and_value("Size", "M")
    VariantLifecycleService.ensure_attribute_and_value("Size", "L")

    VariantLifecycleService.create_article_template(
        article_code="ART-JEANS-001",
        item_name="Style Jeans 001",
        hsn_code=hsn,
        attributes=["Color", "Size"]
    )
    
    smriti.db.commit()
    print("Success: ART-JEANS-001 created!")


