# -*- coding: utf-8 -*-
# SMRITI Matrix Validator
import frappe
from frappe import _

class MatrixValidator:
    @staticmethod
    def validate_session(session_data):
        """
        Validates cells and coordinates in matrix session.
        session_data is a dict containing 'cells' list with keys 'x_val', 'y_val', 'qty'.
        """
        cells = session_data.get("cells", [])
        
        for c in cells:
            qty = float(c.get("qty") or 0)
            if qty < 0:
                frappe.throw(_("Quantity for Cell ({0}, {1}) cannot be negative.").format(c.get("x_val"), c.get("y_val")))
                
        seen = set()
        for c in cells:
            key = (c.get("x_val"), c.get("y_val"))
            if key in seen:
                frappe.throw(_("Duplicate Cell coordinates found: ({0}, {1})").format(key[0], key[1]))
            seen.add(key)
            
        return True
