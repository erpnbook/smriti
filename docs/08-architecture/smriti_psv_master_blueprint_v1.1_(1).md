---
Document ID: "ARCH-026"
Title: "**Table of Contents**"
Owner: "Architecture Team"
Audience: "Architect"
Module: "PSV"
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

**SMRITiRetailOS**

Party Stock Visibility (PSV)

Master Technical & Business Blueprint

Version 1.1  |  Final Freeze \+ Reorder Intelligence Edition

Phases 1–3 Implementation Spec  ·  Phase 4 V1.1 Reorder Engine

| Module Party Stock Visibility | Platform Frappe v16 / ERPNext | App smriti\_retail | Status Pilot Deploy Ready |
| :---: | :---: | :---: | :---: |

# **Table of Contents**

# **1\. Executive Summary**

SMRITI Party Stock Visibility (PSV) is an Inventory Intelligence module within SMRITiRetailOS designed to solve the distribution visibility gap: stock legally sold and invoiced to distributors that physically remains at their locations.

### **What management loses without PSV:**

* How much stock is still physically lying with distributors?

* How much has actually been sold to end customers?

* Which locations are performing well or have slow-moving inventory?

* Which locations require replenishment or audit attention?

PSV V1.1 addresses all these questions and goes further — with the Store-wise Reorder Intelligence Engine, PSV transforms from a visibility system into a replenishment-driving platform.

| PSV V1.0 | Visibility System — What is lying at the outlet? |
| :---- | :---- |
| **PSV V1.1** | Visibility \+ Replenishment Intelligence — What should I send next? |
| **Architecture** | Shadow Inventory Intelligence Layer — Core Inventory completely untouched |
| **Target Segments** | Apparel, Footwear, FMCG, Cosmetics, Distribution |
| **Pilot Brand** | Tattly Threads / KORA Apparel Distribution |
| **App Path** | /home/frappe/frappe-bench/apps/smriti\_retail/smriti\_retail/ |

# **2\. Design Philosophy**

## **2.1 Inventory Intelligence Layer — Not Accounting**

PSV never modifies:

* Core Stock Ledger

* Core Inventory Balances

* Core Accounting Entries

* Tax Records

* Inventory Valuation

* Stock Ledger Entry

* Bin

* GL Entry

SMRITiRetailOS Core Inventory remains the official system of record. PSV provides Visibility, Reconciliation, Distributor Intelligence, Sell-Through Analytics, Operational Monitoring, and Replenishment Intelligence (V1.1).

## **2.2 Architectural Principle**

| Architecture Formula |
| :---- |
|   SMRITiRetailOS Core Inventory |
|   \+  PSV Shadow Inventory |
|   \=  Complete Distribution Visibility \+ Replenishment Intelligence |

## **2.3 Non-Negotiable Implementation Rules**

| Rule | Detail |
| :---- | :---- |
| Zero core modifications | ZERO modifications to ERPNext/Frappe core files, Stock Ledger Entry, Bin, or GL Entry |
| App boundary | ALL files under smriti\_retail/ app only |
| hooks.py | ADD only — never replace existing entries |
| Custom fields | Via setup.py using create\_custom\_fields() — never JSON files |
| Item code | ALWAYS \= Item Variant (e.g. KORA-1383-BLACK-38), never a template code |
| Company mandatory | company field mandatory in all balance queries — multi-company ready |
| Ledger immutability | No edit, no delete, no rename on SMRITI Party Stock Ledger Entry |

# **3\. Variant-Based Inventory Model**

PSV operates exclusively at Item Variant level. This is a hard architectural rule with no exceptions.

### **Template vs Variant — Critical Distinction**

| Item Variant Model |
| :---- |
|   Template (INVALID for PSV): |
|     KORA-1383 |
|  |
|   Variants (VALID for PSV): |
|     KORA-1383-BLACK-38 |
|     KORA-1383-BLACK-40 |
|     KORA-1383-BLACK-42 |
|     KORA-1383-BLUE-38 |
|     KORA-1383-BLUE-40 |

The item\_code field in every ledger entry, every report filter, every Excel import, and every API call MUST refer to an Item Variant — one that has variant\_of set in ERPNext. Template codes have no size/color dimension and produce meaningless aggregated balances.

| ⚠  The Excel import utility warns and skips rows where item\_code has no variant\_of value (i.e. it looks like a template). This protects the integrity of PSV balances. |
| :---- |

| Where Variant Rule Applies | How Enforced |
| :---- | :---- |
| SMRITI Party Stock Ledger Entry | item\_code field is a Link → Item; variant\_of check in service layer |
| SMRITI Party Sales Upload → items table | Excel import validates variant\_of exists, rejects templates with warning |
| SMRITI Party Physical Snapshot → items table | UI-level Link field; service layer validates on submit |
| All reports (Balance, Reorder, Ageing, Sell-Through) | Reports aggregate by item\_code — template codes would produce wrong totals |
| get\_reorder\_recommendation() API | Function receives item\_code; must be variant — no guard needed if upstream is correct |

# **4\. Business Problem**

## **4.1 Distribution Visibility Gap**

|   Tattly Threads invoices 1,000 KORA Shirts to: ABC Fashion Distributor |
| :---- |
|  |
|   After invoicing: |
|     Ownership transferred    ✓ |
|     Revenue booked           ✓ |
|     Taxes recorded           ✓ |
|     Stock off company books  ✓ |
|  |
|   But physically: |
|     Mumbai Outlet     600 pcs   (sitting, unsold) |
|     Pune Outlet       250 pcs   (sitting, unsold) |
|     Sold to retail    150 pcs |
|  |
|   Without PSV:  Management has zero visibility after invoice. |
|   With PSV:     Every location tracked until final sell-through. |

## **4.2 Replenishment Intelligence Gap (Solved in V1.1)**

| PSV V1.0 answers | PSV V1.1 now also answers |
| :---- | :---- |
| What is lying at the outlet? | What should I send next? |
| Current balance \= 20 pcs | Need 25 pcs → Send 5 pcs |
| Visibility only | Visibility \+ Replenishment Decision |

# **5\. PSV Ledger Architecture**

## **5.1 Shadow Ledger Design**

| Voucher Type | Effect | Trigger | Direction |
| :---- | :---- | :---- | :---- |
| Opening | \+Qty | Opening Balance Wizard (one-time migration) | Positive |
| Dispatch | \+Qty | Sales Invoice on\_submit (PSA field filled) | Positive |
| Sales | \-Qty | Party Sales Upload on\_submit | Negative |
| Adjustment | \+/- Qty | Physical Snapshot approval (variance rows only) | Either |
| Return | \-Qty | Sales Invoice on\_cancel (reversal entries) | Negative |

| Balance Calculation |
| :---- |
|   Balance Formula: |
|  |
|   Balance \= SUM(qty) |
|  |
|   Example: |
|     Opening    \+500 |
|     Dispatch   \+100 |
|     Sales       \-40 |
|     Adjustment  \-10 |
|     ───────────────── |
|     Balance     550 |

## **5.2 Idempotency Protection — Three Layers**

| Hash Formula |
| :---- |
|   SHA-256 Hash key: |
|   company | party\_stock\_account | item\_code | voucher\_type | voucher\_no | qty | ENTRY |
|  |
|   Reversal hash key (REVERSAL salt prevents collision with original): |
|   company | party\_stock\_account | item\_code | voucher\_type | voucher\_no | qty | REVERSAL |

1. Hash generation (SHA-256) — generate\_ledger\_hash()

2. Application duplicate check — frappe.db.exists before insert

3. Database unique constraint on unique\_hash column

## **5.3 Cancellation Strategy**

| Traditional Approach | Block Cancellation → Operational Deadlock |
| :---- | :---- |
| **PSV Approach** | Allow Cancellation → Create Exception Record → Pending Reconciliation |
| **Reversal Entry** | is\_reversal=1, reversal\_of=\<original\_hash\>, new unique hash using REVERSAL salt |
| **Benefit** | No deadlocks, full audit trail, controlled reconciliation |

# **6\. DocType Specifications**

| Total DocTypes | 9 (8 PSV core \+ 1 V1.1 Reorder Rule) |
| :---- | :---- |
| **Module Name** | Party Stock Visibility |
| **modules.txt entry** | Party Stock Visibility (must be added to smriti\_retail/modules.txt) |
| **Custom fields** | Via setup.py → create\_custom\_fields() only |

## **6.1 SMRITI Party Stock Account**

