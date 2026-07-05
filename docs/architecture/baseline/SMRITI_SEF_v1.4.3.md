# SMRITI Experience Framework (SEF) — Architectural Blueprint & Governance Directive

> **SMRITI Foundation SDK defines stable architectural contracts. Public interfaces are considered versioned contracts and must remain backward compatible. Internal implementations may evolve or be replaced without affecting dependent modules.**

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Date**: 2026-07-05
- **Document Version**: 1.4.3
- **Status**: **ARCHITECTURE BASELINE v1.4 (FINAL LOCKED BASELINE)**
- **Authority**: AITDL / PrathamOne

---

## 1. Executive Summary & Foundation SDK Pillars

The **SMRITI Experience Framework (SEF)** is the core experience engine of SMRITI Retail OS. It replaces native Frappe/ERPNext exception traces, notifications, and interaction flows with a unified, secure, and branded experience layer.

By standardizing these layers, procurement, sales, inventory, CRM, loyalty, analytics, audits, policies, configurations, and integrations can reuse identical foundations.

### 🏛️ The SMRITI Foundation SDK Pillars (15 Core Pillars)

```
SMRITI Foundation SDK
├── Experience Framework (SEF) [This Module]
├── Interaction Framework
├── Smart Lookup Framework
├── Workflow Framework
├── Security Framework
├── Telemetry Framework
├── Notification Framework
├── Formula Framework
├── Pricing Framework
├── Loyalty Framework
├── Analytics Framework
├── Integration Framework
├── Audit Framework
├── Policy Framework
└── Configuration Framework
```

---

## 2. File Organization & Directory Structure

To prioritize experience first, all interface and interaction control files are structured under an `experience/` package rather than a general foundation utility block.

```text
smriti_foundation/
└── smriti_foundation/
    ├── experience/
    │   ├── __init__.py
    │   ├── error/
    │   │   ├── __init__.py
    │   │   ├── error_codes.py          # Dynamic exception definition matrix
    │   │   ├── error_formatter.py      # Output sanitizer (removes SQL/Frappe keywords & sensitive data)
    │   │   ├── error_repository.py     # Decoupled repository for ORM logs (Abstract Interface)
    │   │   ├── error_logger.py         # Transaction-safe isolated database connection writer (Concrete Adapter)
    │   │   └── error_service.py        # Central Orchestrator (Capture -> Format -> Log -> Telemetry)
    │   ├── dialogs/
    │   │   ├── __init__.py             # Unified dialog & modal control engine
    │   ├── notifications/
    │   │   ├── __init__.py             # Pluggable & verified notification dispatch gateway
    │   ├── toast/
    │   │   ├── __init__.py             # Toast alert templates & dispatchers
    │   ├── loading/
    │   │   ├── __init__.py             # Spinner, Progress, and micro-animation controllers
    │   ├── sidepanel/
    │   │   ├── __init__.py             # Sliding drawer interface controller
    │   ├── feedback/
    │   │   ├── __init__.py             # User feedback collectors
    │   └── telemetry/
    │       ├── __init__.py             # Decoupled event pub-sub engine (Best-Effort)
    └── public/
        └── js/
            └── experience/
                ├── error_ui.js          # SMRITI API and client-side boundary interceptor
                ├── error_dialog.js      # Modal layout conforming to SMRITI style guidelines
                ├── error_side_panel.js  # Slide-out drawer details view for support/admins
                └── error_page.js        # Full crash page template
```

---

## 3. SMRITI SDK Stability & Versioning Policy

To ensure dependent modules can rely on the SDK without breaking, the following contract boundaries are frozen:

### 3.1 Contract Boundaries
* **Public APIs (SDK Core Interfaces)**: Interfaces such as `ErrorService`, `NotificationGateway`, `TelemetryDispatcher`, and `SmartLookupService` are versioned contracts and must remain strictly backward compatible.
* **Internal Adapters (Storage/Transport)**: Concrete classes like `IsolatedDbWriter` or `RealtimeTelemetryAdapter` can be refactored, extended, or replaced entirely without affecting dependent packages.
* **Repositories**: Data repositories can evolve internal data mappings as long as public CRUD interfaces remain backward compatible.
* **Database DocTypes**: Database tables may add optional fields or indices. Deprecating existing fields requires a formal migration roadmap.
* **UI Themes & Tokens**: Theme variables and resolver density layers (e.g. density values in `smriti_ui_resolver.js`) can adjust rendering values, but token names (e.g., `--smriti-color-bg-page`) must remain constant.
* **Public JSON Manifests**: Any config manifests must carry a version key (e.g., `version: "1.0.0"`) and run through compatibility checks during module load.

