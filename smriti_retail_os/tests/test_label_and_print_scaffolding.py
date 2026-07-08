# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/tests/test_label_and_print_scaffolding.py
# @desc:    Unit tests for SMRITI Label Studio and Print Framework.
# @author:  Jawahar R. Mallah
#

import unittest
import frappe
from smriti_retail_os import smriti
from smriti_retail_os.label_studio.service.preview_engine import PreviewEngine
from smriti_retail_os.label_studio.service.render_engine import RenderEngine
from smriti_retail_os.print_framework.registry.printer_registry import PrinterRegistry
from smriti_retail_os.print_framework.dispatcher import print_dispatcher
from smriti_retail_os.print_framework.dispatcher.print_dispatcher import PrintDispatcher
from smriti_retail_os.print_framework.service.print_service import PrintService

class TestLabelAndPrintScaffolding(unittest.TestCase):
    """
    Validates SMRITI Print Framework connectivity, rendering strategies,
    preview coordinates compiling, and end-to-end integration execution flow.
    """

    def setUp(self):
        # Register a mock ZPL USB printer and TSPL Network LAN printer in registry
        PrinterRegistry.clear()
        PrinterRegistry.register_printer(
            printer_id="Zebra_USB_Mock",
            connection_type="USB",
            connection_params={"printer_name": "TestZebraUSB"},
            capabilities={
                "ZPL": True, "TSPL": False, "PDF": False, "ESC_POS": False,
                "max_width_mm": 110, "color_capable": False
            }
        )
        PrinterRegistry.register_printer(
            printer_id="TSC_LAN_Mock",
            connection_type="LAN",
            connection_params={"ip_address": "192.168.2.22", "port": 9100},
            capabilities={
                "ZPL": False, "TSPL": True, "PDF": False, "ESC_POS": False,
                "max_width_mm": 80, "color_capable": False
            }
        )

    def tearDown(self):
        PrinterRegistry.clear()

    def test_preview_engine_coordinates(self):
        """Preview Path: Verify PreviewEngine converts mm elements to canvas px coordinates."""
        label_data = {
            "width_mm": 100,
            "height_mm": 50,
            "elements": [
                {"id": "txt_1", "type": "Text", "x": 10, "y": 15, "content": "SMRITI Standard", "width": 40, "height": 10},
                {"id": "bc_1", "type": "Barcode", "x": 10, "y": 30, "content": "12345678", "width": 50, "height": 15}
            ]
        }
        res = PreviewEngine.render_canvas_json(label_data)
        self.assertEqual(res["width_px"], 378.0)
        self.assertEqual(res["height_px"], 189.0)
        self.assertEqual(len(res["elements"]), 2)
        
        txt_el = res["elements"][0]
        self.assertEqual(txt_el["id"], "txt_1")
        self.assertEqual(txt_el["x_px"], 37.8)
        self.assertEqual(txt_el["y_px"], 56.7)

    def test_render_engine_strategies(self):
        """Render Path: Verify ZPL and TSPL rendering strategies produce valid output formats."""
        label_data = {
            "width_mm": 100,
            "height_mm": 50,
            "elements": [
                {"type": "Barcode", "x": 10, "y": 20, "content": "PRINTSAMPLE"}
            ]
        }
        
        # Test ZPL Strategy
        zpl_output = RenderEngine.render_stream(label_data, "ZPL")
        self.assertTrue(zpl_output.startswith("^XA"))
        self.assertIn("^FO80,160^BCN,60,Y,N,N^FDPRINTSAMPLE^FS", zpl_output)
        self.assertTrue(zpl_output.endswith("^XZ"))

        # Test TSPL Strategy
        tspl_output = RenderEngine.render_stream(label_data, "TSPL")
        self.assertIn("SIZE 100.0 mm, 50.0 mm", tspl_output)
        self.assertIn('BARCODE 80,160,"128",60,1,0,2,2,"PRINTSAMPLE"', tspl_output)

    def test_print_dispatcher_and_registry_mapping(self):
        """Dispatch Path: Verify PrintDispatcher resolves adapters dynamically from registry."""
        # Test USB dispatching
        success_usb = PrintDispatcher.dispatch("Zebra_USB_Mock", b"^XA^XZ")
        self.assertTrue(success_usb)

        # Test LAN dispatching
        success_lan = PrintDispatcher.dispatch("TSC_LAN_Mock", b"SIZE 100,50")
        self.assertTrue(success_lan)

        # Test unregistered printer exception
        with self.assertRaises(ValueError):
            PrintDispatcher.dispatch("Unknown_Printer", b"data")

    def test_end_to_end_printing_service_integration(self):
        """E2E Integration: Verify full path (Label -> Preview -> Render -> Queue -> Dispatch)."""
        label_data = {
            "width_mm": 100,
            "height_mm": 50,
            "elements": [
                {"type": "Text", "x": 10, "y": 10, "content": "E2ETest"}
            ]
        }

        # 1. Preview compilation check
        preview = PreviewEngine.render_canvas_json(label_data)
        self.assertIsNotNone(preview)

        # 2. Render and Dispatch check via print service
        job_id = PrintService.print_label("Label Studio", "Zebra_USB_Mock", "^XA^FO80,80^A0N,28,28^FDE2ETest^FS^XZ")
        self.assertIsNotNone(job_id)

        # Verify that print job document status was marked completed
        job_status = smriti.db.get("SMRITI Print Job", job_id, "status")
        self.assertEqual(job_status, "Completed")
