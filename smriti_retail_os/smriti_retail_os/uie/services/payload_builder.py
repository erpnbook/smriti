# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import frappe
import json

def build_payload(doc, integration):
	"""Maps and validates the payload for a given document and integration schema.
	Accepts either a SMRITI UIE Integration document or a dict/Row containing mapping_rules and schema_validator.
	"""
	doc_dict = doc.as_dict()

	# Support both document object and dictionary/Row safely without triggering N+1 database queries
	mapping_rules = integration.get("mapping_rules") if isinstance(integration, dict) else getattr(integration, "mapping_rules", None)
	if mapping_rules:
		try:
			rules = json.loads(mapping_rules)
			payload_dict = {}
			for target_key, rule_config in rules.items():
				if isinstance(rule_config, dict):
					source_field = rule_config.get("source")
					if source_field:
						payload_dict[target_key] = doc_dict.get(source_field)
					else:
						payload_dict[target_key] = rule_config.get("default")
				else:
					# Literal string fallback
					payload_dict[target_key] = doc_dict.get(rule_config, rule_config)
			
			payload_str = json.dumps(payload_dict, default=str)
		except Exception as e:
			frappe.log_error(f"UIE Payload Builder mapping error: {str(e)}", "UIE Mapping Error")
			payload_str = json.dumps(doc_dict, default=str)
	else:
		# Fallback to standard JSON serialization
		payload_str = json.dumps(doc_dict, default=str)

	# Validate against JSON schema if defined
	schema_validator = integration.get("schema_validator") if isinstance(integration, dict) else getattr(integration, "schema_validator", None)
	if schema_validator:
		try:
			schema = json.loads(schema_validator)
			from jsonschema import validate
			validate(instance=json.loads(payload_str), schema=schema)
		except Exception as val_err:
			frappe.throw(f"UIE Payload Validation failed: {str(val_err)}")

	return payload_str
