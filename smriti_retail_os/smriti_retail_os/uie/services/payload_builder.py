# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import frappe
import json

def build_payload(doc, integration_doc):
	"""Maps and validates the payload for a given document and integration schema."""
	doc_dict = doc.as_dict()

	mapping_rules = integration_doc.mapping_rules
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
	schema_validator = integration_doc.schema_validator
	if schema_validator:
		try:
			schema = json.loads(schema_validator)
			from jsonschema import validate
			validate(instance=json.loads(payload_str), schema=schema)
		except Exception as val_err:
			frappe.throw(f"UIE Payload Validation failed: {str(val_err)}")

	return payload_str
