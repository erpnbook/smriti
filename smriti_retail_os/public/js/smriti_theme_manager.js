/**
 * @file: smriti_retail_os/public/js/smriti_theme_manager.js
 * @description: SMRITI UI Theme Manager — applies theme styles and configuration.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.8.6
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
/**
 * @file smriti_theme_manager.js
 * @description SMRITI UI Configuration Engine — Public Runtime Contract
 *              Implements SMRITI.getResolvedUIConfig() and SMRITI.applyUIConfig()
 *              as defined in:
 *              docs/architecture/ui/SMRITI_UI_CONFIGURATION_ENGINE_V1.md §8
 *
 * GOVERNANCE:
 *   - This is the ONLY file components may call for UI configuration.
 *   - Components must ONLY access the .tokens map from getResolvedUIConfig().
 *   - Components must NEVER access .themeProfile, .experienceProfile, .brandProfile
 *   - Those are resolver internals — they do not exist on the public return object.
 *   - This file depends on smriti_ui_resolver.js (must be loaded first).
 *
 * CORRECT usage from any component:
 *   const ui = SMRITI.getResolvedUIConfig();
 *   ui.tokens["--smriti-color-bg-primary"]   ← CORRECT
 *   ui.tokens["--smriti-spacing-padding-y"]  ← CORRECT
 *   ui.mode                                  ← CORRECT (light/dark hint for icons)
 *   ui.reducedMotion                         ← CORRECT (accessibility flag)
 *   ui.themeProfile                          ← FORBIDDEN (does not exist)
 *
 * @version 1.8.6
 * @status Phase 1A — Foundation Layer
 * @author AITDL / SMRITI Engineering
 * @license MIT — Copyright (c) 2026 AITDL NETWORK & ERPNbook.com
 */

