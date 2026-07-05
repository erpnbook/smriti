# -*- coding: utf-8 -*-
# SMRITI Purchase Order — DocType Controller
from frappe.model.document import Document

class SMRITIPurchaseOrder(Document):
    def validate(self):
        # Validation is orchestrated primarily by PurchaseValidationService
        pass
