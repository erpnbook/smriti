# SMRITI Retail OS — SMRITI v2 Business Domain & Starter Pack Framework Architecture Proposal

---

## About This Proposal
* **Document Version:** 2.0.0-draft
* **Release Date:** 2026-06-28
* **Intended Audience:** Technical Architects, DevOps Engineers, and Product Managers
* **Learning Objectives:** Architectural design and roadmap details for transitioning SMRITI from a domain-neutral UI/monolithic seeder to a metadata-driven, multi-domain Business Domain & Starter Pack Framework.

---

### Author Section (Start)
* **Author:** Jawahar R. Mallah
* **Designation:** Founder & Chief Architect
* **Organization:** AITDL – AI Technology & Development Lab
* **Professional Experience:** 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."
> 
> — Jawahar R. Mallah
> Founder & Chief Architect, AITDL

---

## 1. Background & Problem Statement
In SMRITI v1.x, the Setup Wizard user interface (UI) was decoupled from footwear-specific wording, rebranding standard masters seeding as the **"Business Starter Pack"**. 

While this successfully resolved the branding and first-impression issue for new installations in generic retail sectors, the backend implementation remained monolithic and hardcoded:
- The setup API seeds all footwear attribute doctypes and generic structures unconditionally.
- Multi-domain retailers (e.g. departmental stores with mixed inventory like apparel + grocery) cannot selectively enable specific attributes.
- Adding a new industry domain requires code changes inside Python functions and HTML wizards.

---

## 2. Proposed Architecture Model

The SMRITI v2 design evolves the installation process into a **metadata-driven framework**:

```
Setup Wizard UI (Domain Selection Checklist)
                │
                ▼
      get_enabled_domains()
                │
                ▼
     SMRITI Business Domain (DocType Registry)
                │
                ▼
      Domain Seed Engine
                │
                ▼
[ Core Pack ] ─── [ Footwear Pack ] ─── [ Grocery Pack ] ─── [ Pharma Pack ]
```

---

## 3. Data Dictionary: SMRITI Business Domain DocType

A new metadata registry DocType named `SMRITI Business Domain` will represent domain starter packs as configurable records:

| Fieldname | Label | Fieldtype | Options | Description |
|---|---|---|---|---|
| `domain_name` | Domain Name | Data | | e.g. "Footwear", "Grocery", "Pharma" |
| `domain_code` | Domain Code | Data | | Unique code, e.g. "FW", "GR", "PH" |
| `description` | Description | Small Text | | Description of what this pack provisions. |
| `is_enabled` | Is Enabled | Check | | Whether the domain is selectable in the wizard. |
| `default_uom` | Default UOM | Link | UOM | Default unit of measurement for this domain. |
| `attribute_pack` | Attribute Pack | Table | SMRITI Attribute Entry | Table of custom attribute types and values. |
| `print_templates` | Print Templates | Table | SMRITI Template Mapping | List of raw label print templates to seed. |
| `barcode_templates` | Barcode Templates | Table | SMRITI Barcode Map | Standard barcode layout configuration. |
| `gst_presets` | GST Presets | Data | | JSON array of recommended GST tax rates. |
| `sample_categories`| Sample Categories | Long Text | | JSON metadata representing sample item categories. |
| `seed_script` | Custom Seed Script | Data | | Python path to run additional seeding (e.g., `smriti_retail_os.seeding.pharma.run`). |

---

## 4. Modular Seed Packs

Seeding logic will be split into isolated, independent controller scripts:

### A. Core Starter Pack
Always enqueued and provisioned. Contains:
- Standard currencies and system configuration.
- Generic POS Profiles and Mode of Payment mappings.
- Base System Roles (`SMRITI Cashier`, `SMRITI Store Manager`, `SMRITI Auditor`, etc.).

### B. Business Domain Packs (Selective)
Provisioned only if the respective domain is selected:
- **Footwear:** Seeds Heel Type, Upper Material, Outsole, Genders, and Footwear size charts.
- **Grocery:** Seeds Brands, Storage Categories (Cold/Dry), Expiry alerts, and Weight-based UOMs.
- **Pharmacy:** Seeds Salt Composition registries, Drug Schedule tags, and HSN presets.
- **Electronics:** Seeds IMEI tracking attributes, Warranty length classes, and Tech Brand structures.

---

## 5. Setup Wizard UI Mockup (SMRITI v2)

The Step 4 UI will dynamically fetch enabled domains and present structured checkboxes:

```
GST & Starter Data

Business Profile
[ ] General Retail
[x] Apparel
[x] Footwear
[ ] Grocery
[ ] Pharmacy

Recommended Starter Data
The following starter packs will be installed based on your selections:

✓ GST Templates
✓ Core Print Formats
✓ Core Barcode Labels
✓ Footwear Attributes & Size Charts
✓ Apparel Categories & Sample Data
✓ Default UOM Presets

Estimated Seeding Time:
15 seconds
```

---

## 6. Implementation Roadmap

### Phase 1: DocType & Fixtures Definition
- Create `SMRITI Business Domain` DocType with child tables for attributes, templates, and script mappings.
- Export standard domains (Footwear, Grocery, Apparel, Pharma) as JSON fixtures.

### Phase 2: Engine Development
- Refactor `setup_smriti_retail_os` to accept a list of domain codes.
- Implement the `Domain Seed Engine` to dynamically parse metadata records and insert Custom Fields and Masters.

### Phase 3: Setup Wizard UI Refinement
- Update Step 4 in `setup_wizard.html` to query domain choices asynchronously.
- Render dynamic domain starter checklists instead of hardcoded labels.

---

### Author Section (End)
* **Author:** Jawahar R. Mallah
* **Designation:** Founder & Chief Architect
* **Organization:** AITDL – AI Technology & Development Lab
* **Professional Experience:** 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."
> 
> — Jawahar R. Mallah
> Founder & Chief Architect, AITDL
