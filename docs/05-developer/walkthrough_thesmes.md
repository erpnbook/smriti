---
Document ID: "DEV-069"
Title: "Walkthrough: SMRITI Whitelabel Branding & Frappe Default Theme Integration"
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

# Walkthrough: SMRITI Whitelabel Branding & Frappe Default Theme Integration

We have successfully restored the premium **Frappe Default Theme compatibility** across the entire ERPNext and Frappe Desk interface—including the **POS Retail Billing, Day Open/Close, Inventory, and Barcode Printing pages**—while strictly maintaining all **SMRITI Whitelabel Branding** elements (logos, titles, custom fonts, copyright hides, and login screens).

---

## 🎨 Implemented Theme & Branding Details

By refining the stylesheets ([smriti_theme.css](../../apps/smriti_retail_os/smriti_retail_os/public/css/smriti_theme.css), [smriti_sidebar.css](../../apps/smriti_retail_os/smriti_retail_os/public/css/smriti_sidebar_standalone.css), [smriti_branding.css](../../apps/smriti_retail_os/smriti_retail_os/public/css/smriti_branding.css), [smriti_billing.css](../../apps/smriti_retail_os/smriti_retail_os/public/css/smriti-billing.css), [smriti_shift.css](../../apps/smriti_retail_os/smriti_retail_os/public/css/smriti-shift.css), [smriti_inventory.css](../../apps/smriti_retail_os/smriti_retail_os/public/css/smriti-inventory.css), and [smriti_barcode.css](../../apps/smriti_retail_os/smriti_retail_os/public/css/smriti-barcode.css)), the software integrates SMRITI's whitelabeling seamlessly with Frappe's native light and dark modes:

1. **Restored Frappe Default Theme Compatibility**:
   * Removed all forced `!important` color, background, card, border, and button overrides from the standard Desk pages and the **POS Billing, Shift, Inventory, and Barcode Printing pages**.
   * **Result:** The standard ERPNext/Frappe screens and all main custom pages now display with their clean, highly optimized native colors (perfectly matching Frappe's default light mode and dark mode layouts based on the user's desktop settings).

2. **Custom Pages Light Mode Alignment**:
   * **Day Open / Day Close (`smriti_shift.css`):** Swapped out the custom dark background for a clean off-white canvas (`#f9fafb`), with white glass denomination cards (`#ffffff`) and standard dark slate text. 
   * **Inventory Panel (`smriti_inventory.css`):** Converted item lookup selectors, scanning inputs, and summary rows to render in standard light card styles with grey dividers.
   * **Barcode Printing (`smriti_barcode.css`):** Customized the barcode page layout, item list grids, and label size buttons into standard light theme rendering, while keeping the high-contrast Courier label previews.
   * **POS Billing (`smriti_billing.css`):** Retained its high-readability light card structures and premium cashier indicators.

3. **100% SMRITI Whitelabel Branding & Custom Fonts**:
   * **Custom Typography:** Kept standard Google Font overrides active so all Desk views utilize clean, premium **'Inter'** and **'Outfit'** font families, replacing basic browser sans-serifs.
   * **Navbar & Sidebar Branding:** Replaced all standard Frappe/ERPNext branding layers. The top navbar brand title remains dynamically set to **`SMRITI Retail OS`** using the bold, stylized brand font.
   * **Hide Attributions:** Retained global footers and link cleanups, completely hiding any "Powered by Frappe" or "Built with ERPNext" copyright text across the Desk.
   * **Logo Replacements:** All standard system logos are programmatically redirected to SMRITI's proprietary logo assets.

4. **Premium Custom Login Box**:
   * Preserved SMRITI's gorgeous static Cyberpunk Dark login template served from [login.html](../../apps/smriti_retail_os/smriti_retail_os/www/login.html) (featuring glassmorphism, glowing coral actions, custom autofill overrides, and spring-animated brand elements).

5. **Theme Compliance Policy (Git-Ignored)**:
   * Established a local rule in [BRANDING_POLICY.md](../../apps/smriti_retail_os/BRANDING_POLICY.md) (explicitly hidden from GitHub via `.gitignore`) instructing all developers and AI agents to respect standard Frappe themes and strictly reference native CSS variables instead of forcing hardcoded color hexes.

---

## 🚀 Execution & Synchronization

* **Container Sync**: Copied updated whitelabel assets and billing pages to the running container:
  ```bash
  docker cp apps/smriti_retail_os smriti_retail-backend-1:/home/frappe/frappe-bench/apps/
  ```
* **Asset Synchronization**: Recompiled assets globally inside the shared volume:
  ```bash
  docker exec smriti_retail-backend-1 bench --site frontend execute smriti_retail_os.sync_assets.sync_assets
  ```
* **Cache Purged**: Ran `bench clear-cache` to ensure the clean native layouts render immediately.

---

## 📈 Verification & Results

* **Global Status**: Completed with **0 errors**.
* **Visual Polish**: Checked elements globally. The layout now renders standard Frappe light-mode pages and POS terminal screens cleanly without color clashes, keeping SMRITI's logo and fonts perfectly integrated.
* **Result**: **Frappe default theme compatibility restored across all screens, including POS Billing, Shift, Inventory, and Barcode pages, with whitelabeling fully intact!**


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