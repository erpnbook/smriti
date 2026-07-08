# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import requests
import frappe
from smriti_retail_os import smriti

class TallyTransport:
	"""Handles SOAP/HTTP XML request transmission to TallyPrime."""
	
	@staticmethod
	def send_request(url, xml_payload, timeout=10):
		"""Transmits XML payload to Tally XML port and returns (status_code, response_text)."""
		headers = {
			"Content-Type": "text/xml; charset=utf-8",
			"charset": "utf-8"
		}
		try:
			res = requests.post(url, data=xml_payload.encode("utf-8"), headers=headers, timeout=timeout)
			return res.status_code, res.text
		except Exception as e:
			smriti.errors.log_error(f"Tally transport request failed: {str(e)}", "Tally Transport Error")
			return 500, str(e)