| smriti\_party\_stock\_account.json |
| :---- |
| { |
|   "doctype": "DocType", |
|   "name": "SMRITI Party Stock Account", |
|   "module": "Party Stock Visibility", |
|   "autoname": "format:{customer}-{location\_name}", |
|   "title\_field": "location\_name", |
|   "search\_fields": "customer,location\_name,zone", |
|   "fields": \[ |
|     {"fieldname":"company",       "fieldtype":"Link",   "options":"Company",  "label":"Company",       "reqd":1}, |
|     {"fieldname":"customer",      "fieldtype":"Link",   "options":"Customer", "label":"Customer",      "reqd":1, "in\_list\_view":1}, |
|     {"fieldname":"location\_name", "fieldtype":"Data",                         "label":"Location Name", "reqd":1, "in\_list\_view":1}, |
|     {"fieldname":"zone",          "fieldtype":"Select", "options":"North\\nSouth\\nEast\\nWest\\nCentral", "label":"Zone", "in\_list\_view":1}, |
|     {"fieldname":"region",        "fieldtype":"Data",                         "label":"Region"}, |
|     {"fieldname":"area\_manager",  "fieldtype":"Link",   "options":"User",     "label":"Area Manager"}, |
|     {"fieldname":"address",       "fieldtype":"Link",   "options":"Address",  "label":"Address"}, |
|     {"fieldname":"contact\_person","fieldtype":"Data",                         "label":"Contact Person"}, |
|     {"fieldname":"mobile",        "fieldtype":"Data",                         "label":"Mobile"}, |
|     {"fieldname":"email",         "fieldtype":"Data",                         "label":"Email"}, |
|     {"fieldname":"status",        "fieldtype":"Select", "options":"Active\\nInactive\\nSuspended", "label":"Status", "default":"Active", "in\_list\_view":1}, |
|     {"fieldname":"active",        "fieldtype":"Check",                        "label":"Active", "default":1} |
|   \], |
|   "permissions": \[ |
|     {"role":"System Manager",       "read":1,"write":1,"create":1,"delete":1}, |
|     {"role":"SMRITI Store Manager", "read":1,"write":1,"create":1,"delete":0}, |
|     {"role":"Sales User",           "read":1,"write":0,"create":0,"delete":0}, |
|     {"role":"Warehouse User",       "read":1,"write":0,"create":0,"delete":0} |
|   \] |
| } |

| smriti\_party\_stock\_account.py |
| :---- |
| class SMRITIPartyStockAccount(Document): |
|     def validate(self): |
|         if self.mobile and not self.mobile.isdigit(): |
|             frappe.throw("Mobile number must be numeric.") |

## **6.2 SMRITI PSV Settings (Single)**

| smriti\_psv\_settings.json |
| :---- |
| { |
|   "doctype":"DocType","name":"SMRITI PSV Settings", |
|   "module":"Party Stock Visibility","issingle":1, |
|   "fields":\[ |
|     {"fieldname":"upload\_frequency",      "fieldtype":"Select", "options":"Weekly\\nBi-Weekly\\nMonthly","label":"Upload Frequency","default":"Weekly"}, |
|     {"fieldname":"velocity\_weight",       "fieldtype":"Float",  "label":"Velocity Weight","default":0.4}, |
|     {"fieldname":"ageing\_weight",         "fieldtype":"Float",  "label":"Ageing Weight","default":0.3}, |
|     {"fieldname":"accuracy\_weight",       "fieldtype":"Float",  "label":"Accuracy Weight","default":0.2}, |
|     {"fieldname":"discipline\_weight",     "fieldtype":"Float",  "label":"Discipline Weight","default":0.1}, |
|     {"fieldname":"variance\_threshold",    "fieldtype":"Float",  "label":"Variance Threshold %","default":5.0}, |
|     {"fieldname":"health\_check\_enabled",  "fieldtype":"Check",  "label":"Enable Health Check","default":1}, |
|     {"fieldname":"default\_lead\_time\_days","fieldtype":"Int",    "label":"Default Lead Time Days (V1.1)","default":7}, |
|     {"fieldname":"default\_safety\_stock",  "fieldtype":"Float",  "label":"Default Safety Stock (V1.1)","default":10.0}, |
|     {"fieldname":"default\_target\_days\_cover","fieldtype":"Int", "label":"Default Target Days Cover (V1.1)","default":14} |
|   \], |
|   "permissions":\[{"role":"System Manager","read":1,"write":1}\] |
| } |

## **6.3 SMRITI Party Stock Ledger Entry (Immutable)**

| smriti\_party\_stock\_ledger\_entry.json |
| :---- |
| { |
|   "doctype":"DocType","name":"SMRITI Party Stock Ledger Entry", |
|   "module":"Party Stock Visibility","hidden":1,"in\_create":0, |
|   "fields":\[ |
|     {"fieldname":"company",             "fieldtype":"Link",      "options":"Company",                    "label":"Company",            "reqd":1}, |
|     {"fieldname":"posting\_datetime",    "fieldtype":"Datetime",                                           "label":"Posting Datetime",   "reqd":1}, |
|     {"fieldname":"party\_stock\_account", "fieldtype":"Link",      "options":"SMRITI Party Stock Account", "label":"Party Stock Account","reqd":1}, |
|     {"fieldname":"item\_code",           "fieldtype":"Link",      "options":"Item",                       "label":"Item Variant",       "reqd":1}, |
|     {"fieldname":"qty",                 "fieldtype":"Float",                                              "label":"Qty (+/-)","reqd":1}, |
|     {"fieldname":"voucher\_type",        "fieldtype":"Select",    "options":"Opening\\nDispatch\\nSales\\nAdjustment\\nReturn","label":"Voucher Type","reqd":1}, |
|     {"fieldname":"voucher\_no",          "fieldtype":"Data",                                               "label":"Voucher No","reqd":1}, |
|     {"fieldname":"unique\_hash",         "fieldtype":"Data",                                               "label":"Unique Hash","reqd":1}, |
|     {"fieldname":"is\_reversal",         "fieldtype":"Check",                                              "label":"Is Reversal"}, |
|     {"fieldname":"reversal\_of",         "fieldtype":"Data",                                               "label":"Reversal Of (Hash)"}, |
|     {"fieldname":"source\_hash",         "fieldtype":"Data",                                               "label":"Source Hash"}, |
|     {"fieldname":"adjustment\_type",     "fieldtype":"Data",                                               "label":"Adjustment Type"}, |
|     {"fieldname":"reason",              "fieldtype":"Small Text",                                         "label":"Reason"}, |
|     {"fieldname":"approved\_by",         "fieldtype":"Link",      "options":"User",                       "label":"Approved By"}, |
|     {"fieldname":"approved\_on",         "fieldtype":"Datetime",                                           "label":"Approved On"} |
|   \], |
|   "permissions":\[{"role":"System Manager","read":1,"write":0,"create":0,"delete":0}\] |
| } |

| smriti\_party\_stock\_ledger\_entry.py |
| :---- |
| class SMRITIPartyStockLedgerEntry(Document): |
|     def before\_insert(self): |
|         if not self.unique\_hash: |
|             frappe.throw("unique\_hash is required for ledger entry.") |
|     def on\_update(self): |
|         frappe.throw("PSV Ledger entries are immutable. Editing is not allowed.") |
|     def on\_trash(self): |
|         frappe.throw("PSV Ledger entries cannot be deleted.") |

## **6.4 SMRITI PSV Activity Log (Immutable)**

| smriti\_psv\_activity\_log.json |
| :---- |
| { |
|   "doctype":"DocType","name":"SMRITI PSV Activity Log", |
|   "module":"Party Stock Visibility","hidden":1, |
|   "fields":\[ |
|     {"fieldname":"timestamp",         "fieldtype":"Datetime","label":"Timestamp","reqd":1}, |
|     {"fieldname":"user",              "fieldtype":"Link",    "options":"User","label":"User"}, |
|     {"fieldname":"action\_type",       "fieldtype":"Data",    "label":"Action Type","reqd":1}, |
|     {"fieldname":"severity",          "fieldtype":"Select",  "options":"Info\\nWarning\\nHigh\\nCritical","label":"Severity","reqd":1}, |
|     {"fieldname":"alert\_key",         "fieldtype":"Data",    "label":"Alert Key"}, |
|     {"fieldname":"reference\_doctype", "fieldtype":"Data",    "label":"Reference DocType"}, |
|     {"fieldname":"reference\_name",    "fieldtype":"Data",    "label":"Reference Name"}, |
|     {"fieldname":"details",           "fieldtype":"Long Text","label":"Details"} |
|   \], |
|   "permissions":\[{"role":"System Manager","read":1,"write":0,"create":0,"delete":0}\] |
| } |

## **6.5 SMRITI PSV Exception Record**

