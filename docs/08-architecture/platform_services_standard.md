---
Document ID: "STD-PLATFORM-01"
Title: "SMRITI Platform Services Standard v1.0"
Owner: "Jawahar R. Mallah"
Audience: "Architect, Developers"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: "ADR-0002, ADR-0009"
Related Modules: "print_framework"
Last Updated: "2026-07-04"
Last Reviewed: "2026-07-04"
AI Generated: "No"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI Platform Services Standard v1.0

This standard defines the rules, layering, dependencies, and certification criteria for Platform Primitives and reusable services within the **SMRITI Platform Services Architecture (SPSA)**.

---

## 1. Architectural Classification

SMRITI Platform components are strictly classified into one of three layers:

```
┌────────────────────────────────────────────────────────┐
│                      APPLICATIONS                      │
│            Custom Store Deployments / Configs          │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                        STUDIOS                         │
│   Barcode Studio, Label Studio, Purchase Studio, POS   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                   PLATFORM SERVICES                    │
│   Print Framework, Notifications, Payments, Formulas   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                       FOUNDATION                       │
│    Repository Layer, Architecture Guard, Token Cache   │
└────────────────────────────────────────────────────────┘
```

### A. Foundation Layer
The low-level infrastructure on which all other layers build.
* **Criteria**:
  * Global accessibility across all app routes.
  * Zero dependencies on upper layers (Platform Services or Studios).
  * Implements core architectural enforcements (e.g. Repository Pattern adapters, Architecture Guard, audit ledger tools).

### B. Platform Services Layer
Reusable, headless infrastructure services providing primitive capabilities.
* **Criteria**:
  * **Reusable**: Must be consumed by at least two distinct Studios.
  * **UI Independent**: Must be completely headless. No visual HTML/CSS/JS components.
  * **Domain Agnostic**: Must not contain reference schemas of business entities (e.g. does not know what an `Item` is; processes only raw byte streams).
  * **Independently Testable**: Must pass automated backend unit tests mock-spooling connections.
  * **ADR Governed**: Changes to interfaces must be approved via an ADR.
  * **Architecture Guard Compliant**: Must follow `ADR-0002` (0 direct persistence calls).

### C. Studios Layer
User-facing, workflow-oriented business modules.
* **Criteria**:
  * **User Facing**: Contains custom SMRITI UI www templates (`www/barcode.html`, `www/label.html`).
  * **Uses Platform Services**: Integrates platform services for peripheral actions (e.g. Print Framework, Token Registry).
  * **Isolated Repositories**: Encapsulates its database transactions inside dedicated repository adapters.
  * **Reference Certified**: Certified against the *SMRITI Reference Studio Standard*.

---

## 2. Dependency Rule (SPSA Directional Flow)

To prevent circular dependencies and Spaghetti Architecture:
* **Allowed Flows**:
  * `Foundation` $\rightarrow$ `Platform Services` $\rightarrow$ `Studios` $\rightarrow$ `Applications`.
* **Forbidden Flows**:
  * **Platform Service $\rightarrow$ Studio**: Platform services must *never* import or invoke modules inside `smriti_retail_os/barcode/` or `smriti_retail_os/label_studio/`.
  * **Foundation $\rightarrow$ Platform Service**: Low-level persistence classes must not reference printing or payment services.

---

## 3. Platform Service Certification Checklist

Before any service is classified as "Platform Service Certified", it must satisfy the following checklist:

- [ ] **UI-Free Abstraction**: No template rendering or DOM manipulation in backend services.
- [ ] **Domain Separation**: Consumes raw serialized models or streams rather than DocType models directly.
- [ ] **Repository Isolation**: All persistence operations are routed through a repository.
- [ ] **Dynamic Adapter Registry**: No hardcoded driver selection; connection adapters must resolve via registry bindings.
- [ ] **Unit Test Coverage**: At least 90% test coverage covering individual adapters and dispatch paths.
- [ ] **E2E Integration Test**: A mock end-to-end flow test demonstrating integration from a studio through the service.
- [ ] **Zero Violation Status**: Exits with 0 violations under SMRITI Architecture Guard.

---

## 4. SPSA Capability Matrix

The roadmap and integration status of platform services across business modules are tracked below:

| Platform Service | Barcode Studio | Label Studio | Purchase Studio | POS Studio | Analytics Studio | Certification Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Print Framework** | ✅ | ✅ | ⏳ (Planned) | ⏳ (Planned) | ❌ (N/A) | **CERTIFIED** |
| **Token Registry** | ✅ | ✅ | ✅ | ✅ | ✅ | **CERTIFIED** |
| **Notification Engine**| ❌ (N/A) | ❌ (N/A) | ⏳ (Planned) | ⏳ (Planned) | ❌ (N/A) | ⏳ (Scaffold) |
| **Formula Engine** | ❌ (N/A) | ❌ (N/A) | ✅ | ✅ | ✅ | **CERTIFIED** |

---

## ## Revision History

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-07-04 | 1.0.0 | Initial version defining SPSA layers and checklists. | Jawahar R. Mallah |

---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
