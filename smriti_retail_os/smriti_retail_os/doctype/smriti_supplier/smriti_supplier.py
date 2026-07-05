# -*- coding: utf-8 -*-
# SMRITI Supplier — DocType Controller
from frappe.model.document import Document

class SMRITISupplier(Document):
    def validate(self):
        if self.email_id:
            from frappe.utils import validate_email_address
            validate_email_address(self.email_id, throw=True)
