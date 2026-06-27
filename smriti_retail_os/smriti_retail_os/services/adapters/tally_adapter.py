# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import frappe
from frappe import _
import time
import datetime
from smriti_retail_os.smriti_retail_os.services.adapters.base_adapter import BaseAdapter
from smriti_retail_os.smriti_retail_os.services.adapters.tally_transport import TallyTransport
from smriti_retail_os.smriti_retail_os.services.adapters.tally_builders import accounting_builder

class TallyAdapter(BaseAdapter):
	"""TallyPrime implementation subclassing BaseAdapter for SCF."""
	
	def __init__(self):
		super(TallyAdapter, self).__init__(name="TallyPrime")

	def get_connection_status(self, settings):
		"""Verifies connection with TallyPrime by doing a simple Company verification."""
		company_name = settings.tally_company or "SMRITI Company"
		test_payload = (
			"<ENVELOPE>"
			"  <HEADER>"
			"    <TALLYREQUEST>Export Data</TALLYREQUEST>"
			"  </HEADER>"
			"  <BODY>"
			"    <EXPORTDATA>"
			"      <REQUESTDESC>"
			"        <REPORTNAME>List of Companies</REPORTNAME>"
			"      </REQUESTDESC>"
			"    </EXPORTDATA>"
			"  </BODY>"
			"</ENVELOPE>"
		)
		status_code, res_text = TallyTransport.send_request(settings.tally_url, test_payload, timeout=5)
		connected = (status_code == 200)
		return {
			"connected": connected,
			"company_name": company_name,
			"last_sync_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if connected else None,
			"message": _("Connected to TallyPrime successfully.") if connected else _("Cannot connect to TallyPrime at {0}.").format(settings.tally_url)
		}

	def create_ledger_in_tally(self, ledger_name, parent_group="Sundry Debtors", settings=None):
		"""Helper to create ledger in Tally if missing."""
		if not settings:
			settings = frappe.get_doc("SMRITI Tally Settings")
		xml_lines = [
			"<ENVELOPE>",
			"  <HEADER>",
			"    <TALLYREQUEST>Import Data</TALLYREQUEST>",
			"  </HEADER>",
			"  <BODY>",
			"    <IMPORTDATA>",
			"      <REQUESTDESC>",
			"        <REPORTNAME>All Masters</REPORTNAME>",
			"        <STATICVARIABLES>",
			f"          <SVCOMPANYNAME>{settings.tally_company or 'SMRITI Company'}</SVCOMPANYNAME>",
			"        </STATICVARIABLES>",
			"      </REQUESTDESC>",
			"      <REQUESTDATA>",
			'        <TALLYMESSAGE xmlns:UDF="TallyUDF">',
			f'          <LEDGER NAME="{ledger_name}" ACTION="Create">',
			"            <NAME.LIST>",
			f"              <NAME>{ledger_name}</NAME>",
			"            </NAME.LIST>",
			f"            <PARENT>{parent_group}</PARENT>",
			"          </LEDGER>",
			"        </TALLYMESSAGE>",
			"      </REQUESTDATA>",
			"    </IMPORTDATA>",
			"  </BODY>",
			"</ENVELOPE>"
		]
		xml_payload = "\r\n".join(xml_lines)
		status_code, response_text = TallyTransport.send_request(settings.tally_url, xml_payload)
		return (status_code == 200 and "LINEERROR" not in response_text)

	def sync_accounting(self, vouchers, settings, force=False):
		"""Sends accounting vouchers to TallyPrime."""
		started_at = datetime.datetime.now().isoformat()
		start_time = time.time()
		
		processed = 0
		failed = 0
		skipped = 0
		errors = []
		warnings = []

		for v in vouchers:
			doctype = v.get("doctype")
			doc_name = v.get("name")
			
			# Check zero-value vouchers
			doc = frappe.get_doc(doctype, doc_name)
			total_amt = float(doc.grand_total if doctype != "Payment Entry" else doc.paid_amount)
			if total_amt == 0.0:
				skipped += 1
				warnings.append(f"Skipped zero-value document {doc_name}")
				# Write sync log
				self._log_sync_status(doc, "Success (Skipped: Zero-value voucher)", "Zero amount voucher skipped.", started_at)
				continue

			# Auto-create party ledger if checked
			if settings.auto_create_ledgers:
				party_ledger = doc.get("customer") or doc.get("supplier") or doc.get("party")
				if party_ledger:
					parent_grp = "Sundry Debtors" if doctype in ("Sales Invoice", "Credit Note") or (doctype == "Payment Entry" and doc.party_type == "Customer") else "Sundry Creditors"
					try:
						self.create_ledger_in_tally(party_ledger, parent_grp, settings)
					except Exception as ex:
						warnings.append(f"Ledger auto-creation failed for {party_ledger}: {str(ex)}")

			# Generate XML
			try:
				xml_payload = accounting_builder.generate_voucher_xml(doctype, doc_name, settings)
				status_code, res_text = TallyTransport.send_request(settings.tally_url, xml_payload)
				if status_code == 200 and "LINEERROR" not in res_text:
					processed += 1
					self._log_sync_status(doc, "Success", res_text, started_at)
				else:
					failed += 1
					err_msg = res_text if status_code == 200 else f"HTTP error status: {status_code}"
					errors.append(f"Document {doc_name} failed: {err_msg}")
					self._log_sync_status(doc, "Failed", err_msg, started_at)
			except Exception as e:
				failed += 1
				errors.append(f"Document {doc_name} exception: {str(e)}")
				self._log_sync_status(doc, "Failed", str(e), started_at)

		finished_at = datetime.datetime.now().isoformat()
		duration_ms = int((time.time() - start_time) * 1000)

		return {
			"success": (failed == 0),
			"processed": processed,
			"failed": failed,
			"skipped": skipped,
			"warnings": warnings,
			"errors": errors,
			"duration_ms": duration_ms,
			"job_id": frappe.generate_hash(),
			"adapter": self.name,
			"started_at": started_at,
			"finished_at": finished_at,
			"metrics": {
				"accounting": processed,
				"inventory": 0,
				"masters": 0
			}
		}

	def sync_inventory(self, items, settings, force=False):
		"""Placeholder for inventory sync."""
		# Standard response Contract
		now = datetime.datetime.now().isoformat()
		return {
			"success": True,
			"processed": 0,
			"failed": 0,
			"skipped": 0,
			"warnings": [],
			"errors": [],
			"duration_ms": 0,
			"job_id": frappe.generate_hash(),
			"adapter": self.name,
			"started_at": now,
			"finished_at": now,
			"metrics": {
				"accounting": 0,
				"inventory": 0,
				"masters": 0
			}
		}

	def sync_masters(self, masters, settings, force=False):
		"""Placeholder for master sync."""
		now = datetime.datetime.now().isoformat()
		return {
			"success": True,
			"processed": 0,
			"failed": 0,
			"skipped": 0,
			"warnings": [],
			"errors": [],
			"duration_ms": 0,
			"job_id": frappe.generate_hash(),
			"adapter": self.name,
			"started_at": now,
			"finished_at": now,
			"metrics": {
				"accounting": 0,
				"inventory": 0,
				"masters": 0
			}
		}

	def audit_sync(self, from_date, to_date, voucher_type):
		"""Placeholder for audit status logic."""
		return {
			"total": 0,
			"synced": 0,
			"missing": 0,
			"missing_list": []
		}

	def _log_sync_status(self, doc, status, response, started_at):
		"""Helper to log execution status to SMRITI Tally Sync Log."""
		log = frappe.get_doc({
			"doctype": "SMRITI Tally Sync Log",
			"posting_date": doc.posting_date,
			"voucher_type": "Sales" if doc.doctype == "Sales Invoice" else ("Purchase" if doc.doctype == "Purchase Invoice" else doc.doctype),
			"reference_name": doc.name,
			"status": status,
			"response": response[:1000]
		})
		log.insert(ignore_permissions=True)
		frappe.db.commit()
