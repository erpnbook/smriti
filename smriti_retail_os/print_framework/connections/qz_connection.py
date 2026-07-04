# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/print_framework/connections/qz_connection.py
# @desc:    QZ Tray connection adapter.
# @author:  Jawahar R. Mallah
#

from smriti_retail_os.print_framework.connections.base_connection import BaseConnection

class QZWebClientDriver:
    """Mock browser WebSocket bridge connection wrapper for QZ Tray."""
    @staticmethod
    def send_via_websocket(server_host, data):
        # QZ websocket message push (stubbed)
        return True

class QZConnection(BaseConnection):
    """
    QZ Tray WebSocket connection adapter (delegates raw printing to client-side QZ Tray instance).
    """
    def __init__(self, connection_params=None):
        super().__init__(connection_params)
        self.host = self.params.get("host", "localhost")
        self.driver = QZWebClientDriver()

    def connect(self):
        return True

    def disconnect(self):
        pass

    def send_stream(self, data):
        return self.driver.send_via_websocket(self.host, data)