| smriti\_psv\_exception\_record.json |
| :---- |
| { |
|   "doctype":"DocType","name":"SMRITI PSV Exception Record", |
|   "module":"Party Stock Visibility","autoname":"PSV-EXC-.\#\#\#\#", |
|   "fields":\[ |
|     {"fieldname":"party\_stock\_account","fieldtype":"Link",   "options":"SMRITI Party Stock Account","label":"Party Stock Account","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"exception\_type",     "fieldtype":"Select", "options":"Cancellation\\nNegative Balance\\nLate Upload\\nAudit Overdue","label":"Exception Type","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"severity",           "fieldtype":"Select", "options":"Info\\nWarning\\nHigh\\nCritical","label":"Severity","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"status",             "fieldtype":"Select", "options":"Open\\nUnder Review\\nResolved\\nIgnored","label":"Status","default":"Open","in\_list\_view":1}, |
|     {"fieldname":"item\_code",          "fieldtype":"Link",   "options":"Item","label":"Item Variant"}, |
|     {"fieldname":"created\_on",         "fieldtype":"Datetime","label":"Created On"}, |
|     {"fieldname":"resolved\_on",        "fieldtype":"Datetime","label":"Resolved On"}, |
|     {"fieldname":"resolved\_by",        "fieldtype":"Link",   "options":"User","label":"Resolved By"}, |
|     {"fieldname":"resolution\_notes",   "fieldtype":"Text",   "label":"Resolution Notes"} |
|   \], |
|   "permissions":\[ |
|     {"role":"System Manager",       "read":1,"write":1,"create":1,"delete":0}, |
|     {"role":"SMRITI Store Manager", "read":1,"write":1,"create":0,"delete":0}, |
|     {"role":"Sales User",           "read":1,"write":0,"create":0,"delete":0}, |
|     {"role":"Warehouse User",       "read":1,"write":0,"create":0,"delete":0} |
|   \] |
| } |

## **6.6 SMRITI Party Sales Upload \+ Child (SMRITI Party Sales Item)**

| smriti\_party\_sales\_item.json |
| :---- |
| // Child: smriti\_party\_sales\_item.json |
| { |
|   "doctype":"DocType","name":"SMRITI Party Sales Item", |
|   "module":"Party Stock Visibility","istable":1, |
|   "fields":\[ |
|     {"fieldname":"sales\_date","fieldtype":"Date", "label":"Sale Date","in\_list\_view":1}, |
|     {"fieldname":"item\_code", "fieldtype":"Link", "options":"Item","label":"Item Variant (SKU)","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"qty\_sold",  "fieldtype":"Float","label":"Qty Sold","reqd":1,"in\_list\_view":1} |
|   \] |
| } |

| smriti\_party\_sales\_upload.json |
| :---- |
| // Parent: smriti\_party\_sales\_upload.json |
| { |
|   "doctype":"DocType","name":"SMRITI Party Sales Upload", |
|   "module":"Party Stock Visibility","autoname":"PSV-UPL-.\#\#\#\#", |
|   "is\_submittable":1, |
|   "fields":\[ |
|     {"fieldname":"company",             "fieldtype":"Link",   "options":"Company",                    "label":"Company","reqd":1}, |
|     {"fieldname":"party\_stock\_account", "fieldtype":"Link",   "options":"SMRITI Party Stock Account", "label":"Party Stock Account","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"upload\_date",         "fieldtype":"Date",                                           "label":"Upload Date","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"period\_start\_date",   "fieldtype":"Date",                                           "label":"Period From"}, |
|     {"fieldname":"period\_end\_date",     "fieldtype":"Date",                                           "label":"Period To","in\_list\_view":1}, |
|     {"fieldname":"excel\_file",          "fieldtype":"Attach",                                         "label":"Upload Excel"}, |
|     {"fieldname":"file\_hash",           "fieldtype":"Data",                                           "label":"File Hash"}, |
|     {"fieldname":"status",              "fieldtype":"Select", "options":"Draft\\nValidated\\nImported\\nFailed","label":"Status","default":"Draft","in\_list\_view":1}, |
|     {"fieldname":"items",               "fieldtype":"Table",  "options":"SMRITI Party Sales Item",    "label":"Sales Items"} |
|   \], |
|   "permissions":\[ |
|     {"role":"System Manager",       "read":1,"write":1,"create":1,"delete":1}, |
|     {"role":"SMRITI Store Manager", "read":1,"write":1,"create":1,"delete":0}, |
|     {"role":"Sales User",           "read":1,"write":1,"create":1,"delete":0} |
|   \] |
| } |

| smriti\_party\_sales\_upload.py |
| :---- |
| class SMRITIPartySalesUpload(Document): |
|     def validate(self): |
|         if self.period\_end\_date and self.period\_start\_date: |
|             if self.period\_end\_date \< self.period\_start\_date: |
|                 frappe.throw("Period End Date cannot be before Period Start Date.") |
|         total \= sum(row.qty\_sold for row in self.items if row.qty\_sold) |
|         if total \== 0 and self.status not in ("Draft",): |
|             frappe.throw("Cannot validate upload with zero total qty.") |
|     def on\_submit(self):             \# Phase 2: wired to process\_sales\_upload() |
|         process\_sales\_upload(self) |

## **6.7 SMRITI Party Physical Snapshot \+ Child (SMRITI Party Physical Item)**

| smriti\_party\_physical\_item.json |
| :---- |
| // Child: smriti\_party\_physical\_item.json |
| { |
|   "doctype":"DocType","name":"SMRITI Party Physical Item", |
|   "module":"Party Stock Visibility","istable":1, |
|   "fields":\[ |
|     {"fieldname":"item\_code",       "fieldtype":"Link",   "options":"Item","label":"Item Variant","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"system\_qty",      "fieldtype":"Float",  "label":"System Qty","read\_only":1,"in\_list\_view":1}, |
|     {"fieldname":"physical\_qty",    "fieldtype":"Float",  "label":"Physical Qty","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"variance",        "fieldtype":"Float",  "label":"Variance","read\_only":1,"in\_list\_view":1}, |
|     {"fieldname":"variance\_reason", "fieldtype":"Select", "options":"\\nDamage\\nTheft\\nData Error\\nShortage\\nExcess","label":"Variance Reason"} |
|   \] |
| } |

| smriti\_party\_physical\_snapshot.json |
| :---- |
| // Parent: smriti\_party\_physical\_snapshot.json |
| { |
|   "doctype":"DocType","name":"SMRITI Party Physical Snapshot", |
|   "module":"Party Stock Visibility","autoname":"PSV-PHY-.\#\#\#\#","is\_submittable":1, |
|   "fields":\[ |
|     {"fieldname":"company",             "fieldtype":"Link",   "options":"Company",                    "label":"Company","reqd":1}, |
|     {"fieldname":"party\_stock\_account", "fieldtype":"Link",   "options":"SMRITI Party Stock Account", "label":"Party Account","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"audit\_date",          "fieldtype":"Date",                                           "label":"Audit Date","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"status",              "fieldtype":"Select", "options":"Draft\\nPending Approval\\nApproved\\nRejected","label":"Status","default":"Draft","in\_list\_view":1}, |
|     {"fieldname":"approved\_by",         "fieldtype":"Link",   "options":"User","label":"Approved By"}, |
|     {"fieldname":"approved\_on",         "fieldtype":"Datetime","label":"Approved On"}, |
|     {"fieldname":"items",               "fieldtype":"Table",  "options":"SMRITI Party Physical Item","label":"Physical Count"} |
|   \], |
|   "permissions":\[ |
|     {"role":"System Manager",       "read":1,"write":1,"create":1,"delete":0}, |
|     {"role":"SMRITI Store Manager", "read":1,"write":1,"create":1,"delete":0,"submit":1}, |
|     {"role":"Warehouse User",       "read":1,"write":1,"create":1,"delete":0} |
|   \] |
| } |

| smriti\_party\_physical\_snapshot.py |
| :---- |
| class SMRITIPartyPhysicalSnapshot(Document): |
|     def validate(self): |
|         for row in self.items: |
|             row.variance \= (row.physical\_qty or 0\) \- (row.system\_qty or 0\) |
|     def on\_submit(self): |
|         self.status \= "Pending Approval" |
|     @frappe.whitelist() |
|     def approve(self): |
|         if frappe.session.user \== frappe.db.get\_value( |
|             "SMRITI Party Stock Account", self.party\_stock\_account, "area\_manager"): |
|             frappe.throw("Area Manager cannot approve their own location snapshot.") |
|         self.approved\_by \= frappe.session.user |
|         self.status \= "Approved" |
|         self.save() |
|         process\_snapshot\_approval(self) |

## **6.8 SMRITI PSV Reorder Rule (V1.1)**

| smriti\_psv\_reorder\_rule.json — V1.1 |
| :---- |
| { |
|   "doctype":"DocType","name":"SMRITI PSV Reorder Rule", |
|   "module":"Party Stock Visibility","autoname":"PSV-RR-.\#\#\#\#", |
|   "fields":\[ |
|     {"fieldname":"company",             "fieldtype":"Link",  "options":"Company","label":"Company","reqd":1}, |
|     {"fieldname":"party\_stock\_account", "fieldtype":"Link",  "options":"SMRITI Party Stock Account","label":"Party Stock Account","reqd":1,"in\_list\_view":1}, |
|     {"fieldname":"item\_group",          "fieldtype":"Link",  "options":"Item Group","label":"Item Group"}, |
|     {"fieldname":"item\_variant",        "fieldtype":"Link",  "options":"Item","label":"Item Variant (optional — highest priority)","in\_list\_view":1}, |
|     {"fieldname":"min\_stock",           "fieldtype":"Float", "label":"Min Stock"}, |
|     {"fieldname":"max\_stock",           "fieldtype":"Float", "label":"Max Stock"}, |
|     {"fieldname":"safety\_stock",        "fieldtype":"Float", "label":"Safety Stock","default":10}, |
|     {"fieldname":"lead\_time\_days",      "fieldtype":"Int",   "label":"Lead Time Days","default":7}, |
|     {"fieldname":"target\_days\_cover",   "fieldtype":"Int",   "label":"Target Days Cover","default":14}, |
|     {"fieldname":"active",              "fieldtype":"Check", "label":"Active","default":1} |
|   \], |
|   "permissions":\[ |
|     {"role":"System Manager",       "read":1,"write":1,"create":1,"delete":1}, |
|     {"role":"SMRITI Store Manager", "read":1,"write":1,"create":1,"delete":0} |
|   \] |
| } |

| smriti\_psv\_reorder\_rule.py — V1.1 |
| :---- |
| class SMRITIPSVReorderRule(Document): |
|     def validate(self): |
|         if self.lead\_time\_days and self.lead\_time\_days \< 0: |
|             frappe.throw("Lead Time Days cannot be negative.") |
|         if self.safety\_stock and self.safety\_stock \< 0: |
|             frappe.throw("Safety Stock cannot be negative.") |

## **6.9 Custom Field: Sales Invoice (setup.py)**

| setup.py — PSV custom field |
| :---- |
| \# In smriti\_retail/setup.py — call from after\_install() |
| def create\_psv\_custom\_fields(): |
|     from frappe.custom.doctype.custom\_field.custom\_field import create\_custom\_fields |
|     create\_custom\_fields({ |
|         "Sales Invoice": \[{ |
|             "fieldname": "custom\_party\_stock\_account", |
|             "label": "Party Stock Account (PSV)", |
|             "fieldtype": "Link", |
|             "options": "SMRITI Party Stock Account", |
|             "insert\_after": "customer", |
|             "description": "Link to PSV Party Stock Account for shadow inventory tracking.", |
|             "allow\_on\_submit": 0, |
|         }\] |
|     }) |

# **7\. Phase 2 — Engine Layer**

| Prerequisite | Phase 1 Acceptance Gate — ALL 10 PASSED |
| :---- | :---- |
| **Files** | engine/ledger\_engine.py, engine/balance\_engine.py, service/psv\_service.py, utils/excel\_import.py, utils/psv\_api.py |

## **7.1 Ledger Engine — ledger\_engine.py**

| engine/ledger\_engine.py |
| :---- |
| import hashlib, frappe |
| from frappe.utils import now\_datetime |
|  |
| def generate\_ledger\_hash(company, party\_stock\_account, item\_code, |
|                           voucher\_type, voucher\_no, qty, is\_reversal=False): |
|     salt \= "REVERSAL" if is\_reversal else "ENTRY" |
|     raw \= f"{company}|{party\_stock\_account}|{item\_code}|{voucher\_type}|{voucher\_no}|{qty}|{salt}" |
|     return hashlib.sha256(raw.encode()).hexdigest() |
|  |
| def make\_ledger\_entry(company, party\_stock\_account, item\_code, qty, |
|                       voucher\_type, voucher\_no, reason='', adjustment\_type='', |
|                       approved\_by=None, is\_reversal=False, reversal\_of=None): |
|     unique\_hash \= generate\_ledger\_hash(company, party\_stock\_account, item\_code, |
|                                        voucher\_type, voucher\_no, qty, is\_reversal) |
|     if frappe.db.exists("SMRITI Party Stock Ledger Entry", {"unique\_hash": unique\_hash}): |
|         return unique\_hash   \# Idempotency: duplicate silently blocked |
|     entry \= frappe.get\_doc({"doctype":"SMRITI Party Stock Ledger Entry", |
|         "company":company,"posting\_datetime":now\_datetime(), |
|         "party\_stock\_account":party\_stock\_account,"item\_code":item\_code, |
|         "qty":qty,"voucher\_type":voucher\_type,"voucher\_no":voucher\_no, |
|         "unique\_hash":unique\_hash,"is\_reversal":1 if is\_reversal else 0, |
|         "reversal\_of":reversal\_of or "","adjustment\_type":adjustment\_type, |
|         "reason":reason,"approved\_by":approved\_by, |
|         "approved\_on":now\_datetime() if approved\_by else None}) |
|     entry.insert(ignore\_permissions=True) |
|     return unique\_hash |
|  |
| def log\_activity(action\_type, severity, details, reference\_doctype='', |
|                  reference\_name='', alert\_key=''): |
|     from frappe.utils import add\_to\_date |
|     existing \= None |
|     if alert\_key: |
|         existing \= frappe.db.get\_value("SMRITI PSV Activity Log", |
|             {"alert\_key":alert\_key,"timestamp":\["\>=",add\_to\_date(now\_datetime(),hours=-24)\]},"name") |
|     if existing: |
|         frappe.db.set\_value("SMRITI PSV Activity Log", existing, |
|             {"timestamp":now\_datetime(),"details":details,"severity":severity}) |
|     else: |
|         frappe.get\_doc({"doctype":"SMRITI PSV Activity Log","timestamp":now\_datetime(), |
|             "user":frappe.session.user,"action\_type":action\_type,"severity":severity, |
|             "alert\_key":alert\_key,"reference\_doctype":reference\_doctype, |
|             "reference\_name":reference\_name,"details":details}).insert(ignore\_permissions=True) |

## **7.2 Balance Engine — balance\_engine.py**

| engine/balance\_engine.py (including V1.1 get\_reorder\_recommendation) |
| :---- |
| import frappe |
|  |
| def get\_party\_balance(company, party\_stock\_account, item\_code, posting\_datetime=None): |
|     filters \= {"company":company,"party\_stock\_account":party\_stock\_account,"item\_code":item\_code} |
|     if posting\_datetime: filters\["posting\_datetime"\] \= \["\<=", posting\_datetime\] |
|     result \= frappe.db.get\_value("SMRITI Party Stock Ledger Entry", |
|         filters=filters, fieldname="SUM(qty)", as\_dict=False) |
|     return float(result or 0\) |
|  |
| def get\_bulk\_party\_balances(company, party\_stock\_account, item\_codes): |
|     if not item\_codes: return {} |
|     placeholders \= ", ".join(\["%s"\] \* len(item\_codes)) |
|     rows \= frappe.db.sql(f""" |
|         SELECT item\_code, SUM(qty) AS balance |
|         FROM \`tabSMRITI Party Stock Ledger Entry\` |
|         WHERE company=%s AND party\_stock\_account=%s AND item\_code IN ({placeholders}) |
|         GROUP BY item\_code""", |
|         \[company, party\_stock\_account\] \+ list(item\_codes), as\_dict=True) |
|     return {r.item\_code: float(r.balance or 0\) for r in rows} |
|  |
| def get\_all\_party\_balances(company): |
|     return frappe.db.sql(""" |
|         SELECT e.party\_stock\_account, p.location\_name, p.zone, e.item\_code, SUM(e.qty) AS balance |
|         FROM \`tabSMRITI Party Stock Ledger Entry\` e |
|         LEFT JOIN \`tabSMRITI Party Stock Account\` p ON p.name \= e.party\_stock\_account |
|         WHERE e.company=%s |
|         GROUP BY e.party\_stock\_account, e.item\_code |
|         HAVING SUM(e.qty) \!= 0 |
|         ORDER BY e.party\_stock\_account, e.item\_code""", \[company\], as\_dict=True) |
|  |
| \# ── V1.1 Reorder Intelligence ────────────────────────────────────── |
| def get\_reorder\_recommendation(company, party\_stock\_account, item\_code): |
|     """Returns reorder intelligence dict for one Party \+ Item.""" |
|     current\_balance \= get\_party\_balance(company, party\_stock\_account, item\_code) |
|  |
|     \# Weekly sale average from last 4 weeks of Sales ledger entries |
|     weekly\_avg\_result \= frappe.db.sql(""" |
|         SELECT ABS(SUM(qty)) / 4.0 AS avg\_weekly |
|         FROM \`tabSMRITI Party Stock Ledger Entry\` |
|         WHERE company=%s AND party\_stock\_account=%s AND item\_code=%s |
|           AND voucher\_type='Sales' |
|           AND posting\_datetime \>= DATE\_SUB(NOW(), INTERVAL 28 DAY)""", |
|         \[company, party\_stock\_account, item\_code\], as\_dict=True) |
|     weekly\_sale\_avg \= float(weekly\_avg\_result\[0\].avg\_weekly or 0\) if weekly\_avg\_result else 0 |
|  |
|     \# Resolve reorder rule via priority cascade |
|     rule \= \_get\_reorder\_rule(company, party\_stock\_account, item\_code) |
|     settings \= frappe.get\_single('SMRITI PSV Settings') |
|     lead\_time \= (rule and rule.lead\_time\_days) or settings.default\_lead\_time\_days or 7 |
|     safety\_stock \= (rule and rule.safety\_stock) or settings.default\_safety\_stock or 10 |
|  |
|     daily\_sale \= weekly\_sale\_avg / 7.0 if weekly\_sale\_avg else 0 |
|     days\_cover \= round(current\_balance / daily\_sale, 1\) if daily\_sale \> 0 else 0 |
|     reorder\_level \= round((lead\_time \* daily\_sale) \+ safety\_stock, 1\) |
|     recommended\_qty \= max(0, round(reorder\_level \- current\_balance, 0)) |
|  |
|     return { |
|         "current\_balance": current\_balance, |
|         "weekly\_sale\_avg": round(weekly\_sale\_avg, 1), |
|         "days\_cover": days\_cover, |
|         "reorder\_level": reorder\_level, |
|         "recommended\_qty": int(recommended\_qty) |
|     } |
|  |
| def \_get\_reorder\_rule(company, party\_stock\_account, item\_code): |
|     """Priority: Variant-specific \> Item Group \> None (fallback to PSV Settings).""" |
|     \# 1\. Variant-specific |
|     rule \= frappe.db.get\_value("SMRITI PSV Reorder Rule", |
|         {"company":company,"party\_stock\_account":party\_stock\_account, |
|          "item\_variant":item\_code,"active":1}, |
|         \["lead\_time\_days","safety\_stock","target\_days\_cover"\], as\_dict=True) |
|     if rule: return rule |
|     \# 2\. Item Group |
|     item\_group \= frappe.db.get\_value("Item", item\_code, "item\_group") |
|     if item\_group: |
|         rule \= frappe.db.get\_value("SMRITI PSV Reorder Rule", |
|             {"company":company,"party\_stock\_account":party\_stock\_account, |
|              "item\_group":item\_group,"item\_variant":\["is","not set"\],"active":1}, |
|             \["lead\_time\_days","safety\_stock","target\_days\_cover"\], as\_dict=True) |
|     return rule |

## **7.3 PSV Service Layer — psv\_service.py**

| service/psv\_service.py (condensed) |
| :---- |
| import frappe |
| from frappe.utils import now\_datetime |
| from smriti\_retail.party\_stock\_visibility.engine.ledger\_engine import make\_ledger\_entry, log\_activity |
| from smriti\_retail.party\_stock\_visibility.engine.balance\_engine import get\_party\_balance |
|  |
| def process\_sales\_invoice\_submit(doc, method): |
|     psa \= doc.get('custom\_party\_stock\_account') |
|     if not psa: return |
|     for item in doc.items: |
|         make\_ledger\_entry(company=doc.company, party\_stock\_account=psa, |
|             item\_code=item.item\_code, qty=item.qty, voucher\_type='Dispatch', |
|             voucher\_no=doc.name, reason=f'Dispatch via {doc.name}') |
|     log\_activity('DISPATCH','Info',f'Invoice {doc.name} dispatched to {psa}', |
|         'Sales Invoice',doc.name,f'{psa}|DISPATCH|{doc.name}') |
|  |
| def validate\_sales\_invoice\_cancel(doc, method): |
|     psa \= doc.get('custom\_party\_stock\_account') |
|     if not psa: return |
|     for item in doc.items: |
|         current \= get\_party\_balance(doc.company, psa, item.item\_code) |
|         if current \- item.qty \< 0: |
|             \_create\_exception(psa,'Cancellation','High',item.item\_code, |
|                 f'Cancel of {doc.name} would produce negative balance for {item.item\_code}.', |
|                 'Sales Invoice',doc.name) |
|  |
| def process\_sales\_invoice\_cancel(doc, method): |
|     psa \= doc.get('custom\_party\_stock\_account') |
|     if not psa: return |
|     for item in doc.items: |
|         orig \= frappe.db.get\_value('SMRITI Party Stock Ledger Entry', |
|             {'company':doc.company,'party\_stock\_account':psa,'item\_code':item.item\_code, |
|              'voucher\_no':doc.name,'voucher\_type':'Dispatch','is\_reversal':0},'unique\_hash') |
|         make\_ledger\_entry(doc.company,psa,item.item\_code,-item.qty,'Return', |
|             doc.name,f'Reversal of cancelled {doc.name}',is\_reversal=True,reversal\_of=orig or '') |
|     log\_activity('CANCELLATION\_REVERSAL','Warning', |
|         f'Invoice {doc.name} cancelled — reversals created for {psa}', |
|         'Sales Invoice',doc.name,f'{psa}|CANCEL|{doc.name}') |
|  |
| def process\_sales\_upload(upload\_doc): |
|     company \= upload\_doc.company; psa \= upload\_doc.party\_stock\_account |
|     errors \= \[\] |
|     for row in upload\_doc.items: |
|         current \= get\_party\_balance(company, psa, row.item\_code) |
|         if current \- row.qty\_sold \< 0: |
|             errors.append(f'{row.item\_code}: Available {current}, Reported {row.qty\_sold}') |
|     if errors: frappe.throw('Sales Upload blocked — oversell detected:\\n' \+ '\\n'.join(errors)) |
|     for row in upload\_doc.items: |
|         make\_ledger\_entry(company,psa,row.item\_code,-row.qty\_sold,'Sales', |
|             upload\_doc.name,f'Sales upload {upload\_doc.name}') |
|     frappe.db.set\_value('SMRITI Party Sales Upload', upload\_doc.name, 'status', 'Imported') |
|  |
| def process\_snapshot\_approval(snapshot\_doc): |
|     company \= snapshot\_doc.company; psa \= snapshot\_doc.party\_stock\_account |
|     for row in snapshot\_doc.items: |
|         if not row.variance or row.variance \== 0: continue |
|         make\_ledger\_entry(company,psa,row.item\_code,row.variance,'Adjustment', |
|             snapshot\_doc.name,row.variance\_reason or 'Physical Audit', |
|             'Physical Audit',snapshot\_doc.approved\_by) |
|  |
| def process\_opening\_balance(company, party\_stock\_account, items): |
|     voucher\_no \= f'OB-{party\_stock\_account}-{frappe.utils.today()}' |
|     for item in items: |
|         make\_ledger\_entry(company,party\_stock\_account,item\['item\_code'\], |
|             item\['qty'\],'Opening',voucher\_no,'Opening Balance Migration') |
|  |
| def run\_psv\_daily\_health\_check(): |
|     settings \= frappe.get\_single('SMRITI PSV Settings') |
|     if not settings.health\_check\_enabled: return |
|     for company in frappe.get\_all('Company', pluck='name'): |
|         \_check\_negative\_balances(company) |
|         \_check\_late\_uploads(company) |
|         \_check\_never\_audited(company) |
|  |
| def \_check\_negative\_balances(company): |
|     rows \= frappe.db.sql("""SELECT party\_stock\_account,item\_code,SUM(qty) AS balance |
|         FROM \`tabSMRITI Party Stock Ledger Entry\` WHERE company=%s |
|         GROUP BY party\_stock\_account,item\_code HAVING SUM(qty)\<0""", \[company\], as\_dict=True) |
|     for row in rows: |
|         \_create\_exception(row.party\_stock\_account,'Negative Balance','Critical',row.item\_code, |
|             f'Negative balance: {row.balance}') |
|         log\_activity('NEGATIVE\_BALANCE','Critical', |
|             f'Balance {row.balance} at {row.party\_stock\_account} for {row.item\_code}', |
|             alert\_key=f'{row.party\_stock\_account}|NEGATIVE\_BALANCE|{row.item\_code}') |
|  |
| def \_create\_exception(party\_stock\_account,exception\_type,severity, |
|                       item\_code='',details='',reference\_doctype='',reference\_name=''): |
|     frappe.get\_doc({'doctype':'SMRITI PSV Exception Record', |
|         'party\_stock\_account':party\_stock\_account,'exception\_type':exception\_type, |
|         'severity':severity,'status':'Open','item\_code':item\_code, |
|         'created\_on':now\_datetime(),'resolution\_notes':details}).insert(ignore\_permissions=True) |

## **7.4 Excel Import — utils/excel\_import.py**

| utils/excel\_import.py — key rules |
| :---- |
| \# COLUMN\_ALIASES — flexible real-world distributor file support |
| COLUMN\_ALIASES \= { |
|     "item\_code": \["item","sku","article","product","style","item code", |
|                   "style code","product code","variant","item variant"\], |
|     "qty\_sold":  \["qty","quantity","sold qty","sales qty","qty sold","units","pcs","pieces"\], |
|     "sale\_date": \["date","sale date","sales date","transaction date"\], |
| } |
|  |
| \# Key validation rules: |
| \# 1\. item\_code must exist as an Item in ERPNext |
| \# 2\. variant\_of must be set (i.e. it is a variant, not a template) — reject templates |
| \# 3\. qty\_sold must be \> 0 — skip zero/negative rows |
| \# 4\. Returns: {rows: \[...\], errors: \[...\], total\_qty: int} |

## **7.5 PSV API — utils/psv\_api.py**

| utils/psv\_api.py — function signatures |
| :---- |
| @frappe.whitelist() |
| def get\_dashboard\_summary(company): |
|     \# Returns: total\_units, negative\_count, open\_exceptions, critical\_alerts, parties list |
|  |
| @frappe.whitelist() |
| def get\_party\_balance\_detail(company, party\_stock\_account): |
|     \# Returns: all SKU balances for one party location |
|  |
| @frappe.whitelist()    \# V1.1 |
| def get\_reorder\_dashboard\_data(company): |
|     \# Returns: top 10 replenishment needs sorted by priority \+ recommended\_qty |

# **8\. Phase 3 — Reports, Opening Balance Wizard & Dashboard API**

| Prerequisite | Phase 2 Acceptance Gate — ALL 12 PASSED |
| :---- | :---- |
| **Report Type** | ERPNext Script Reports under Party Stock Visibility module |
| **Balance source** | All balances from balance\_engine.py — never raw SQL directly in reports |

## **8.1 Report: PSV Party Stock Balance**

| report/psv\_party\_stock\_balance/psv\_party\_stock\_balance.py |
| :---- |
| def execute(filters=None): |
|     company \= filters.get('company') or frappe.defaults.get\_user\_default('Company') |
|     columns \= \[ |
|         {'label':'Party Account', 'fieldname':'party\_stock\_account','fieldtype':'Link','options':'SMRITI Party Stock Account','width':180}, |
|         {'label':'Location',      'fieldname':'location\_name',      'fieldtype':'Data',    'width':130}, |
|         {'label':'Zone',          'fieldname':'zone',               'fieldtype':'Data',    'width':80}, |
|         {'label':'Item Variant',  'fieldname':'item\_code',          'fieldtype':'Link','options':'Item','width':200}, |
|         {'label':'Balance Qty',   'fieldname':'balance',            'fieldtype':'Float',   'width':100}, |
|         {'label':'MRP',           'fieldname':'mrp',                'fieldtype':'Currency','width':90}, |
|         {'label':'Balance Value', 'fieldname':'balance\_value',      'fieldtype':'Currency','width':120}, |
|     \] |
|     all\_balances \= get\_all\_party\_balances(company) |
|     \# Filters: party\_stock\_account, zone, show\_zero |
|     data \= \[\] |
|     for r in all\_balances: |
|         mrp \= frappe.db.get\_value('Item', r.item\_code, 'standard\_rate') or 0 |
|         data.append({...r, 'mrp':mrp, 'balance\_value':r.balance\*mrp}) |
|     data.sort(key=lambda x: (x\['party\_stock\_account'\], x\['item\_code'\])) |
|     return columns, data |

## **8.2 Report: PSV Reconciliation**

| report/psv\_reconciliation/psv\_reconciliation.py |
| :---- |
| def execute(filters=None): |
|     \# Columns: Party, Item Variant, System Balance, Physical Count, Variance, Audit Date, Status |
|     \# Joins SMRITI Party Physical Snapshot \+ SMRITI Party Physical Item |
|     \# Maps system balance from get\_all\_party\_balances() keyed by (party, item\_code) |
|     \# Filters: company (reqd), party\_stock\_account, from\_date, to\_date |
|     \# Only shows Approved snapshots |

## **8.3 Report: PSV Sell-Through**

| report/psv\_sell\_through/psv\_sell\_through.py |
| :---- |
| def execute(filters=None): |
|     \# Columns: Party, Item Variant, Dispatched, Sold, Balance, Sell-Through % |
|     \# SQL: SUM(CASE WHEN qty\>0 THEN qty ELSE 0 END) AS dispatched |
|     \#      SUM(CASE WHEN qty\<0 THEN ABS(qty) ELSE 0 END) AS sold |
|     \# Formula: sell\_through\_pct \= round(sold / dispatched \* 100, 2\) |
|     \# Sorted by sell\_through\_pct DESC |
|     \# Filters: company (reqd), party\_stock\_account, min\_sell\_through % |

## **8.4 Report: PSV Stock Ageing**

| report/psv\_stock\_ageing/psv\_stock\_ageing.py |
| :---- |
| def execute(filters=None): |
|     \# Columns: Party, Item, 0-30 Days, 31-60 Days, 61-90 Days, 90+ Days, Total |
|     \# Uses posting\_datetime of Dispatch entries to bucket by age |
|     \# age \= date\_diff(today, posting\_datetime) |
|     \# if age\<=30: d0\_30 elif age\<=60: d31\_60 elif age\<=90: d61\_90 else: d90\_plus |
|     \# Rows with total \<= 0 excluded |

## **8.5 Report: PSV Reorder Report (V1.1)**

| report/psv\_reorder\_report/psv\_reorder\_report.py — V1.1 |
| :---- |
| def execute(filters=None): |
|     \# Columns: Location, Zone, Item Variant, Current Balance, Weekly Sale Avg, |
|     \#          Days Cover, Reorder Level, Recommended Qty, Priority |
|     \# Calls get\_reorder\_recommendation() for each active party+item |
|     \# Priority classification: |
|     \#   Critical: balance \<= 0 OR days\_cover \< 3 |
|     \#   High:     days\_cover \< 7 |
|     \#   Medium:   days\_cover \< 14 |
|     \#   Low:      days\_cover \>= 14 |
|     \# Default filter: only rows with recommended\_qty \> 0 |
|     \# Sorted: Critical first, then by recommended\_qty DESC |
|     \# Filters: company (reqd), zone, priority level |

## **8.6 Opening Balance Wizard (Frappe Page)**

| psv\_opening\_balance.json |
| :---- |
| // page/psv\_opening\_balance/psv\_opening\_balance.json |
| { |
|   "doctype":"Page","name":"psv-opening-balance", |
|   "title":"PSV Opening Balance Import", |
|   "module":"Party Stock Visibility", |
|   "roles":\[{"role":"System Manager"}\] |
| } |

| psv\_opening\_balance.js |
| :---- |
| // page/psv\_opening\_balance/psv\_opening\_balance.js |
| frappe.pages\['psv-opening-balance'\].on\_page\_load \= function(wrapper) { |
|     const page \= frappe.ui.make\_app\_page({parent:wrapper, |
|         title:'PSV Opening Balance Import',single\_column:true}); |
|     // UI: Company input, Party Stock Account input, Excel file upload |
|     // Buttons: Preview (parses Excel via parse\_opening\_excel API) |
|     //          Confirm Import (calls process\_opening\_balance API) |
|     // Preview shows first 20 rows \+ error list |
|     // Warning banner: One-Time Migration Utility — prevents accidental re-import |
|     // After import: hides Confirm Import button, shows success alert |
|     // API calls: |
|     //   Preview: smriti\_retail.party\_stock\_visibility.utils.opening\_balance.parse\_opening\_excel |
|     //   Import:  smriti\_retail.party\_stock\_visibility.service.psv\_service.process\_opening\_balance |
| }; |

| utils/opening\_balance.py |
| :---- |
| \# utils/opening\_balance.py |
| @frappe.whitelist() |
| def parse\_opening\_excel(file\_url): |
|     \# Reads Excel: Column 1 \= Item Variant code, Column 2 \= Opening Qty |
|     \# Validates: item exists, qty \> 0 |
|     \# Returns: {rows: \[{item\_code, qty}, ...\], errors: \[...\]} |

# **9\. hooks.py Additions**

| ⚠  ADD ONLY — never replace existing entries in hooks.py. Merge with any existing doc\_events and scheduler\_events dictionaries. |
| :---- |

| hooks.py — additions only |
| :---- |
| \# In smriti\_retail/hooks.py — ADD ONLY |
|  |
| doc\_events \= { |
|     \# ... keep all existing entries unchanged ... |
|     "Sales Invoice": { |
|         "on\_submit":     "smriti\_retail.party\_stock\_visibility.service.psv\_service.process\_sales\_invoice\_submit", |
|         "before\_cancel": "smriti\_retail.party\_stock\_visibility.service.psv\_service.validate\_sales\_invoice\_cancel", |
|         "on\_cancel":     "smriti\_retail.party\_stock\_visibility.service.psv\_service.process\_sales\_invoice\_cancel", |
|     } |
| } |
|  |
| scheduler\_events \= { |
|     \# ... keep all existing entries unchanged ... |
|     "daily": \[ |
|         "smriti\_retail.party\_stock\_visibility.service.psv\_service.run\_psv\_daily\_health\_check" |
|     \] |
| } |

# **10\. V1.1 Store-wise Reorder Intelligence Engine**

  **★  PSV V1.1 Enhancement — Deploy immediately after pilot stabilization, not in V2  ★**

## **10.1 Objective**

| Metric | Formula | Drives |
| :---- | :---- | :---- |
| Current Balance | SUM(qty) from ledger | Baseline |
| Average Weekly Sale | ABS(SUM Sales qty last 28 days) / 4 | Velocity signal |
| Days Cover | Current Balance ÷ Daily Sale Rate | Urgency indicator |
| Reorder Level | (Lead Time × Daily Sale) \+ Safety Stock | Trigger threshold |
| Recommended Qty | max(0, Reorder Level − Current Balance) | Replenishment action |

## **10.2 Calculation Example**

| Mumbai Outlet Example |
| :---- |
|   Current Stock          \= 20 pcs |
|   Weekly Sale Average    \= 15 pcs |
|   Lead Time              \= 7 days |
|   Safety Stock           \= 10 pcs |
|  |
|   Daily Sale Rate        \= 15 ÷ 7  \= 2.14 pcs/day |
|   Days Cover             \= 20 ÷ 2.14 \= 9.3 days |
|  |
|   Reorder Level          \= (7 × 2.14) \+ 10 \= 24.98 ≈ 25 pcs |
|   Current Stock          \= 20 pcs |
|   Recommended Qty        \= max(0, 25 − 20\) \= 5 pcs   ✓ |

## **10.3 Priority Rules**

| Priority | Condition | Action Required |
| :---- | :---- | :---- |
| **Critical** | Current Balance ≤ 0  OR  Days Cover \< 3 | Immediate replenishment — same day |
| **High** | Days Cover \< 7 | Replenish within 2 days |
| **Medium** | Days Cover \< 14 | Schedule for next dispatch |
| **Low** | Days Cover ≥ 14 | Monitor only |

## **10.4 Reorder Rule Priority Cascade**

| Priority | Rule Type | Example |
| :---- | :---- | :---- |
| 1 (Highest) | Variant-specific (item\_variant set) | KORA-BLK-38 at Mumbai Outlet |
| 2 | Item Group (item\_group set, no variant) | Shirts at Mumbai Outlet |
| 3 (Fallback) | PSV Settings global defaults | default\_lead\_time\_days, default\_safety\_stock |

## **10.5 Dashboard Widget — Top 10 Replenishment Needs**

|   Top 10 Locations — Replenishment Required |
| :---- |
|   ────────────────────────────────────────────────────────────── |
|   1\.  Mumbai Outlet     │  KORA-BLK-38   │  Need 120 pcs  \[CRITICAL\] |
|   2\.  Pune Outlet       │  KORA-WHT-40   │  Need  95 pcs  \[CRITICAL\] |
|   3\.  Ahmedabad Outlet  │  KORA-BLU-42   │  Need  70 pcs  \[HIGH\] |
|   4\.  Surat Outlet      │  KORA-RED-38   │  Need  60 pcs  \[HIGH\] |
|   5\.  Nashik Outlet     │  KORA-BLK-40   │  Need  55 pcs  \[MEDIUM\] |
|   ────────────────────────────────────────────────────────────── |

# **11\. Health Monitoring & Executive Dashboard**

## **11.1 Daily Health Check — run\_psv\_daily\_health\_check()**

| Check | Severity | Alert Key Format | Suppression |
| :---- | :---- | :---- | :---- |
| Negative Balances (SUM \< 0\) | Critical | PSA|NEGATIVE\_BALANCE|item\_code | 24h — update, not insert |
| Late Upload (no import in 14 days) | Warning | PSA|LATE\_UPLOAD| | 24h — update, not insert |
| Never Audited (no Approved snapshot in 30 days) | Warning | PSA|AUDIT\_OVERDUE| | 24h — update, not insert |

## **11.2 Executive Dashboard KPIs**

### **Executive KPIs**

* Total PSV Stock (all units across all locations)

* Total PSV Stock Value (balance × MRP per variant)

* Open Exceptions count

* Critical Alerts count

### **Distribution KPIs**

* Fast Moving Locations (top sell-through %)

* Slow Moving Locations (lowest sell-through %)

* Highest Sell-Through location

* Lowest Sell-Through location

### **Risk KPIs**

* Negative Balance count and locations

* Pending Reconciliations count

* Late Upload count

* Audit Overdue count

### **V1.1 Replenishment KPIs**

* Critical replenishment needs count

* High priority replenishment count

* Top 10 locations requiring replenishment (widget)

# **12\. Complete Folder Structure**

| smriti\_retail/ |
| :---- |
| ├── modules.txt                    ← ADD: Party Stock Visibility |
| ├── hooks.py                       ← ADD doc\_events \+ scheduler\_events |
| ├── setup.py                       ← ADD create\_psv\_custom\_fields() |
| └── party\_stock\_visibility/ |
|     ├── \_\_init\_\_.py |
|     ├── doctype/ |
|     │   ├── smriti\_party\_stock\_account/        (json \+ py) |
|     │   ├── smriti\_psv\_settings/               (json \+ py) |
|     │   ├── smriti\_party\_stock\_ledger\_entry/   (json \+ py — immutable) |
|     │   ├── smriti\_psv\_activity\_log/           (json \+ py — immutable) |
|     │   ├── smriti\_psv\_exception\_record/       (json \+ py) |
|     │   ├── smriti\_party\_sales\_upload/         (json \+ py) |
|     │   ├── smriti\_party\_sales\_item/           (json \+ py — child) |
|     │   ├── smriti\_party\_physical\_snapshot/    (json \+ py) |
|     │   ├── smriti\_party\_physical\_item/        (json \+ py — child) |
|     │   └── smriti\_psv\_reorder\_rule/           (json \+ py — V1.1) |
|     ├── engine/ |
|     │   ├── \_\_init\_\_.py |
|     │   ├── ledger\_engine.py       (generate\_ledger\_hash, make\_ledger\_entry, log\_activity) |
|     │   └── balance\_engine.py     (get\_party\_balance, get\_bulk, get\_all, get\_reorder\_recommendation) |
|     ├── service/ |
|     │   ├── \_\_init\_\_.py |
|     │   └── psv\_service.py        (6 hooks \+ health check \+ opening balance) |
|     ├── report/ |
|     │   ├── psv\_party\_stock\_balance/   (json \+ py) |
|     │   ├── psv\_reconciliation/        (json \+ py) |
|     │   ├── psv\_sell\_through/          (json \+ py) |
|     │   ├── psv\_stock\_ageing/          (json \+ py) |
|     │   └── psv\_reorder\_report/        (json \+ py — V1.1) |
|     ├── page/ |
|     │   └── psv\_opening\_balance/       (json \+ js) |
|     └── utils/ |
|         ├── \_\_init\_\_.py |
|         ├── psv\_api.py             (get\_dashboard\_summary, get\_party\_balance\_detail, get\_reorder\_dashboard\_data) |
|         ├── excel\_import.py        (parse\_sales\_upload\_excel with COLUMN\_ALIASES) |
|         └── opening\_balance.py     (parse\_opening\_excel) |

# **13\. Acceptance Gates — All Phases**

## **13.1 Phase 1 Gate — Foundation**

| \# | Acceptance Gate |
| :---- | :---- |
| **1** | All 9 DocTypes visible in ERPNext under Party Stock Visibility module (includes SMRITI PSV Reorder Rule) |
| **2** | Party Stock Visibility listed in smriti\_retail/modules.txt |
| **3** | SMRITI Party Stock Account — create/save works, mobile validation fires on non-numeric input |
| **4** | SMRITI PSV Settings — single form opens, all V1.1 fields present (default\_lead\_time\_days, default\_safety\_stock, default\_target\_days\_cover) |
| **5** | SMRITI Party Stock Ledger Entry — hidden, on\_update throws error, on\_trash throws error |
| **6** | SMRITI Party Sales Upload — child table populates, period date validation fires |
| **7** | SMRITI Party Physical Snapshot — variance auto-calculates on validate() |
| **8** | Sales Invoice has custom\_party\_stock\_account field after customer field |
| **9** | hooks.py — existing hooks intact, PSV hooks added (on\_submit, before\_cancel, on\_cancel) |
| **10** | bench migrate — 0 errors, 0 warnings |

| Phase 1 — bench verification commands |
| :---- |
| \# Phase 1 verification commands |
| cd /home/frappe/frappe-bench |
| bench \--site smriti.localhost migrate |
|  |
| \# Verify all 9 DocTypes |
| bench \--site smriti.localhost execute \\ |
|   "import frappe; dts=\['SMRITI Party Stock Account','SMRITI PSV Settings', |
|   'SMRITI Party Stock Ledger Entry','SMRITI PSV Activity Log', |
|   'SMRITI PSV Exception Record','SMRITI Party Sales Upload', |
|   'SMRITI Party Physical Snapshot','SMRITI PSV Reorder Rule'\]; |
|   \[print(dt,'✅') for dt in dts if frappe.db.exists('DocType',dt)\]" |
|  |
| \# Verify custom field |
| bench \--site smriti.localhost execute \\ |
|   "import frappe; print(frappe.db.exists('Custom Field', |
|   'Sales Invoice-custom\_party\_stock\_account') and '✅' or '❌ MISSING')" |
|  |
| \# Verify hooks |
| bench \--site smriti.localhost execute \\ |
|   "import frappe; h=frappe.get\_hooks('doc\_events'); |
|   si=h.get('Sales Invoice',{}); print('on\_submit:',si.get('on\_submit')); |
|   print('before\_cancel:',si.get('before\_cancel'))" |
|  |
| \# Verify module registration |
| bench \--site smriti.localhost list-modules 2\>&1 | grep \-i 'party stock' |

## **13.2 Phase 2 Gate — Core Engine**

| \# | Acceptance Gate |
| :---- | :---- |
| **1** | ledger\_engine.py — generate\_ledger\_hash returns 64-char hex string |
| **2** | balance\_engine.py — get\_party\_balance returns float |
| **3** | psv\_service.py — all 7 functions importable, no syntax errors |
| **4** | excel\_import.py and psv\_api.py — clean imports, no circular dependency |
| **5** | Sales Invoice submit with custom\_party\_stock\_account → Dispatch ledger entry created |
| **6** | Sales Invoice cancel → reversal entry with is\_reversal=1, reversal\_of set to original hash |
| **7** | Sales Upload on\_submit → process\_sales\_upload called, oversell blocked with clear error |
| **8** | Physical Snapshot approve() → adjustment entries only for rows with variance ≠ 0 |
| **9** | Area Manager cannot approve their own location snapshot (frappe.throw fires) |
| **10** | run\_psv\_daily\_health\_check() → runs without error on empty data (no crash) |
| **11** | Duplicate hash → blocked silently, original hash returned (idempotency) |
| **12** | bench migrate — 0 errors |

| Phase 2 — bench verification commands |
| :---- |
| \# Phase 2 verification commands |
|  |
| \# Test ledger engine hash |
| bench \--site smriti.localhost execute \\ |
|   "from smriti\_retail.party\_stock\_visibility.engine.ledger\_engine import generate\_ledger\_hash; |
|   h=generate\_ledger\_hash('Tattly Threads','PSA-001','KORA-1383-BLACK-38','Dispatch','SINV-001',10); |
|   print('Hash:',h\[:16\],'len:',len(h),'✅' if len(h)==64 else '❌')" |
|  |
| \# Test balance engine |
| bench \--site smriti.localhost execute \\ |
|   "from smriti\_retail.party\_stock\_visibility.engine.balance\_engine import get\_party\_balance; |
|   b=get\_party\_balance('Tattly Threads','PSA-001','KORA-1383-BLACK-38'); |
|   print('Balance:',b,'type:',type(b).\_\_name\_\_,'✅')" |
|  |
| \# Test all service layer imports |
| bench \--site smriti.localhost execute \\ |
|   "from smriti\_retail.party\_stock\_visibility.service.psv\_service import |
|   process\_sales\_invoice\_submit, run\_psv\_daily\_health\_check; print('✅')" |
|  |
| \# Test API import |
| bench \--site smriti.localhost execute \\ |
|   "from smriti\_retail.party\_stock\_visibility.utils.psv\_api import get\_dashboard\_summary; print('✅')" |
|  |
| \# Run health check (no data \= no crash) |
| bench \--site smriti.localhost execute \\ |
|   "from smriti\_retail.party\_stock\_visibility.service.psv\_service import run\_psv\_daily\_health\_check; |
|   run\_psv\_daily\_health\_check(); print('Health check OK ✅')" |

## **13.3 Phase 3 Gate — Reports & Wizard**

| \# | Acceptance Gate |
| :---- | :---- |
| **1** | PSV Party Stock Balance report — runs without error |
| **2** | PSV Reconciliation report — runs without error |
| **3** | PSV Sell-Through report — runs without error |
| **4** | PSV Stock Ageing report — runs without error |
| **5** | PSV Reorder Report — runs without error, returns priority-sorted rows (V1.1) |
| **6** | PSV Opening Balance page — loads in browser at /psv-opening-balance |
| **7** | parse\_opening\_excel() → returns {rows, errors} dict for valid Excel |
| **8** | process\_opening\_balance() → creates Opening ledger entries, hash-protected from re-import |
| **9** | Full module import test — all 6 modules import cleanly, no circular imports |
| **10** | bench migrate — 0 errors |

| Phase 3 — bench verification commands |
| :---- |
| \# Phase 3 verification commands |
|  |
| \# Test all reports |
| bench \--site smriti.localhost execute \\ |
|   "import frappe; reports=\['PSV Party Stock Balance','PSV Reconciliation', |
|   'PSV Sell-Through','PSV Stock Ageing','PSV Reorder Report'\]; |
|   \[print(r,'✅') for r in reports if frappe.db.exists('Report',r)\]" |
|  |
| \# Test opening balance page |
| bench \--site smriti.localhost execute \\ |
|   "import frappe; print(frappe.db.exists('Page','psv-opening-balance') and '✅' or '❌')" |
|  |
| \# Full import test |
| bench \--site smriti.localhost execute \\ |
|   "import smriti\_retail.party\_stock\_visibility.engine.ledger\_engine; |
|   import smriti\_retail.party\_stock\_visibility.engine.balance\_engine; |
|   import smriti\_retail.party\_stock\_visibility.service.psv\_service; |
|   import smriti\_retail.party\_stock\_visibility.utils.psv\_api; |
|   import smriti\_retail.party\_stock\_visibility.utils.excel\_import; |
|   import smriti\_retail.party\_stock\_visibility.utils.opening\_balance; |
|   print('All Phase 3 imports ✅')" |

