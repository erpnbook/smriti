# SMRITI Experience Constitution v1.0

> **Status:** LOCKED — v1.0.0
> **Authority:** Jawahar R. Mallah, Founder & Chief Architect, AITDL
> **Applies to:** All UI Developers, UX Designers, AI Agents, Product Contributors
> **Companion to:** SMRITI_PLATFORM_VISION.md, SMRITI_UI_ARCHITECTURE.md

---

## Purpose

The Platform Vision defines what SMRITI is.
The Engineering Constitution defines how it is built.
This document defines how it **behaves and feels**.

Every page, every form, every button, every word that a business user encounters
must follow the rules in this document. Architecture compliance is necessary but
not sufficient. A correctly-architected page that uses confusing language, broken
navigation, or inconsistent controls is still a failure.

The goal of this constitution is that a retailer in Agra, a store manager in Surat,
and an owner in Mumbai all use SMRITI the same way -- because every page follows
the same rules.

---

## User Personas

Understanding who uses SMRITI determines every other decision in this document.

### Persona 1 -- Store Owner

**Profile:** Business owner. May not be technical. Opens SMRITI on phone and tablet.
Wants to see the health of the business, not the health of the software.

**Primary pages:** Dashboard, Reports, Analytics, PSV
**Key actions:** View sales summary, check inventory value, review staff performance
**Must never see:** Technical errors, DocType names, Platform Engine terminology
**Time available:** 5 minutes per session on average

### Persona 2 -- Store Manager

**Profile:** Operates the store day-to-day. Handles staff, stock, and customer issues.
Power user. Comfortable with software. Uses laptop and tablet.

**Primary pages:** Inventory, Purchase, Customers, Stock Audit, Shift
**Key actions:** Raise purchase orders, receive stock, resolve customer issues, manage shift
**Must never see:** Platform Engine error messages, raw stack traces
**Time available:** Works in SMRITI for hours at a time

### Persona 3 -- Cashier / Billing Staff

**Profile:** Frontline operator. Serves customers directly. Works under time pressure.
Uses the billing screen many times per hour. Must not be interrupted by pop-ups or
slow load times.

**Primary pages:** Billing, POS, Shift
**Key actions:** Create bills, process payments, apply discounts
**Tolerance for errors:** Zero -- a billing error is a customer-facing event
**Time available:** Seconds per transaction

### Persona 4 -- Purchase Manager

**Profile:** Manages vendor relationships and stock replenishment.
Works methodically. Needs accuracy over speed.

**Primary pages:** Purchase, Suppliers, GRN, Inventory
**Key actions:** Create purchase orders, receive goods, verify prices
**Time available:** Works through a queue of tasks daily

### Persona 5 -- CA / Accountant

**Profile:** External or internal accountant. Handles books, GST, filing.
Does NOT use SMRITI directly. Uses TallyPrime or another accounting system.
SMRITI sends data to their system via the Accounting Adapter.

**SMRITI interaction:** None (by design)
**System used:** TallyPrime, Busy, Zoho Books, etc.

---

## Navigation Constitution

### Rule N1 -- Sidebar is the Primary Navigation

Every SMRITI business page must include the standard SMRITI sidebar.
The sidebar shows the user's current location, available modules, and quick actions.
The sidebar must be identical across all pages -- no page-specific sidebar modifications.

### Rule N2 -- Every Page Has a Breadcrumb

Every page must show a breadcrumb trail at the top.
Minimum breadcrumb: Home > [Module Name]
With a record open: Home > [Module Name] > [Record Name]

The breadcrumb is always clickable. Clicking any segment navigates to that level.

### Rule N3 -- Back Navigation is Always Available

Every page and drawer must provide a back or close control.
No page should trap the user -- there is always a way out.

Keyboard: Escape closes the current drawer, dialog, or panel.

### Rule N4 -- No Platform Engine Navigation

