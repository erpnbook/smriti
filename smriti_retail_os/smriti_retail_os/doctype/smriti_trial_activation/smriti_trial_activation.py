# Copyright (c) 2026, AITDL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SMRITITrialActivation(Document):
    def before_insert(self):
        """Auto-generate activation_reference if not set."""
        if not self.activation_reference:
            self.activation_reference = _generate_ref()

    def before_save(self):
        """Sync quick-view fields from linked trial lead."""
        if self.trial_lead and (not self.store_name or not self.owner_name):
            lead = frappe.get_doc('SMRITI Trial Lead', self.trial_lead)
            self.store_name  = lead.store_name
            self.owner_name  = lead.owner_name
            self.mobile      = lead.mobile


def _generate_ref():
    """Return next TA-YYYY-NNNNN reference number."""
    import datetime
    year = datetime.date.today().year
    last = frappe.db.sql(
        """
        SELECT activation_reference
        FROM   `tabSMRITI Trial Activation`
        WHERE  activation_reference LIKE %s
        ORDER  BY creation DESC
        LIMIT  1
        """,
        (f'TA-{year}-%',),
    )
    if last and last[0][0]:
        try:
            seq = int(last[0][0].split('-')[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f'TA-{year}-{seq:05d}'
