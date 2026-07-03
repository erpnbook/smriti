# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/integration/core/base_adapter.py
# @desc:    Abstract Base Class defining the lifecycle hooks for SMRITI Connect Adapters.
# @author:  Jawahar R. Mallah
#

class BaseIntegrationAdapter:
    """
    Abstract interface that all SMRITI Connect Integration Adapters must implement.
    
    Provides lifecycle hooks for connection, health checks, and transaction routing.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}

    def get_adapter_id(self) -> str:
        """
        Returns the unique identifier of this adapter.
        Must match the provider_id in 'SMRITI Integration Provider' DocType.
        """
        raise NotImplementedError("Subclasses must implement get_adapter_id")

    def connect(self) -> bool:
        """
        Establishes a connection to the external destination integration service.
        Returns: True if connection is successfully established/active, else False.
        """
        raise NotImplementedError("Subclasses must implement connect")

    def disconnect(self) -> bool:
        """
        Safely tears down and closes connections.
        Returns: True if cleanly closed.
        """
        raise NotImplementedError("Subclasses must implement disconnect")

    def health_check(self) -> dict:
        """
        Performs connectivity diagnostic checking.
        Returns:
            dict with keys:
                - status: 'Healthy' or 'Unhealthy'
                - latency_ms: int representing response duration
                - error: str message if status is Unhealthy
        """
        raise NotImplementedError("Subclasses must implement health_check")

    def handle_event(self, event_type: str, payload: dict) -> dict:
        """
        Standard routing entrypoint to process an integration event.
        
        Args:
            event_type: String namespace (e.g. 'SALE_CREATED')
            payload: Dict containing validated business data
            
        Returns:
            dict containing outcome status:
                - success: bool
                - transaction_id: str identifier from target system (if success)
                - error: str message if failed
        """
        raise NotImplementedError("Subclasses must implement handle_event")
