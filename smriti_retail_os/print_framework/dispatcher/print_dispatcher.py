# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/print_framework/dispatcher/print_dispatcher.py
# @desc:    Print Dispatcher layer.
# @author:  Jawahar R. Mallah
#

from smriti_retail_os.print_framework.registry.printer_registry import PrinterRegistry

class PrintDispatcher:
    """
    Resolves targets from PrinterRegistry and dispatches print streams to adapters.
    """

    @staticmethod
    def dispatch(printer_id, payload_bytes) -> bool:
        """
        Instantiates correct adapter based on printer connection configurations
        and pushes the payload stream.
        """
        printer_meta = PrinterRegistry.get_printer(printer_id)
        if not printer_meta:
            raise ValueError(f"Printer '{printer_id}' is not registered in the SMRITI registry.")

        connection_type = printer_meta["connection_type"]
        params = printer_meta["params"]

        adapter_class = PrinterRegistry.get_adapter_class(connection_type)
        if not adapter_class:
            raise ValueError(f"No connection adapter registered for type '{connection_type}'.")

        # Instantiate adapter
        adapter = adapter_class(params)
        
        # Connect, send, and disconnect
        success = False
        if adapter.connect():
            try:
                success = adapter.send_stream(payload_bytes)
            finally:
                adapter.disconnect()
        return success
