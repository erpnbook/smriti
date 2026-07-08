# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/commands.py
# @description: Custom CLI bench commands for SMRITI Retail OS.
# @author: Jawahar R. Mallah
#

import click
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.commands import pass_context

@click.command('smriti-audit-navigation')
@pass_context
def smriti_audit_navigation(context):
    """
    Runs SMRITI Navigation health validator and checks for orphaned overrides or deprecated references.
    """
    site = context.sites[0]
    frappe.init(site)
    frappe.connect()
    
    click.echo("=== SMRITI Navigation Health Validator ===")
    
    # 1. Fetch canonical navigation keys
    from smriti_retail_os.navigation.navigation_service import CANONICAL_NAV
    canonical_ids = set()
    for section in CANONICAL_NAV.get("sections", []):
        canonical_ids.add(section["id"])
        for item in section.get("items", []):
            canonical_ids.add(item["id"])
            
    click.echo(f"Canonical Menu IDs registered: {len(canonical_ids)}")
    
    # 2. Check overrides
    overrides = smriti.db.get_list("SMRITI Navigation Override", fields=["name", "menu_id", "navigation_profile"])
    orphans = []
    for ov in overrides:
        if ov.menu_id not in canonical_ids:
            orphans.append(ov)
            
    if orphans:
        click.secho(f"WARNING: Found {len(orphans)} orphaned overrides referencing non-existent Menu IDs:", fg="yellow")
        for o in orphans:
            click.echo(f"  - Override {o.name} (Menu ID: '{o.menu_id}') under Profile '{o.navigation_profile}'")
    else:
        click.secho("OK: No orphaned overrides found.", fg="green")
        
    # 3. Check duplicate ordering
    profiles = smriti.db.get_list("SMRITI Navigation Profile", fields=["name"])
    for prof in profiles:
        doc = smriti.documents.get("SMRITI Navigation Profile", prof.name)
        orders = doc.get("order_overrides") or []
        seen = {}
        dups = []
        for o in orders:
            key = (o.parent_menu_id, o.display_order)
            if key in seen:
                dups.append(o.menu_id)
            else:
                seen[key] = o.menu_id
        if dups:
            click.secho(f"WARNING: Profile '{prof.name}' has duplicate display order weights for menus: {dups}", fg="yellow")
            
    click.echo("=== Health Validation Complete ===")

commands = [
    smriti_audit_navigation
]
