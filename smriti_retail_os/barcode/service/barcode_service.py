# -*- coding: utf-8 -*-
# SMRITI Barcode Platform Service
import frappe
from frappe import _

class BarcodeService:
    @staticmethod
    def generate(format_name="EAN13"):
        """
        Generates a unique barcode based on the requested format.
        Default is EAN-13.
        """
        if format_name.upper() == "EAN13":
            return BarcodeService.generate_ean13()
        else:
            frappe.throw(_("Barcode format {0} is not supported by the system yet.").format(format_name))

    @staticmethod
    def generate_ean13():
        """
        Generates a unique EAN-13 barcode with collision avoidance.
        """
        from smriti_retail_os.item_master_api import generate_ean13_barcode
        return generate_ean13_barcode()

    @staticmethod
    def validate(barcode, format_name="EAN13"):
        """
        Validates the mathematical correctness and uniqueness of the barcode.
        """
        from smriti_retail_os.item_master_api import validate_barcode
        validate_barcode(barcode, raise_exception=True)
        return True
