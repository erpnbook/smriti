# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/integration/providers/accounting/busy/busy_adapter.py
# @desc:    Busy ERP Integration Adapter Class - SMRITI Connect Plugin Shell.
# @author:  Jawahar R. Mallah
#

from smriti_retail_os.integration.core.base_adapter import BaseIntegrationAdapter

class BusyAdapter(BaseIntegrationAdapter):
    """
    Busy ERP integration adapter shell.
    To be fully implemented in a future sprint.
    """

    def get_adapter_id(self) -> str:
        return "accounting.busy"

    def connect(self) -> bool:
        return False

    def disconnect(self) -> bool:
        return True

    def health_check(self) -> dict:
        return {"status": "Unhealthy", "latency_ms": 0, "error": "Busy ERP Adapter is not configured."}

    def handle_event(self, event_type: str, payload: dict) -> dict:
        return {"success": False, "error": "Busy ERP Adapter is not implemented yet."}
