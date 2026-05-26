# Implementation Plan - Custom SMRITI Sidebar Component

Build and integrate the Custom SMRITI Sidebar Component to ensure a consistent, premium dark-themed navigation experience for SMRITI retail users. Standard ERPNext sidebar and workspace features will be hidden and replaced with the custom sidebar for cashier/manager roles, with System Managers bypassed.

## User Review Required

> [!IMPORTANT]
> The custom sidebar completely replaces the default ERPNext workspace layout for SMRITI users. No-code workspace customizations will not be visible to cashiers or store managers.

> [!NOTE]
> System Managers (`Administrator` or any user with the `System Manager` role) will bypass the SMRITI sidebar entirely and retain the standard ERPNext Desk view for full administrative capabilities.

## Proposed Changes

---

### File Naming & Build Consistency

To ensure the Frappe Page controller loading mechanism maps correctly to custom pages (resolving possible underscore vs. hyphen file naming issues), we will copy/ensure both hyphenated and underscored `.js` files exist for pages.

#### [NEW] [smriti-barcode.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/page/smriti-barcode/smriti-barcode.js)
Copy of `smriti_barcode.js` inside the `smriti-barcode` page folder to align with Frappe page loading conventions.

#### [NEW] [smriti-desk.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/page/smriti-desk/smriti-desk.js)
Copy of `smriti_desk.js` inside the `smriti-desk` page folder.

#### [NEW] [smriti-shift.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/page/smriti-shift/smriti-shift.js)
Copy of `smriti_shift.js` inside the `smriti-shift` page folder.

---

### Custom Page Integration

Modify each page JS controller to invoke the reusable sidebar component, passing the correct active page ID to highlight the active menu item.

#### [MODIFY] [smriti-billing.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/page/smriti-billing/smriti-billing.js)
Add `SMRITI.renderSidebar("billing");` inside `on_page_load`.

#### [MODIFY] [smriti-inventory.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/page/smriti-inventory/smriti-inventory.js)
Add `SMRITI.renderSidebar("inventory");` inside `on_page_load`.

#### [MODIFY] [smriti-barcode.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/page/smriti-barcode/smriti-barcode.js)
Add `SMRITI.renderSidebar("barcode");` inside `on_page_load`.

#### [MODIFY] [smriti-purchase.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/page/smriti-purchase/smriti-purchase.js)
Add `SMRITI.renderSidebar("purchase");` inside `on_page_load`.

#### [MODIFY] [smriti-desk.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/page/smriti-desk/smriti-desk.js)
Add `SMRITI.renderSidebar("reports");` inside `on_page_load`.

---

### Global Desk Safety Net

Integrate SMRITI sidebar rendering into the global lifecycle hooks inside `main.js` so that standard list/form views (e.g. `/app/customer`) hide the default sidebar and render the custom one.

#### [MODIFY] [main.js](file:///d:/Smriti_Retail_OS/apps/smriti_retail_os/smriti_retail_os/public/js/main.js)
- Implement `get_smriti_active_page()` route analyzer.
- Hook into `app_ready` and `page-change route-change` events to invoke `SMRITI.renderSidebar(active_page)`.

---

## Verification Plan

### Automated Build Verification
1. Run Bench build command to compile the assets:
   ```bash
   docker compose -f pwd.yml exec backend bench build --app smriti_retail_os
   ```
2. Clear bench/site cache:
   ```bash
   docker compose -f pwd.yml exec backend bench --site frontend clear-cache
   ```

### Manual Verification
1. Log in with a cashier/manager user profile (e.g. user `Rahul`).
2. Navigate between `Billing`, `Inventory`, `Barcodes`, `Customers`, `Purchase`, and `Reports` custom pages:
   - Verify that the custom sidebar renders and the corresponding menu item is highlighted.
   - Verify that the bottom section shows live Shift status (Open/Closed) and Cashier details.
   - Verify that clicking the mobile hamburger toggle/collapsible button collapses the sidebar into an icon-only menu.
3. Navigate to a standard DocType view (e.g. `/app/customer` or `/app/item` or `/app/supplier` list/form views):
   - Verify that the standard ERPNext workspace sidebar is hidden and the SMRITI custom sidebar is injected.
4. Log in as `Administrator` or a System Manager:
   - Verify that the custom sidebar does NOT render, and the standard ERPNext desk workspace remains completely functional.
