# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/print_framework/registry/printer_registry.py
# @desc:    Map of configured printers and capability matrices.
# @author:  Jawahar R. Mallah
#

from smriti_retail_os.print_framework.connections.usb_connection import USBConnection
from smriti_retail_os.print_framework.connections.lan_connection import LANConnection
from smriti_retail_os.print_framework.connections.bluetooth_connection import BluetoothConnection
from smriti_retail_os.print_framework.connections.qz_connection import QZConnection

class PrinterRegistry:
    """
    Registry for configured printers, connection bindings, and capability profiles.
    Follows SMRITI Print Framework open-closed design.
    """
    _printers = {}
    _adapters = {
        "USB": USBConnection,
        "LAN": LANConnection,
        "Bluetooth": BluetoothConnection,
        "QZ": QZConnection
    }

    @classmethod
    def register_printer(cls, printer_id, connection_type, connection_params, capabilities=None):
        """Registers a printer with its connection type, parameters, and capabilities."""
        cls._printers[printer_id] = {
            "connection_type": connection_type,
            "params": connection_params or {},
            "capabilities": capabilities or {
                "ZPL": True,
                "TSPL": False,
                "PDF": False,
                "ESC_POS": False,
                "max_width_mm": 100,
                "color_capable": False
            }
        }

    @classmethod
    def get_printer(cls, printer_id):
        """Returns the registration metadata of the specified printer ID."""
        return cls._printers.get(printer_id)

    @classmethod
    def get_adapter_class(cls, connection_type):
        """Returns the Connection Adapter class associated with the connection type."""
        return cls._adapters.get(connection_type)

    @classmethod
    def get_registered_ids(cls):
        """Returns list of registered printer IDs."""
        return list(cls._printers.keys())

    @classmethod
    def clear(cls):
        """Clears the registry metadata (mainly for testing)."""
        cls._printers.clear()
