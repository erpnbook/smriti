# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/print_framework/connections/base_connection.py
# @desc:    Abstract Base Connection interface.
# @author:  Jawahar R. Mallah
#

class BaseConnection:
    """
    Abstract Base Class for all printer connection adapters.
    Defines the unified connection interface.
    """
    def __init__(self, connection_params=None):
        self.params = connection_params or {}

    def connect(self) -> bool:
        """Establish connection to printer device. Returns True if successful."""
        raise NotImplementedError("Connection adapters must implement connect().")

    def disconnect(self) -> None:
        """Close connection to printer device."""
        raise NotImplementedError("Connection adapters must implement disconnect().")

    def send_stream(self, data: bytes) -> bool:
        """Send raw print commands (e.g. ZPL/TSPL) to the device."""
        raise NotImplementedError("Connection adapters must implement send_stream().")
