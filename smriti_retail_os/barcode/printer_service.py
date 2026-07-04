# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/barcode/printer_service.py
# @description: Printer communication service for SMRITI Label Studio.
#               Handles LAN/TCP printing, connection testing, test labels,
#               and the field mapping reference API.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
#

import socket
import datetime
import frappe
from frappe.utils import flt, cint
from frappe import _
from smriti_retail_os.barcode.token_registry import get_registry_for_api


# ---------------------------------------------------------------------------
# CORE SOCKET PRIMITIVE
# ---------------------------------------------------------------------------

def _send_to_printer_sync(payload, printer_ip, printer_port=9100):
    """
    Sends raw bytes to a LAN/TCP label printer.
    Used internally by send_to_network_printer and batch_service._process_print_job.
    """
    port = cint(printer_port) or 9100
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((printer_ip.strip(), port))
            s.sendall(payload.encode("utf-8", errors="replace"))
    except socket.timeout:
        frappe.throw(_("Connection timed out. Verify printer IP {0} and port {1} are reachable.").format(printer_ip, port))
    except ConnectionRefusedError:
        frappe.throw(_("Printer at {0}:{1} refused the connection. Ensure the printer is online and raw TCP port is enabled.").format(printer_ip, port))
    except Exception as e:
        frappe.throw(_("Printer error: {0}").format(str(e)))


# ---------------------------------------------------------------------------
# PUBLIC API FUNCTIONS
# ---------------------------------------------------------------------------

def send_to_network_printer(items, template_name=None, printer_ip=None, printer_port=9100):
    """
    Generates PRN content and streams it directly to a network label printer
    via a raw TCP/IP socket connection (LAN/Wi-Fi).

    Args:
        items (str):         JSON string of items (same format as generate_prn)
        template_name (str): Name of SMRITI Print Template to use
        printer_ip (str):    IP address of the label printer on the network
        printer_port (int):  TCP port — default 9100

    Returns:
        dict: { success: bool, message: str, labels_sent: int }
    """
    if not printer_ip:
        frappe.throw(_("Printer IP address is required for LAN printing."))

    from smriti_retail_os.barcode.prn_generator import generate_prn
    res = generate_prn(items, template_name=template_name)
    prn_data = res.get("prn") if isinstance(res, dict) else res
    if not prn_data:
        frappe.throw(_("No PRN data generated. Check items and template."))

    port = cint(printer_port) or 9100
    labels_sent = prn_data.count("^XA") + prn_data.count("PRINT 1,1")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((printer_ip.strip(), port))
            s.sendall(prn_data.encode("utf-8", errors="replace"))

        return {
            "success": True,
            "message": _(
                "Successfully sent {0} label(s) to printer at {1}:{2}"
            ).format(labels_sent, printer_ip, port),
            "labels_sent": labels_sent
        }

    except socket.timeout:
        frappe.throw(
            _("Connection timed out. Verify printer IP {0} and port {1} are reachable.").format(printer_ip, port)
        )
    except ConnectionRefusedError:
        frappe.throw(
            _("Printer at {0}:{1} refused the connection. Ensure the printer is online and raw TCP port is enabled.").format(printer_ip, port)
        )
    except Exception as e:
        frappe.throw(_("Printer error: {0}").format(str(e)))


def get_field_mapping_reference():
    """
    Returns a structured reference of Item Master fields and their
    corresponding PRN template placeholder tokens.
    Sourced from the central token_registry — single source of truth.
    """
    return get_registry_for_api()


def get_recent_transactions(doctype, limit=15):
    """
    Fetches the latest records of type Purchase Receipt or Stock Entry.
    """
    if doctype not in ["Purchase Receipt", "Stock Entry"]:
        return []

    if doctype == "Purchase Receipt":
        query_res = frappe.db.sql(
            """
            SELECT
                pr.name,
                pr.posting_date,
                pr.supplier_name as extra_info,
                (SELECT COUNT(*) FROM `tabPurchase Receipt Item` pri WHERE pri.parent = pr.name) as items_count
            FROM `tabPurchase Receipt` pr
            ORDER BY pr.creation DESC
            LIMIT %s
            """,
            (cint(limit) or 15,),
            as_dict=True
        )
    else:
        query_res = frappe.db.sql(
            """
            SELECT
                se.name,
                se.posting_date,
                se.purpose as extra_info,
                (SELECT COUNT(*) FROM `tabStock Entry Detail` sed WHERE sed.parent = se.name) as items_count
            FROM `tabStock Entry` se
            ORDER BY se.creation DESC
            LIMIT %s
            """,
            (cint(limit) or 15,),
            as_dict=True
        )

    for r in query_res:
        if r.posting_date:
            r.posting_date = r.posting_date.strftime("%Y-%m-%d")
    return query_res


def test_printer_connection(printer_ip, printer_port=9100):
    """
    TCP ping/connection test to label printer IP/Port.
    """
    import time
    port = cint(printer_port) or 9100
    start_time = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3.0)
            s.connect((printer_ip.strip(), port))
        elapsed = (time.time() - start_time) * 1000
        return {
            "success": True,
            "latency_ms": round(elapsed, 1),
            "message": f"Connection successful! Response time: {elapsed:.1f} ms"
        }
    except socket.timeout:
        return {"success": False, "latency_ms": None, "message": "Connection timed out. Verify IP and Port."}
    except Exception as e:
        return {"success": False, "latency_ms": None, "message": f"Connection failed: {str(e)}"}


def print_test_label(printer_ip, printer_port=9100, printer_language="ZPL"):
    """
    Sends a test print layout directly to raw printer socket.
    """
    port = cint(printer_port) or 9100
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if printer_language == "TSPL":
        test_code = (
            f"SIZE 50 mm, 25 mm\n"
            f"GAP 3 mm, 0 mm\n"
            f"DIRECTION 1\n"
            f"CLS\n"
            f'TEXT 20,20,"3",0,1,1,"SMRITI TEST"\n'
            f'TEXT 20,60,"2",0,1,1,"IP: {printer_ip}"\n'
            f'TEXT 20,100,"2",0,1,1,"PORT: {printer_port}"\n'
            f'TEXT 20,140,"1",0,1,1,"{now_str}"\n'
            f"PRINT 1,1\n"
        )
    else:
        test_code = (
            f"^XA\n"
            f"^FO40,30^ADN,24,14^FDSMRITI PRINTER TEST^FS\n"
            f"^FO40,70^ADN,18,10^FDPrinter IP: {printer_ip}^FS\n"
            f"^FO40,100^ADN,18,10^FDPort: {printer_port}^FS\n"
            f"^FO40,135^ADN,14,8^FDTime: {now_str}^FS\n"
            f"^XZ\n"
        )

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((printer_ip.strip(), port))
            s.sendall(test_code.encode("utf-8", errors="replace"))
        return {"success": True, "message": "Test label sent successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}
