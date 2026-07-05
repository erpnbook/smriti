---
Document ID: "USER-031"
Title: "SMRITI OS UIE Integration Center — User Manual v1.0"
Owner: "Operations Team"
Audience: "End User"
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

# SMRITI OS UIE Integration Center — User Manual v1.0

## Author Profile (Document Start)

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

---

## 1. Introduction & Overview

The **SMRITI Universal Integration Engine (UIE) Integration Center** is the unified control panel for configuring, dispatching, and monitoring outbound integration connections to external systems (such as TallyPrime, Busy, Marg ERP, e-commerce platforms like Shopify, and Mall POS APIs). 

Served directly at the custom route `/smriti-uie`, it replaces all vendor-specific synchronization interfaces with an adapter-driven, event-based orchestration dashboard.

---

## 2. Navigating the Workspace Panels

The console is organized into the following workspace panels:

### 2.1 Dashboard
Provides a graphical view of connectivity health and adapter registry tiles:
- **Total Integrations:** The number of integrations registered.
- **Active Connections:** The number of enabled connectors.
- **Pending Queue:** Transient items waiting to be dispatched.
- **Success Rate:** The average execution success rate percentage.
- **Connector Registry Tiles:** Displays live statuses (Connected, Not Configured, Disabled) for active connectors like TallyPrime and Phoenix Mall.

### 2.2 Connectors
Displays all active connector records (`SMRITI UIE Integration` models) showing the protocol type (SOAP, REST, SFTP, etc.), endpoint addresses, credential profiles, and active status.

### 2.3 Jobs
A business-friendly view of the outbound dispatch queue (`SMRITI UIE Sync Queue`):
- Displays Document ID, Destination Connector, Event Type (Submit/Cancel), Retry Count, and Execution Status.
- Includes a **Payload Preview** action allowing operators to select a document and preview its serialized payload before dispatching.

### 2.4 Mappings
Provides a visual interface to map standard SMRITI database columns to external vendor fields. For example:
- `name` (Invoice ID) $\rightarrow$ `BillNumber`
- `customer` (Customer Name) $\rightarrow$ `PartyName`
- `grand_total` (Grand Total) $\rightarrow$ `Amount`

### 2.5 Credentials
Encrypted Vault configuration (`SMRITI UIE Credential`) mapping Auth Types (Basic, Bearer, API-Key) and credentials parameters per connection.

### 2.6 Monitoring
Tracks detailed, real-time integration statistics:
- **Queue Depth:** Total items currently queued.
- **Average Latency:** Request-response roundtrip latency (ms).
- **Events / Min:** Rate of outbound integration messages.
- **Health Indicators:** Status indicators for Pending, Sending, Retrying, Failed, and Dead Letter categories.

### 2.7 Audit
Accesses detailed sync execution logs (`SMRITI UIE Sync Log`) capturing timestamps, HTTP request/response payloads, HTTP statuses, retry attempt metrics, and correlation IDs for support diagnostics.

### 2.8 Settings
Preserves legacy configuration parameters for the TallyPrime adapter, including URL connections and general ledger/statutory tax account mapping.

---

## 3. Worked Example: Outbound Mall POS Sync

When a Sales Invoice is finalized on the SMRITI POS terminal, the UIE automatically intercepts the submission event.

### 3.1 Source Transaction
- **Document Name:** `SINV-2026-00001`
- **Party Name:** `Walk-in Customer`
- **Grand Total:** `4,500.0`

### 3.2 Dynamic Mapping Rule
```text
SMRITI Field          Target Field
name           -->    BillNumber
customer       -->    PartyName
grand_total    -->    Amount
```

### 3.3 Serialized JSON Payload Output
```json
{
  "BillNumber": "SINV-2026-00001",
  "PartyName": "Walk-in Customer",
  "Amount": 4500.0
}
```

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
