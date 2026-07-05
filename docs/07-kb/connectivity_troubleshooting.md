---
Document ID: "KB-032"
Title: "Connectivity & UIE Troubleshooting Guide"
Owner: "Support Team"
Audience: "Support Engineer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-28"
Last Reviewed: "2026-06-28"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# Connectivity & UIE Troubleshooting Guide

## Author Profile (Document Start)

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

---

## 1. Troubleshooting Sync Queue Issues

When transactions fail to reach external endpoints (such as TallyPrime, Busy, or Mall APIs), support engineers should execute the following verification steps:

### 1.1 Checking Sync Logs (Audit Panel)
Verify transmission failures inside `SMRITI UIE Sync Log` or under the **Audit** panel:
1. Search for records matching the Document ID or transaction hash.
2. Inspect the **HTTP Status** and **Response Content** columns.
3. Review the execution duration (`duration_ms`) to identify potential endpoint timeouts.

### 1.2 Inspecting the Dead-Letter Queue (Jobs Panel)
A transaction transitions to **Dead-Letter** state after 5 failed retries:
1. Navigate to the **Jobs** tab inside the UIE Integration Center (`/smriti-uie`).
2. Locate the item in the `SMRITI UIE Sync Queue` list.
3. Read the last error message from the log trail.
4. To retry a DLQ item after fixing the connection, reset its status to `Pending` and clear the `retry_count` back to `0`.

---

## 2. Legacy Route Redirect Verification

To maintain backward compatibility, a redirection handler is installed on the legacy route.
- If a user accesses `/smriti-tally`, the system logs a deprecation warning:
  ```text
  [2026-06-28 04:00:00] [WARNING] Accessing deprecated route /smriti-tally. Redirecting to /smriti-uie.
  ```
- The browser is redirected via an HTTP 302 to `/smriti-uie`.
- If the redirect fails, check that `www/smriti-tally.py` is present and compiles cleanly.

---

## 3. Connector Validation Exceptions

During queue dispatching, the engine validates the connector type against registered adapters.
- **Unsupported Connector Type:** If the connector type is configured incorrectly (e.g. `GraphQL`), the engine raises a validation error:
  ```text
  frappe.exceptions.ValidationError: Unsupported connector type: GraphQL. Supported: REST, SOAP, SFTP, File.
  ```
- **Resolution:** Navigate to the **Connectors** tab, edit the active `SMRITI UIE Integration` connector card, and update the **Connector Type** field to a supported value.

---

## 4. Tally Connection Debugging

### 4.1 Verifying the SOAP Port
Tally Prime operates on a local SOAP port (e.g. `http://localhost:9000`).
* Try executing `curl -X POST http://localhost:9000` from the app server terminal to ensure the port is exposed and receiving requests.

### 4.2 Handling Schema Errors
If Tally throws XML parsing errors (such as missing ledgers):
1. Verify if **Auto-Create Ledgers** is enabled in `SMRITI Tally Settings` under the **Settings** panel.
2. Inspect `Tally.imp` (located at `F:\Tally.ERP9\Tally.imp`) for detailed parser error stacks.

---

## Author Profile (Document End)

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."
> 
> — Jawahar R. Mallah
> Founder & Chief Architect, AITDL
