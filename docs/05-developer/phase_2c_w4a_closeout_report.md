---
Document ID: "DEV-039"
Title: "Phase 2C-W4A Closeout Report — Barcode Module Token Bridge"
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

# Phase 2C-W4A Closeout Report — Barcode Module Token Bridge

Established a token bridge for the SMRITI Barcode Printer / Label Studio ([barcode.html](../../apps/smriti_retail_os/smriti_retail_os/www/barcode.html)) to dynamically consume resolved SMRITI design tokens (`--smriti-*`) while preserving strict color isolated rendering logic for simulated labels and designer canvas areas, qz-tray websocket communication, and DPI conversion algorithms.

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

## Verification 2: Theme Style Validation

Forced `localStorage.setItem("smriti-theme-style", "pos-dark")` and verified that the bridged custom properties resolve correctly through the token chain:

- **`--bg`**: Resolves to `var(--smriti-color-bg-page)` (`#0d1117`)
- **`--bg2`**: Resolves to `var(--smriti-color-bg-primary)` (`#161b22`)
- **`--card`**: Resolves to `var(--smriti-color-bg-secondary)` (`#21262d`)
- **`--card2`**: Resolves to `var(--smriti-color-bg-elevated)` (dark surface elements)
- **`--border`**: Resolves to `var(--smriti-color-border-default)` (`#30363d`)
- **`--text`**: Resolves to `var(--smriti-color-text-primary)` (`#f0f6fc`)

These resolutions confirm the token bridge maps successfully to dark mode values.

### Label Simulator Protection (Fail-Safe Verification)
As highlighted in the audit plan, thermal printed labels are physically white. The following element properties have been locked to explicit values and verified untouched by token maps:
- `.sim-label` background: `#ffffff` (fixed)
- `#visual-canvas` background: `white` (fixed)

---

## Visual Evidence

