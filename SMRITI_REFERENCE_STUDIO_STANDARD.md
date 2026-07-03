# SMRITI Reference Studio Standard

This document outlines the mandatory requirements that every business module (Studio) in SMRITI Retail OS must satisfy to be certified as a SMRITI Reference Studio.

---

## 📋 Certification Checklist

Any new business module (e.g., Sales, Inventory, CRM) must strictly satisfy the following criteria:

### 1. UI Ownership
* **Requirement:** All interfaces must be built as custom SMRITI pages.
* **Constraint:** Never expose Frappe Desk `/desk` or `/app` URLs to retail users.

### 2. Navigation Ownership
* **Requirement:** Sidebars, workspaces, dashboard quick links, and redirection rules must only route to SMRITI www pages.
* **Constraint:** Intercept and block access to `/desk/setup-wizard` or raw Frappe workspaces.

### 3. Thin APIs
* **Requirement:** API controllers (`*_api.py`) must only parse inputs, validate permissions, and call the service layer.
* **Constraint:** No business logic, DB queries, or ORM updates inside API files.

### 4. Service-Only Business Logic
* **Requirement:** All workflows, validation policies, and transaction boundaries (`commit`/`rollback`) must reside inside the service layer (`*_service.py`).
* **Constraint:** No direct SQL or raw ORM insert/update operations inside the service layer.

### 5. Platform Persistence Adapter
* **Requirement:** All platform-specific queries, counts, factory instantiations, and updates must go through the dedicated persistence adapter (e.g., `erp_adapter.py`).
* **Constraint:** Decouple the service layer so that if the underlying platform engine (e.g., ERPNext/Frappe) changes, only the adapter layer is modified.

### 6. Platform Engine Isolation
* **Requirement:** Maintain database operations strictly in the persistence boundary, isolating SMRITI's business domain from the platform engine's schemas.

### 7. Architecture Guard PASS
* **Requirement:** Run `python smriti_architecture_guard.py` with zero regressions and lock in the baseline.
* **Constraint:** Ensure no forbidden persistence calls are introduced in the API or Service layers.

### 8. Backward Compatibility
* **Requirement:** Retain support for existing whitelisted entry points, integration schemas, and legacy bookmarks.

### 9. Test Coverage
* **Requirement:** Implement a comprehensive suite of unit and API integration tests.
* **Constraint:** All tests must pass cleanly in the testing environment container.

### 10. UX Constitution
* **Requirement:** Adhere to the SMRITI UX styling system (Navy `#1A2B5C` + Blue `#2563EB` + Arial), displaying SMRITI logo and layout standards.

---

## 🏆 Certified Studios

| Module | Architecture Status | Operational Status | Reference Standard Version |
| :--- | :---: | :---: | :---: |
| **Purchase Studio** | **PASS** | **Pending GA Validation** | SMRITI Reference Studio v1.0 |
