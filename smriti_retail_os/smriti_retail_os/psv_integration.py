# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_integration.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_integration.py
#
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                   DEPRECATED — DO NOT USE THIS FILE                        ║
# ║                                                                            ║
# ║  This file was the original stub placeholder for PSV hook handlers.        ║
# ║  It has been SUPERSEDED by the canonical top-level module:                 ║
# ║                                                                            ║
# ║      smriti_retail_os.psv_integration                                      ║
# ║      (d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/          ║
# ║       psv_integration.py)                                                  ║
# ║                                                                            ║
# ║  All hooks.py references now use the top-level path (PSV-F1-FIX).         ║
# ║  This file will be removed in the next major release.                      ║
# ║                                                                            ║
# ║  If you reached this file by following a hook reference,                   ║
# ║  the hooks.py file has NOT been updated yet. Update it to use:             ║
# ║      smriti_retail_os.psv_integration.<handler_name>                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# @date: 2026-06-11 (deprecated)
# @version: 1.0.0 → DEPRECATED
#

import frappe

# Re-export from the canonical top-level module so any lingering import still works.
# The real implementations live in smriti_retail_os.psv_integration.
try:
    from smriti_retail_os.psv_integration import (
        handle_delivery_note_submit,
        handle_delivery_note_cancel,
        handle_sales_return_submit,
        handle_sales_return_cancel,
    )
    frappe.logger().warning(
        "SMRITI DEPRECATION: smriti_retail_os.smriti_retail_os.psv_integration is deprecated. "
        "Update all references to smriti_retail_os.psv_integration (top-level). "
        "This nested module will be removed in the next major release."
    )
except ImportError:
    # Fallback: silent no-ops if top-level module is missing (should never happen)
    def handle_delivery_note_submit(doc, method=None): pass  # noqa: E704
    def handle_delivery_note_cancel(doc, method=None): pass  # noqa: E704
    def handle_sales_return_submit(doc, method=None): pass   # noqa: E704
    def handle_sales_return_cancel(doc, method=None): pass   # noqa: E704
