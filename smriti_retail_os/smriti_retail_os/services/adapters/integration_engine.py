# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import frappe
from frappe import _
from smriti_retail_os.smriti_retail_os.services.adapters.registry import INTEGRATION_REGISTRY

def get_active_adapter_name():
	"""Returns the active adapter name (TallyPrime as default)."""
	return "TallyPrime"

def get_active_adapter():
	"""Loads and instantiates the active adapter dynamically from the registry."""
	name = get_active_adapter_name()
	if name not in INTEGRATION_REGISTRY:
		frappe.throw(_("Adapter '{0}' is not registered in SCF.").format(name))
		
	meta = INTEGRATION_REGISTRY[name]
	class_path = meta["class_path"]
	
	# Split class path to dynamically import
	parts = class_path.split(".")
	module_path = ".".join(parts[:-1])
	class_name = parts[-1]
	
	try:
		module = __import__(module_path, fromlist=[class_name])
		class_obj = getattr(module, class_name)
		return class_obj()
	except Exception as e:
		frappe.throw(_("Failed to load adapter '{0}' from class path '{1}': {2}").format(
			name, class_path, str(e)
		))