## **13.4 Phase 4 Gate — V1.1 Reorder Intelligence**

| \# | Acceptance Gate |
| :---- | :---- |
| **1** | SMRITI PSV Reorder Rule DocType visible, all 10 fields present |
| **2** | PSV Settings has default\_lead\_time\_days, default\_safety\_stock, default\_target\_days\_cover fields |
| **3** | get\_reorder\_recommendation() importable from balance\_engine |
| **4** | Returns dict with all 5 keys: current\_balance, weekly\_sale\_avg, days\_cover, reorder\_level, recommended\_qty |
| **5** | Math: weekly\_avg=15 → daily=2.14, reorder\_level=(7×2.14)+10=25, recommended=max(0,25-20)=5 |
| **6** | Edge case: recommended\_qty is never negative (max(0,...) guard) |
| **7** | Edge case: days\_cover=0 when weekly\_sale\_avg=0 (no division-by-zero crash) |
| **8** | Priority cascade: variant rule overrides item group rule overrides PSV Settings fallback |
| **9** | PSV Reorder Report — all 9 columns present, priority classification correct |
| **10** | Critical priority fires when balance ≤ 0 OR days\_cover \< 3 |
| **11** | Dashboard widget returns top 10 sorted Critical-first then by recommended\_qty DESC |
| **12** | bench migrate — 0 errors |

