---
Document ID: "DEV-038"
Title: "Phase 2C-W3 Closeout Report — Platform Center Token Bridge"
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

# Phase 2C-W3 Closeout Report — Platform Center Token Bridge

Established a token bridge for the SMRITI Platform Center ([platform_center.html](../../apps/smriti_retail_os/smriti_retail_os/www/platform_center.html)) to dynamically consume resolved SMRITI design tokens (`--smriti-*`) while preserving existing technical administration tools, DB backups logic, diagnostics center, and maintenance mode systems.

---

## Verification 1: SMRITI.getResolvedUIConfig()

The UI Configuration Engine successfully bootstraps and resolves the styling profile at runtime. Running `SMRITI.getResolvedUIConfig()` in the browser console returns the following:

```json
{
  "tokens": {
    "--smriti-color-bg-page": "#0d1117",
    "--smriti-color-bg-primary": "#161b22",
    "--smriti-color-bg-secondary": "#21262d",
    "--smriti-color-text-primary": "#f0f6fc",
    "--smriti-color-text-muted": "#8b949e",
    "--smriti-color-text-subtle": "#484f58",
    "--smriti-color-brand-primary": "#6941c6",
    "--smriti-color-brand-light": "#9e77ed",
    "--smriti-color-brand-dark": "#53389e",
    "--smriti-color-border-default": "#30363d",
    "--smriti-color-border-strong": "#484f58",
    "--smriti-color-status-success": "#027a48",
    "--smriti-color-status-danger": "#b42318",
    "--smriti-color-status-warning": "#b54708",
    "--smriti-color-status-info": "#0ea5e9",
    "--smriti-spacing-xs": "4px",
    "--smriti-spacing-sm": "8px",
    "--smriti-spacing-md": "12px",
    "--smriti-spacing-lg": "16px",
    "--smriti-spacing-xl": "24px",
    "--smriti-spacing-2xl": "32px",
    "--smriti-spacing-padding-y": "8px",
    "--smriti-spacing-padding-x": "10px",
    "--smriti-spacing-gap": "12px",
    "--smriti-dimension-sidebar-width": "260px",
    "--smriti-dimension-sidebar-collapsed-width": "68px",
    "--smriti-radius-xs": "4px",
    "--smriti-radius-sm": "6px",
    "--smriti-radius-md": "10px",
    "--smriti-radius-lg": "14px",
    "--smriti-radius-xl": "18px",
    "--smriti-radius-2xl": "24px",
    "--smriti-radius-full": "9999px",
    "--smriti-shadow-xs": "0 1px 2px rgba(15,23,42,.05)",
    "--smriti-shadow-sm": "0 1px 3px rgba(0,0,0,.7)",
    "--smriti-shadow-md": "0 4px 12px rgba(0,0,0,.8)",
    "--smriti-shadow-lg": "0 12px 28px rgba(15,23,42,.10), 0 4px 8px rgba(15,23,42,.04)",
    "--smriti-shadow-xl": "0 24px 48px rgba(15,23,42,.12), 0 8px 16px rgba(15,23,42,.05)",
    "--smriti-shadow-neu-float": "6px 6px 14px #c5c9d4, -6px -6px 14px #ffffff",
    "--smriti-shadow-neu-pressed": "inset 6px 6px 12px #c5c9d4, inset -6px -6px 12px #ffffff",
    "--smriti-font-size-xs": "0.72rem",
    "--smriti-font-size-sm": "0.82rem",
    "--smriti-font-size-base": "0.95rem",
    "--smriti-font-size-md": "1rem",
    "--smriti-font-size-lg": "1.15rem",
    "--smriti-font-size-xl": "1.35rem",
    "--smriti-font-size-2xl": "1.6rem",
    "--smriti-font-weight-regular": "400",
    "--smriti-font-weight-medium": "500",
    "--smriti-font-weight-semibold": "600",
    "--smriti-font-weight-bold": "700",
    "--smriti-font-weight-extrabold": "800",
    "--smriti-z-index-base": "0",
    "--smriti-z-index-dropdown": "100",
    "--smriti-z-index-sticky": "200",
    "--smriti-z-index-overlay": "500",
    "--smriti-z-index-modal": "1000",
    "--smriti-z-index-sidebar": "1041",
    "--smriti-z-index-toast": "1100",
    "--smriti-z-index-tooltip": "1200"
  },
  "mode": "dark",
  "reducedMotion": false
}
```

---

## Verification 2: pos-dark Theme Switch

Forced `localStorage.setItem("smriti-theme-style", "pos-dark")` and verified that the bridged custom properties resolve correctly through the token chain:

- **`--bg-base`**: Resolves to `#0d1117` (Dark Mode Clay Base)
- **`--bg-surface`**: Resolves to `#161b22` (Dark Mode Flat Surface)
- **`--bg-card`**: Resolves to `#21262d` (Dark Mode Secondary Card)

These resolutions confirm the token bridge maps successfully to dark mode values.

---

## Visual Evidence

### Baseline (Before Token Bridge):
![Platform Center Baseline](file:///C:/Users/netma/.gemini/antigravity-ide/brain/09e3b5f9-6959-4d24-a9e6-7783495c187f/platform_center_before.png)

### Active UI Engine (POS-Dark Mode):
![Platform Center in POS-Dark Mode](file:///C:/Users/netma/.gemini/antigravity-ide/brain/09e3b5f9-6959-4d24-a9e6-7783495c187f/platform_center_pos_dark.png)

---

## Verification 4: Git Diff Scope

The `git diff` shows only `platform_center.html` and `platform_center.py` were modified. No backend workflows or administrative permissions were changed:

```diff
diff --git a/smriti_retail_os/www/platform_center.html b/smriti_retail_os/www/platform_center.html
index fdc2541..f16d187 100644
--- a/smriti_retail_os/www/platform_center.html
+++ b/smriti_retail_os/www/platform_center.html
@@ -18,28 +18,29 @@
   <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
   <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
+  <link rel="stylesheet" href="/assets/smriti_retail_os/css/smriti_tokens.css">
   <style>
     /* ────────── Design Tokens ────────── */
     :root {
-      --bg-base:     #080810;
-      --bg-surface:  #0e0f1e;
-      --bg-card:     #13152d;
-      --bg-input:    #1a1c3b;
-      --border:      #2b2e5a;
-      --border-glow: #7c3aed35;
-      --accent:      #8b5cf6;
-      --accent-glow: #8b5cf660;
-      --accent-cyan:  #06b6d4;
-      --success:     #10b981;
-      --warning:     #f59e0b;
-      --danger:      #ef4444;
-      --text-1:      #f3f4f6;
-      --text-2:      #9ca3af;
-      --text-3:      #4b5563;
-      --radius:      12px;
-      --radius-lg:   20px;
-      --shadow:      0 8px 32px 0 rgba(0, 0, 0, 0.6);
-      --font-mono:   'JetBrains Mono', monospace;
+      --bg-base:     var(--smriti-color-bg-page);
+      --bg-surface:  var(--smriti-color-bg-primary);
+      --bg-card:     var(--smriti-color-bg-secondary);
+      --bg-input:    var(--smriti-color-bg-elevated);
+      --border:      var(--smriti-color-border-default);
+      --border-glow: var(--smriti-color-brand-light);
+      --accent:      var(--smriti-color-brand-primary);
+      --accent-glow: var(--smriti-color-brand-light);
+      --accent-cyan: var(--smriti-color-status-info);
+      --success:     var(--smriti-color-status-success);
+      --warning:     var(--smriti-color-status-warning);
+      --danger:      var(--smriti-color-status-danger);
+      --text-1:      var(--smriti-color-text-primary);
+      --text-2:      var(--smriti-color-text-muted);
+      --text-3:      var(--smriti-color-text-subtle);
+      --radius:      var(--smriti-radius-lg);
+      --radius-lg:   var(--smriti-radius-xl);
+      --shadow:      var(--smriti-shadow-lg);
+      --font-mono:   'JetBrains Mono', monospace; /* Documented Exception */
     }
     *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
     html { font-size: 15px; scroll-behavior: smooth; }
@@ -1630,5 +1631,24 @@ window.addEventListener('DOMContentLoaded', () => {
   log(`Platform Center loaded. User: ${CURRENT_USER}, Mode: ${IS_ADMIN_ACCOUNT ? 'Business Owner (Restricted)' : 'Full Administrator'}`, 'system');
 });
 </script>
+
+<script>
+    window.frappe = window.frappe || {};
+    window.frappe.boot = window.frappe.boot || {};
+    window.frappe.boot.smriti_license = {{ smriti_license | tojson }};
+    window.frappe.boot.smriti_site_config = {{ smriti_site_config | tojson }};
+</script>
+
+<!-- SMRITI UI Configuration Engine — loaded last to merge safely into SMRITI global -->
+<script src="/assets/smriti_retail_os/js/smriti_ui_resolver.js?v=2.0.4"></script>
+<script src="/assets/smriti_retail_os/js/smriti_theme_manager.js?v=2.0.4"></script>
+<script>
+    /* Activate UI Configuration Engine for Platform Center. */
+    document.addEventListener('DOMContentLoaded', function() {
+        if (window.SMRITI && typeof SMRITI.initUIEngine === 'function') {
+            SMRITI.initUIEngine();
+        }
+    });
+</script>
 </body>
 </html>
diff --git a/smriti_retail_os/www/platform_center.py b/smriti_retail_os/www/platform_center.py
index e9d6259..c2c2d69 100644
--- a/smriti_retail_os/www/platform_center.py
+++ b/smriti_retail_os/www/platform_center.py
@@ -58,4 +58,19 @@ def get_context(context):
     # Flag consumed by the Jinja template to conditionally render restricted UI
     context.is_admin_account = (user == "Admin")
 
+    # Pass license and site config for UI Configuration Engine
+    from smriti_retail_os.license.manager import get_license_summary
+    context.smriti_license = get_license_summary()
+    
+    from smriti_retail_os.company_api import get_company_settings, get_active_company
+    active_company = get_active_company()
+    comp_settings = get_company_settings(active_company) if active_company else {}
+    
+    context.smriti_site_config = {
+        "store_theme": comp_settings.get("store_theme") or "hybrid",
+        "store_experience": comp_settings.get("store_experience") or "standard",
+        "terminal_type": comp_settings.get("terminal_type") or "standard",
+        "brand_overrides": comp_settings.get("brand_overrides") or {}
+    }
+
     return context
```


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