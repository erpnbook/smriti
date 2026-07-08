# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/integration/core/registry.py
# @desc:    Dynamic Registry Loader for SMRITI Connect Integration Platform.
# @author:  Jawahar R. Mallah
#

import frappe
from smriti_retail_os import smriti
from smriti_retail_os.integration.repository.queue_repository import QueueRepository

class IntegrationRegistry:
    """
    Dynamically loads and instantiates active SMRITI Connect integration adapters
    from the database configuration registry (SMRITI Integration Provider).
    """

    @staticmethod
    def get_active_adapters() -> dict:
        """
        Loads all enabled adapters from SMRITI Integration Provider settings.
        
        Returns:
            dict mapping adapter_id -> Instantiated Adapter Class
        """
        active_adapters = {}
        providers = QueueRepository.get_active_providers()
        
        # Fallback to local reference implementations if DocType isn't populated yet
        if not providers:
            # Safe default registration for reference testing
            providers = [
                {
                    "provider_id": "accounting.tally",
                    "provider_name": "TallyPrime reference integration",
                    "adapter_class": "smriti_retail_os.integration.providers.accounting.tally.tally_adapter.TallyAdapter",
                    "enabled": 1
                }
            ]

        for p in providers:
            provider_id = p.get("provider_id")
            class_path = p.get("adapter_class")
            
            if not class_path:
                continue
                
            try:
                # Dynamically load the class using Frappe's helper
                adapter_class = frappe.get_attr(class_path)
                
                # Fetch adapter-specific config (Tally settings, etc.)
                config = IntegrationRegistry.get_provider_config(provider_id)
                
                # Instantiate adapter with its configuration
                active_adapters[provider_id] = adapter_class(config)
                
            except Exception as e:
                # Log registry failure and auto-update health status to Unhealthy in DB
                error_msg = f"Failed to dynamically import adapter class '{class_path}': {str(e)}"
                smriti.errors.log_error(title=f"SMRITI Connect Registry Error: {provider_id}", message=error_msg)
                QueueRepository.update_provider_health(provider_id, "Unhealthy", 0, error_msg)
                
        return active_adapters

    @staticmethod
    def get_provider_config(provider_id: str) -> dict:
        """
        Extracts configuration settings for a given provider.
        Reuses existing DocType configurations (like smriti_tally_settings) where possible.
        """
        config = {}
        if provider_id == "accounting.tally":
            if smriti.db.exists("DocType", "SMRITI Tally Settings"):
                doc = frappe.get_single("SMRITI Tally Settings")
                config = doc.as_dict()
            elif smriti.db.exists("DocType", "SMRITI Tally Sync Log"): # check fallback settings
                # Default settings fallback if single settings not set
                config = {
                    "tally_url": "http://localhost:9000",
                    "tally_company": "SMRITI Retail Store"
                }
        
        # Add dynamic configuration query for other custom provider configurations
        if not config:
            config = {
                "tally_url": "http://localhost:9000",
                "tally_company": "Default Retail Store"
            }
        return config