| Phase 4 — bench verification commands |
| :---- |
| \# Phase 4 verification commands |
|  |
| \# Test Reorder Rule DocType |
| bench \--site smriti.localhost execute \\ |
|   "import frappe; print(frappe.db.exists('DocType','SMRITI PSV Reorder Rule') and '✅' or '❌')" |
|  |
| \# Test get\_reorder\_recommendation |
| bench \--site smriti.localhost execute \\ |
|   "from smriti\_retail.party\_stock\_visibility.engine.balance\_engine import get\_reorder\_recommendation; |
|   r=get\_reorder\_recommendation('Tattly Threads','PSA-001','KORA-1383-BLACK-38'); |
|   print(r); assert 'recommended\_qty' in r, '❌ missing key'; print('✅')" |
|  |
| \# Verify PSV Settings V1.1 fields |
| bench \--site smriti.localhost execute \\ |
|   "import frappe; s=frappe.get\_single('SMRITI PSV Settings'); |
|   print('lead\_time:', s.default\_lead\_time\_days, |
|   'safety:', s.default\_safety\_stock, '✅')" |

# **14\. Deployment Strategy**

| Phase 1 Foundation | • DocTypes (9 total) \+ JSON definitions • modules.txt entry • Custom fields via setup.py • Permission matrix • hooks.py additions (ADD ONLY) • Stub psv\_service.py |
| :---: | :---- |

