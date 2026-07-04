# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/print_framework/queue/print_queue.py
# @desc:    Job queue lifecycle manager.
# @author:  Jawahar R. Mallah
#

import frappe
from smriti_retail_os.print_framework.repository.print_job_repository import PrintJobRepository

class ModuleType:
    BARCODE = "Barcode Studio"
    LABEL = "Label Studio"
    POS = "POS Billing"

class PrintQueue:
    """
    Manages enqueuing, tracking, retrying, and state transit for print jobs.
    Uses PrintJobRepository to perform persistence tasks.
    """

    @staticmethod
    def enqueue(module_name, printer_id, payload_hash, payload_file_url):
        """Creates a new pending print job in the audit database log."""
        job = PrintJobRepository.new_doc("SMRITI Print Job")
        job.job_id = "JOB-" + frappe.generate_hash(length=12)
        job.module = module_name
        job.printer = printer_id
        job.payload_hash = payload_hash
        job.payload_file = payload_file_url
        job.status = "Pending"
        job.retry_count = 0
        job.insert(ignore_permissions=True)
        PrintJobRepository.commit()
        return job.name

    @staticmethod
    def mark_completed(job_id):
        """Marks print job as completed successfully."""
        PrintJobRepository.set_value("SMRITI Print Job", job_id, "status", "Completed")
        PrintJobRepository.commit()

    @staticmethod
    def mark_failed(job_id, error_msg):
        """Marks print job as failed and records the error details."""
        PrintJobRepository.set_value("SMRITI Print Job", job_id, "status", "Failed")
        PrintJobRepository.set_value("SMRITI Print Job", job_id, "error_message", error_msg)
        PrintJobRepository.commit()

    @staticmethod
    def increment_retry(job_id, max_retries=3):
        """Increments retry counter and resets status if under maximum retries."""
        job = PrintJobRepository.get_doc("SMRITI Print Job", job_id)
        new_retry = (job.retry_count or 0) + 1
        if new_retry >= max_retries:
            job.status = "Failed"
            job.error_message = "Max retries exceeded."
        else:
            job.status = "Pending"
        job.retry_count = new_retry
        job.save(ignore_permissions=True)
        PrintJobRepository.commit()