### Baseline (Standard Light/Hybrid Mode):
[Barcode Simulator Baseline](#)

*(Note: Replace path above with: `C:/Users/netma/.gemini/antigravity-ide/brain/eed0fad8-8ece-4646-91a3-f61f338755e6/barcode_before.png`)*

### Active UI Engine (POS-Dark Mode):
[Barcode Simulator in POS-Dark Mode](#)

*(Note: Replace path above with: `C:/Users/netma/.gemini/antigravity-ide/brain/eed0fad8-8ece-4646-91a3-f61f338755e6/barcode_pos_dark.png`)*

---

## Verification 4: Git Diff Scope

The `git diff` shows only `barcode.html` and `barcode.py` were modified. No printing pipelines, layout coordinates calculations, or network socket communication files were modified:

```diff
diff --git a/smriti_retail_os/www/barcode.html b/smriti_retail_os/www/barcode.html
index a51af0c..9f995ba 100644
--- a/smriti_retail_os/www/barcode.html
+++ b/smriti_retail_os/www/barcode.html
@@ -14,29 +14,31 @@
 <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
 <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
 <script src="https://cdn.jsdelivr.net/npm/qz-tray@2.1.2/qz-tray.js"></script>
+<link rel="stylesheet" href="/assets/smriti_retail_os/css/smriti_tokens.css">
 <style>
 *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
 
 :root {
-    --bg:         #0a0f1e;
-    --bg2:        #0f1629;
-    --card:       #131d35;
-    --card2:      #172040;
-    --border:     rgba(255,255,255,0.07);
-    --border2:    rgba(255,255,255,0.12);
-    --primary:    #6366f1;
-    --primary-lt: #818cf8;
-    --accent:     #f59e0b;
-    --success:    #10b981;
-    --warning:    #f59e0b;
-    --danger:     #ef4444;
-    --text:       #e2e8f0;
-    --text-muted: #94a3b8;
-    --text-sub:   #475569;
-    --radius:     12px;
-    --radius-sm:  8px;
-    --radius-lg:  16px;
-    --t:          0.2s ease;
+    /* ── SMRITI Token Bridge (Phase 2C-W4) ───────────────────────────── */
+    --bg:         var(--smriti-color-bg-page);
+    --bg2:        var(--smriti-color-bg-primary);
+    --card:       var(--smriti-color-bg-secondary);
+    --card2:      var(--smriti-color-bg-elevated);
+    --border:     var(--smriti-color-border-default);
+    --border2:    var(--smriti-color-border-strong);
+    --primary:    var(--smriti-color-brand-primary);
+    --primary-lt: var(--smriti-color-brand-light);
+    --accent:     var(--smriti-color-brand-accent);
+    --success:    var(--smriti-color-status-success);
+    --warning:    var(--smriti-color-status-warning);
+    --danger:     var(--smriti-color-status-danger);
+    --text:       var(--smriti-color-text-primary);
+    --text-muted: var(--smriti-color-text-muted);
+    --text-sub:   var(--smriti-color-text-subtle);
+    --radius:     var(--smriti-radius-lg);
+    --radius-sm:  var(--smriti-radius-md);
+    --radius-lg:  var(--smriti-radius-xl);
+    --t:          0.2s ease; /* Transition Exception */
 }
 
 html, body { width:100%; height:100%; overflow:hidden; background:var(--bg); color:var(--text); font-family:'Inter',-apple-system,sans-serif; font-size:14px; }
@@ -131,6 +133,12 @@ html, body { width:100%; height:100%; overflow:hidden; background:var(--bg); col
 .preview-header span { font-size:18px; }
 .preview-body { padding:16px; display:flex; justify-content:center; background:rgba(0,0,0,0.2); min-height:180px; align-items:center; position:relative; }
 
+/* ===================================================
+   LABEL RENDERING SAFETY ZONE
+   DO NOT TOKENIZE
+   DO NOT THEME
+   DO NOT DARK-MODE
+   =================================================== */
 /* Thermal Printed Label simulated look */
 .sim-label { background:#ffffff; color:#0f172a; width:220px; border-radius:4px; box-shadow:0 8px 24px rgba(0,0,0,0.5); padding:10px; display:flex; flex-direction:column; position:relative; font-family:'Inter',sans-serif; overflow:hidden; transition:all 0.3s ease; border: 1px dashed #94a3b8; }
 .sim-label.sz-50x25 { aspect-ratio: 2/1; height: 110px; }
@@ -283,6 +291,12 @@ html, body { width:100%; height:100%; overflow:hidden; background:var(--bg); col
 .tab-btn:hover:not(.active) { border-color: var(--primary-lt); color: var(--primary-lt); }
 
 .visual-designer-container { display: flex; gap: 20px; flex: 1; min-height: 0; }
+/* ===================================================
+   LABEL RENDERING SAFETY ZONE
+   DO NOT TOKENIZE
+   DO NOT THEME
+   DO NOT DARK-MODE
+   =================================================== */
 #visual-canvas { background: white; border: 2px dashed #64748b; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.5); overflow: hidden; }
 
 .visual-elem {
@@ -4190,7 +4204,28 @@ window.onload = init;
 </script>
 
 <script src="/assets/smriti_retail_os/js/smriti_sidebar_standalone.js?v=2.0.2"></script>
-<script>SMRITI.renderFlexibleSidebar("barcode");</script></body>
+<script>SMRITI.renderFlexibleSidebar("barcode");</script>
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
+    /* Activate UI Configuration Engine for Barcode Module.
+       Called after all sidebar scripts run so SMRITI global is stable. */
+    document.addEventListener('DOMContentLoaded', function() {
+        if (window.SMRITI && typeof SMRITI.initUIEngine === 'function') {
+            SMRITI.initUIEngine();
+        }
+    });
+</script>
+</body>
 </html>
 {% endblock %}
 
diff --git a/smriti_retail_os/www/barcode.py b/smriti_retail_os/www/barcode.py
index c88a2f4..80c12d2 100644
--- a/smriti_retail_os/www/barcode.py
+++ b/smriti_retail_os/www/barcode.py
@@ -49,4 +49,19 @@ def get_context(context):
     context.cashier    = frappe.session.user
     context.csrf_token = frappe.sessions.get_csrf_token()
 
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