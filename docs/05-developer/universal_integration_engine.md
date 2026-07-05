---
Document ID: "DEV-072"
Title: "SMRITI Universal Integration Engine (UIE) — Developer Reference Spec v1.0"
Owner: "Development Team"
Audience: "Developer"
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

# SMRITI Universal Integration Engine (UIE) — Developer Reference Spec v1.0

## Author Profile (Document Start)

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

---

## 1. UIE Architectural Workflow

The SMRITI Universal Integration Engine (UIE) utilizes a decoupled, asynchronous queue model to dispatch transactional payloads to external systems (such as malls, distributors, or ERPs).

```text
                    Sales Invoice (on_submit/on_cancel)
                                   │
                                   ▼
                    SMRITI UIE Sync Queue (Idempotency Check)
                                   │
                                   ▼
                       Frappe Background Queue
                                   │
                                   ▼
                         UIE Queue Dispatcher
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
                RestAdapter                SFTP / CSV Adapter
                     │                           │
                     ▼                           ▼
             Partner Webhook / API           SFTP Target
```

---

## 2. DocType Definitions

The module operates using five database models:
1. **`SMRITI UIE Integration`:** Links an active connector instance to endpoints and credentials. Contains payload mapping rules and retry parameters.
2. **`SMRITI UIE Endpoint`:** Defines request method (POST, PUT, GET), content type, URL, headers, and request timeouts.
3. **`SMRITI UIE Credential`:** Implements password encryption for Bearer tokens, basic auth, and API keys.
4. **`SMRITI UIE Sync Queue`:** Tracks pending, sending, success, failed, and dead-letter records.
5. **`SMRITI UIE Sync Log`:** Logs all outbound attempts with exact duration in milliseconds, HTTP statuses, and request-response payloads.

---

## 3. Creating Custom Mappings & Adapters

### 3.1 Mapping Rules
Payloads are transformed using JSON mapping declarations. For example:
```json
{
  "bill_no": {"source": "name"},
  "date": {"source": "posting_date"},
  "total": {"source": "grand_total"},
  "currency": {"default": "INR"}
}
```

### 3.2 Adapter SDK
All connectors subclass the abstract `BaseAdapter`:
- `validate(payload, schema)`: Performs schema checks.
- `authenticate(credential)`: Returns authorization header key-value dictionary.
- `send(queue_item, integration, endpoint)`: Transmits payload and returns `(success, http_status, response_content)`.

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