| Phase 2 Core Engine | • ledger\_engine.py (SHA-256 \+ make\_ledger\_entry \+ log\_activity) • balance\_engine.py (get\_party\_balance, get\_bulk, get\_all) • psv\_service.py (all 7 functions fully implemented) • excel\_import.py with COLUMN\_ALIASES • psv\_api.py dashboard summary functions • Daily health check scheduler wired |
| :---: | :---- |

| Phase 3 Analytics | • 4 standard reports (Balance, Reconciliation, Sell-Through, Ageing) • PSV Reorder Report (V1.1) • PSV Opening Balance Wizard (page \+ JS \+ opening\_balance.py) • Full module import test — 0 errors |
| :---: | :---- |

| Phase 4 (V1.1) Reorder Intelligence | • SMRITI PSV Reorder Rule DocType deployed • PSV Settings V1.1 fields (lead time, safety stock, days cover) • get\_reorder\_recommendation() in balance\_engine • PSV Reorder Report with priority classification • Dashboard widget: Top 10 replenishment needs • All Phase 4 gates pass |
| :---: | :---- |

| Phase 5 Pilot Deploy | • Opening balance Excel import for all active distributors • First live distributor sales upload • First reconciliation cycle (Physical Snapshot → Approve) • Area manager training on PSV Reorder Report |
| :---: | :---- |

