# Sales Studio Phase 1 — Walkthrough

## Purpose

Sales Studio Phase 1 formalizes the existing Sales Order and Quotation functionality into the same `api/service/repository` layering used by `customer_studio`, `purchase_studio`, and `matrix_engine`. This is an evolutionary extension — no existing functionality is replaced or broken.

## Scope

| Area | Description |
|---|---|
| **Backend** | New `sales_studio/` package with 4 subpackages (adapter, api, repository, service) |
| **UI Refactoring** | `sales_orders.html` rewired from legacy `sales_order_api` to `sales_studio.api.sales_api` |
| **New UI** | `smriti-quotation.html` — Quotation Manager with dual-mode entry (manual + matrix grid) |
| **Security** | `smriti_quotation` page registered in `security_api.py` access policy |
| **Tests** | Unit tests for all layers + integration tests for Quotation→SO flow |

---

## Files Created

| File | Layer | Description |
|---|---|---|
| [sales_studio/__init__.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/__init__.py) | Package | Package init |
| [adapter/__init__.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/adapter/__init__.py) | Package | Adapter subpackage init |
| [adapter/sales_matrix_adapter.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/adapter/sales_matrix_adapter.py) | Adapter | Matrix cell → item line conversion |
| [api/__init__.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/api/__init__.py) | Package | API subpackage init |
| [api/sales_api.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/api/sales_api.py) | API | 10 whitelisted endpoints for Quotation/SO CRUD |
| [repository/__init__.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/repository/__init__.py) | Package | Repository subpackage init |
| [repository/sales_repository.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/repository/sales_repository.py) | Repository | DB access for native Quotation/Sales Order doctypes |
| [service/__init__.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/service/__init__.py) | Package | Service subpackage init |
| [service/sales_service.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/service/sales_service.py) | Service | Core orchestration: item resolution, rate/MRP lookup, taxes |
| [service/sales_validation_service.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/service/sales_validation_service.py) | Service | Live stock checks, role enforcement |
| [service/sales_workflow_service.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/sales_studio/service/sales_workflow_service.py) | Service | Status transitions, Quotation→SO conversion |
| [www/smriti-quotation.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti-quotation.html) | UI | Quotation Manager page with matrix grid |
| [www/smriti_quotation.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/smriti_quotation.py) | Controller | Python controller for quotation page |
| [tests/test_sales_studio.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/tests/test_sales_studio.py) | Tests | Unit + integration test suite |

## Files Modified

| File | Change |
|---|---|
| [www/sales_orders.html](file:///D:/Smriti_Retail_OS/smriti_retail_os/www/sales_orders.html) | Rewired 3 API calls from `sales_order_api` → `sales_studio.api.sales_api`; updated field names to match new response schema |
| [security_api.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/security_api.py) | Added `smriti_quotation: manager_roles` to `check_page_access` policies |

---

## Architecture Decisions

1. **Layered architecture** — Follows the same pattern as `purchase_studio`:
   - `repository/` — thin DB access (no business logic)
   - `service/` — business rules, validation, orchestration
   - `adapter/` — data transformation (matrix cells → item lines)
   - `api/` — thin whitelisted endpoints delegating to services

2. **Legacy API preserved** — `sales_order_api.py` is NOT deleted; the UI simply routes to the new endpoints. Existing integrations that reference `sales_order_api` continue to work.

3. **Dual-mode entry** — The Quotation UI supports both manual item search and matrix grid entry (Article/Color/Size), matching the Purchase Order creation workflow.

4. **india_compliance bypass** — All document insertions call `initialize_item_wise_tax_details()` before save to prevent `TypeError` in the `india_compliance` app's `before_validate` hook.

## Design Rationale

- **Why not replace `sales_order_api.py`?** — The pilot branch and other modules may reference it. The new layer is additive, not destructive.
- **Why resolve_variant_item in SalesService?** — It mirrors `purchase_service.resolve_variant_item` but with sales-appropriate role checks. Keeps the service layer self-contained.
- **Why matrix grid on Quotations?** — Retail footwear/apparel quotations need size/color breakdowns. Matrix entry is the standard SMRITI pattern for this.

## Implementation Summary

**Backend**: 7 Python files creating the full `sales_studio` package. The service layer resolves item prices from `Item Price` (Standard Selling price list), falls back to `valuation_rate`, and back-calculates tax-exclusive rates from MRP when GST percentages are known.

**Frontend**: The Sales Orders page (`sales_orders.html`) now calls `sales_studio.api.sales_api.*` endpoints instead of `sales_order_api.*`. The new Quotation Manager (`smriti-quotation.html`) provides a complete CRUD interface with list/detail/create views and Quotation→Sales Order conversion.

---

## Tests Executed

**Syntax validation** — All 8 Python files pass `ast.parse()` without errors.

```
sales_repository.py: syntax OK
sales_service.py: syntax OK
sales_validation_service.py: syntax OK
sales_workflow_service.py: syntax OK
sales_matrix_adapter.py: syntax OK
sales_api.py: syntax OK
smriti_quotation.py: syntax OK
test_sales_studio.py: syntax OK
```

**Test suite structure** — `test_sales_studio.py` contains:
- `TestSalesRepository` — 4 tests (new_doc, list operations)
- `TestSalesValidationService` — 3 tests (role checks, stock availability)
- `TestSalesMatrixAdapter` — 4 tests (filtering, attribute summary, empty list)
- `TestSalesWorkflowService` — 1 test (importability)
- `TestSalesService` — 2 tests (method existence, allowed roles)
- `TestSalesAPI` — 1 test (endpoint existence)
- `TestQuotationToSOIntegration` — 4 tests (full CRUD flow, requires test site)

> [!NOTE]
> Integration tests require `bench run-tests` on a site with test fixtures. They are designed to skip gracefully if no Company/Item/Customer exists.

## Verification Results

| Check | Status | Evidence |
|---|---|---|
| Python syntax (8 files) | Done | `ast.parse()` output: all OK |
| Git commit | Done | `79b93b7` on `smriti-next` branch |
| `git diff` for `security_api.py` | Done | +1 line: `"smriti_quotation": manager_roles` |
| `git diff` for `sales_orders.html` | Done | 4 API call rewrites, field name updates |
| Directory structure | Done | `sales_studio/` with 4 subpackages verified |
| HTML file structure | Done | `smriti-quotation.html`: 4 script blocks, 51,831 bytes |
| Integration tests | Unverified | Requires `bench run-tests` on test site |
| Browser UI rendering | Unverified | Requires deployment to F:\Smriti9 and browser testing |

## Known Limitations

1. **Legacy API not deprecated** — `sales_order_api.py` remains active. Should be formally deprecated in a future phase.
2. **Quotation listing filter** — Current `list_quotations` returns all quotations (draft + submitted). May need status filtering for Open-only.
3. **Matrix grid variant creation** — `resolve_variant_item` only finds existing variants. If a variant doesn't exist, the user gets an error. Auto-creation is delegated to the `resolve_or_create_variant` endpoint (separate flow).

## Future Work

- **Phase 2**: Add Delivery Note creation from Sales Order
- **Phase 3**: Sales analytics dashboard integration with `analytics_studio`
- **Deprecation**: Formally deprecate `sales_order_api.py` and migrate all callers

## Related ADRs

None (first implementation of Sales Studio).

## Related RFCs

None.
