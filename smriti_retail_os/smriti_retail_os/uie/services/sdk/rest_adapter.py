# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import requests
import json
import frappe
from smriti_retail_os.smriti_retail_os.uie.services.sdk.base_adapter import BaseAdapter

class RestAdapter(BaseAdapter):
	"""HTTP/REST adapter implementing UIE BaseAdapter."""
	
	def authenticate(self, credential):
		"""Resolves and injects authentication headers from UIE credential vault."""
		headers = {}
		if not credential:
			return headers
			
		cred_doc = frappe.get_doc("SMRITI UIE Credential", credential)
		if cred_doc.type == "API Key" and cred_doc.api_key_header:
			headers[cred_doc.api_key_header] = cred_doc.get_password("api_key_value")
		elif cred_doc.type == "Bearer Token" and cred_doc.token:
			headers["Authorization"] = f"Bearer {cred_doc.get_password('token')}"
		elif cred_doc.type == "Username Password":
			import base64
			auth_str = f"{cred_doc.username}:{cred_doc.get_password('password')}"
			encoded = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
			headers["Authorization"] = f"Basic {encoded}"
			
		return headers

	def send(self, queue_item, integration, endpoint):
		"""Sends REST request to the target URL."""
		endpoint_doc = frappe.get_doc("SMRITI UIE Endpoint", endpoint)
		
		# Resolve headers
		headers = {
			"Content-Type": endpoint_doc.content_type or "application/json"
		}
		
		# Load endpoint static headers
		if endpoint_doc.headers:
			try:
				static_headers = json.loads(endpoint_doc.headers)
				headers.update(static_headers)
			except Exception:
				pass
				
		# Ingest Auth headers
		if integration.credential:
			auth_headers = self.authenticate(integration.credential)
			headers.update(auth_headers)
			
		timeout = endpoint_doc.timeout or integration.timeout or 30
		url = endpoint_doc.url
		method = endpoint_doc.method or "POST"
		payload_str = queue_item.payload or ""
		
		try:
			res = requests.request(
				method=method,
				url=url,
				headers=headers,
				data=payload_str,
				timeout=timeout
			)
			success = (200 <= res.status_code < 300)
			return success, res.status_code, res.text
		except Exception as e:
			return False, 500, str(e)
