/**
 * @file: smriti_retail_os/public/js/smriti_ui_resolver.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
/**
 * @file smriti_ui_resolver.js
 * @description SMRITI UI Configuration Engine — Deterministic 7-Level Resolver
 *              Implements the resolver hierarchy defined in:
 *              docs/architecture/ui/SMRITI_UI_CONFIGURATION_ENGINE_V1.md
 *
 * GOVERNANCE:
 *   - This file must comply with SMRITI_UI_CONFIGURATION_ENGINE_V1.md §3, §4, §5
 *   - Hierarchy order is FROZEN. Do not modify without ACP approval.
 *   - This file contains resolver internals ONLY.
 *   - It does NOT expose themeProfile, experienceProfile, or brandProfile externally.
 *   - Components must never import this file directly — use smriti_theme_manager.js
 *
 * @version 1.0.0
 * @status Phase 1A — Foundation Layer
 * @author AITDL / SMRITI Engineering
 * @license MIT — Copyright (c) 2026 AITDL NETWORK & ERPNbook.com
 */

(function (global) {
    "use strict";

    global.SMRITI = global.SMRITI || {};

    /* ═══════════════════════════════════════════════════════════════════
       SECTION 1 — SYSTEM DEFAULT TOKENS (Level 7 — lowest priority)
       Source of truth: smriti_tokens.css
       These JS values mirror the CSS file for programmatic access.
       CSS file is the canonical source; JS mirrors for resolver use.
    ═══════════════════════════════════════════════════════════════════ */
    var SYSTEM_DEFAULT_TOKENS = {
        /* Colors */
        "--smriti-color-bg-page":              "#e8ecf2",
        "--smriti-color-bg-primary":           "#ffffff",
        "--smriti-color-bg-secondary":         "#f6f8fb",
        "--smriti-color-text-primary":         "#0f172a",
        "--smriti-color-text-muted":           "#475467",
        "--smriti-color-text-subtle":          "#94a3b8",
        "--smriti-color-brand-primary":        "#6941c6",
        "--smriti-color-brand-light":          "#9e77ed",
        "--smriti-color-brand-dark":           "#53389e",
        "--smriti-color-border-default":       "#e2e8f0",
        "--smriti-color-border-strong":        "#d0d5dd",
        "--smriti-color-status-success":       "#027a48",
        "--smriti-color-status-danger":        "#b42318",
        "--smriti-color-status-warning":       "#b54708",
        "--smriti-color-status-info":          "#0ea5e9",
        /* Spacing */
        "--smriti-spacing-xs":                 "4px",
        "--smriti-spacing-sm":                 "8px",
        "--smriti-spacing-md":                 "12px",
        "--smriti-spacing-lg":                 "16px",
        "--smriti-spacing-xl":                 "24px",
        "--smriti-spacing-2xl":                "32px",
        "--smriti-spacing-padding-y":          "10px",
        "--smriti-spacing-padding-x":          "14px",
        "--smriti-spacing-gap":                "12px",
        /* Radius */
        "--smriti-radius-xs":                  "4px",
        "--smriti-radius-sm":                  "6px",
        "--smriti-radius-md":                  "10px",
        "--smriti-radius-lg":                  "14px",
        "--smriti-radius-xl":                  "18px",
        "--smriti-radius-2xl":                 "24px",
        "--smriti-radius-full":                "9999px",
        /* Shadows */
        "--smriti-shadow-xs":                  "0 1px 2px rgba(15,23,42,.05)",
        "--smriti-shadow-sm":                  "0 1px 3px rgba(15,23,42,.08), 0 1px 2px rgba(15,23,42,.04)",
        "--smriti-shadow-md":                  "0 4px 12px rgba(15,23,42,.08), 0 2px 4px rgba(15,23,42,.04)",
        "--smriti-shadow-lg":                  "0 12px 28px rgba(15,23,42,.10), 0 4px 8px rgba(15,23,42,.04)",
        "--smriti-shadow-xl":                  "0 24px 48px rgba(15,23,42,.12), 0 8px 16px rgba(15,23,42,.05)",
        "--smriti-shadow-neu-float":           "6px 6px 14px #c5c9d4, -6px -6px 14px #ffffff",
        "--smriti-shadow-neu-pressed":         "inset 6px 6px 12px #c5c9d4, inset -6px -6px 12px #ffffff",
        /* Font Size */
        "--smriti-font-size-xs":               "0.72rem",
        "--smriti-font-size-sm":               "0.82rem",
        "--smriti-font-size-base":             "0.95rem",
        "--smriti-font-size-md":               "1rem",
        "--smriti-font-size-lg":               "1.15rem",
        "--smriti-font-size-xl":               "1.35rem",
        "--smriti-font-size-2xl":              "1.6rem",
        /* Font Weight */
        "--smriti-font-weight-regular":        "400",
        "--smriti-font-weight-medium":         "500",
        "--smriti-font-weight-semibold":       "600",
        "--smriti-font-weight-bold":           "700",
        "--smriti-font-weight-extrabold":      "800",
        /* Z-Index */
        "--smriti-z-index-base":               "0",
        "--smriti-z-index-dropdown":           "100",
        "--smriti-z-index-sticky":             "200",
        "--smriti-z-index-overlay":            "500",
        "--smriti-z-index-modal":              "1000",
        "--smriti-z-index-sidebar":            "1041",
        "--smriti-z-index-toast":              "1100",
        "--smriti-z-index-tooltip":            "1200"
    };

    /* ═══════════════════════════════════════════════════════════════════
       SECTION 2 — PROFILE TOKEN OVERRIDES (resolver internals)
       GOVERNANCE: These objects are NEVER exposed to components.
       They are consumed exclusively inside _resolveHierarchy().
    ═══════════════════════════════════════════════════════════════════ */

    /** Theme profiles — internal resolver use only */
    var _THEME_PROFILES = {
        "hybrid": {
            /* inherits all system defaults — no overrides for hybrid */
        },
        "minimalist": {
            "--smriti-color-bg-page":          "#f8fafc",
            "--smriti-color-border-default":   "#cbd5e1",
            "--smriti-shadow-neu-float":       "0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04)",
            "--smriti-shadow-neu-pressed":     "none",
            "--smriti-shadow-sm":              "0 1px 2px rgba(15,23,42,0.06)"
        },
        "dark": {
            "--smriti-color-bg-page":          "#09090b",
            "--smriti-color-bg-primary":       "#18181b",
            "--smriti-color-bg-secondary":     "#27272a",
            "--smriti-color-text-primary":     "#f4f4f5",
            "--smriti-color-text-muted":       "#a1a1aa",
            "--smriti-color-text-subtle":      "#52525b",
            "--smriti-color-border-default":   "#27272a",
            "--smriti-color-border-strong":    "#3f3f46",
            "--smriti-shadow-neu-float":       "6px 6px 14px #020203, -6px -6px 14px #27272a",
            "--smriti-shadow-neu-pressed":     "inset 6px 6px 12px #020203, inset -6px -6px 12px #27272a",
            "--smriti-shadow-sm":              "0 1px 3px rgba(0,0,0,.5)",
            "--smriti-shadow-md":              "0 4px 12px rgba(0,0,0,.6)",
            "--smriti-shadow-lg":              "0 12px 28px rgba(0,0,0,.7)",
            "--smriti-shadow-xl":              "0 24px 48px rgba(0,0,0,.8)"
        },
        "pos-dark": {
            /* POS terminal forced dark — subset of dark + compact spacing */
            "--smriti-color-bg-page":          "#0d1117",
            "--smriti-color-bg-primary":       "#161b22",
            "--smriti-color-bg-secondary":     "#21262d",
            "--smriti-color-text-primary":     "#f0f6fc",
            "--smriti-color-text-muted":       "#8b949e",
            "--smriti-color-text-subtle":      "#484f58",
            "--smriti-color-border-default":   "#30363d",
            "--smriti-color-border-strong":    "#484f58",
            "--smriti-spacing-padding-y":      "8px",
            "--smriti-spacing-padding-x":      "10px",
            "--smriti-shadow-sm":              "0 1px 3px rgba(0,0,0,.7)",
            "--smriti-shadow-md":              "0 4px 12px rgba(0,0,0,.8)"
        }
    };

    /** Experience profiles — internal resolver use only */
    var _EXPERIENCE_PROFILES = {
        "standard": { /* no token overrides — standard spacing and typography */ },
        "compact": {
            "--smriti-spacing-padding-y":      "6px",
            "--smriti-spacing-padding-x":      "10px",
            "--smriti-spacing-gap":            "8px",
            "--smriti-font-size-base":         "0.88rem",
            "--smriti-font-size-sm":           "0.78rem"
        },
        "comfortable": {
            "--smriti-spacing-padding-y":      "14px",
            "--smriti-spacing-padding-x":      "18px",
            "--smriti-spacing-gap":            "16px",
            "--smriti-font-size-base":         "1rem",
            "--smriti-font-size-sm":           "0.88rem"
        }
    };

    /** Brand profiles — internal resolver use only */
    var _BRAND_PROFILES = {
        "smriti": { /* default brand — no overrides */ },
        "whitelabel": {
            /* Populated from frappe.boot.smriti_site_config.brand_overrides */
        }
    };

    /* ═══════════════════════════════════════════════════════════════════
       SECTION 3 — RESOLVER LEVEL READERS
       Each function reads one level of the hierarchy.
       Returns a partial token map (only tokens that level overrides).
       Returns {} if that level has no opinion.
    ═══════════════════════════════════════════════════════════════════ */

    /** Level 7 — System Default */
    function _readSystemDefault() {
        return Object.assign({}, SYSTEM_DEFAULT_TOKENS);
    }

    /** Level 6 — Store Default (from frappe.boot.smriti_site_config) */
    function _readStoreDefault() {
        try {
            var cfg = (window.frappe && window.frappe.boot && window.frappe.boot.smriti_site_config) || {};
            var themeProfile = cfg.store_theme || "hybrid";
            var expProfile   = cfg.store_experience || "standard";
            return _mergeProfileTokens(themeProfile, expProfile, "smriti");
        } catch (e) {
            return {};
        }
    }

    /** Level 5 — Role Default */
    function _readRoleDefault() {
        try {
            var roles = (window.frappe && window.frappe.user_roles) || [];
            if (roles.indexOf("SMRITI Cashier") !== -1) {
                /* Cashier default: compact experience */
                return Object.assign({}, _EXPERIENCE_PROFILES["compact"] || {});
            }
            return {};
        } catch (e) {
            return {};
        }
    }

    /** Level 4 — User Theme Preference (localStorage) */
    function _readUserThemePreference() {
        try {
            var style = localStorage.getItem("smriti-theme-style") || "hybrid";
            var dark  = document.body && (
                document.body.getAttribute("data-theme") === "dark" ||
                document.body.classList.contains("dark-mode")
            );
            if (dark) return Object.assign({}, _THEME_PROFILES["dark"] || {});
            return Object.assign({}, _THEME_PROFILES[style] || {});
        } catch (e) {
            return {};
        }
    }

    /** Level 3 — User Module Override (per-page user pref, reserved for Phase 2) */
    function _readUserModuleOverride() {
        /* Phase 1: not yet implemented — returns empty */
        return {};
    }

    /** Level 2 — System Module Policy (per-route forced overrides) */
    function _readSystemModulePolicy() {
        try {
            var path = window.location.pathname || "";
            /* Billing terminal: always forced dark (pos-dark) */
            if (path === "/billing" || path === "/billing/") {
                return Object.assign({}, _THEME_PROFILES["pos-dark"] || {});
            }
            return {};
        } catch (e) {
            return {};
        }
    }

    /** Level 1 — Terminal Policy (highest — cannot be overridden) */
    function _readTerminalPolicy() {
        try {
            var cfg = (window.frappe && window.frappe.boot && window.frappe.boot.smriti_site_config) || {};
            var terminalType = cfg.terminal_type || "standard";
            if (terminalType === "pos") {
                /* POS terminals: forced dark, compact, no animations */
                var posTokens = Object.assign({}, _THEME_PROFILES["pos-dark"] || {});
                posTokens["--smriti-shadow-neu-float"]  = "none";
                posTokens["--smriti-shadow-neu-pressed"] = "none";
                return posTokens;
            }
            return {};
        } catch (e) {
            return {};
        }
    }

    /* ═══════════════════════════════════════════════════════════════════
       SECTION 4 — ACCESSIBILITY OVERRIDE LAYER
       Applied AFTER hierarchy resolution (post-resolution layer).
       Cannot be suppressed by any resolver level.
    ═══════════════════════════════════════════════════════════════════ */
    function _applyAccessibilityOverrides(tokens) {
        var result = Object.assign({}, tokens);
        var reducedMotion = false;

        try {
            /* Reduced motion */
            var prefersReducedMotion = window.matchMedia &&
                window.matchMedia("(prefers-reduced-motion: reduce)").matches;
            var userReducedMotion = localStorage.getItem("smriti-a11y-reduced-motion") === "true";

            if (prefersReducedMotion || userReducedMotion) {
                reducedMotion = true;
                result["--smriti-shadow-neu-float"]  = "none";
                result["--smriti-shadow-neu-pressed"] = "none";
            }

            /* High contrast */
            var prefersHighContrast = window.matchMedia &&
                window.matchMedia("(prefers-contrast: more)").matches;
            var userHighContrast = localStorage.getItem("smriti-a11y-high-contrast") === "true";

            if (prefersHighContrast || userHighContrast) {
                result["--smriti-color-border-default"] = "#000000";
                result["--smriti-color-border-strong"]  = "#000000";
                result["--smriti-color-text-muted"]     = result["--smriti-color-text-primary"] || "#0f172a";
            }
        } catch (e) { /* accessibility APIs unavailable — continue */ }

        return { tokens: result, reducedMotion: reducedMotion };
    }

    /* ═══════════════════════════════════════════════════════════════════
       SECTION 5 — LICENSE VALIDATION GATE
       Reads boot-time license snapshot only. No live API calls.
    ═══════════════════════════════════════════════════════════════════ */
    function _isFullResolutionAllowed() {
        try {
            var lic = (window.frappe && window.frappe.boot && window.frappe.boot.smriti_license) || {};
            var status = lic.license_status || "Unregistered";
            /* Full resolution allowed for Active and Grace Period only */
            return (status === "Active" || status === "Grace Period");
        } catch (e) {
            return false;
        }
    }

    /* ═══════════════════════════════════════════════════════════════════
       SECTION 6 — INTERNAL HELPERS
    ═══════════════════════════════════════════════════════════════════ */
    function _mergeProfileTokens(themeProfile, expProfile, brandProfile) {
        var tokens = {};
        /* Theme → Experience → Brand (left to right, later keys win) */
        Object.assign(tokens, _THEME_PROFILES[themeProfile]  || {});
        Object.assign(tokens, _EXPERIENCE_PROFILES[expProfile] || {});
        Object.assign(tokens, _BRAND_PROFILES[brandProfile]  || {});
        return tokens;
    }

    function _detectMode(tokens) {
        var bg = tokens["--smriti-color-bg-page"] || "#e8ecf2";
        /* Simple luminance heuristic: dark backgrounds have low hex brightness */
        if (bg.charAt(0) === "#" && bg.length >= 4) {
            var r = parseInt(bg.slice(1, 3), 16) || 0;
            var g = parseInt(bg.slice(3, 5), 16) || 0;
            var b = parseInt(bg.slice(5, 7), 16) || 0;
            var luminance = (0.299 * r + 0.587 * g + 0.114 * b);
            return luminance < 80 ? "dark" : "light";
        }
        return "light";
    }

    /* ═══════════════════════════════════════════════════════════════════
       SECTION 7 — CORE RESOLVER
       Implements hierarchy exactly as frozen in §3 of the spec.
       Merge order: Level 7 (lowest) → Level 1 (highest).
       Later merge always wins.
    ═══════════════════════════════════════════════════════════════════ */
    function _resolveHierarchy() {
        /* License gate: if not Active/Grace, return System Default only */
        if (!_isFullResolutionAllowed()) {
            return Object.assign({}, SYSTEM_DEFAULT_TOKENS);
        }

        var resolved = {};
        /* Merge from lowest to highest — each level overwrites previous */
        Object.assign(resolved, _readSystemDefault());    /* Level 7 */
        Object.assign(resolved, _readStoreDefault());     /* Level 6 */
        Object.assign(resolved, _readRoleDefault());      /* Level 5 */
        Object.assign(resolved, _readUserThemePreference()); /* Level 4 */
        Object.assign(resolved, _readUserModuleOverride()); /* Level 3 */
        Object.assign(resolved, _readSystemModulePolicy()); /* Level 2 */
        Object.assign(resolved, _readTerminalPolicy());   /* Level 1 */
        return resolved;
    }

    /* ═══════════════════════════════════════════════════════════════════
       SECTION 8 — PUBLIC EXPORT
       Only _resolveHierarchy is exposed — as an internal engine function.
       Components must NEVER call this directly.
       Components use SMRITI.getResolvedUIConfig() from smriti_theme_manager.js
    ═══════════════════════════════════════════════════════════════════ */
    global.SMRITI._uiResolverEngine = {
        resolveHierarchy:          _resolveHierarchy,
        applyAccessibilityLayer:   _applyAccessibilityOverrides,
        detectMode:                _detectMode,
        SYSTEM_DEFAULT_TOKENS:     SYSTEM_DEFAULT_TOKENS   /* read-only reference */
    };

}(window));
