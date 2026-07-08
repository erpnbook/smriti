# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/utils/ensure_doctype_schema.py
# @description: Reusable helper utility to ensure custom DocType metadata and database
#               tables are dynamically provisioned in isolated test databases.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-25
# @version: 1.8.6
# @sprint: 3C — Trial Health Snapshot
# @authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
#

import frappe
from smriti_retail_os import smriti

def ensure_doctype_schema(doctype_name, creator_fn=None):
    """
    Ensures that a custom DocType's metadata and its corresponding physical database
    table exist in the active database.
    
    If the metadata does not exist, it runs the `creator_fn` callback (if provided),
    or attempts to resolve the creation function from the setup module automatically.
    
    If the metadata exists but the physical database table is missing, it runs
    `frappe.db.updatedb` to create and synchronize the table.
    """
    if not smriti.db.exists("DocType", doctype_name):
        if creator_fn:
            creator_fn()
            smriti.db.commit()
        else:
            # Try to resolve creator dynamically from setup module by convention:
            # e.g., "SMRITI Trial Health Snapshot" -> "create_smriti_trial_health_snapshot_doctype"
            import smriti_retail_os.setup as setup_module
            words = doctype_name.lower().split()
            func_name = f"create_{'_'.join(words)}_doctype"
            
            if hasattr(setup_module, func_name):
                creator_func = getattr(setup_module, func_name)
                creator_func()
                smriti.db.commit()
            else:
                raise ValueError(
                    f"DocType '{doctype_name}' metadata does not exist, and no creator "
                    f"callback was provided. Dynamic lookup for '{func_name}' in setup.py failed."
                )
    elif not frappe.db.table_exists(doctype_name):
        frappe.db.updatedb(doctype_name)
        smriti.db.commit()