(function (global) {
    "use strict";

    global.SMRITI = global.SMRITI || global.smriti || {};
    global.smriti = global.SMRITI;

    /* ═══════════════════════════════════════════════════════════════════
       DEPENDENCY GUARD
       smriti_ui_resolver.js must be loaded before this file.
    ═══════════════════════════════════════════════════════════════════ */
    if (!global.SMRITI._uiResolverEngine) {
        console.error("[SMRITI Theme Manager] smriti_ui_resolver.js must be loaded before smriti_theme_manager.js");
    }

    /* ═══════════════════════════════════════════════════════════════════
       INTERNAL STATE
    ═══════════════════════════════════════════════════════════════════ */
    var _lastAppliedConfig = null;
    var _applyStyleTag     = null;
    var _STYLE_TAG_ID      = "smriti-ui-engine-tokens";

    /* ═══════════════════════════════════════════════════════════════════
       SMRITI.getResolvedUIConfig()
       Public contract — as frozen in spec §8.
       Returns resolved token map + mode + reducedMotion flag.
       Never returns themeProfile, experienceProfile, or brandProfile.
    ═══════════════════════════════════════════════════════════════════ */
    SMRITI.getResolvedUIConfig = function () {
        if (!global.SMRITI._uiResolverEngine) {
            /* Fallback: return system defaults if resolver not loaded */
            return {
                tokens:       {},
                mode:         "light",
                reducedMotion: false
            };
        }

        var engine = global.SMRITI._uiResolverEngine;

        /* Step 1: Run 7-level hierarchy resolver */
        var resolvedTokens = engine.resolveHierarchy();

        /* Step 2: Apply accessibility override layer (post-resolution, cannot be suppressed) */
        var a11y = engine.applyAccessibilityLayer(resolvedTokens);

        /* Step 3: Detect light/dark mode from resolved tokens */
        var mode = engine.detectMode(a11y.tokens);

        /* Step 4: Build public return object — NO profile names exposed */
        return {
            tokens:        a11y.tokens,       /* Map of --smriti-* → resolved value */
            mode:          mode,              /* "light" | "dark" */
            reducedMotion: a11y.reducedMotion /* true if reduced motion active */
            /*
             * themeProfile, experienceProfile, brandProfile are NOT here.
             * They are resolver internals consumed inside smriti_ui_resolver.js.
             * If you need them for debugging, use SMRITI.debugUIConfig() (dev only).
             */
        };
    };

    /* ═══════════════════════════════════════════════════════════════════
       SMRITI.applyUIConfig(config)
       Public contract — as frozen in spec §8.
       Writes resolved token map to :root as CSS Custom Properties.
       Idempotent — safe to call multiple times.
    ═══════════════════════════════════════════════════════════════════ */
    SMRITI.applyUIConfig = function (config) {
        if (!config || !config.tokens) {
            console.warn("[SMRITI Theme Manager] applyUIConfig called with invalid config.");
            return;
        }

        var tokens = config.tokens;
        var cssLines = [":root, body {"];

        /* Write each token as a CSS Custom Property */
        Object.keys(tokens).forEach(function (key) {
            if (key.indexOf("--smriti-") === 0) {
                cssLines.push("  " + key + ": " + tokens[key] + ";");
            }
        });

        /* Bridge common shorthand variables for instant theme reactivity across standalone modules */
        cssLines.push("  --bg: var(--smriti-color-bg-page);");
        cssLines.push("  --bg2: var(--smriti-color-bg-primary);");
        cssLines.push("  --card: var(--smriti-color-bg-secondary);");
        cssLines.push("  --card2: var(--smriti-color-bg-elevated, var(--smriti-color-bg-secondary));");
        cssLines.push("  --border: var(--smriti-color-border-default);");
        cssLines.push("  --border2: var(--smriti-color-border-strong);");
        cssLines.push("  --primary: var(--smriti-color-brand-primary);");
        cssLines.push("  --primary-lt: var(--smriti-color-brand-light);");
        cssLines.push("  --accent: var(--smriti-color-brand-accent, var(--smriti-color-brand-light));");
        cssLines.push("  --text: var(--smriti-color-text-primary);");
        cssLines.push("  --text-muted: var(--smriti-color-text-muted);");
        cssLines.push("  --text-sub: var(--smriti-color-text-subtle);");

        cssLines.push("}");

        /* Write dark-mode body attribute tokens if mode is dark */
        if (config.mode === "dark") {
            cssLines.push('body[data-theme="dark"], body.dark-mode, body.smriti-pos-dark {');
            Object.keys(tokens).forEach(function (key) {
                if (key.indexOf("--smriti-") === 0) {
                    cssLines.push("  " + key + ": " + tokens[key] + ";");
                }
            });
            cssLines.push("}");
        }

        var cssText = cssLines.join("\n");

        /* Inject or update the engine-owned style tag */
        _applyStyleTag = document.getElementById(_STYLE_TAG_ID);
        if (!_applyStyleTag) {
            _applyStyleTag = document.createElement("style");
            _applyStyleTag.id = _STYLE_TAG_ID;
            _applyStyleTag.setAttribute("data-smriti-engine", "v1");
            /* Append as LAST child of head so engine :root wins cascade over
               any earlier page-level :root block (same specificity, later wins). */
            var head = document.head || document.getElementsByTagName("head")[0];
            head.appendChild(_applyStyleTag);
        }

        _applyStyleTag.textContent = cssText;

        /* Apply profile_token_set class to body safely */
        if (typeof document !== "undefined" && document.body) {
            var body = document.body;
            
            /* Sync dark mode state */
            if (config.mode === "dark") {
                body.classList.add("dark-mode");
                body.setAttribute("data-theme", "dark");
            } else {
                body.classList.remove("dark-mode");
                body.removeAttribute("data-theme");
            }

            var classesToRemove = [];
            for (var i = 0; i < body.classList.length; i++) {
                var cls = body.classList.item(i);
                if (cls && cls.indexOf("smriti-theme-") === 0) {
                    classesToRemove.push(cls);
                }
            }
            classesToRemove.forEach(function (cls) {
                body.classList.remove(cls);
            });

            var profileTokenSet = tokens["profile_token_set"];
            if (profileTokenSet) {
                body.classList.add("smriti-theme-" + profileTokenSet);
                body.setAttribute("data-theme-profile", profileTokenSet);
            } else {
                body.removeAttribute("data-theme-profile");
            }
        }

        _lastAppliedConfig = config;

        /* Dispatch event for listeners (e.g., charts that need to redraw) */
        try {
            document.dispatchEvent(new CustomEvent("smriti-ui-config-applied", {
                detail: { mode: config.mode, reducedMotion: config.reducedMotion }
            }));
        } catch (e) { /* IE11 fallback — ignore */ }
    };

    /* ═══════════════════════════════════════════════════════════════════
       SMRITI.initUIEngine()
       Call once on page load. Resolves and applies configuration immediately.
       Also sets up re-apply listeners for theme changes.
    ═══════════════════════════════════════════════════════════════════ */
    SMRITI.initUIEngine = function () {
        /* Initial apply */
        var config = SMRITI.getResolvedUIConfig();
        SMRITI.applyUIConfig(config);

        /* Re-apply on theme toggle (existing sidebar toggle fires this event) */
        document.addEventListener("smriti-theme-style-changed", function () {
            SMRITI.applyUIConfig(SMRITI.getResolvedUIConfig());
        });

        /* Re-apply on OS dark mode change */
        try {
            var darkMQ = window.matchMedia("(prefers-color-scheme: dark)");
            if (darkMQ && darkMQ.addEventListener) {
                darkMQ.addEventListener("change", function () {
                    SMRITI.applyUIConfig(SMRITI.getResolvedUIConfig());
                });
            }
        } catch (e) { /* matchMedia not available */ }

        /* Re-apply on reduced motion change */
        try {
            var motionMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
            if (motionMQ && motionMQ.addEventListener) {
                motionMQ.addEventListener("change", function () {
                    SMRITI.applyUIConfig(SMRITI.getResolvedUIConfig());
                });
            }
        } catch (e) { /* matchMedia not available */ }
    };

    /* ═══════════════════════════════════════════════════════════════════
       SMRITI.debugUIConfig()
       Development only — never call from production components.
       Returns resolver internals for debugging purposes.
       This is NOT part of the frozen public contract.
    ═══════════════════════════════════════════════════════════════════ */
    SMRITI.debugUIConfig = function () {
        if (window.location.hostname === "localhost" ||
            window.location.hostname === "127.0.0.1") {
            return {
                publicConfig:  _lastAppliedConfig,
                resolverAvailable: !!global.SMRITI._uiResolverEngine,
                note: "DEBUG ONLY — do not use resolver internals in components"
            };
        }
        console.warn("[SMRITI Theme Manager] debugUIConfig is only available on localhost.");
        return null;
    };

    /* ═══════════════════════════════════════════════════════════════════
       SMRITI.switchTheme(themeKey)
       Pre-condition 2 (THEME-002): Real-time theme switching without reload.
       Status: IMPLEMENTED — 2026-06-24 (ux_theme_audit_v1.1.md)

        Valid themeKey values:
          'hybrid-light'    — Neumorphic clay. Premium visual.
          'hybrid-dark'     — Dark mode. Night-shift / technical users.
          'sleek-compact'   — High-density flat. Default. Inventory / purchase ops.
          'minimalist'      — Ultra-clean enterprise white.

       Fires 'smriti-theme-changed' CustomEvent on document.
       Components that render theme-sensitive content should listen for it.

       Usage:
         SMRITI.switchTheme('sleek-compact');
    ═══════════════════════════════════════════════════════════════════ */
    SMRITI.switchTheme = function (themeKey) {
        var validKeys = ["hybrid-light", "hybrid-dark", "sleek-compact", "minimalist"];

        /* Normalize legacy keys */
        if (themeKey === "hybrid")    themeKey = "hybrid-light";
        if (themeKey === "smriti-default") themeKey = "sleek-compact";

        if (validKeys.indexOf(themeKey) === -1) {
            console.warn("[SMRITI Theme Manager] Invalid theme key:", themeKey,
                         "— must be one of:", validKeys.join(", "));
            return;
        }

        try {
            /* Persist preference — resolver reads this at Level 4 */
            localStorage.setItem("smriti-theme-style", themeKey);

            /* Re-resolve with new preference and apply immediately */
            var config = SMRITI.getResolvedUIConfig();
            SMRITI.applyUIConfig(config);

            /* Apply body class for CSS-only selectors (backward compat) */
            document.body.classList.remove(
                "theme-minimalist", "theme-sleek-compact",
                "theme-hybrid-light", "theme-hybrid-dark"
            );
            document.body.classList.add("theme-" + themeKey);
            document.body.setAttribute("data-smriti-theme", themeKey);

            /* Dispatch event for subscribers (charts, components, sidebar pills) */
            document.dispatchEvent(new CustomEvent("smriti-theme-changed", {
                bubbles: true,
                detail: {
                    theme:  themeKey,
                    mode:   config.mode,
                    tokens: config.tokens
                }
            }));

            /* Also fire legacy event for sidebar style-changed listeners */
            document.dispatchEvent(new CustomEvent("smriti-theme-style-changed", {
                bubbles: true,
                detail: { style: themeKey }
            }));

        } catch (e) {
            console.error("[SMRITI Theme Manager] switchTheme failed:", e);
        }
    };

    /* ═══════════════════════════════════════════════════════════════════
       SMRITI.getCurrentTheme()
       Returns the currently active theme key from localStorage.
       Defaults to 'sleek-compact' if not set (THEME-005, Founder Approved 2026-06-24).
       Used by sidebar theme pills to sync active state.
    ═══════════════════════════════════════════════════════════════════ */
    SMRITI.getCurrentTheme = function () {
        try {
            /* Fallback reads from resolver's DEFAULT_THEME_PROFILE — single source of truth.
             * SMRITI.getDefaultTheme() is set to "sleek-compact" per THEME-005 (Founder Approved 2026-06-24).
             * If resolver hasn't loaded yet, fall back to "hybrid-light" as a safe guard. */
            var _default = (SMRITI.getDefaultTheme && SMRITI.getDefaultTheme()) || "sleek-compact";
            var raw = localStorage.getItem("smriti-theme-style") || _default;
            /* Normalise legacy aliases */
            if (raw === "hybrid")         raw = "hybrid-light";
            if (raw === "smriti-default") raw = _default;
            return raw;
        } catch (e) {
            return (SMRITI.getDefaultTheme && SMRITI.getDefaultTheme()) || "sleek-compact";
        }
    };

    /* ═══════════════════════════════════════════════════════════════════
       ENTERPRISE THEME REGISTRY & APPEARANCE API
    ═══════════════════════════════════════════════════════════════════ */
    SMRITI.getInstalledThemes = function (callback) {
        var builtInThemes = [
            { id: "sleek-compact", name: "SMRITI Midnight Edition", dark: true, default: true, description: "High-density flat navy modern theme." },
            { id: "hybrid-light", name: "Neumorphic Clay Light", dark: false, description: "Soft neumorphic clay surfaces with purple brand accents." },
            { id: "hybrid-dark", name: "Neumorphic Dark", dark: true, description: "Tactile dark neumorphic surfaces for night-shift operators." },
            { id: "minimalist", name: "Enterprise Pure White", dark: false, description: "Ultra-clean high-contrast white layout." }
        ];

        if (typeof frappe !== "undefined" && frappe.call) {
            frappe.call({
                method: "smriti_retail_os.api.theme_api.get_installed_themes",
                callback: function (r) {
                    if (r && r.message && Array.isArray(r.message) && r.message.length > 0) {
                        if (callback) callback(r.message);
                    } else {
                        if (callback) callback(builtInThemes);
                    }
                },
                error: function () {
                    if (callback) callback(builtInThemes);
                }
            });
        } else {
            if (callback) callback(builtInThemes);
        }
    };

    SMRITI.applyAppearanceSettings = function (opts) {
        if (!opts) return;
        if (opts.theme) {
            SMRITI.switchTheme(opts.theme);
        }
        if (opts.density) {
            localStorage.setItem("smriti-ui-density", opts.density);
            document.body.classList.remove("density-compact", "density-comfortable", "density-spacious");
            document.body.classList.add("density-" + opts.density);
            document.body.setAttribute("data-density", opts.density);
        }
        if (opts.accentColor) {
            localStorage.setItem("smriti-accent-color", opts.accentColor);
            document.documentElement.style.setProperty("--smriti-color-brand-primary", opts.accentColor);
        }
        if (typeof opts.highContrast !== "undefined") {
            localStorage.setItem("smriti-a11y-high-contrast", opts.highContrast ? "true" : "false");
        }
        if (typeof opts.reducedMotion !== "undefined") {
            localStorage.setItem("smriti-a11y-reduced-motion", opts.reducedMotion ? "true" : "false");
        }

        SMRITI.applyUIConfig(SMRITI.getResolvedUIConfig());

        if (typeof frappe !== "undefined" && frappe.call && frappe.session && frappe.session.user !== "Guest") {
            frappe.call({
                method: "smriti_retail_os.api.theme_api.save_user_appearance",
                args: {
                    theme_id: opts.theme,
                    density: opts.density,
                    accent_color: opts.accentColor,
                    high_contrast: opts.highContrast,
                    reduced_motion: opts.reducedMotion
                }
            });
        }
    };

    /* ═══════════════════════════════════════════════════════════════════
       AUTO-INIT
       Initialize on DOMContentLoaded if frappe is not managing the load.
       For Frappe pages, initUIEngine() should be called from the page's
       frappe.ready() or page init function to ensure frappe.boot is loaded.
    ═══════════════════════════════════════════════════════════════════ */
    if (document.readyState !== "loading") {
        SMRITI.initUIEngine();
    } else {
        document.addEventListener("DOMContentLoaded", function () {
            SMRITI.initUIEngine();
        });
    }

}(window));
