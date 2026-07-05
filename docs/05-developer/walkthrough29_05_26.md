---
Document ID: "DEV-064"
Title: "Walkthrough: Sidebar Popouts & Floating Controls"
Owner: "Development Team"
Audience: "Developer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# Walkthrough: Sidebar Popouts & Floating Controls

I have completed the implementation of sidebar popout buttons for all links, global popout layout overrides, and a floating window control panel for distraction-free/popout modes.

## Changes Made

### 1. Sidebar Navigation
- **Popout Button Render**: Updated `public/js/smriti_sidebar.js` to render a small popout button (using the `open_in_new` icon) to the right of each navigation item.
- **Hover Reveal**: Added CSS rules to `public/css/smriti_sidebar.css` so that the popout icon reveals itself on hover, keeping the sidebar layout clean and readable. The icon is automatically hidden when the sidebar is collapsed.
- **Launch Functionality**: Bound click listeners to open the respective link in a new popout window (`window.open`) with the `?popout=true` URL parameter appended.

### 2. Global Popout Mode & Floating Controls
- **sessionStorage State Persistence**: Enhanced `public/js/main.js` to store a `smriti_popout_mode: "true"` flag in `sessionStorage` upon first detection of `?popout=true`. This ensures that even when the user navigates between different pages within the Single Page App (SPA) and the query parameters are replaced/cleared by the Frappe router, the popout distraction-free styles remain fully active. It also handles `?popout=false` to clear this flag if needed.
- **Layout Overrides**: Added styling rules to `public/css/smriti_sidebar.css` under the `body.smriti-popout-active` class. This hides all default header/navbar elements, SMRITI and standard sidebars, and stretches the page containers to 100% width.
- **Selective Page Head (Header Actions) Styling**:
  - **Custom Pages**: Custom SMRITI pages (like Billing, Inventory, Reports) hide the `.page-head` container completely as they contain their own custom action controls.
  - **Standard DocType Pages**: Standard lists and forms (like Sales Invoice or Customer) keep the `.page-head` visible so that Save, Submit, Edit, and status actions are fully functional. The header is styled cleanly, removing breadcrumbs and resetting margins to look like a sleek toolbar.
- **Floating Control Bar**: Auto-renders a glassmorphic floating control bar in the top-right corner of any page in popout mode, containing:
  - **Fullscreen Toggle**: Toggles full-screen mode on/off.
  - **Close Window**: Closes the popout tab/window.

### 3. Deep Audit and Full-Width Layout Fixes (White Left-Side Gap Resolution)
During a deep audit of Frappe v16's page wrapper layout, several structural challenges were resolved:
- **CSS Grid Column Shifting**: Frappe uses a 2-column CSS Grid inside `.body-sidebar-container` and `.page-content`. Even if child sidebar columns are hidden (`display: none`), the grid track definitions still allocate width for the sidebar, creating a massive blank gap on the left.
  - **Fix**: Added explicit rules to `smriti_sidebar.css` forcing layout wrapper elements (`.body-sidebar-container`, `.page-content`, `.layout-main-section-wrapper`, `.layout-main`) to fall back to block layouts (`display: block !important`) and single grid tracks (`grid-template-columns: 1fr !important`).
  - **Fix**: Forced main content panels (`.layout-main`, `.layout-main-section`, `.layout-main-section-wrapper`, `[id^="page-"]`) to span across all grid columns using `grid-column: 1 / -1 !important;`.
- **CSS Variables Redefinition**: Overrode core variables on `body.smriti-popout-active` (like `--sidebar-width: 0px !important`, `--page-sidebar-width: 0px !important`) so any standard Frappe selectors relying on CSS variables for indentation automatically collapse to `0`.
- **JS DOM-Tree Walker (`_force_popout_full_width()`)**: Climbs recursively from content nodes to the `body` element and forces full-width properties at runtime (on transitions and periodic interval checks).
- **Dynamic Path Normalization (`/desk` vs `/app`)**:
  - In Frappe v16, the base desk URL is served at `/desk` rather than `/app`.
  - Updated `_redirect_to_smriti_home()` in `main.js` to dynamically detect the current path base (supporting both `/app` and `/desk`) to prevent redirection failures or skipped lifecycle handlers.

### 4. Billing Page Synchronizations
- **Synchronized Controllers**: Copied the public assets for billing JS/CSS into the active page-level directory (`page/smriti-billing/smriti-billing.js` and `page/smriti-billing/smriti-billing.css`) so they are loaded and applied correctly on the Retail Billing page.
- **Billing Actions**: Added the top navbar Fullscreen and Popout action buttons directly in the active billing layout.

### 5. SMRITI Control Center Dashboard Buttons
- **Multi-Option Action Cards**: Redesigned all action cards (Retail Billing, Day Open/Close, Inventory Operations, Purchase Management, Barcode Printing) in the main Control Center dashboard page (`page/smriti-desk/smriti-desk.js` and `public/js/smriti_desk.js`) to contain both a "Standard" button and a "Popout" button.
- **Explicit Bindings**: Bound specific navigation routes for standard buttons and called `SMRITI.openPopout` directly for the popout buttons.

### 6. Bug Fixes & Corrections
- **Sidebar Syntax Error**: Removed an extra closing brace `};` at the end of `public/js/smriti_sidebar.js` which caused an `Uncaught SyntaxError` and prevented the sidebar from rendering.
- **Purchase Manager DOM Binding**: Wrapped the page `wrapper` parameter in jQuery (`$(wrapper)`) inside `smriti-purchase.js` constructor, resolving a `TypeError: this.wrapper.find is not a function` when loading the Purchase Manager.
- **Global GST Settings Fallback**: Added `window.gst_settings = window.gst_settings || {};` in `public/js/main.js` to ensure the global `gst_settings` object is always defined. This completely prevents `depends_on` visibility evaluations in standard ERPNext list/form views from crashing when bundle loading is delayed or offline.

---

## How to Verify
1. **Refresh the app** using a hard reload (`Ctrl + Shift + R`) to clear browser-cached scripts.
2. **Hover over sidebar items** (e.g. Shift Management, Inventory, Sales Invoices). You will see a small popout icon (`open_in_new`) appear on the right side of the list item.
3. **Click the popout icon** of any menu link. It will launch in a clean, windowed view.
4. **Navigate inside the popout window** to other pages. Verify that popout mode persists and the sidebar remains hidden even when routing.
5. **Verify DocType Forms**: Open a standard Sales Invoice or Customer form in the popout window. Note that the top navbar, breadcrumbs, and sidebars are completely hidden, but the sleek top page header containing the **Save** and **Submit** actions is kept visible and accessible.
6. **Verify Custom Pages**: Open the custom Billing or Item Master Import page in the popout window and verify that the standard `.page-head` is completely hidden, and that the custom layout occupies **100% width** with no white spacing on the left.


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL