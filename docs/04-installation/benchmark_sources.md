---
Document ID: "INSTALL-002"
Title: "SMRITI Benchmark Source Register"
Owner: "Installation Team"
Audience: "Installer"
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

# SMRITI Benchmark Source Register
**File**: docs/audit/evidence/benchmark_sources.md  
**Created**: 2026-06-24  
**Purpose**: Source transparency for all benchmark metrics used in Part 3 of the UX Theme Audit  
**Classification Policy**: Sources are classified only as "DevTools measurement", "Public docs URL", or "Expert assessment — unverified". No URL is listed unless it was fetched and confirmed live. No DevTools measurement is claimed without a screenshot in evidence/screenshots/.

> [!IMPORTANT]
> The majority of entries below are classified as **Expert assessment — unverified**. This is the honest and correct classification. These values were sourced from published design research, industry analysis, and pattern recognition — not from direct measurement of production interfaces. Where public documentation URLs are known, they are listed for reference but not confirmed live unless explicitly stated.

---

### Shopify Admin (Polaris)

- **Metric**: Sidebar width  
- **Value claimed in audit**: ~240px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Polaris design system documentation references sidebar as a "fixed, non-configurable element". Width not published as a specific pixel value in public tokens. Estimated from design system screenshots in published blog posts.  
- **Date observed**: 2026-06-24  

- **Metric**: Table row height  
- **Value claimed in audit**: 40px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Not directly stated in public Polaris docs. Estimated from Polaris DataTable component documentation showing "medium density" rows.  
- **Date observed**: 2026-06-24  

- **Metric**: Base font size  
- **Value claimed in audit**: 14px (0.875rem)  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Polaris typography scale documented as 14px body. Reference: https://polaris.shopify.com/design/typography — URL not confirmed live at time of audit.  
- **Date observed**: 2026-06-24  

- **Metric**: Spacing base grid  
- **Value claimed in audit**: 4px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Polaris spacing system is documented as 4px grid. Confirmed in multiple published Polaris migration guides.  
- **Date observed**: 2026-06-24  

---

### Stripe Dashboard

- **Metric**: Sidebar width  
- **Value claimed in audit**: ~220px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Stripe Dashboard sidebar width not published. Value estimated from Stripe's published UI screenshots in their engineering blog.  
- **Date observed**: 2026-06-24  

- **Metric**: Table row height  
- **Value claimed in audit**: 44px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Stripe's design system (Elements) mentions 44px as the default touch target minimum. Table row alignment inferred from this constraint.  
- **Date observed**: 2026-06-24  

- **Metric**: Base font size  
- **Value claimed in audit**: 14px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Stripe's Elements documentation references `fontSizeBase` as a configurable value, with examples showing 14px as default. Reference: https://stripe.com/docs/elements/appearance-api — URL not confirmed live.  
- **Date observed**: 2026-06-24  

---

### Linear

- **Metric**: Sidebar width  
- **Value claimed in audit**: ~240px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Linear's sidebar width is widely cited as ~240px in design community benchmarks. Not published officially by Linear. Confirmed by independent research sources in web search results dated 2025.  
- **Date observed**: 2026-06-24  

- **Metric**: Table row height  
- **Value claimed in audit**: 36px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Linear's issue list row height cited as 36px compact mode in multiple design benchmarks. Not published in official Linear documentation.  
- **Date observed**: 2026-06-24  

- **Metric**: Base font size  
- **Value claimed in audit**: 13px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Linear is known for aggressive density; 13px base has been cited in design system analysis articles. Not confirmed via DevTools.  
- **Date observed**: 2026-06-24  

---

### Notion

- **Metric**: Sidebar width  
- **Value claimed in audit**: ~240px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Notion's sidebar width is approximately 240px in default state, widely cited in productivity tool comparisons. Not confirmed via DevTools.  
- **Date observed**: 2026-06-24  

- **Metric**: Table row height  
- **Value claimed in audit**: Variable  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Notion database views have variable row heights depending on content and user configuration. No fixed default published.  
- **Date observed**: 2026-06-24  

- **Metric**: Base font size  
- **Value claimed in audit**: 16px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Notion is content-first and uses larger base typography than productivity tools. 16px cited in multiple analyses. Not confirmed via DevTools.  
- **Date observed**: 2026-06-24  

---

### HubSpot

- **Metric**: Sidebar width  
- **Value claimed in audit**: ~250px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: HubSpot navigation width estimated from published screenshots. Not measured.  
- **Date observed**: 2026-06-24  

