---
Document ID: "USER-004"
Title: "How to Generate E-Way Bills on the E-Way Bill Portal?"
Owner: "Operations Team"
Audience: "End User"
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

# How to Generate E-Way Bills on the E-Way Bill Portal?

**Author:** Annapoorna  
**Updated on:** May 25th, 2026 | ⏱️ **5 min read**

---

The **e-Way Bill (EWB) Portal** provides a seamless, unified gateway to generate e-Way bills (both single and consolidated options), update vehicle numbers on already generated EWBs, cancel generated EWBs, and perform lifecycle management.

E-way bills under the **Form GST EWB-01** structure can be generated through three primary mechanisms:
1. **On the Web Portal** (browser-based interactive generation)
2. **Via SMS** (mobile-based queries)
3. **Through e-Invoicing Integration** (automated API syncing)

*This article focuses on the step-by-step process of generating e-Way bills on the common web portal.*

---

## ⚡ Latest GSTN Advisory: Improvements in the E-Way Bill System

::: info GSTN Advisory — Issued 20 May 2026
GSTN has introduced two major operational developments into the e-way bill system. All entities, including taxpayers, transporters, ERP/API providers, and stakeholder companies, must verify that their systems and configurations are fully compliant with these changes.
:::

### 1. Mandatory "Ship To GSTIN" for Bill-to/Ship-to Transactions
Whenever there is a **Bill-To/Ship-To** transaction, the **"Ship To GSTIN"** must be entered as part of the mandatory dataset when generating the e-Way bill. 

* **Registered Consignee:** Enter the valid 15-digit GSTIN of the shipping recipient.
* **Unregistered Consignee:** If the consignee is an unregistered person acting as the shipping destination, enter **"URP"** (Unregistered Person) in the *Ship To GSTIN* field.

### 2. Voluntary Facility to Close E-Way Bills
A new voluntary **E-Way Bill Closure Facility** has been launched by GSTN. Taxpayers and drivers can now close an e-Way bill after goods have been successfully delivered to their destination.

#### Who Can Close the E-Way Bill?
* **Supplier** (Seller)
* **Recipient** (Buyer)
* **Driver / Authorized Person** (linked with a valid mobile number for closure)

#### Closure via Portal Login (For Registered Users)
For suppliers, receivers, and carriers, the option to close their e-Way bill via the portal login is available under the **e-Way Bill** menu option. Such users can execute closures in two ways:
* **E-Way Bill-wise Closure:** Select and close a single specific EWB.
* **Date-wise Closure:** Batch close EWBs generated on a particular date.

#### Closure via Mobile Number (For Drivers / Authorized Persons)
Authorized personnel can close EWBs via their mobile number using the search function on the e-Way bill common portal. 
* Entering the authorized mobile number will display all active e-Way bills associated with that number.
* The authorized person can then close them directly from this screen.
* *Note:* The mobile number for closure can be specified during EWB generation, especially for the purpose of closure. It can be updated in the event of **Vehicle Updates**, **Consolidated E-way Bill Operations**, or **Validity Extensions**.

#### When Can You Close an E-Way Bill?
You may close an e-way bill on the **same day** that delivery is made, or on the **succeeding day** immediately after.

#### Closing Through API (For ERP, API Users, & System Integrators)
The National Informatics Centre (NIC) has provided the new API changes in the **Sandbox environment**. The deployment timeline is:

::: warning Production Deployment Timeline
* **Sandbox Testing:** Available now for systems integration.
* **Production Go-Live:** Planned by **15 June 2026**.
:::

For closing via the API, system integrators and ERP packages must supply:
1. **Number of the E-Way Bill** (`ewaybill_no`)
2. **Date of Closing** (`close_date`)
3. **Remarks** (`remarks`)

---

## 🛠️ Prerequisites for E-Way Bill Generation

Before initiating an e-Way bill generation under any method, ensure the following prerequisites are in hand:

1. **Active Registration** on the EWB common portal (`ewaybillgst.gov.in`).
2. **Document Details:** The Invoice, Bill of Supply, or Delivery Challan related to the consignment of goods must be readily available.
3. **Transportation Details:**
   * **If transport is by Road:** Transporter ID or the Vehicle Number (e.g. `MH-04-GP-1234`).
   * **If transport is by Rail, Air, or Ship:** Transporter ID, Transport Document Number (e.g. Railway Receipt No, Airway Bill No, Bill of Lading), and the document date.

---

## 📋 Step-by-Step Portal Generation Workflow

1. **Login:** Access the [E-way Bill Portal](https://ewaybillgst.gov.in) and enter your username, password, and captcha.
2. **Navigate:** On the left sidebar menu, click **E-Way Bill** -> **Generate New**.
3. **Form Entry:** Fill in the transactional parameters in **Form GST EWB-01**:
   * **Transaction Type:** Select *Outward* (if supplier) or *Inward* (if recipient).
   * **Sub-Type:** Select Supply, Export, Job Work, SKD/CKD, Recipient Not Known, For Own Use, Exhibition/Fairs, Line Sales, or Others.
   * **Document Details:** Specify Document Type (Invoice, Bill, Challan), Document Number, and Document Date.
   * **Bill From / Bill To Address:** Auto-populates from the user's GSTIN. Ensure the inter-state or intra-state checkboxes align.
   * **Item Details:** Enter HSN Code, description, quantity, taxable value, and CGST/SGST/IGST tax rates.
   * **Transporter / Vehicle Details:** Input Transporter Name, Transporter ID, Distance (in km), Mode of Transport, and Vehicle Number.
4. **Submit:** Click **Submit**. The portal will validate the entry and instantly generate a unique **12-digit E-way Bill number** alongside a QR code.

---

## 🎯 Your Action Plan

To adapt to the latest GSTN improvements before the **15 June 2026** production release, execute the following steps:

* [ ] **Enforce Validation Rules:** Update your POS, billing desk, and ERP databases to ensure `Ship To GSTIN` is treated as a mandatory input for all multi-party wholesales.
* [ ] **Perform Sandbox API Integration:** If you utilize custom API links (such as SMRITI’s automated billing triggers), obtain the latest NIC closure API specs, conduct sandbox testing, and configure the new parameters.
* [ ] **Train Operations Team:** Educate billing managers, dispatch cashiers, and drivers on the voluntary closure workflows to maintain high compliance scores.
* [ ] **Document Adjustments:** Keep log files updated with closing remarks, ensuring seamless compliance audits.

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