/**
 * @file: smriti_retail_os/public/js/smriti_ui_resolver.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.4.0
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

    /**
     * DEFAULT_THEME_PROFILE — SMRITI-THEME-005
     * Founder Approved: Jawahar R. Mallah, AITDL — 2026-06-24
     *
     * Controls the out-of-box theme for new users (no stored preference).
     * Does NOT affect SYSTEM_DEFAULT_TOKENS or any existing user preference.
     * Rollback: change value to "hybrid-light" and redeploy assets only.
     *
     * Valid values: "hybrid-light" | "hybrid-dark" | "sleek-compact" | "minimalist"
     */
    var DEFAULT_THEME_PROFILE = "sleek-compact";   /* THEME-005 — Founder Approved 2026-06-24 */

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
        /* Spacing & Layout Density */
        "--smriti-spacing-xs":                 "4px",
        "--smriti-spacing-sm":                 "8px",
        "--smriti-spacing-md":                 "12px",
        "--smriti-spacing-lg":                 "16px",
        "--smriti-spacing-xl":                 "24px",
        "--smriti-spacing-2xl":                "32px",
        "--smriti-spacing-padding-y":          "10px",
        "--smriti-spacing-padding-x":          "14px",
        "--smriti-spacing-gap":                "12px",
        "--smriti-spacing-card":               "16px",
        "--smriti-spacing-section":            "24px",
        "--smriti-table-row-height":           "44px",
        "--smriti-card-header-height":         "48px",
        "--smriti-toolbar-height":             "56px",
        "--smriti-form-field-height":          "38px",
        /* Layout Dimensions */
        "--smriti-dimension-sidebar-width":           "260px",
        "--smriti-dimension-sidebar-collapsed-width": "68px",
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
        "--smriti-z-index-tooltip":            "1200",
        /* Font Family — Q3 Foundation Hardening (ux_theme_audit_v1.2) */
        "--smriti-font-family-primary":        "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "--smriti-font-family-display":        "'Outfit', 'Inter', sans-serif",
        "--smriti-font-family-mono":           "'JetBrains Mono', 'Fira Code', monospace",
        /* Line Height — Q3 Foundation Hardening */
        "--smriti-line-height-tight":          "1.25",
        "--smriti-line-height-snug":           "1.375",
        "--smriti-line-height-normal":         "1.5",
        "--smriti-line-height-relaxed":        "1.625",
        "--smriti-line-height-loose":          "2",
        /* Content & Panel Widths — Q3 Foundation Hardening */
        "--smriti-content-max-width":          "1400px",
        "--smriti-panel-width-sm":             "280px",
        "--smriti-panel-width-md":             "360px",
        "--smriti-panel-width-lg":             "480px",
        "--smriti-panel-width-xl":             "640px",
        "--smriti-drawer-width":               "420px"
    };

    /* ═══════════════════════════════════════════════════════════════════
       SECTION 2 — PROFILE TOKEN OVERRIDES (resolver internals)
       GOVERNANCE: These objects are NEVER exposed to components.
       They are consumed exclusively inside _resolveHierarchy().
     ═══════════════════════════════════════════════════════════════════ */

    /**
     * Theme profiles — internal resolver use only.
     * Pre-condition 3 (THEME-003): All 4 profiles now have explicit token sets.
     * Status: PASSED — 2026-06-24 (ux_theme_audit_v1.1.md)
     */
    var _THEME_PROFILES = {

        /* ── hybrid-light ─────────────────────────────────────────────────
           Neumorphic clay base. Premium visual appeal. Spacious layout.
           Audience: Dashboards, Executive views.
           Score: 5.5/10 (productivity) | 8/10 (visual premium)
        ────────────────────────────────────────────────────────────────── */
        "hybrid-light": {
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
            "--smriti-color-bg-overlay":           "rgba(15,23,42,0.55)",
            "--smriti-shadow-neu-float":           "6px 6px 14px #c5c9d4, -6px -6px 14px #ffffff",
            "--smriti-shadow-neu-pressed":         "inset 6px 6px 12px #c5c9d4, inset -6px -6px 12px #ffffff",
            "--smriti-shadow-neu-float-lg":        "10px 10px 24px #c0c4d0, -10px -10px 24px #ffffff",
            "--smriti-shadow-neu-pressed-sm":      "inset 3px 3px 7px #c8ccd6, inset -3px -3px 7px #ffffff",
            "--smriti-spacing-padding-y":          "10px",
            "--smriti-spacing-padding-x":          "14px",
            "--smriti-spacing-card":               "16px",
            "--smriti-spacing-gap":                "12px",
            "--smriti-table-row-height":           "44px",
            "--smriti-card-header-height":         "48px",
            "--smriti-toolbar-height":             "56px",
            "--smriti-form-field-height":          "38px",
            "--smriti-dimension-sidebar-width":    "260px",
            "--smriti-font-size-base":             "0.95rem",
            "--smriti-font-size-sm":               "0.82rem",
            "--smriti-radius-md":                  "10px",
            "--smriti-radius-lg":                  "14px"
        },

        /* ── hybrid-dark ──────────────────────────────────────────────────
           Dark neumorphic. Low-light environments, technical users.
           Score: 7.0/10 | Audience: Night-shift, Technical users.
        ────────────────────────────────────────────────────────────────── */
        "hybrid-dark": {
            "--smriti-color-bg-page":              "#0f0f13",
            "--smriti-color-bg-primary":           "#18181b",
            "--smriti-color-bg-secondary":         "#1e1e23",
            "--smriti-color-bg-elevated":          "#26262d",
            "--smriti-color-text-primary":         "#f1f5f9",
            "--smriti-color-text-muted":           "#94a3b8",
            "--smriti-color-text-subtle":          "#64748b",
            "--smriti-color-brand-primary":        "#7c3aed",
            "--smriti-color-brand-light":          "#a78bfa",
            "--smriti-color-brand-dark":           "#5b21b6",
            "--smriti-color-border-default":       "#2d2d35",
            "--smriti-color-border-strong":        "#3d3d47",
            "--smriti-color-bg-overlay":           "rgba(0,0,0,0.70)",
            "--smriti-color-status-success":       "#10b981",
            "--smriti-color-status-success-bg":    "rgba(16,185,129,0.12)",
            "--smriti-color-status-success-border":"rgba(16,185,129,0.3)",
            "--smriti-color-status-danger":        "#f87171",
            "--smriti-color-status-danger-bg":     "rgba(248,113,113,0.12)",
            "--smriti-color-status-danger-border": "rgba(248,113,113,0.3)",
            "--smriti-color-status-warning":       "#fbbf24",
            "--smriti-color-status-warning-bg":    "rgba(251,191,36,0.12)",
            "--smriti-color-status-warning-border":"rgba(251,191,36,0.3)",
            "--smriti-color-status-info":          "#38bdf8",
            "--smriti-color-status-info-bg":       "rgba(56,189,248,0.12)",
            "--smriti-color-status-info-border":   "rgba(56,189,248,0.3)",
            "--smriti-shadow-xs":                  "0 1px 2px rgba(0,0,0,0.4)",
            "--smriti-shadow-sm":                  "0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.3)",
            "--smriti-shadow-md":                  "0 4px 12px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.3)",
            "--smriti-shadow-lg":                  "0 12px 28px rgba(0,0,0,0.55), 0 4px 8px rgba(0,0,0,0.3)",
            "--smriti-shadow-neu-float":           "4px 4px 10px rgba(0,0,0,0.6), -2px -2px 8px rgba(50,50,60,0.4)",
            "--smriti-shadow-neu-pressed":         "inset 4px 4px 8px rgba(0,0,0,0.6), inset -2px -2px 6px rgba(50,50,60,0.3)",
            "--smriti-spacing-padding-y":          "10px",
            "--smriti-spacing-padding-x":          "14px",
            "--smriti-spacing-card":               "16px",
            "--smriti-spacing-gap":                "12px",
            "--smriti-table-row-height":           "44px",
            "--smriti-card-header-height":         "48px",
            "--smriti-toolbar-height":             "56px",
            "--smriti-form-field-height":          "38px",
            "--smriti-dimension-sidebar-width":    "260px",
            "--smriti-font-size-base":             "0.95rem",
            "--smriti-font-size-sm":               "0.82rem"
        },

        /* ── sleek-compact ────────────────────────────────────────────────
           High-density flat modern layout. Benchmark-aligned (Linear/Odoo).
           Score: 8.2/10 | Pre-condition 1 PASSED — token adoption verified.
           Audience: Inventory controllers, purchase team, PSV, reports.
        ────────────────────────────────────────────────────────────────── */
        "sleek-compact": {
            "--smriti-color-bg-page":              "#f1f4f8",
            "--smriti-color-bg-primary":           "#ffffff",
            "--smriti-color-bg-secondary":         "#f8fafc",
            "--smriti-color-bg-elevated":          "#ffffff",
            "--smriti-color-text-primary":         "#111827",
            "--smriti-color-text-muted":           "#4b5563",
            "--smriti-color-text-subtle":          "#9ca3af",
            "--smriti-color-brand-primary":        "#6941c6",
            "--smriti-color-brand-light":          "#9e77ed",
            "--smriti-color-brand-dark":           "#53389e",
            "--smriti-color-border-default":       "#e5e7eb",
            "--smriti-color-border-strong":        "#d1d5db",
            "--smriti-color-bg-overlay":           "rgba(17,24,39,0.50)",
            /* Flat shadows — no neumorphism on data surfaces */
            "--smriti-shadow-xs":                  "0 1px 2px rgba(0,0,0,0.04)",
            "--smriti-shadow-sm":                  "0 1px 2px rgba(0,0,0,0.06), 0 1px 1px rgba(0,0,0,0.04)",
            "--smriti-shadow-md":                  "0 2px 6px rgba(0,0,0,0.08)",
            "--smriti-shadow-lg":                  "0 4px 16px rgba(0,0,0,0.10)",
            "--smriti-shadow-neu-float":           "0 1px 3px rgba(0,0,0,0.08)",
            "--smriti-shadow-neu-pressed":         "inset 0 1px 2px rgba(0,0,0,0.06)",
            /* Density: 32px rows, 40px toolbar, 36px card header */
            "--smriti-spacing-padding-y":          "6px",
            "--smriti-spacing-padding-x":          "10px",
            "--smriti-spacing-card":               "12px",
            "--smriti-spacing-gap":                "8px",
            "--smriti-table-row-height":           "32px",
            "--smriti-card-header-height":         "36px",
            "--smriti-toolbar-height":             "40px",
            "--smriti-form-field-height":          "32px",
            "--smriti-dimension-sidebar-width":    "220px",
            "--smriti-font-size-base":             "0.88rem",
            "--smriti-font-size-sm":               "0.78rem",
            "--smriti-font-size-xs":               "0.70rem",
            "--smriti-radius-sm":                  "4px",
            "--smriti-radius-md":                  "6px",
            "--smriti-radius-lg":                  "8px"
        },

        /* ── minimalist ───────────────────────────────────────────────────
           Ultra-clean enterprise white. Maximum content focus.
           Score: 4.5/10 (incomplete) | Status: Foundation only.
           Audience: N/A (not production-ready until full token set added)
        ────────────────────────────────────────────────────────────────── */
        "minimalist": {
            "--smriti-color-bg-page":              "#ffffff",
            "--smriti-color-bg-primary":           "#ffffff",
            "--smriti-color-bg-secondary":         "#fafafa",
            "--smriti-color-bg-elevated":          "#ffffff",
            "--smriti-color-text-primary":         "#18181b",
            "--smriti-color-text-muted":           "#52525b",
            "--smriti-color-text-subtle":          "#a1a1aa",
            "--smriti-color-brand-primary":        "#18181b",
            "--smriti-color-brand-light":          "#52525b",
            "--smriti-color-brand-dark":           "#09090b",
            "--smriti-color-border-default":       "#f4f4f5",
            "--smriti-color-border-strong":        "#e4e4e7",
            "--smriti-color-bg-overlay":           "rgba(0,0,0,0.30)",
            /* Zero-shadow design */
            "--smriti-shadow-xs":                  "none",
            "--smriti-shadow-sm":                  "0 1px 0 #f4f4f5",
            "--smriti-shadow-md":                  "0 1px 0 #e4e4e7",
            "--smriti-shadow-lg":                  "0 1px 3px rgba(0,0,0,0.06)",
            "--smriti-shadow-neu-float":           "none",
            "--smriti-shadow-neu-pressed":         "none",
            /* Balanced density — not as tight as sleek-compact */
            "--smriti-spacing-padding-y":          "8px",
            "--smriti-spacing-padding-x":          "12px",
            "--smriti-spacing-card":               "14px",
            "--smriti-spacing-gap":                "10px",
            "--smriti-table-row-height":           "36px",
            "--smriti-card-header-height":         "40px",
            "--smriti-toolbar-height":             "44px",
            "--smriti-form-field-height":          "34px",
            "--smriti-dimension-sidebar-width":    "240px",
            "--smriti-font-size-base":             "0.90rem",
            "--smriti-font-size-sm":               "0.80rem",
            "--smriti-radius-sm":                  "3px",
            "--smriti-radius-md":                  "5px",
            "--smriti-radius-lg":                  "8px"
        },

        /* ── smriti-default (alias for hybrid-light) ──────────────────────
           Backward-compatibility alias. Do not use in new code.
           Use 'hybrid-light' explicitly.
        ────────────────────────────────────────────────────────────────── */
        "smriti-default": null  /* resolved dynamically in _mergeProfileTokens */
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

    /** Level 6 — Store Default
     *  Source priority (own-defined first, frappe.boot second):
     *    1. window.SMRITI_SITE_CONFIG  — injected by www page Python controller
     *    2. frappe.boot.smriti_site_config — Frappe SPA context
     *  No frappe dependency required.
     */
    function _readStoreDefault() {
        try {
            /* Own-defined config wins over frappe.boot — no frappe dependency */
            var cfg = window.SMRITI_SITE_CONFIG ||
                      (window.frappe && window.frappe.boot && window.frappe.boot.smriti_site_config) ||
                      {};
            var expProfile = cfg.store_experience || "standard";
            return _mergeProfileTokens("hybrid-light", expProfile, "smriti");
        } catch (e) {
            return {};
        }
    }

    /** Level 5 — Role Default
     *  Source priority:
     *    1. window.SMRITI_USER_ROLES — injected by www page Python controller
     *    2. frappe.user_roles — Frappe SPA context
     *  No frappe dependency required.
     */
    function _readRoleDefault() {
        try {
            var roles = window.SMRITI_USER_ROLES ||
                        (window.frappe && window.frappe.user_roles) ||
                        [];
            if (roles.indexOf("SMRITI Cashier") !== -1) {
                return Object.assign({}, _EXPERIENCE_PROFILES["compact"] || {});
            }
            return {};
        } catch (e) {
            return {};
        }
    }

    /** Level 4 — User Theme Preference (localStorage)
     *  Reads smriti-theme-style key set by the sidebar theme switcher.
     *  Valid keys: 'hybrid-light', 'hybrid-dark', 'sleek-compact', 'minimalist'
     *  Legacy aliases: 'hybrid' → 'hybrid-light'
     *  Pre-condition 2 (THEME-002): this function now powers real-time switching.
     */
    function _readUserThemePreference() {
        try {
            /* Level 4 — User Stored Theme Preference
             * Reads localStorage["smriti-theme-style"] set by sidebar pill / SMRITI.switchTheme().
             * Falls back to DEFAULT_THEME_PROFILE for new users with no stored preference.
             * DEFAULT_THEME_PROFILE is set to "sleek-compact" per THEME-005 (Founder Approved 2026-06-24).
             * SYSTEM_DEFAULT_TOKENS is NOT modified by this change.
             */
            var raw = localStorage.getItem("smriti-theme-style") || DEFAULT_THEME_PROFILE;
            /* Normalise legacy alias */
            var key = raw === "hybrid" ? "hybrid-light" : raw;
            var profile = _THEME_PROFILES[key];
            if (!profile || key === "smriti-default") {
                /* smriti-default is null — fall through to DEFAULT_THEME_PROFILE */
                profile = _THEME_PROFILES[DEFAULT_THEME_PROFILE] || _THEME_PROFILES["hybrid-light"];
            }
            return Object.assign({}, profile || {});
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
        return {};
    }

    /** Level 1 — Terminal Policy (highest — cannot be overridden) */
    function _readTerminalPolicy() {
        return {};
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
       OWN-DEFINED — no frappe dependency.

       Resolution priority:
         1. window.SMRITI_LICENSE  — injected by www page Python controller
         2. frappe.boot.smriti_license — Frappe SPA context
         3. No frappe / no SMRITI_LICENSE on page → ALLOW
            (Python controller already enforced license before serving HTML)

       The gate only BLOCKS when we have explicit negative license data.
       Absence of frappe is NOT a block condition.
    ═══════════════════════════════════════════════════════════════════ */
    function _isFullResolutionAllowed() {
        try {
            /* Own-defined source (www page Python controller injects this) */
            if (window.SMRITI_LICENSE) {
                var s = window.SMRITI_LICENSE.status || window.SMRITI_LICENSE.license_status || "Unregistered";
                return (s === "Active" || s === "Grace Period");
            }

            /* Frappe SPA context */
            if (window.frappe && window.frappe.boot && window.frappe.boot.smriti_license) {
                var lic = window.frappe.boot.smriti_license;
                var status = lic.license_status || lic.status || "Unregistered";
                return (status === "Active" || status === "Grace Period");
            }

            /* No frappe, no SMRITI_LICENSE — standalone www page.
               Python controller already enforced license at server level.
               Allow full resolution. */
            return true;
        } catch (e) {
            /* On error, allow — fail-open for UX, fail-closed only on explicit denial */
            return true;
        }
    }

    /* ═══════════════════════════════════════════════════════════════════
       SECTION 6 — INTERNAL HELPERS
    ═══════════════════════════════════════════════════════════════════ */
    function _mergeProfileTokens(themeProfile, expProfile, brandProfile) {
        var tokens = {};
        /* Resolve null alias (smriti-default → hybrid-light) */
        var tp = _THEME_PROFILES[themeProfile];
        if (!tp) tp = _THEME_PROFILES["hybrid-light"] || {};
        /* Theme → Experience → Brand (left to right, later keys win) */
        Object.assign(tokens, tp);
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

        // Check for URL Parameter override (Highest Priority preview/override)
        // Usage: ?theme=hybrid-light | hybrid-dark | sleek-compact | minimalist
        try {
            var urlParams = new URLSearchParams(window.location.search);
            var themeParam = urlParams.get("theme");
            var validThemes = ["hybrid-light", "hybrid-dark", "sleek-compact", "minimalist", "smriti-default"];
            if (themeParam && validThemes.indexOf(themeParam) !== -1) {
                var urlThemeKey = themeParam === "smriti-default" ? "hybrid-light" : themeParam;
                var urlProfile  = _THEME_PROFILES[urlThemeKey];
                if (urlProfile) Object.assign(resolved, urlProfile);
            }
        } catch(e) {}

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

    /**
     * SMRITI.getDefaultTheme() — Public API
     * Returns the platform default theme profile key.
     * Single source of truth: DEFAULT_THEME_PROFILE constant above.
     * Used by smriti_theme_manager.getCurrentTheme() as its fallback.
     * Change the default via DEFAULT_THEME_PROFILE, not here.
     */
    global.SMRITI.getDefaultTheme = function() {
        return DEFAULT_THEME_PROFILE;
    };

}(window));
