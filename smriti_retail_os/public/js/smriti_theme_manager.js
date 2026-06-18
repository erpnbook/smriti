/**
 * @file: smriti_retail_os/public/js/smriti_theme_manager.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
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
 * @version 1.0.0
 * @status Phase 1A — Foundation Layer
 * @author AITDL / SMRITI Engineering
 * @license MIT — Copyright (c) 2026 AITDL NETWORK & ERPNbook.com
 */

(function (global) {
    "use strict";

    global.SMRITI = global.SMRITI || {};

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
        var cssLines = [":root {"];

        /* Write each token as a CSS Custom Property */
        Object.keys(tokens).forEach(function (key) {
            if (key.indexOf("--smriti-") === 0) {
                cssLines.push("  " + key + ": " + tokens[key] + ";");
            }
        });

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
            /* Insert as first child of head for lowest specificity cascade position */
            var head = document.head || document.getElementsByTagName("head")[0];
            head.insertBefore(_applyStyleTag, head.firstChild);
        }

        _applyStyleTag.textContent = cssText;
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
       AUTO-INIT
       Initialize on DOMContentLoaded if frappe is not managing the load.
       For Frappe pages, initUIEngine() should be called from the page's
       frappe.ready() or page init function to ensure frappe.boot is loaded.
    ═══════════════════════════════════════════════════════════════════ */
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            /* Only auto-init if Frappe is not present (standalone pages) */
            if (!window.frappe) {
                SMRITI.initUIEngine();
            }
        });
    }

}(window));
