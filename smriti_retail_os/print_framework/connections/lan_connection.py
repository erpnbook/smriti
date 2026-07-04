# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/print_framework/connections/lan_connection.py
# @desc:    LAN/Socket connection adapter.
# @author:  Jawahar R. Mallah
#

from smriti_retail_os.print_framework.connections.base_connection import BaseConnection
import socket

class SocketDriver:
    """Standard network raw socket communication driver."""
    @staticmethod
    def send_raw_network(ip_address, port, data):
        # Socket raw TCP write (stubbed)
        return True

class LANConnection(BaseConnection):
    """
    Network LAN connection adapter (Socket print over TCP/IP).
    """
    def __init__(self, connection_params=None):
        super().__init__(connection_params)
        self.ip_address = self.params.get("ip_address", "192.168.1.100")
        self.port = int(self.params.get("port", 9100))
        self.driver = SocketDriver()

    def connect(self):
        return True

    def disconnect(self):
        pass

    def send_stream(self, data):
        return self.driver.send_raw_network(self.ip_address, self.port, data)