No SMRITI page may contain a link, button, or redirect to any Platform Engine URL.
This includes /app/*, /desk/*, /background-jobs, and any frappe.set_route("List", ...) call.

If a business user needs information that is only available in the Platform Engine,
build a Category A SMRITI page to surface that information. (See Category B Protection Rule.)

### Rule N5 -- Navigation is Role-Aware

The sidebar and navigation must only show modules the logged-in user has access to.
Do not show links to pages the user cannot access.
If a user lands on a page they cannot access, show the SMRITI 403 page -- never a
Platform Engine permission error.

---

## Page Constitution

### Rule P1 -- Every Business Page has These Four Elements

1. **Title** -- one H1, in plain retail language (not DocType names)
2. **Search** -- always visible, always focused on Tab or Ctrl+F
3. **Primary Action** -- one prominent button per page context (New, Save, Submit)
4. **Status Indicator** -- current state of the page (Loading, Empty, Error, Data)

### Rule P2 -- Pages Have Three States

**Empty State:** When there is no data to show.
- Show a friendly message explaining why the page is empty
- Offer the primary action to create the first record
- Never show a blank white page

**Loading State:** While data is being fetched.
- Show a skeleton or spinner that matches the page layout
- Never block the page with a full-screen loading overlay for more than 300ms

**Error State:** When something went wrong.
- Show a plain-language error message -- never a stack trace or Python exception
- Offer a "Try Again" action
- Log the technical error to the console, not the UI

### Rule P3 -- Page Titles Use Retail Language

| Use This | Not This |
|---|---|
| Items | Item DocType |
| Customers | Customer Master |
| Bills | Sales Invoice List |
| Purchase Orders | Purchase Order DocType |
| Stock | Stock Ledger Entry |
| Shift | POS Shift |
| Brand | Brand Master |

### Rule P4 -- Pages Are Fast

A business page must display its first meaningful content in under 2 seconds
on a standard 4G connection.

Lists must paginate -- never load all records at once.
Default page size: 50 records for lists, 200 for lookup dropdowns.

---

## Form Constitution

### Rule F1 -- Every Form has a Clear Save Path

Every form that collects data must have:
- A visible Save or Submit button
- A visible Cancel or Discard button
- Keyboard shortcut: Ctrl+S = Save, Escape = Cancel / Close

### Rule F2 -- Validation Happens Before Save

All required fields must be validated before the save request is sent to the API.
Do not show a server-side "Item Name is required" error -- catch it in the UI first.

Validation error display:
- Highlight the field with a red border
- Show the error message directly below the field
- Focus the first invalid field automatically
- Do not clear fields that already have valid data

### Rule F3 -- Required Fields are Marked

Every required field must be visually marked (asterisk or label).
The user must know which fields are mandatory before they start filling the form.

### Rule F4 -- Errors Are Written in Human Language

| System Error | User-Facing Message |
|---|---|
| ValidationError: item_code required | Product code is required |
| DoesNotExistError: Customer not found | This customer was not found |
| PermissionError: No write access | You do not have permission to edit this record |
| frappe.exceptions.LinkValidationError | The selected value is not valid |

Never show exception class names, Python tracebacks, or HTTP status codes to users.

### Rule F5 -- Drawers for Detail, Pages for Lists

Use the Drawer pattern for:
- Creating a new record
- Editing an existing record
- Viewing record details without leaving the list

Use a full Page for:
- Workflows that span multiple steps (e.g., Billing, Purchase)
- Contexts where the list view is not needed

---

## Button and Action Constitution

### Rule B1 -- One Primary Action Per Context

Every page, section, or drawer has exactly one Primary Action button.
It is visually distinct (filled, brand color) and positioned consistently
(top-right on list pages, bottom-right or top-right on forms).

### Rule B2 -- Button Labels Use Verbs

| Use This | Not This |
|---|---|
| Save | Submit Form |
| Add Product | New Item |
| Create Bill | New Sales Invoice |
| Print Label | Generate Barcode PDF |
| Cancel Order | Delete Purchase Order |

### Rule B3 -- Destructive Actions Require Confirmation

Any action that:
- Deletes a record
- Cancels a submitted document
- Clears a form
- Closes a shift

...must show a confirmation dialog before proceeding.

Confirmation dialog must:
- State what will happen in plain language
- Name the record being affected
- Offer a "Confirm" (destructive, red) and "Cancel" (safe) button
- Default focus on "Cancel" to prevent accidental destruction

### Rule B4 -- Loading States on Buttons

When an action is in progress, the button must:
- Show a spinner or "Saving..." text
- Disable itself to prevent double-submission
- Re-enable and restore its label when the action completes or fails

---

## Vocabulary Constitution

The language SMRITI uses in its UI is part of the product experience.
Platform Engine terminology must never reach the business user.

### Forbidden Words (in user-facing text)

| Forbidden | Reason |
|---|---|
| DocType | Platform Engine concept |
| Frappe | Platform Engine name |
| ERPNext | Platform Engine product name |
| Workspace | Frappe UI concept |
| Desk | Frappe UI concept |
| Document | Generic -- use the actual name (Bill, Order, etc.) |
| Party | Generic -- use Customer or Supplier |
| Master | Generic -- use the actual name (Customer Directory, Item Catalog, etc.) |
| Submit | Frappe workflow concept -- use "Confirm" or "Create Bill" |
| Amend | Frappe workflow concept -- use "Edit" or "Revise" |
| Cancel (for docstatus) | Use "Void" or "Reverse" instead when referring to submitted documents |

### Preferred Vocabulary

| Concept | SMRITI Word |
|---|---|
| Sales Invoice | Bill |
| Purchase Order | Purchase Order (this one is universally understood) |
| Stock Entry | Stock Adjustment |
| Item | Product or Item (both are acceptable in retail context) |
| Customer Master | Customer Directory |
| Item Group | Category |
| Brand | Brand |
| Warehouse | Store (or Warehouse if multi-location) |
| Price List | Price List (universally understood) |

### Error Messages Use Retail Context

When validation fails because of a business rule, the message must explain
the business reason, not the technical reason.

Example:
- WRONG: "frappe.exceptions.ValidationError: cost_price cannot exceed mrp"
- RIGHT: "Cost price cannot be higher than the selling price (MRP). Please check the values."

---

## Keyboard Shortcuts Constitution

Every SMRITI page must support these universal shortcuts:

| Shortcut | Action |
|---|---|
| Ctrl+S | Save the current form |
| Ctrl+N | Open New record (where applicable) |
| Ctrl+F | Focus the search bar on the current page |
| Escape | Close the current drawer, dialog, or panel |
| Enter | Confirm the active dialog (primary action) |
| Tab | Move to next form field |
| Shift+Tab | Move to previous form field |

Billing-specific shortcuts (Persona 3 -- Cashier):

| Shortcut | Action |
|---|---|
| Ctrl+B | New Bill |
| Ctrl+P | Print current bill |
| F2 | Focus item search in billing |
| F12 | Open payment panel |

These shortcuts must be documented in the SMRITI Help page.

---

## Search Constitution

### Rule S1 -- Every Business Page Has Search

No business page may exist without a search bar.
Search is the primary way business users find records.
The search bar must be visible without scrolling.

### Rule S2 -- Search is Instant

Search results must appear within 300ms of the user stopping typing.
Use debouncing (250ms) on the search input.
Do not require the user to press Enter to trigger search.

### Rule S3 -- Search Scope is Retailer-Aware

Search must search across the fields the retailer actually uses:
- Items: item_name, item_code, barcode, brand
- Customers: customer_name, mobile, email, customer_group
- Suppliers: supplier_name, mobile, gstin
- Bills: bill number, customer name, date
- Purchase: PO number, supplier name, date

Do not search only by system ID or document name.

### Rule S4 -- Empty Search Results Are Friendly

If search returns no results:
- Show a clear "No results found" message
- Suggest checking the spelling
- Offer the primary action to create a new record if appropriate

---

## Dashboard Constitution

### Rule D1 -- The Dashboard Belongs to the Owner Persona

The main SMRITI Dashboard is designed for Persona 1 (Store Owner).
It shows the health of the business, not the health of the software.

Required sections:
- Today's Sales (revenue, transaction count, average bill value)
- Inventory Value (current stock value across warehouses)
- Purchase Summary (pending orders, recent receipts)
- Top Products (by sales volume in current period)
- Alerts (low stock, pending approvals, failed sync)

### Rule D2 -- Every KPI Has an Explain Button

Every calculated KPI, score, or metric on the dashboard must have an (i) Explain button.
Clicking it shows:
- What this number means in plain language
- How it was calculated (formula)
- What the user should do if the number is concerning

This is required by the Formula Registry policy (DOC-02).

### Rule D3 -- Dashboard Metrics Come From the Platform Engine Via Repository

Dashboard data must flow through:
  SMRITI Dashboard -> smriti_*_api -> smriti_*_service -> smriti_*_repository -> Platform Engine

Dashboard must NEVER call frappe.client.get_list directly.
(This is also enforced by the Architecture Guard.)

### Rule D4 -- Dashboard Must Load in Under 3 Seconds

Use lazy loading for non-critical sections.
Show critical KPIs (today's sales) first, then load secondary cards progressively.

---

## AI Behavior Constitution

SMRITI's AI capabilities are Category D (Pure SMRITI Innovation).
The rules below govern how AI presents itself to business users.

### Rule AI1 -- AI Recommends, Humans Decide

AI must never take a business action automatically without explicit human approval.

Allowed: "We suggest reordering 50 units of Nike Air Max 90. [Order Now] [Dismiss]"
Forbidden: Auto-creating a purchase order without user confirmation

### Rule AI2 -- Every AI Suggestion is Explainable

Every AI recommendation must show:
- What it recommends
- Why it recommends it (in plain retail language)
- The data it used to reach the recommendation
- The confidence level (if applicable)

Clicking the Explain button on any AI card shows the full calculation.

### Rule AI3 -- AI Uses Retail Language

AI output must never contain:
- Technical model names or algorithm names
- Statistical jargon (regression, confidence interval)
- Platform Engine concepts (DocType, ORM, Ledger)

AI output must use:
- The retailer's own product names and category names
- Plain retail language ("This product is selling fast", "Stock may run out in 5 days")
- Simple numbers with context ("You have 12 units. At current sales rate, this lasts 3 days.")

### Rule AI4 -- AI is a Feature Flag

All AI features must be behind a feature flag.
AI features must not be exposed until they have been tested and verified
against real retail data.

---

## Compliance with This Constitution

This constitution is enforced by:

1. **Architecture Guard (Guard 5 -- UX Boundary)** [Planned]
   Automated checks for missing Search, Save, Cancel, and Breadcrumb on every page.

2. **Design Tokens** (smriti_retail_os/public/css/smriti_tokens.css)
   Token-based CSS ensures visual consistency without page-level overrides.

3. **Code Review**
   Any PR that introduces:
   - Forbidden vocabulary in user-facing text
   - Missing breadcrumb or search
   - Missing form Save/Cancel
   - Direct frappe.client.* calls from UI
   ...must be rejected and revised.

4. **User Acceptance Testing**
   Every new page must be tested by a non-technical user (matching one of the five personas)
   before it is considered complete.

---

## Constitution Checklist (for every new page or form)

Before a page is declared A2 (fully migrated) or "new page complete", verify:

Navigation:
- [ ] SMRITI sidebar present
- [ ] Breadcrumb present and clickable
- [ ] No Platform Engine navigation links or buttons
- [ ] Back / Close control present

Page structure:
- [ ] H1 title in retail language (no DocType names)
- [ ] Search bar visible without scrolling
- [ ] Primary action button present
- [ ] Empty, Loading, and Error states handled

Forms:
- [ ] Required fields marked
- [ ] Ctrl+S saves, Escape cancels
- [ ] Validation messages in plain retail language
- [ ] No stack traces or exception names visible

Data layer:
- [ ] No frappe.client.* calls in the page JavaScript
- [ ] All data routed through SMRITI API endpoints
- [ ] Architecture Guard clean (Guard 1, ratchet mode)

Language:
- [ ] No forbidden vocabulary in any user-visible text
- [ ] Button labels use verbs
- [ ] Error messages describe the business problem, not the technical cause

AI (if applicable):
- [ ] Explain button present on every AI recommendation
- [ ] No automatic business actions without user confirmation
- [ ] AI uses retail language only

---

*SMRITI Experience Constitution v1.0.0*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Status: LOCKED*