### 3.2 Semantic Versioning (SemVer) Rules
The SMRITI SDK version follows strict semantic specifications:
* **MAJOR (X.y.z)**: Breaking contract changes (deprecating signature parameters in public interfaces, changing structural properties). Increments trigger required audits for all registered plugins.
* **MINOR (x.Y.z)**: Introduction of backward-compatible features, new classes, or configuration helpers.
* **PATCH (x.y.Z)**: Backward-compatible bug fixes, optimizations, and internal adapter refinements.

---

## 4. Core Component Responsibilities & Policies

### 4.1 Error Formatter & Sanitizer Policy (`error_formatter.py`)
The `error_formatter.py` component is strictly responsible for output cleansing and security scrubbing:
* **Framework Leakage Prevention**: It scrubs all raw internal framework details including direct database query structures, `frappe` API namespaces, python files, SQL schemas, and syntax trace patterns.
* **Sensitive Data Redaction**: It must automatically scan all logs, contexts, and payload structures. It runs structured recursive checks on nested dictionaries/arrays to scrub sensitive parameters, falling back to regex patterns on flat text strings. It blocks:
  * Passwords, PINs, Keys, Secrets, and OTPs
  * PAN (Permanent Account Number), Aadhaar Number
  * GST API Keys, Private Certificates, and Private Keys
  * Credit Card Numbers, CVV Numbers
  * Bearer Tokens, Refresh Tokens, JWT Bearer tokens, and Cookies
  * Authorization Headers and Session IDs

### 4.2 Decoupled Write Pipeline
To prevent database locks or rollbacks during failed requests, writes follow an isolated contract:
```
Error Service -> Error Repository (Interface) -> Database Writer Adapter (Isolated Conn) -> [Fallback] Local Logger
```
* **Interface Freeze**: The `ErrorRepository` defines the public database signature. The underlying storage strategy (direct SQL thread, file logger, redis queue) is kept behind this contract as a replaceable adapter, isolating the app from future Frappe database upgrades.
* **Telemetry Rule (Fail-Silent & Async)**: Real-time events, analytics pings, and pub-sub notifications must **never block** user responses. Telemetry failures in Redis, MQTT, or socket systems must fail silently and permit the response thread to terminate cleanly.

### 4.3 Dynamic Plugin Registry
The notification gateway restricts subscriber registrations to verified and compatible plugins. The list of authorized modules and version mappings is fetched dynamically from the `SMRITI Plugin Registry` DocType.
```python
class SmritiNotificationGateway:
    _handlers = {}
    SDK_VERSION = "1.4"

    @classmethod
    def register_handler(cls, plugin_id, channel_name, handler_instance):
        """Allows only verified, active, and compatible plugins in the registry to register handlers."""
        import frappe
        plugin = frappe.db.get_value(
            "SMRITI Plugin Registry",
            {"plugin_id": plugin_id, "verified": 1, "enabled": 1},
            ["name", "minimum_sdk_version"],
            as_dict=True
        )
        if not plugin:
            raise PermissionError(f"Plugin '{plugin_id}' is not authorized or is disabled in the SMRITI Registry.")
            
        # Compatibility Verification
        min_sdk = plugin.get("minimum_sdk_version") or "1.0"
        if float(min_sdk) > float(cls.SDK_VERSION):
            raise ImportError(
                f"Plugin '{plugin_id}' requires SDK Version {min_sdk} or higher. "
                f"Current SDK Baseline is {cls.SDK_VERSION}."
            )
            
        cls._handlers[channel_name] = handler_instance
```

---

## 5. Ingress Middleware, Policy Engine & Tracing

### 5.1 Ingress Correlation Middleware
Correlation tokens are injected at the HTTP/Request ingress point:
* **Ingress Hook**: A `before_request` hook executes during app startup, binding a unique `smriti_correlation_id` (e.g., `REQ-20260705-ABCD1234`) to the thread-local request namespace (`frappe.local`).
* **Trace Propagation**: All subsequent actions (Lookups, Pricing computations, Inventory writes) use this local identifier for tracing and logging.

### 5.2 Decoupled Telemetry Abstraction
Realtime/telemetry dispatching is abstracted via a interface wrapper to support modular backends:
```python
class ITelemetryDispatcher:
    def dispatch(self, event_name, payload):
        raise NotImplementedError

class RealtimeTelemetryDispatcher(ITelemetryDispatcher):
    def dispatch(self, event_name, payload):
        import frappe
        frappe.publish_realtime(event_name, payload)
```

### 5.3 Policy Engine & Priority Hierarchy
Under the Policy Framework, the `Policy Engine` acts as a dynamic resolver that fetches and enforces runtime parameters (e.g. UI theme preferences, security access control thresholds, workflow rules, lookup bounds).
* **Override Hierarchy**: Policies are evaluated using a strict override hierarchy to support multi-tenant customization:
  ```
  Global Policy (Lowest) ──> Tenant Policy ──> Company Policy ──> Branch Policy ──> Department Policy ──> Role Policy ──> User Policy (Highest)
  ```
* **Evaluation Matrix**: The policy engine traverses this structure, resolving specific parameters based on the active user context before committing execution parameters.

---

## 6. Rich Diagnostic Context Map

| Context Category | Variable | Description |
| :--- | :--- | :--- |
| **Observability** | `correlation_id` | Unique Correlation ID tracking the transaction life cycle. |
| | `trace_id` | OpenTelemetry compatibility Trace ID. |
| | `span_id` | OpenTelemetry compatibility Span ID. |
| **Identity & Access** | `user` | Captured user session ID or Email. |
| | `company` | The active business company context. |
| | `branch` | Active physical store branch. |
| | `warehouse` | Active inventory warehouse. |
| **Environment & Build**| `app_version` | The semantic version of SMRITI Retail OS. |
| | `git_commit` | Exact git commit hash of the deployed codebase. |
| | `release_number` | Build/Release ID for deployment verification. |
| | `environment` | Context environment (e.g., `production`, `staging`, `dev`). |
| | `docker_container` | Container ID, host, or replica. |
| **System Lifecycle** | `site_name` | Active Multi-tenant site name. |
| | `database_name` | Name of the database schema executing the query. |
| | `worker` | Name of the RQ/Celery background worker. |
| | `request_duration` | Time taken by the request thread before exception occurred. |
| **Client Context** | `url` | HTTP request path or background CLI module. |
| | `payload` | Sanitized parameters (passwords, tokens, pins stripped). |
| | `browser` | User-agent string (device, browser version). |

---

## 7. Refactored Code Blueprints

### A. Isolated Database Writer Adapter (`error_repository.py` & Interface)

```python
# smriti_foundation/experience/error/error_repository.py

import frappe
from frappe.database import get_db
import logging
import time

class IErrorWriter:
    """Interface for error persistence strategies to ensure upgrade-safety."""
    def write_log(self, ref_id, exc_type, category, severity, message, stack_trace, context_data):
        raise NotImplementedError

class IsolatedDbWriter(IErrorWriter):
    """Primary transaction-safe database writer using isolated connections."""
    def write_log(self, ref_id, exc_type, category, severity, message, stack_trace, context_data):
        db_name = frappe.conf.db_name
        db_host = frappe.conf.db_host or "localhost"
        db_port = frappe.conf.db_port or 3306
        db_password = frappe.conf.get("db_password")
        
        new_db = None
        try:
            new_db = get_db(
                host=db_host,
                port=db_port,
                user=db_name,
                password=db_password,
                socket=frappe.conf.get("db_socket")
            )
            
            query = """
                INSERT INTO `tabSMRITI Error Log` (
                    name, creation, modified, modified_by, owner, docstatus,
                    reference_id, correlation_id, trace_id, span_id, error_code, category, severity, message,
                    user, url, request_payload, stack_trace, context, resolved, status
                ) VALUES (
                    %s, NOW(), NOW(), %s, %s, 0,
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, 0, 'Open'
                )
            """
            
            new_db.sql(query, (
                ref_id,
                context_data.get("user") or "Guest",
                context_data.get("user") or "Guest",
                ref_id,
                context_data.get("correlation_id") or "",
                context_data.get("trace_id") or "",
                context_data.get("span_id") or "",
                exc_type,
                category,
                severity,
                message,
                context_data.get("user") or "Guest",
                context_data.get("url") or "CLI/Background",
                context_data.get("payload") or "{}",
                stack_trace,
                frappe.as_json(context_data)
            ))
            new_db.commit()
            return True
        except Exception as db_exc:
            logger = logging.getLogger("smriti_error_fallback")
            logger.error(f"[SMRITI-ERR] Fail-safe active. Ref: {ref_id}. Ex: {str(db_exc)}")
            return False
        finally:
            if new_db:
                new_db.close()

class SmritiErrorRepository:
    """Public frozen repository interface."""
    _writer = IsolatedDbWriter()

    @classmethod
    def set_writer(cls, writer_instance):
        """Inject different storage engines (Mock, Queue, Async) without changing consumer code."""
        if isinstance(writer_instance, IErrorWriter):
            cls._writer = writer_instance

    @classmethod
    def save(cls, ref_id, exc_type, category, severity, message, stack_trace, context_data):
        return cls._writer.write_log(ref_id, exc_type, category, severity, message, stack_trace, context_data)
```