- **Metric**: Table row height  
- **Value claimed in audit**: 48px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: HubSpot contact/deal tables are known for comfortable (not dense) row heights. 48px estimated from comparison screenshots. Not confirmed via DevTools.  
- **Date observed**: 2026-06-24  

- **Metric**: Base font size  
- **Value claimed in audit**: 14px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: HubSpot CMS hub documentation references 14px body as standard. Not confirmed against the live app UI.  
- **Date observed**: 2026-06-24  

---

### Zoho Inventory

- **Metric**: Sidebar width  
- **Value claimed in audit**: ~260px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Zoho Inventory sidebar estimated from published help documentation screenshots. Not measured.  
- **Date observed**: 2026-06-24  

- **Metric**: Table row height  
- **Value claimed in audit**: 44px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Zoho Inventory uses standard comfortable row heights consistent with Zoho's cross-product design language. 44px estimated.  
- **Date observed**: 2026-06-24  

---

### Lightspeed Retail POS

- **Metric**: Sidebar width  
- **Value claimed in audit**: ~280px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Lightspeed POS back-office sidebar estimated from published Lightspeed help center documentation screenshots.  
- **Date observed**: 2026-06-24  

- **Metric**: Table row height  
- **Value claimed in audit**: 40px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Lightspeed emphasizes "pleasant" UX over density. 40px estimated as moderate row height consistent with this philosophy.  
- **Date observed**: 2026-06-24  

---

### Square POS

- **Metric**: Sidebar width  
- **Value claimed in audit**: Full-screen  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Square POS uses a full-screen tablet/register interface without a traditional sidebar. This is a design pattern distinction, not a specific measurement.  
- **Date observed**: 2026-06-24  

- **Metric**: Table row height  
- **Value claimed in audit**: N/A  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Square POS is optimized for touch/tablet — traditional table row height comparison does not apply.  
- **Date observed**: 2026-06-24  

---

### Odoo

- **Metric**: Sidebar width  
- **Value claimed in audit**: ~250px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Odoo's left navigation menu approximately 250px based on Odoo 17 published screenshots. Not measured via DevTools.  
- **Date observed**: 2026-06-24  

- **Metric**: Table row height  
- **Value claimed in audit**: 40px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Odoo list view row heights estimated at ~40px from published Odoo 17 documentation screenshots.  
- **Date observed**: 2026-06-24  

- **Metric**: Base font size  
- **Value claimed in audit**: 14px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Odoo's web client documented as using 14px base font in framework documentation. Not confirmed against live instance.  
- **Date observed**: 2026-06-24  

---

### Microsoft Dynamics 365

- **Metric**: Sidebar width  
- **Value claimed in audit**: ~300px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Dynamics 365 navigation pane is known to be wider than typical SaaS due to enterprise module complexity. ~300px estimated from published Microsoft Learn documentation screenshots.  
- **Date observed**: 2026-06-24  

- **Metric**: Table row height  
- **Value claimed in audit**: 48px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Dynamics 365 uses "comfortable" density by default in list views. 48px estimated from Microsoft's Fluent UI design system which uses 40–48px for standard list rows.  
- **Date observed**: 2026-06-24  

- **Metric**: Base font size  
- **Value claimed in audit**: 14px  
- **Source type**: Expert assessment — unverified  
- **Evidence**: Microsoft Fluent UI design system publishes 14px as the body text standard. Reference: https://developer.microsoft.com/en-us/fluentui — URL not confirmed live.  
- **Date observed**: 2026-06-24  

---

## Classification Summary

| Product | Source Type |
|---|---|
| Shopify Admin | Expert assessment — unverified |
| Stripe | Expert assessment — unverified |
| Linear | Expert assessment — unverified |
| Notion | Expert assessment — unverified |
| HubSpot | Expert assessment — unverified |
| Zoho Inventory | Expert assessment — unverified |
| Lightspeed POS | Expert assessment — unverified |
| Square POS | Expert assessment — unverified |
| Odoo | Expert assessment — unverified |
| Microsoft Dynamics 365 | Expert assessment — unverified |

**Note**: No entries were confirmed via DevTools measurement or live URL fetch. All values reflect expert-level knowledge of published design system research, industry analysis, and pattern recognition as of 2025–2026. Independent verification via DevTools measurement is recommended for any metric used in a production decision.


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