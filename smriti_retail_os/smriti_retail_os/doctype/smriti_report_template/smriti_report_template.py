# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_report_template/smriti_report_template.py
# @description: Document class controller for SMRITI Report Template.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-18
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.model.document import Document

class SMRITIReportTemplate(Document):
    def before_save(self):
        # 1. Deterministic version serialization on modify
        if not self.is_new():
            db_version = frappe.db.get_value("SMRITI Report Template", self.name, "template_version", for_update=True)
            self.template_version = (db_version or 0) + 1
            
            # 2. Audit Trail logging
            db_doc = frappe.get_doc("SMRITI Report Template", self.name)
            before_state = db_doc.as_dict()
            after_state = self.as_dict()
            
            from smriti_retail_os.utils import get_client_ip
            ip_addr = get_client_ip()
                
            company = frappe.defaults.get_user_default("Company") or ""
            
            log_doc = frappe.get_doc({
                "doctype": "SMRITI Audit Event",
                "timestamp": frappe.utils.now_datetime(),
                "user": frappe.session.user,
                "event_type": "REPORT_TEMPLATE_MODIFIED",
                "company": company,
                "ip_address": ip_addr,
                "before_state": frappe.as_json(before_state),
                "after_state": frappe.as_json(after_state)
            })
            log_doc.insert(ignore_permissions=True)
        else:
            self.template_version = 1