### B. Cleaned & Redacted Context Aggregation (`error_service.py`)

```python
# smriti_foundation/experience/error/error_service.py

import frappe
import traceback
import uuid
import sys
import os
import re
import time
from datetime import datetime
from smriti_foundation.experience.error.error_repository import SmritiErrorRepository

class ITelemetryDispatcher:
    def dispatch(self, event_name, payload):
        raise NotImplementedError

class RealtimeTelemetryDispatcher(ITelemetryDispatcher):
    def dispatch(self, event_name, payload):
        import frappe
        frappe.publish_realtime(event_name, payload)

class SmritiErrorService:
    _telemetry_dispatcher = RealtimeTelemetryDispatcher()

    @classmethod
    def set_telemetry_dispatcher(cls, dispatcher_instance):
        if isinstance(dispatcher_instance, ITelemetryDispatcher):
            cls._telemetry_dispatcher = dispatcher_instance

    @classmethod
    def capture(cls, exception, custom_message=None):
        start_time = time.time()
        timestamp = datetime.now()
        ref_id = f"SMRITI-ERR-{timestamp.strftime('%Y%m%d')}-{str(uuid.uuid4().hex[:6]).upper()}"
        
        exc_type = type(exception).__name__
        category, severity, friendly_msg = cls.get_error_definition(exc_type)
        
        stack_trace = traceback.format_exc()
        context_data = cls.capture_context()
        context_data["request_duration"] = f"{round((time.time() - start_time) * 1000, 2)}ms"
        
        # Redact Sensitive Fields (Recursive Structured Scrubbing)
        sanitized_msg = cls.redact_sensitive_keys(custom_message or friendly_msg)
        sanitized_stack = cls.redact_sensitive_keys(stack_trace)
        
        raw_payload = context_data["payload"]
        try:
            import json
            parsed = json.loads(raw_payload)
            scrubbed_dict = cls.redact_structured_dict(parsed)
            context_data["payload"] = json.dumps(scrubbed_dict)
        except Exception:
            context_data["payload"] = cls.redact_sensitive_keys(raw_payload)
        
        # Save error safely
        SmritiErrorRepository.save(
            ref_id=ref_id,
            exc_type=exc_type,
            category=category,
            severity=severity,
            message=sanitized_msg,
            stack_trace=sanitized_stack,
            context_data=context_data
        )
        
        # Fail-silent async telemetry dispatch
        try:
            cls._telemetry_dispatcher.dispatch("smriti_error_event", {
                "reference_id": ref_id,
                "correlation_id": context_data.get("correlation_id"),
                "category": category,
                "severity": severity
            })
        except Exception:
            pass  
            
        return cls.render_sanitized_response(ref_id, category, severity, sanitized_msg)

    @classmethod
    def redact_structured_dict(cls, data):
        """Recursively scrubs sensitive keys from nested dicts and lists."""
        sensitive_keys = {"password", "token", "pin", "secret", "authorization", "otp", "cvv", "card_number", "aadhaar", "pan"}
        if isinstance(data, dict):
            return {k: ("[REDACTED]" if k.lower() in sensitive_keys else cls.redact_structured_dict(v)) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.redact_structured_dict(item) for item in data]
        return data

    @staticmethod
    def redact_sensitive_keys(content_str):
        """Flat-text Regex scrubbing fallback."""
        if not content_str:
            return content_str
        
        sensitive_patterns = [
            r'(?i)("password"\s*:\s*)"[^"]+"',
            r'(?i)(password\s*=\s*)\'[^\']+\'',
            r'(?i)(password\s*=\s*)"[^"]+"',
            r'(?i)("token"\s*:\s*)"[^"]+"',
            r'(?i)("pin"\s*:\s*)"[^"]+"',
            r'(?i)("secret"\s*:\s*)"[^"]+"',
            r'(?i)("authorization"\s*:\s*)"[^"]+"',
            r'(?i)("otp"\s*:\s*)"[^"]+"',
            r'(?i)("cvv"\s*:\s*)"[^"]+"',
            r'(?i)("card_number"\s*:\s*)"[^"]+"',
            r'(?i)("aadhaar"\s*:\s*)"[^"]+"',
            r'(?i)("pan"\s*:\s*)"[^"]+"',
            r'(?i)(cookie:\s*)[^\r\n]+',
            r'(?i)(bearer\s+[A-Za-z0-9\-\._~\+\/]+=*)',
        ]
        
        sanitized = content_str
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, r'\1"[REDACTED]"', sanitized)
        return sanitized

    @staticmethod
    def get_error_definition(exc_type):
        """Dynamic lookup from SMRITI Error Definition DocType"""
        try:
            mapping = frappe.db.get_value(
                "SMRITI Error Definition",
                {"exception_name": exc_type, "enabled": 1},
                ["category", "severity", "friendly_message"],
                as_dict=True
            )
            if mapping:
                return mapping.category, mapping.severity, mapping.friendly_message
        except Exception:
            pass
            
        fallbacks = {
            "ValidationError": ("SMRITI-VAL", "Warning", "Validation failed. Please correct the values entered."),
            "PermissionError": ("SMRITI-PERM", "Business Error", "You do not have permission to execute this operation."),
            "DoesNotExistError": ("SMRITI-NOTFOUND", "Information", "The requested record was not found."),
        }
        return fallbacks.get(exc_type, ("SMRITI-INT", "System Error", "An unexpected operational error occurred."))

    @staticmethod
    def capture_context():
        """Aggregates system context. Thread local correlation ID generated by Ingress Middleware."""
        correlation_id = frappe.local.get("smriti_correlation_id")
        if not correlation_id:
            correlation_id = f"REQ-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4().hex[:8]).upper()}"
            frappe.local.smriti_correlation_id = correlation_id
            
        context = {
            # Distributed Observability
            "correlation_id": correlation_id,
            "trace_id": frappe.local.get("smriti_trace_id") or "",
            "span_id": frappe.local.get("smriti_span_id") or "",
            
            # Identity & Context
            "user": frappe.session.user if frappe.session else "Guest",
            "url": frappe.request.path if (frappe.request and hasattr(frappe.request, 'path')) else "CLI/Background",
            "payload": frappe.as_json(frappe.form_dict) if frappe.form_dict else "{}",
            "timestamp": frappe.utils.now_datetime().isoformat(),
            
            # Environment Context
            "app_version": frappe.get_attr("smriti_retail_os.__version__") if hasattr(frappe, "get_attr") else "1.0.0",
            "git_commit": frappe.conf.get("git_commit_version") or "Unknown",
            "release_number": frappe.conf.get("release_number") or "Unknown",
            "environment": os.getenv("SMRITI_ENV") or "production",
            "docker_container": os.getenv("HOSTNAME") or "Host",
            
            # Tenant and System Context
            "site_name": frappe.local.site if hasattr(frappe.local, "site") else "Unknown",
            "database_name": frappe.conf.db_name,
            "worker": os.getenv("WORKER_NAME") or "Main",
            "company": frappe.defaults.get_user_default("company") or "Unknown",
            "warehouse": frappe.defaults.get_user_default("warehouse") or "Unknown",
        }
        return context

    @staticmethod
    def render_sanitized_response(ref_id, category, severity, friendly_message):
        return {
            "smriti_framework_status": "error",
            "reference_id": ref_id,
            "category": category,
            "severity": severity,
            "friendly_message": friendly_message,
            "suggested_actions": ["Retry", "Go Back", "Return to Dashboard"]
        }
```

