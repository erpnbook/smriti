---
Document ID: "DEV-037"
Title: "Phase 2C-W2 Closeout Report — Security Module Token Bridge"
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

# Phase 2C-W2 Closeout Report — Security Module Token Bridge

Established a token bridge for the SMRITI Security & Workflow Center ([security.html](../../apps/smriti_retail_os/smriti_retail_os/www/security.html)) to dynamically consume resolved SMRITI design tokens (`--smriti-*`) while preserving existing role controls, workflows, and administrative layouts.

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

Below is a viewport screenshot demonstrating SMRITI Security Center rendering in POS-Dark mode:

![Security Center in POS-Dark Mode](file:///C:/Users/netma/.gemini/antigravity-ide/brain/09e3b5f9-6959-4d24-a9e6-7783495c187f/security_page_pos_dark.png)

---

## Verification 3: Git Diff Output

The `git diff` shows only `security.html` and `security.py` were modified. No backend workflows or administrative permissions were changed:

```diff
diff --git a/smriti_retail_os/www/security.html b/smriti_retail_os/www/security.html
index ef64923..1eb1918 100644
--- a/smriti_retail_os/www/security.html
+++ b/smriti_retail_os/www/security.html
@@ -18,31 +18,32 @@
   <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
   <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
   <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>
+  <link rel="stylesheet" href="/assets/smriti_retail_os/css/smriti_tokens.css">
   
   <style>
     /* ────────── Core SMRITI UI Tokens ────────── */
     :root {
-      --bg-base:     #0a0f1e;
-      --bg-surface:  #0f1629;
-      --bg-card:     #131d35;
-      --bg-input:    #172040;
-      --border:      rgba(255,255,255,0.07);
-      --border-glow: rgba(99,102,241,0.2);
-      --accent:      #6366f1;
-      --accent-glow: rgba(99,102,241,0.5);
-      --accent-2:    #818cf8;
-      --success:     #10b981;
-      --warning:     #f59e0b;
-      --danger:      #ef4444;
-      --text-1:      #e2e8f0;
-      --text-2:      #94a3b8;
-      --text-3:      #475569;
-      --radius:      12px;
-      --radius-sm:   8px;
-      --radius-lg:   16px;
-      --shadow:      0 8px 32px rgba(0,0,0,0.5);
+      --bg-base:     var(--smriti-color-bg-page);
+      --bg-surface:  var(--smriti-color-bg-primary);
+      --bg-card:     var(--smriti-color-bg-secondary);
+      --bg-input:    var(--smriti-color-bg-elevated);
+      --border:      var(--smriti-color-border-default);
+      --border-glow: var(--smriti-color-brand-light);
+      --accent:      var(--smriti-color-brand-primary);
+      --accent-glow: var(--smriti-color-brand-light);
+      --accent-2:    var(--smriti-color-brand-light);
+      --success:     var(--smriti-color-status-success);
+      --warning:     var(--smriti-color-status-warning);
+      --danger:      var(--smriti-color-status-danger);
+      --text-1:      var(--smriti-color-text-primary);
+      --text-2:      var(--smriti-color-text-muted);
+      --text-3:      var(--smriti-color-text-subtle);
+      --radius:      var(--smriti-radius-lg);
+      --radius-sm:   var(--smriti-radius-md);
+      --radius-lg:   var(--smriti-radius-xl);
+      --shadow:      var(--smriti-shadow-lg);
       --font-mono:   'JetBrains Mono', monospace;
-      --t:           0.2s ease;
+      --t:           var(--smriti-t-base) ease;
     }
     
     *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
@@ -1993,6 +1994,26 @@ function cint(v) {
 
 <script src="/assets/smriti_retail_os/js/smriti_sidebar_standalone.js?v=2.0.2"></script>
 <script>SMRITI.renderFlexibleSidebar("security");</script>
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
+    /* Activate UI Configuration Engine for Security Center.
+       Called after all sidebar scripts run so SMRITI global is stable. */
+    document.addEventListener('DOMContentLoaded', function() {
+        if (window.SMRITI && typeof SMRITI.initUIEngine === 'function') {
+            SMRITI.initUIEngine();
+        }
+    });
+</script>
 </body>
 </html>
 {% endblock %}
diff --git a/smriti_retail_os/www/security.py b/smriti_retail_os/www/security.py
index ea7d774..5562733 100644
--- a/smriti_retail_os/www/security.py
+++ b/smriti_retail_os/www/security.py
@@ -55,4 +55,19 @@ def get_context(context):
     # Fetch retail doctypes list that managers can assign permissions for
     context.retail_doctypes = ["Company", "Warehouse"]
 
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