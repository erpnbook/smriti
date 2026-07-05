# SMRITI Foundation SDK — Coding Standards & Implementation Guidelines

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Date**: 2026-07-05
- **Document Version**: 1.0.0
- **Status**: **APPROVED & LOCKED**
- **Authority**: AITDL / PrathamOne

---

## 1. Directory Structure & Folder Layout

All components created within the SMRITI Foundation SDK must conform to a standardized package structure:

```text
smriti_foundation/
└── smriti_foundation/
    ├── <pillar_name>/               # E.g., experience, policy, lookup, telemetry
    │   ├── __init__.py
    │   ├── api/                     # Whitelisted frontend API endpoints
    │   │   └── <pillar>_api.py
    │   ├── service/                 # Business logic and coordination layer
    │   │   └── <pillar>_service.py
    │   ├── repository/              # Data access interfaces and adapters
    │   │   └── <pillar>_repository.py
    │   └── common/                  # Internally shared helpers or constants
    └── public/
        ├── js/                      # Frontend JS bundles mapped by pillar
        │   └── <pillar_name>/
        └── css/                     # CSS templates mapped by pillar
            └── <pillar_name>/
```

---

## 2. Naming Conventions

### 2.1 Python Naming Rules
* **Interfaces**: Must start with an uppercase `I` followed by CamelCase (e.g., `IErrorWriter`, `ITelemetryDispatcher`).
* **Concrete Classes**: Must use CamelCase representing their specific implementation role (e.g., `IsolatedDbWriter`, `RealtimeTelemetryDispatcher`).
* **Methods & Functions**: Must use snake_case (e.g., `insert_log_transaction_safe`, `capture_context`).
* **Variables**: Must use snake_case.
* **Modules/Files**: Must use snake_case (e.g., `error_repository.py`, `error_service.py`).

### 2.2 JavaScript Naming Rules
* **Global Namespace**: Capitalized `SMRITI` object.
* **Modules/Managers**: CamelCase (e.g., `SMRITI.ui.error.Manager`).
* **Variables & Properties**: snake_case (e.g., `error_payload`, `fallback_ref_id`).
* **Events**: snake_case prefixed with `smriti_` (e.g., `smriti_error_event`).

### 2.3 CSS Naming Rules
* **Tokens**: Must start with `--smriti-` (e.g., `--smriti-color-bg-page`, `--smriti-spacing-md`).
* **Selectors**: Must be prefixed with `smriti-` (e.g., `.smriti-error-container`, `.smriti-action-btn`). Ad-hoc overrides are forbidden.

---

## 3. Dependency Rules & Allowed Imports

### 3.1 Strict Layer Separation
To maintain architectural stability and ensure upgrade-safety, components must adhere to a strict linear dependency hierarchy:

```
UI Components (HTML/JS) ──> Whitelisted APIs ──> Service Controllers ──> Repositories ──> Database Writers
```

* **No Bypass**: A UI file or client-side controller is strictly forbidden from importing or calling database operations directly.
* **No Circular Dependencies**: Services must not import components from dependent business modules (e.g. `smriti_foundation` must never import `smriti_retail_os.procurement`).

### 3.2 Forbidden Imports
To isolate SMRITI from Frappe v16+ runtime modifications:
* **UI Code**: Direct database queries, raw AJAX calls bypassing the SEF boundary manager (`SMRITI.ui.error.Manager.call`), and global namespace overrides are forbidden.
* **Backend Code**: Accessing database pools without going through the repository interface or invoking `frappe.db.commit()` inside transactional workflows is strictly prohibited.

---

## 4. Repository & Service Design Patterns

### 4.1 The Repository Pattern
* **Rule**: All database operations (inserts, updates, deletes, raw SQL) must be encapsulated within a repository class implementing a defined interface.
* **Isolated Transactions**: Any repository responsible for diagnostic or error logging must execute writes using isolated connection instances, protecting the active HTTP request transaction from side-effects or rollbacks.

### 4.2 The Service Layer
* **Rule**: Business logic, workflow rules, validation checks, and telemetry dispatches must be coordinated exclusively within stateless Service classes.
* **Statelessness**: Service classes must not maintain state flags across request lifecycles. They must process parameters explicitly provided by the controller thread.

---

## 5. Event and Plugin Naming Standards

### 5.1 Telemetry Events
* Real-time events and telemetry updates published over Socket.IO or Redis must use the standard naming format:
  `smriti_<event_scope>_event` (e.g., `smriti_error_event`, `smriti_telemetry_event`).

### 5.2 Plugin Architecture
* Any external integration plugin (e.g. WhatsApp, Slack, Teams) must be registered in the `SMRITI Plugin Registry` DocType using a clean kebab-case identifier (e.g., `slack-notification-service`, `whatsapp-crm-gateway`).
* The registry mapping must explicitly specify the `minimum_sdk_version` (e.g. `1.4`) required to prevent runtime crashes.

---

## 6. Performance Benchmarks & Targets

* **Execution Overhead Target**: The combined CPU latency introduced by the SMRITI Experience Framework (context aggregation, structured scrubbing, formatting) must target **under 5ms** per request thread in production environments.
* **Database Connections**: Decoupled connection threads created for writing log data must be closed and returned to the database pool in **under 10ms** to prevent connection starvation.

---

## 7. Deprecation & Backward Compatibility Policy

To prevent breaking dependent applications, the SDK enforces strict backward-compatibility rules:
* **Contract Freeze**: Any method signature exposed by public classes in `experience/`, `policy/`, `telemetry/`, and `configuration/` is frozen.
* **Deprecation Notice**: If a public contract must be replaced, it must be marked with a `@deprecated` annotation. The deprecated signature must remain functional and backward-compatible for a minimum of **two minor versions** before removal in a major release.

---

> "Always decision-ready."
> 
> — Jawahar R. Mallah
> Founder & Chief Architect, AITDL
