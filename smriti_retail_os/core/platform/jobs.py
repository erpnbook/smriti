# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/platform/jobs.py
# @desc:    SMRITI Platform Background Jobs Adapter.
#           Wraps frappe.enqueue behind a clean SMRITI API.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# Usage:
#   from smriti_retail_os.core.platform import jobs
#
#   jobs.enqueue("smriti_retail_os.services.sync.run_full_sync", company="SM")
#   jobs.enqueue_in(300, "smriti_retail_os.services.report.build_daily_summary")
#

_DEFAULT_QUEUE = "default"
_LONG_QUEUE = "long"
_SHORT_QUEUE = "short"


def enqueue(method: str, queue: str = _DEFAULT_QUEUE,
            timeout: int = 300, now: bool = False, **kwargs):
    """
    Enqueue a background job.

    Args:
        method (str): Dotted Python path to the function, e.g.
                      "smriti_retail_os.services.sync.run_sync"
        queue (str): Queue name — "default", "short", or "long"
        timeout (int): Job timeout in seconds (default: 300)
        now (bool): If True, run synchronously (for testing)
        **kwargs: Arguments forwarded to the target function

    Example:
        jobs.enqueue(
            "smriti_retail_os.services.psv.rebuild_stock_visibility",
            queue="long",
            timeout=600,
            company="SM",
            warehouse="Stores - SM"
        )
    """
    import frappe
    frappe.enqueue(method, queue=queue, timeout=timeout, now=now, **kwargs)


def enqueue_in(seconds: int, method: str, queue: str = _DEFAULT_QUEUE, **kwargs):
    """
    Enqueue a background job to run after a delay.

    Args:
        seconds (int): Delay in seconds before the job starts
        method (str): Dotted Python path to the function
        queue (str): Queue name
        **kwargs: Arguments forwarded to the target function

    Example:
        jobs.enqueue_in(60, "smriti_retail_os.services.alert.send_shift_reminder",
                        shift_id="SHIFT-001")
    """
    import frappe
    frappe.enqueue(method, queue=queue, enqueue_after_commit=False,
                   at_front=False, **kwargs)


def enqueue_doc(model_name: str, name: str, method_name: str,
                queue: str = _DEFAULT_QUEUE, **kwargs):
    """
    Enqueue a method call on a specific document.

    Args:
        model_name (str): SMRITI model name (will be resolved to DocType)
        name (str): Document name
        method_name (str): Method name to call on the document
        queue (str): Queue name
        **kwargs: Extra arguments

    Example:
        jobs.enqueue_doc("Purchase", "PO-2026-00001", "submit", queue="default")
    """
    import frappe
    from smriti_retail_os.core.platform.registry import resolve
    frappe.enqueue_doc(
        resolve(model_name), name, method_name,
        queue=queue, **kwargs
    )
