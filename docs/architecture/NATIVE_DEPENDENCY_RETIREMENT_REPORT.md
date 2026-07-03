# Native Dependency Retirement Report

---
**DOCUMENT METADATA**
- **Document Title**: SMRITI Native Dependency Retirement Report
- **Document Owner**: Jawahar R. Mallah
- **Organization**: AITDL – AI Technology & Development Lab
- **Prepared By**: SMRITI Engineering Team
- **Reviewed By**: —
- **Approved By**: —
- **Status**: Draft
- **Version**: 1.0.0
- **Revision Date**: 04-Jul-2026
---

## 1. Executive Summary
To prevent exposing the native ERPNext/Frappe `/desk` or `/app` interfaces to standard users (Rule 9 compliance), SMRITI Retail OS has retired legacy desk pages and native list view routing.

## 2. Page Retirement Metrics
- **Legacy Desk Pages**: 22 → 1 (Only numbering engine `smriti_udne` remains, pending task 4.1).
- **Native Route Calls**: Removed from all client code (zero `List` view route references).
- **Desk Redirects**: Implemented at boot level (`boot.py`) and website rules (`hooks.py`).

## 3. List of Retired Pages (Deleted Directories)
1. `psv_opening_balance`
2. `smriti_backup`
3. `smriti_barcode`
4. `smriti_billing`
5. `smriti_cge`
6. `smriti_customers`
7. `smriti_delivery_challan`
8. `smriti_desk`
9. `smriti_inventory`
10. `smriti_item_master`
11. `smriti_loyalty`
12. `smriti_negative_stock`
13. `smriti_payments`
14. `smriti_purchase`
15. `smriti_purchase_invoice`
16. `smriti_purchase_receipt`
17. `smriti_reports`
18. `smriti_sales_invoices`
19. `smriti_sales_return`
20. `smriti_shift`
21. `smriti_supplier_returns`
22. `smriti_suppliers`

---
**REVISION HISTORY**
- **Prepared By**: SMRITI Engineering Team
- **Reviewed By**: —
- **Approved By**: —
- **Status**: Draft