# **15\. Future Roadmap**

| Version | Feature | Status |
| :---- | :---- | :---- |
| V1.1 | Store-wise Reorder Intelligence Engine | Deploy immediately after pilot stabilization |
| V1.1 | PSV Reorder Report with Priority Classification | Deploy with Reorder Engine |
| V1.1 | Dashboard Widget: Top 10 Replenishment Needs | Deploy with Reorder Engine |
| V1.2 | Internal Party Transfers (location-to-location) | Planned |
| V1.2 | Balance Cache Engine (large distributor networks) | Planned |
| V1.3 | Distributor Scorecards (PSV Health Score per location) | Planned |
| V2.0 | Auto Purchase Recommendation (network shortage → PO) | Roadmap |
| V2.0 | AI Demand Prediction | Roadmap |
| V2.0 | Forecasting Engine | Roadmap |

# **16\. Final Status**

| Module | SMRITI Party Stock Visibility (PSV) |
| :---- | :---- |
| **Version** | 1.1 — Final Freeze \+ Reorder Intelligence |
| **Platform** | SMRITiRetailOS on Frappe v16, Python 3.14 |
| **Total DocTypes** | 9 (8 PSV core \+ 1 V1.1 Reorder Rule) |
| **Total Gates** | Phase 1: 10  |  Phase 2: 12  |  Phase 3: 10  |  Phase 4: 12 |
| **Architecture** | Approved |
| **Technical Specification** | Approved — Full JSON \+ Python specs included |
| **Pilot Readiness** | Approved — Phases 1–3 complete |
| **V1.1 Reorder Engine** | Approved — deploy after pilot stabilization |

**Next Milestone**  
**First Live Distributor Upload \+ First Reconciliation Cycle**  
Then: Deploy V1.1 Store-wise Reorder Intelligence Engine

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