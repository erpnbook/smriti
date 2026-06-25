# Copyright (c) 2026, AITDL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SMRITITrialSettings(Document):
    """
    Singleton settings DocType for SMRITI Trial Operations.

    Configuration is read by scheduler jobs at runtime — no bench restart needed
    after changes. Use frappe.get_single('SMRITI Trial Settings') to read.
    """

    def get_reminder_days(self):
        """Parse reminder_days string (e.g. '7,3,1') → sorted list of ints desc."""
        raw = (self.reminder_days or '7,3,1').strip()
        try:
            days = sorted({int(d.strip()) for d in raw.split(',') if d.strip()}, reverse=True)
        except ValueError:
            days = [7, 3, 1]
        return days

    def get_stale_hours(self):
        return int(self.stale_provisioning_hours or 24)