---

## 8. Constitution Amendments & Core UI Rules

### Rule 16: SMRITI Experience Framework (SEF) Boundary Rule
All user-facing interaction channels—including validation prompts, crash screens, info warnings, progress overlays, and search helpers—must be handled exclusively through the **SMRITI Experience Framework (SEF)**. 

* **No Raw Tracebacks**: Raw SQL errors, Python traces, or browser stack logs must never reach the user interface.
* **No Global Hijacking**: Interception logic must operate strictly at SMRITI boundaries (whitelisted API wrappers, SMRITI page routes) and must not modify native Frappe Desk (`frappe.throw`, `frappe.msgprint`) globally, to prevent breaking core administration tools.
* **Transaction-Safe Logs**: Error logging must use isolated database connection interfaces or file-based fallbacks. Calling `frappe.db.commit()` inside an error logger is strictly forbidden.

### Rule 17: UI Experience Standard (Experience Rule)
Every SMRITI UI component must return and render a structured, branded experience matching one of these categories:
1. **Success Experience**: Styled with SMRITI primary branding, showing successful completion and next workflow actions.
2. **Validation Experience**: Clear, field-specific notifications mapped directly to form controls.
3. **Warning Experience**: Warns of potential data loss, stock discrepancies, or non-blocking issues.
4. **Error Experience**: Intercepts structural or connection crashes, presenting a reference ID, friendly feedback, and suggested recovery buttons.
5. **Progress Experience**: Standardized spinners or progress bars rendering execution states during slow database operations.

