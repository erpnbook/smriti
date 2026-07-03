# SMRITI Connect™ — Integration Platform Architecture

> **Status**: LOCKED — v1.0.0
> **Authority**: Jawahar R. Mallah, Founder & Chief Architect, AITDL
> **Applies to**: All Developers, Contributors, AI Agents, Integration Partners
> **Scope**: SMRITI Connect Framework and Plugin Lifecycle

---

## 1. Platform Philosophy

**SMRITI Connect** is the unified integration platform for SMRITI Retail OS. It handles all outbound and inbound transactions, events, and communications between SMRITI business modules and external applications (accounting engines, notification gateways, e-commerce channels, and AI providers).

Every external integration — whether TallyPrime, WhatsApp, ONDC, Amazon, or OpenAI — must route through SMRITI Connect. SMRITI business modules remain 100% decoupled from external APIs, formats, transport layers, and status checks.

---

## 2. Platform Architecture Model

```
        SMRITI Business Module (e.g. Billing)
                       │
                       ▼
         Business Event (e.g. SALE_CREATED)
                       │
                       ▼
          Integration Policy Engine
  (Checks SMRITI Integration Policy config rules)
                       │
                       ▼
          Event Bus (dispatcher.py)
          (Routes to Sync & Async listeners)
           │                       │
     (Synchronous)            (Asynchronous)
           │                       │
           ▼                       ▼
    Local Listeners     Integration Outbox Queue
  (e.g., Inventory)     (SMRITI Integration Queue)
                                   │
                                   ▼
                       Integration Engine Worker
                       (engine.py - cron execution)
                                   │
                                   ▼
                        Dynamic Provider Registry
                      (Loads class from DocType)
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
            Accounting Plugin            WhatsApp Plugin
                     │                           │
             TallyPrime Adapter            Meta Adapter
```

---

## 3. Core Components

### 3.1 Event Bus (`core/dispatcher.py`)
Decouples producers and consumers.
- Receives events via `dispatch_event(event_type, doc_type, doc_name, payload, priority)`.
- Validates the payload structure against the versioned JSON schema in `SMRITI Event Definition`.
- Routes synchronous events immediately to local execution handlers.
- Routes asynchronous events to the Transactional Outbox Queue.

### 3.2 Integration Policy Engine (`core/policy.py`)
Performs conditional evaluation for all outbound integrations.
- Evaluates rules stored in `SMRITI Integration Policy` DocType before queuing an event.
- Parameters checked: Company, Location/Branch, Active Status, Adapter Target.
- Example Policy: *"If company is India Corp and Location is Warehouse-01, sync Sales Invoices to TallyPrime, but if Location is Warehouse-02, do not sync."*

### 3.3 Transactional Outbox Queue (`core/queue.py`)
Prevents data inconsistencies.
- Event records are inserted into `SMRITI Integration Queue` inside the active MariaDB database transaction of the parent document.
- If the parent document submission fails and database rolls back, the integration event also rolls back.

### 3.4 Dynamic Provider Registry (`core/registry.py`)
Loads adapters dynamically based on database configuration.
- Reads active integration targets from `SMRITI Integration Provider` DocType.
- Instantiates classes on the fly using standard Python module importing.
- Eliminates hardcoded dictionary imports in core code.

---

## 4. Platform DocTypes (Configuration & Queue Models)

All database management uses standard Category C ORM models.

### 4.1 `SMRITI Integration Provider`

Dynamic plugin registry.

| Fieldname | Fieldtype | Label | Options / Values |
|---|---|---|---|
| `provider_id` | Data | Provider ID | Unique key (e.g. `accounting.tally`) |
| `provider_name` | Data | Provider Name | e.g. TallyPrime Integration |
| `provider_type` | Select | Provider Type | `Accounting`, `AI`, `CRM`, `Marketplace`, `Notification` |
| `version` | Data | Version | e.g. `1.0.0` |
| `min_platform_version` | Data | Min Platform Version | Compatibility constraint |
| `status` | Select | Status | `Stable`, `Beta`, `Deprecated` |
| `enabled` | Check | Enabled | True/False toggle |
| `adapter_class` | Data | Adapter Class Path | e.g. `smriti_retail_os.integration.providers.accounting.tally.tally_adapter.TallyAdapter` |
| `health_status` | Select | Health Status | `Healthy`, `Unhealthy` (auto-updated by engine) |
| `last_check` | Datetime | Last Check | Last health check timestamp |

### 4.2 `SMRITI Event Definition`

Schema validation and consumer graph definition.

| Fieldname | Fieldtype | Label | Purpose |
|---|---|---|---|
| `event_name` | Data | Event Name | Unique key (e.g. `SALE_CREATED`) |
| `version` | Int | Version | Schema version tracking |
| `producer` | Data | Producer Module | e.g. `Billing` |
| `consumers` | Small Text | Registered Consumers | Comma-separated list of target adapters |
| `required_fields` | Long Text | Schema Definition | JSON schema containing required keys |

### 4.3 `SMRITI Integration Queue`

Outbox Queue supporting logical partitions.

| Fieldname | Fieldtype | Label | Values / Purpose |
|---|---|---|---|
| `queue_id` | Data | Queue ID | Unique hash |
| `event_type` | Data | Event Type | e.g. `SALE_CREATED` |
| `priority` | Select | Priority | `Critical`, `Normal`, `Low` (Queue partitioning) |
| `adapter_id` | Data | Target Adapter | Mapped to `SMRITI Integration Provider` |
| `payload` | Long Text | Payload JSON | Target-agnostic business parameters |
| `status` | Select | Sync Status | `Pending`, `Success`, `Failed`, `Retrying`, `Dead-Letter` |
| `retry_count` | Int | Retry Count | Increments on failed attempt |
| `last_attempt` | Datetime | Last Attempt | Timestamp |
| `error_details` | Long Text | Error Log | Traceback or HTTP error status |

---

## 5. Plugin Lifecycle (Base Adapter Spec)

All adapters must inherit from `BaseIntegrationAdapter` (`core/base_adapter.py`) and implement these four methods:

```python
class BaseIntegrationAdapter:
    def __init__(self, config: dict):
        self.config = config

    def connect(self) -> bool:
        """Establishes transport connection."""
        pass

    def disconnect(self) -> bool:
        """Closes transport connection."""
        pass

    def health_check(self) -> dict:
        """Runs diagnostics. Returns status, latency_ms, and error."""
        pass

    def handle_event(self, event_type: str, payload: dict) -> dict:
        """Executes transaction export. Returns success, transaction_id, and error."""
        pass
```

---

## 6. SMRITI Connect Admin Console

All integrations are managed through a unified SMRITI Connect panel at `/connect` (template: `smriti-connect.html`):

- **Health Dashboard:** Shows live status, latency metrics, and API health for Tally, WhatsApp, etc.
- **Provider Registry:** Toggle enabled/disabled state for each integration provider.
- **Queue Monitor:** Sort and filter the transactional outbox by priority, status, and target adapter. Trigger manual retries for failed/dead-letter entries.
- **Audit Logs:** Full logging of payloads sent, response times, and transport-level error details.

---

*SMRITI Connect Architecture v1.0.0*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Status: LOCKED*
