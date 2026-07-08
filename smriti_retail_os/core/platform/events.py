# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/platform/events.py
# @desc:    SMRITI Platform Realtime Events Adapter.
#           Wraps frappe.publish_realtime behind a clean SMRITI API.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# Usage:
#   from smriti_retail_os.core.platform import events
#
#   events.publish("stock_update", {"item": "ITEM-001", "qty": 50})
#   events.publish_to_user("sync_complete", data, user="cashier@store.com")
#   events.publish_to_room("shift_alert", data, room="shift-001")
#


def publish(event: str, message: dict, room: str = None):
    """
    Publish a realtime event to all connected clients (or a specific room).

    Args:
        event (str): Event name (use SMRITI namespaced names, e.g. "smriti:stock_update")
        message (dict): Payload to send to the client
        room (str): Optional Socket.IO room to target

    Example:
        events.publish("smriti:stock_update", {
            "item_code": "ITEM-001",
            "available_qty": 48,
            "warehouse": "Stores - SM"
        })
    """
    import frappe
    frappe.publish_realtime(event=event, message=message, room=room)


def publish_to_user(event: str, message: dict, user: str):
    """
    Publish a realtime event to a specific user only.

    Args:
        event (str): Event name
        message (dict): Payload
        user (str): Target user email

    Example:
        events.publish_to_user("smriti:shift_alert", {
            "message": "Your shift is about to end in 30 minutes."
        }, user="cashier@store.com")
    """
    import frappe
    frappe.publish_realtime(event=event, message=message, user=user)


def publish_to_room(event: str, message: dict, room: str):
    """
    Publish a realtime event to a named Socket.IO room.

    Args:
        event (str): Event name
        message (dict): Payload
        room (str): Room name (e.g. a shift ID, a store code)

    Example:
        events.publish_to_room("smriti:pos_update", data, room="SHIFT-2026-001")
    """
    import frappe
    frappe.publish_realtime(event=event, message=message, room=room)


def publish_to_doctype(event: str, message: dict, doctype: str, docname: str):
    """
    Publish a realtime event scoped to a specific document (Frappe's doc-level realtime).

    Args:
        event (str): Event name
        message (dict): Payload
        doctype (str): Raw platform DocType name (used for Frappe's room routing)
        docname (str): Document name

    Example:
        events.publish_to_doctype("smriti:po_status_change", data,
            doctype="Purchase Order", docname="PO-2026-00001")
    """
    import frappe
    frappe.publish_realtime(
        event=event,
        message=message,
        doctype=doctype,
        docname=docname
    )
