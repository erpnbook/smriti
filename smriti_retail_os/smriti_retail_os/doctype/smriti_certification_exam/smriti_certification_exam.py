# -*- coding: utf-8 -*-
#
# @file: smriti_certification_exam.py
# @description: Document controller class for SMRITI Certification Exam.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-23
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.model.document import Document

class SMRITICertificationExam(Document):
    def autoname(self):
        # The key is the unique exam_id field
        self.name = self.exam_id
