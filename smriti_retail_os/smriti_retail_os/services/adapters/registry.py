# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

INTEGRATION_REGISTRY = {
	"TallyPrime": {
		"class_path": "smriti_retail_os.smriti_retail_os.services.adapters.tally_adapter.TallyAdapter",
		"version": "1.0",
		"label": "TallyPrime Integration",
		"supports_accounting": True,
		"supports_inventory": True,
		"supports_masters": True,
		"supports_delta": True,
		"supports_audit": True
	}
}

def get_registered_adapters():
	"""Returns the registry metadata of all registered adapters."""
	return INTEGRATION_REGISTRY
