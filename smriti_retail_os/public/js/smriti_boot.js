/**
 * @file: smriti_retail_os/public/js/smriti_boot.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
(function () {
    'use strict';

    var SMRITI_NAME  = 'SMRITI Retail OS';
    var SMRITI_LOGO  = '/assets/smriti_retail_os/images/smriti_logo.svg';
    var SAFE_ROUTE   = '/smriti';
    var DESK_ROLES   = ['System Manager'];
    var ADMIN_USER   = 'Administrator';

    // ─── CRITICAL: Override frappe.boot.setup_complete ASAP ──────────────────
    // Frappe's router.js checks frappe.boot.setup_complete and redirects to setup-wizard
    // if it's falsy. We must override it before frappe.ready() fires.
    // This is a client-side safety net complementing the server-side boot hook.
    (function forceSetupComplete() {
        if (typeof frappe !== 'undefined' && frappe.boot) {
            frappe.boot.setup_complete = true;
            frappe.boot.sysdefaults = frappe.boot.sysdefaults || {};
            frappe.boot.sysdefaults.setup_complete = true;
        }
    })();

    // Override frappe.set_route to intercept setup-wizard navigation
    var _originalSetRoute = (typeof frappe !== 'undefined' && frappe.set_route) ? frappe.set_route.bind(frappe) : null;
    if (_originalSetRoute) {
        frappe.set_route = function() {
            var args = Array.prototype.slice.call(arguments);
            var firstArg = args[0];
            // Block any attempt to route to setup-wizard
            if (firstArg === 'setup-wizard' ||
                (Array.isArray(firstArg) && firstArg[0] === 'setup-wizard') ||
                (typeof firstArg === 'string' && firstArg.includes('setup-wizard'))) {
                console.warn('[SMRITI] Blocked frappe.set_route to setup-wizard. Staying on SMRITI.');
                return;
            }
            return _originalSetRoute.apply(frappe, args);
        };
    }

    function init() {
        applyBranding();
        enforceDesktopAccess();
        hideSetupWizard();
        // Re-apply the boot override after frappe is fully loaded
        if (typeof frappe !== 'undefined' && frappe.boot) {
            frappe.boot.setup_complete = true;
        }
    }

    function applyBranding() {
        // Page title — JS only (CSS cannot set title)
        if (document.title && !document.title.includes(SMRITI_NAME)) {
            document.title = SMRITI_NAME;
        }

        // Logo replacement
        var logos = document.querySelectorAll(
            '.navbar-brand img, .desk-logo img, img[src*="frappe"], img[src*="erpnext"]'
        );
        logos.forEach(function(img) {
            if (!img.src.includes('smriti')) {
                img.src = SMRITI_LOGO;
            }
        });

        // Favicon
        var fav = document.querySelector("link[rel~='icon']");
        if (!fav) {
            fav      = document.createElement('link');
            fav.rel  = 'icon';
            document.head.appendChild(fav);
        }
        fav.href = '/assets/smriti_retail_os/images/smriti_logo.svg';

        // Brand text — replace "Frappe" or "ERPNext" in nav
        document.querySelectorAll('.navbar-brand span, .brand-name').forEach(function(el) {
            if (el.textContent.includes('Frappe') || el.textContent.includes('ERPNext')) {
                el.textContent = SMRITI_NAME;
            }
        });
    }

    function enforceDesktopAccess() {
        var path = window.location.pathname;
        if (!path.startsWith('/desk')) return;

        // Use Frappe boot roles if available
        if (typeof frappe === 'undefined') return;

        frappe.ready(function() {
            var user  = frappe.session && frappe.session.user;
            var roles = (frappe.boot && frappe.boot.user && frappe.boot.user.roles) || [];
            var hasDesk = user === ADMIN_USER
                       || roles.some(function(r) { return DESK_ROLES.indexOf(r) !== -1; });

            if (!hasDesk) {
                window.location.href = SAFE_ROUTE;
            }
        });
    }

    function hideSetupWizard() {
        function _hide() {
            var selectors = [
                '.setup-wizard-container',
                '[data-page="setup-wizard"]',
                '.setup-wizard-slide',
                '#setup-wizard'
            ];
            selectors.forEach(function(sel) {
                var el = document.querySelector(sel);
                if (el) {
                    el.style.display = 'none';
                    // Also redirect away
                    if (window.location.pathname.includes('setup-wizard')) {
                        window.location.href = SAFE_ROUTE;
                    }
                }
            });
        }

        _hide();

        // Watch for dynamic injection
        if (window.MutationObserver) {
            var obs = new MutationObserver(_hide);
            obs.observe(document.body || document.documentElement, {
                childList: true,
                subtree: true
            });
            setTimeout(function() { obs.disconnect(); }, 15000);
        }
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Also run after Frappe finishes loading (belt + suspenders)
    if (typeof frappe !== 'undefined' && frappe.ready) {
        frappe.ready(init);
    }

})();