No raw backend database strings or default browser exceptions are permitted to render directly.

### Rule 18: Sensitive Data Redaction Rule
Personally identifiable information, auth keys, tokens, session IDs, authorization headers, passwords, cookies, cryptographic secrets, OTPs, Aadhaar, PAN, GST API Keys, and credit card numbers must never be logged, persisted, or displayed in raw format inside the SMRITI logs or frontend UIs. The SMRITI Error Formatter (`error_formatter.py`) must proactively filter and redact sensitive elements before logging or client display.

### Rule 19: Correlation & Distributed Tracing Rule
Every transaction flow traversing the SMRITI Foundation SDK must carry a unique `Correlation ID` generated at the request ingress point. All services, background workers, and telemetry messages executed during that request thread must log and preserve this Correlation ID to facilitate distributed request tracking across the SMRITI platform.

---

## 10. Architectural Governance & Change Control

Following the baseline freeze, future refinements to this blueprint must be managed using formal Change Control channels:
* **Baseline Freeze**: This document represents **SMRITI Architecture Baseline v1.4**. Direct updates to this baseline specification are frozen.
* **Change Ingress (ADRs & RFCs)**: Subsequent structural recommendations, interface versions, or schema expansions must be submitted as **Architecture Decision Records (ADRs)** or **Requests for Comments (RFCs)**.
* **Governance Gate**: Decisions documented in ADRs must go through gaps analysis and Founder approval before being merged into the next baseline release iteration (e.g., v1.5.0).

---

## 11. SDK Implementation Quality & Delivery Governance

### 11.1 Definition of Done (DoD) for Foundation Pillars
To guarantee enterprise reliability, no component or sub-module within the SMRITI Foundation SDK shall be considered complete or ready for release until it passes the following checklist:
* [ ] **Architecture Alignment**: The module strictly implements the frozen baseline contracts.
* [ ] **Unit Tests**: Minimum 90% code coverage on all services, repositories, and formatter utilities.
* [ ] **Integration Tests**: Verification of end-to-end telemetry and logging dispatches under transaction rollbacks.
* [ ] **Architecture Guard Validation**: Successfully verified against SMRITI imports constraints (e.g. no direct raw inserts from UI files).
* [ ] **License & Security Guards**: Checks executed confirming that no unvetted libraries are added and that the Sensitive Data Redaction Rule (Rule 18) matches blocklists.
* [ ] **Dynamic Policy Mapping**: Fully configured dynamic mappings (`SMRITI Error Definition` table and default overrides).
* [ ] **Performance Target**: Average request and log formatting overhead is target-benchmarked under **5ms** in production environments.

---

> "Always decision-ready."
> 
> — Jawahar R. Mallah
> Founder & Chief Architect, AITDL
