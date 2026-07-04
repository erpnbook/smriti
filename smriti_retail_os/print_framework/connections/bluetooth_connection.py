# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/print_framework/connections/bluetooth_connection.py
# @desc:    Bluetooth connection adapter.
# @author:  Jawahar R. Mallah
#

from smriti_retail_os.print_framework.connections.base_connection import BaseConnection

class BLEDriver:
    """Mock BLE serial port profile driver wrapper."""
    @staticmethod
    def send_raw_bluetooth(mac_address, data):
        # Bluetooth BLE raw output (stubbed)
        return True

class BluetoothConnection(BaseConnection):
    """
    Bluetooth Serial / BLE connection adapter.
    """
    def __init__(self, connection_params=None):
        super().__init__(connection_params)
        self.mac_address = self.params.get("mac_address", "00:11:22:33:FF:EE")
        self.driver = BLEDriver()

    def connect(self):
        return True

    def disconnect(self):
        pass

    def send_stream(self, data):
        return self.driver.send_raw_bluetooth(self.mac_address, data)
