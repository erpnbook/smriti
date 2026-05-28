/**
 * @file: smriti_retail_os/public/js/main.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI Retail OS — Client-Side Branding Safety Net
   Priority order:
     1. frappe.boot data patch  (prevents re-render from ERPNext data)
     2. DOM TreeWalker scrubber (catches dynamic re-renders / modals)
     3. MutationObserver        (re-runs scrubber on every DOM add)
     4. About dialog override   (replaces Frappe's about modal)
   ============================================================ */

var SMRITI_LOGO  = '/assets/smriti_retail_os/images/logo.svg';
var SMRITI_BRAND = 'SMRITI Retail OS';
var SMRITI_YEAR  = new Date().getFullYear();

// Global Fallback for India Compliance GST settings to prevent depends_on evaluation crashes
window.gst_settings = window.gst_settings || {};

/* ── 1. Favicon + initial title ─────────────────────────────────────────── */
(function () {
    document.title = SMRITI_BRAND;
    var link = document.querySelector("link[rel*='icon']") || document.createElement('link');
    link.rel  = 'shortcut icon';
    link.href = '/assets/smriti_retail_os/favicon.png';
    document.head.appendChild(link);
})();

/* ── 2. String replacement helper ───────────────────────────────────────── */
var _SCRUB_RE   = /ERPNext|Frappe\s+(Technologies|Framework)|Built\s+with\s+Frappe|Powered\s+by\s+Frappe/i;
var _SKIP_TAGS  = new Set(['SCRIPT','STYLE','NOSCRIPT','TEXTAREA','CODE','PRE']);
var _scrub_pending = false;

function _replace(txt) {
    return txt
        .replace(/ERPNext\s*[—\-]\s*/g, SMRITI_BRAND + ' — ')
        .replace(/[—\-]\s*ERPNext/g,    '— ' + SMRITI_BRAND)
        .replace(/ERPNext/g,             SMRITI_BRAND)
        .replace(/Frappe Technologies/g, 'SMRITI')
        .replace(/Frappe Framework/g,    SMRITI_BRAND)
        .replace(/Built with Frappe/g,   SMRITI_BRAND)
        .replace(/Powered by Frappe/g,   SMRITI_BRAND);
}

/* ── 3. frappe.boot data patch ──────────────────────────────────────────── */
/*
 * Frappe's workspace sidebar reads:
 *   frappe.boot.installed_apps[app_name].title  → shown as "ERPNext" under workspaces
 *   frappe.boot.app_name                        → global app label
 *   frappe.boot.sysdefaults.app_name            → used in page <title> generation
 *   frappe.workspace_sidebar.pages              → each page has { app, app_title }
 *
 * We patch ALL of these so Frappe's own renderer never produces "ERPNext".
 */
function _patch_frappe_boot() {
    if (!window.frappe) return;

    /* a) Global app name */
    if (frappe.boot) {
        frappe.boot.app_name = SMRITI_BRAND;
        if (frappe.boot.sysdefaults) {
            frappe.boot.sysdefaults.app_name = SMRITI_BRAND;
        }

        /* b) Installed apps — replace erpnext title everywhere */
        if (frappe.boot.installed_apps && Array.isArray(frappe.boot.installed_apps)) {
            frappe.boot.installed_apps.forEach(function (app) {
                if (/erpnext/i.test(app)) { /* installed_apps is a list of app names */ }
            });
        }
        /* installed_apps may also be an object keyed by app name */
        if (frappe.boot.installed_apps && typeof frappe.boot.installed_apps === 'object') {
            Object.keys(frappe.boot.installed_apps).forEach(function (key) {
                var app = frappe.boot.installed_apps[key];
                if (app && app.title && _SCRUB_RE.test(app.title)) {
                    app.title = _replace(app.title);
                }
            });
        }

        /* app_data — replace app titles in app switcher/sidebar headers */
        if (frappe.boot.app_data && Array.isArray(frappe.boot.app_data)) {
            frappe.boot.app_data.forEach(function (app) {
                if (app && app.app_title && _SCRUB_RE.test(app.app_title)) {
                    app.app_title = _replace(app.app_title);
                }
            });
        }

        /* c) Sidebar pages — each workspace page carries an app_title */
        var pages = (frappe.boot.sidebar_pages && frappe.boot.sidebar_pages.pages) ||
                    (frappe.boot.workspaces && frappe.boot.workspaces.pages) ||
                    (frappe.workspace_sidebar && frappe.workspace_sidebar.all_pages) || [];
        if (Array.isArray(pages)) {
            pages.forEach(function (page) {
                if (page.app_title && _SCRUB_RE.test(page.app_title)) {
                    page.app_title = _replace(page.app_title);
                }
                if (page.app && /erpnext/i.test(page.app)) {
                    page.app_title = SMRITI_BRAND;
                }
            });
        }

        /* c2) workspace_sidebar_item / workspace_sidebar_items */
        ['workspace_sidebar_item', 'workspace_sidebar_items'].forEach(function (key) {
            var ws_items = frappe.boot[key];
            if (ws_items && typeof ws_items === 'object') {
                Object.keys(ws_items).forEach(function (ws_name) {
                    var ws_data = ws_items[ws_name];
                    if (ws_data && typeof ws_data === 'object') {
                        if (ws_data.app_title && _SCRUB_RE.test(ws_data.app_title)) ws_data.app_title = _replace(ws_data.app_title);
                        if (ws_data.app && /erpnext/i.test(ws_data.app)) ws_data.app_title = SMRITI_BRAND;
                        var items = ws_data.items || [];
                        if (Array.isArray(items)) {
                            items.forEach(function (item) {
                                if (item.app_title && _SCRUB_RE.test(item.app_title)) item.app_title = _replace(item.app_title);
                                if (item.app && /erpnext/i.test(item.app)) item.app_title = SMRITI_BRAND;
                            });
                        }
                    }
                });
            }
        });

        /* d) Version map */
        if (frappe.boot.versions) {
            Object.keys(frappe.boot.versions).forEach(function (k) {
                if (_SCRUB_RE.test(k)) {
                    var v = frappe.boot.versions[k];
                    delete frappe.boot.versions[k];
                    frappe.boot.versions[_replace(k)] = v;
                }
            });
        }
    }

    /* e) frappe.sys_defaults alias */
    if (frappe.sys_defaults && frappe.sys_defaults.app_name) {
        frappe.sys_defaults.app_name = SMRITI_BRAND;
    }

    /* f) Workspace sidebar controller (Frappe v14/v15) */
    try {
        if (frappe.workspace_sidebar) {
            var ws = frappe.workspace_sidebar;
            /* all_pages is the master list used to render sidebar items */
            if (ws.all_pages) {
                ws.all_pages.forEach(function (p) {
                    if (p.app_title && _SCRUB_RE.test(p.app_title)) p.app_title = _replace(p.app_title);
                    if (p.app && /erpnext/i.test(p.app)) p.app_title = SMRITI_BRAND;
                });
            }
            /* public_pages */
            if (ws.public_pages) {
                ws.public_pages.forEach(function (p) {
                    if (p.app_title && _SCRUB_RE.test(p.app_title)) p.app_title = _replace(p.app_title);
                });
            }
        }
    } catch (e) { /* ignore — workspace_sidebar may not exist on all page types */ }

    /* g) frappe.boot.app_logo_url */
    if (frappe.boot) {
        frappe.boot.app_logo_url = SMRITI_LOGO;
    }

    /* h) frappe.app.sidebar.header_subtitle */
    if (window.frappe && frappe.app && frappe.app.sidebar) {
        if (frappe.app.sidebar.header_subtitle && _SCRUB_RE.test(frappe.app.sidebar.header_subtitle)) {
            frappe.app.sidebar.header_subtitle = _replace(frappe.app.sidebar.header_subtitle);
        }
    }

    /* i) desktop_icons — replace parent_icon and other branding references */
    if (frappe.boot && frappe.boot.desktop_icons && Array.isArray(frappe.boot.desktop_icons)) {
        frappe.boot.desktop_icons.forEach(function (icon) {
            if (icon && icon.parent_icon && _SCRUB_RE.test(icon.parent_icon)) {
                icon.parent_icon = _replace(icon.parent_icon);
            }
        });
    }
}

/* ── 4. DOM TreeWalker scrubber ─────────────────────────────────────────── */
function _scrub_dom() {
    if (_scrub_pending) return;
    _scrub_pending = true;
    requestAnimationFrame(function () {
        _scrub_pending = false;
        _do_scrub();
    });
}

function _do_scrub() {
    _patch_frappe_boot();   /* always re-patch data model first */

    var root = document.body;
    if (!root) return;

    /* A. Text nodes */
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode: function (n) {
            var p = n.parentElement;
            while (p && p !== root) {
                if (_SKIP_TAGS.has(p.tagName)) return NodeFilter.FILTER_REJECT;
                p = p.parentElement;
            }
            return _SCRUB_RE.test(n.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
        }
    });
    var nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(function (node) {
        var v = _replace(node.nodeValue);
        if (v !== node.nodeValue) node.nodeValue = v;
    });

    /* B. Attributes */
    root.querySelectorAll('[title],[placeholder],[data-label],[aria-label],[alt],[data-title]').forEach(function (el) {
        ['title','placeholder','data-label','aria-label','alt','data-title'].forEach(function (attr) {
            var val = el.getAttribute(attr);
            if (val && _SCRUB_RE.test(val)) el.setAttribute(attr, _replace(val));
        });
    });

    /* C. Logo images still pointing to ERPNext/Frappe */
    root.querySelectorAll('img').forEach(function (img) {
        var src = img.getAttribute('src') || '';
        var alt = img.getAttribute('alt') || '';
        if (/erpnext|frappe-logo|frappe\/images/i.test(src) || /ERPNext|Frappe/i.test(alt)) {
            if (img.src !== location.origin + SMRITI_LOGO) {
                img.src = SMRITI_LOGO;
                img.style.cssText += ';max-height:38px;width:auto;';
            }
        }
    });

    /* D. Navbar brand images */
    root.querySelectorAll('.navbar-brand img, header .brand-logo').forEach(function (img) {
        if (img.src !== location.origin + SMRITI_LOGO) {
            img.src = SMRITI_LOGO;
            img.style.height = '32px';
            img.style.width  = 'auto';
        }
    });

    /* E. Page title */
    if (_SCRUB_RE.test(document.title)) document.title = _replace(document.title);
    if (!document.title.includes('SMRITI')) document.title = SMRITI_BRAND;

    /* F. Hide external branding links/footers */
    root.querySelectorAll(
        'a[href*="frappe.io"],a[href*="frappeframework.com"],a[href*="erpnext.com"],' +
        '.powered-by,.built-with,.frappe-copyright,.footer-info'
    ).forEach(function (el) {
        (el.closest('p,div,span,li,footer') || el).style.display = 'none';
    });

    /* G. Sidebar-specific: .sidebar-label, .module-title hold app names rendered by Frappe's
       workspace controller. Target them explicitly to prevent flash-of-ERPNext. */
    root.querySelectorAll(
        '.sidebar-label,.module-title,.workspace-sidebar .item-anchor .title,' +
        '.standard-sidebar-item .sidebar-item-label,.sidebar-item .subtitle,.header-subtitle'
    ).forEach(function (el) {
        if (_SCRUB_RE.test(el.textContent)) el.textContent = _replace(el.textContent);
    });

    /* H. Help & Support Navbar override - replace erpnext/frappe support with erpnbook.com */
    _sanitize_navbar_help(root);

    /* I. Hide standard sidebar Help button completely in SMRITI layout */
    if (_is_smriti_user()) {
        root.querySelectorAll('.standard-sidebar-item, .sidebar-item, .sidebar-link, .nav-link, a').forEach(function (el) {
            var txt = (el.textContent || '').trim();
            if (txt === 'Help' && el.closest('.desk-sidebar, .sidebar-wrapper, .layout-side-section')) {
                el.style.display = 'none';
                var li = el.closest('li, .sidebar-item-container');
                if (li) li.style.display = 'none';
            }
        });
    }
}

function _sanitize_navbar_help(root) {
    if (!window.frappe) return;
    
    // Find the Help dropdown item in the header
    var help_menu = root.querySelector('#navbar-help, .dropdown-help');
    if (help_menu) {
        if (!_is_smriti_user()) {
            help_menu.style.display = '';
            return;
        }
        
        // Clean out default ERPNext/Frappe help links and substitute erpnbook.com support
        var dropdown_menu = help_menu.querySelector('.dropdown-menu');
        if (dropdown_menu && !dropdown_menu.getAttribute('data-smriti-sanitized')) {
            dropdown_menu.setAttribute('data-smriti-sanitized', 'true');
            dropdown_menu.innerHTML = `
                <li><a class="dropdown-item" href="https://erpnbook.com" target="_blank">🌐 erpnbook.com Support</a></li>
                <li><a class="dropdown-item" href="https://erpnbook.com" target="_blank">📖 SMRITI User Guide</a></li>
                <li class="divider"></li>
                <li><a class="dropdown-item" href="#" onclick="window.frappe.ui.misc.about(); return false;">ℹ️ About SMRITI Retail OS</a></li>
            `;
            
            // Customize the main Help dropdown button text
            var main_link = help_menu.querySelector('.nav-link');
            if (main_link) {
                main_link.innerHTML = 'Help & Support';
            }
        }
    }
}

/* ── 5. MutationObserver — re-scrub on every DOM addition ───────────────── */
(function () {
    var obs = new MutationObserver(function (mutations) {
        var added = mutations.some(function (m) { return m.addedNodes.length > 0; });
        if (added) _scrub_dom();
        _scan_modals();
    });
    obs.observe(document.documentElement, { childList: true, subtree: true });
})();

/* ── 6. About dialog HTML & version loader ───────────────────────────────── */
var _about_patched = new WeakSet();

function _smriti_about_html() {
    return '<div style="font-family:Inter,sans-serif;padding:4px 0">' +
        '<div style="text-align:center;padding:12px 0 8px">' +
        '<img src="' + SMRITI_LOGO + '" style="height:64px;width:auto" alt="SMRITI"></div>' +
        '<p style="text-align:center;font-size:1.15rem;font-weight:800;color:var(--smriti-primary,#4f46e5);margin:0 0 2px">' + SMRITI_BRAND + '</p>' +
        '<p style="text-align:center;color:#888;font-size:.82rem;margin:0 0 14px">Smarter Retail. Built for India.</p>' +
        '<hr>' +
        '<p>🌐 <a href="https://erpnbook.com" target="_blank" style="color:var(--smriti-primary,#4f46e5)">erpnbook.com</a></p>' +
        '<p>✉ <a href="mailto:support@erpnbook.com" style="color:var(--smriti-primary,#4f46e5)">support@erpnbook.com</a></p>' +
        '<hr>' +
        '<h5 style="margin:8px 0 4px">Installed Apps</h5><div id="smriti-versions">Loading…</div><hr>' +
        '<p style="font-size:.78rem;color:#aaa;margin:6px 0 0">' +
        '&copy; ' + SMRITI_YEAR + ' ' + SMRITI_BRAND + ' &mdash; All rights reserved.</p></div>';
}

function _load_about_versions(body_el) {
    if (!window.frappe || !frappe.call) return;
    frappe.call({
        method: 'smriti_retail_os.branding_api.get_versions',
        callback: function (r) {
            var wrap = body_el && body_el.querySelector('#smriti-versions');
            if (!wrap || !r.message) return;
            wrap.innerHTML = '';
            Object.keys(r.message).forEach(function (k) {
                var app = r.message[k];
                var ver = app.branch ? 'v' + (app.branch_version || app.version) + ' (' + app.branch + ')' : 'v' + app.version;
                var p = document.createElement('p');
                p.style.margin = '3px 0';
                p.innerHTML = '<b>' + app.title + ':</b> ' + ver;
                wrap.appendChild(p);
            });
        }
    });
}

/* Our canonical SMRITI about function — stored so defineProperty can reference it */
function _smriti_about_fn() {
    if (window.frappe && frappe.ui && frappe.ui.Dialog) {
        try {
            if (_smriti_about_fn._dlg) { _smriti_about_fn._dlg.$wrapper.remove(); }
        } catch (e) {}
        _smriti_about_fn._dlg = null;
        var d = new frappe.ui.Dialog({ title: 'About ' + SMRITI_BRAND });
        $(d.body).html(_smriti_about_html());
        d.on_page_show = function () { _load_about_versions(d.body); };
        _smriti_about_fn._dlg = d;
        d.show();
        _load_about_versions(d.body);
    }
}

/* Our toolbar handler function */
function _smriti_about_toolbar_fn() {
    _smriti_about_fn();
    return false;
}

/* ── 7. Monkey-patch frappe.ui.misc.about & frappe.ui.toolbar.show_about ──── */
function _monkey_patch_about() {
    if (!window.frappe || !frappe.ui) return false;

    var patched = false;

    /* 1. Patch Help -> About toolbar handler */
    if (frappe.ui.toolbar) {
        if (frappe.ui.toolbar.show_about !== _smriti_about_toolbar_fn) {
            frappe.ui.toolbar.show_about = _smriti_about_toolbar_fn;
            patched = true;
        }
    }

    /* 2. Patch frappe.ui.misc.about */
    if (frappe.ui.misc) {
        if (frappe.ui.misc.about !== _smriti_about_fn) {
            /* Destroy any existing Frappe-branded about_dialog */
            try { frappe.ui.misc.about_dialog && frappe.ui.misc.about_dialog.$wrapper.remove(); } catch (e) {}
            frappe.ui.misc.about_dialog = null;

            try {
                Object.defineProperty(frappe.ui.misc, 'about', {
                    get: function () { return _smriti_about_fn; },
                    set: function () { /* silently ignore overwrite attempts */ },
                    configurable: true,
                    enumerable: true
                });
            } catch (e) {
                frappe.ui.misc.about = _smriti_about_fn;
            }
            patched = true;
        }
    }
    return patched;
}

/* Poll every 200 ms until we succeed in applying the initial hooks */
(function _poll_patch_about() {
    _monkey_patch_about();
    setTimeout(_poll_patch_about, 200);
})();

/* ── 8. Intercept open modals — scan & replace Frappe About if it still shows ── */
function _patch_modal(el) {
    if (!el) return;
    var body = el.querySelector('.modal-body,.frappe-dialog-body');
    var title_el = el.querySelector('.modal-title,h4.modal-title,.title-text');
    
    var title_text = title_el ? (title_el.textContent || '').trim() : '';
    var body_text = body ? (body.textContent || '') : '';
    var body_html = body ? (body.innerHTML || '') : '';

    /* Detect any Frappe-branded about dialog */
    var is_frappe_about = (
        title_text === 'Frappe Framework' ||
        body_text.includes('frappe.io') ||
        body_text.includes('Frappe Technologies') ||
        body_html.includes('frappe.io') ||
        body_html.includes('frappetech') ||
        body_html.includes('discuss.frappe.io')
    );
    if (!is_frappe_about) return;
    if (_about_patched.has(el)) return;
    _about_patched.add(el);

    /* Cleanly hide the Frappe dialog and open our custom one */
    try {
        if (window.cur_dialog && (cur_dialog.title === 'Frappe Framework' || cur_dialog.title === 'About Frappe Framework')) {
            cur_dialog.hide();
        }
    } catch (e) {}

    try {
        $(el).modal('hide');
    } catch (e) {}

    el.style.display = 'none';
    setTimeout(function () {
        try { el.remove(); } catch (e) {}
        _smriti_about_fn();
    }, 50);
}

function _scan_modals() {
    document.querySelectorAll('.modal,.frappe-dialog,[role="dialog"]').forEach(function (el) {
        _patch_modal(el.closest('.modal,.frappe-dialog,[role="dialog"]') || el);
    });
}

/* ── 8. Workspace sidebar controller patch ──────────────────────────────── */
/*
 * Frappe v14/v15 WorkspaceSidebar renders each item with { app_title }.
 * We hook frappe.workspace_sidebar.render_sidebar_items (if present)
 * and patch the data before it renders.
 */
function _patch_workspace_sidebar_controller() {
    if (!window.frappe || !frappe.workspace_sidebar) return;
    var ws = frappe.workspace_sidebar;

    /* Already patched? */
    if (ws.__smriti_patched) return;
    ws.__smriti_patched = true;

    /* Patch the data arrays */
    function _fix_pages(arr) {
        if (!Array.isArray(arr)) return;
        arr.forEach(function (p) {
            if (p.app_title && _SCRUB_RE.test(p.app_title)) p.app_title = _replace(p.app_title);
            if (p.app && /erpnext/i.test(p.app)) p.app_title = SMRITI_BRAND;
        });
    }
    _fix_pages(ws.all_pages);
    _fix_pages(ws.public_pages);
    _fix_pages(ws.private_pages);

    /* Wrap render method so future calls also patch data first */
    var _orig_render = ws.render_sidebar_items && ws.render_sidebar_items.bind(ws);
    if (_orig_render) {
        ws.render_sidebar_items = function () {
            _fix_pages(ws.all_pages);
            _fix_pages(ws.public_pages);
            _fix_pages(ws.private_pages);
            var result = _orig_render.apply(this, arguments);
            /* Scrub DOM immediately after render */
            setTimeout(_do_scrub, 0);
            return result;
        };
    }
}

function _patch_sidebar_prototype() {
    if (!window.frappe) return;
    try {
        if (frappe.ui && frappe.ui.Sidebar) {
            var orig_choose = frappe.ui.Sidebar.prototype.choose_app_name;
            if (orig_choose && !orig_choose.__smriti_patched) {
                frappe.ui.Sidebar.prototype.choose_app_name = function() {
                    orig_choose.apply(this, arguments);
                    if (this.header_subtitle && _SCRUB_RE.test(this.header_subtitle)) {
                        this.header_subtitle = _replace(this.header_subtitle);
                    }
                };
                frappe.ui.Sidebar.prototype.choose_app_name.__smriti_patched = true;
            }
        }
    } catch(e) {}
}

/* ── 9. Role-based redirect to dedicated desk ───────────────────────────── */
function _redirect_to_smriti_home() {
    if (!window.frappe || !frappe.session) return;
    
    // If not logged in, do nothing
    if (frappe.session.user === "Guest") return;

    var current_route = "";
    try {
        current_route = (typeof frappe.get_route_str === 'function') ? frappe.get_route_str() : "";
    } catch (e) {}

    var base_path = window.location.pathname.startsWith('/desk') ? '/desk' : '/app';
    var is_desk_env = window.location.pathname.startsWith('/app') || window.location.pathname.startsWith('/desk');

    // 1. If we are in the Desk (SPA)
    if (is_desk_env) {
        if (current_route === 'workspace/Home' || current_route === '' || current_route === 'desk') {
            var roles = frappe.user_roles || [];
            if (roles.includes('SMRITI Cashier')) {
                frappe.set_route('smriti-billing');
            } else {
                frappe.set_route('smriti-desk');
            }
        }
    } 
    // 2. If we are on the Website Home Page
    else if (window.location.pathname === '/' || window.location.pathname === '/smriti-home') {
        console.log("[SMRITI] Logged in user on home page, redirecting to app...");
        var roles = frappe.user_roles || [];
        if (roles.includes('SMRITI Cashier')) {
            window.location.href = base_path + '/smriti-billing';
        } else {
            window.location.href = base_path + '/smriti-desk';
        }
    }
}

function _sidebar_lockdown() {
    /* Disabled: Show all menus in sidebar for all users */
    return;
}

function _is_smriti_user() {
    if (!window.frappe || !frappe.session) return false;
    if (frappe.session.user === "Guest") return false;
    
    var roles = frappe.user_roles || [];
    // Retail users always get the SMRITI layout
    if (roles.includes("SMRITI Cashier") || roles.includes("SMRITI Store Manager")) return true;

    // System Manager: since this is a SMRITI-branded install, always show our sidebar
    // so admins can navigate SMRITI pages easily
    if (roles.includes("System Manager")) return true;

    return false;
}

function get_smriti_active_page() {
    if (!window.frappe || typeof frappe.get_route !== 'function') return null;
    var route = frappe.get_route() || [];
    if (route.length === 0) return null;
    
    var page_name = route[0];
    var page_name_lower = (page_name || "").toLowerCase();
    
    // Workspace routes — check both slug and human-readable name
    if (page_name_lower === "smriti-retail-os") return "desk";
    if (page_name_lower === "workspace" || page_name_lower === "workspaces") {
        var ws_name = (route[1] || "").toLowerCase().replace(/\s+/g, "-");
        if (ws_name === "smriti-retail-os" || ws_name.includes("smriti")) return "desk";
    }
    
    if (page_name === "smriti-billing")   return "billing";
    if (page_name === "smriti-inventory") return "inventory";
    if (page_name === "smriti-barcode")   return "barcode";
    if (page_name === "smriti-purchase")  return "purchase";
    if (page_name === "smriti-desk")      return "desk";
    if (page_name === "smriti-shift")     return "shift";
    if (page_name === "smriti-reports")   return "reports";
    if (page_name === "smriti-loyalty")   return "loyalty";
    if (page_name === "smriti-item-master") return "item_import";
    if (page_name === "customer" || route[1] === "Customer") return "customers";
    if (page_name === "item" || route[1] === "Item") return "products";
    if (page_name === "supplier" || route[1] === "Supplier") return "suppliers";
    if (page_name === "sales-invoice" || route[1] === "Sales Invoice") return "sales_invoices";
    if (page_name === "purchase-order" || route[1] === "Purchase Order") return "purchase_orders";
    if (page_name === "purchase-receipt" || route[1] === "Purchase Receipt") return "purchase_receipts";
    return null;
}

function _render_smriti_sidebar_if_applicable() {
    var active_page = get_smriti_active_page();
    if (active_page || _is_smriti_user()) {
        document.body.classList.add("smriti-sidebar-active");
        if (window.SMRITI && typeof SMRITI.renderSidebar === 'function') {
            SMRITI.renderSidebar(active_page);
        }
    } else {
        document.body.classList.remove("smriti-sidebar-active");
        document.body.classList.remove("smriti-sidebar-collapsed");
        document.body.classList.remove("smriti-mobile-sidebar-open");
        document.getElementById("smriti-sidebar")?.remove();
        document.getElementById("smriti-sidebar-backdrop")?.remove();
        document.getElementById("smriti-mobile-hamburger-btn")?.remove();
    }
}

function _setup_smriti_layout_class() {
    if ($('body').hasClass('smriti-user-layout')) {
        console.log("[SMRITI] Removing SMRITI layout class from body");
        $('body').removeClass('smriti-user-layout');
    }
}

function _setup_sidebar_toggle() {
    if (!window.frappe) return;
    if (_is_smriti_user()) {
        // Skip native toggle logic when on SMRITI layout
        $('body').removeClass('smriti-sidebar-right');
        return;
    }
    
    // 1. Read position from localStorage and apply immediately to body
    var savedPosition = localStorage.getItem('smriti-sidebar-position') || 'left';
    var hasRightClass = $('body').hasClass('smriti-sidebar-right');
    if (savedPosition === 'right' && !hasRightClass) {
        $('body').addClass('smriti-sidebar-right');
    } else if (savedPosition === 'left' && hasRightClass) {
        $('body').removeClass('smriti-sidebar-right');
    }

    // 2. Inject toggle button into the sidebar header if it's not already there
    var sidebarHeader = $('.body-sidebar-container .sidebar-header');
    if (sidebarHeader.length && !sidebarHeader.find('.smriti-sidebar-toggle-sidebtn').length) {
        var toggleBtn = $(
            '<button class="smriti-sidebar-toggle-sidebtn" title="Toggle Sidebar Left/Right" type="button">' +
                '<span class="material-symbols-outlined">swap_horiz</span>' +
            '</button>'
        );
        
        toggleBtn.on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            var currentPos = localStorage.getItem('smriti-sidebar-position') || 'left';
            var newPos = (currentPos === 'left') ? 'right' : 'left';
            
            localStorage.setItem('smriti-sidebar-position', newPos);
            
            if (newPos === 'right') {
                $('body').addClass('smriti-sidebar-right');
            } else {
                $('body').removeClass('smriti-sidebar-right');
            }
        });
        
        var titleContainer = sidebarHeader.find('.title-container');
        if (titleContainer.length) {
            titleContainer.after(toggleBtn);
        } else {
            sidebarHeader.append(toggleBtn);
        }
    }
}

function is_doctype_route() {
    if (!window.frappe || typeof frappe.get_route !== 'function') return false;
    var route = frappe.get_route() || [];
    if (route.length === 0) return false;
    var first = route[0];
    if (['List', 'Form', 'query-report', 'view', 'tree', 'kanban', 'dashboard', 'calendar', 'gantt'].includes(first)) {
        return true;
    }
    var standard_doctypes = ['customer', 'item', 'supplier', 'sales-invoice', 'purchase-order', 'purchase-receipt'];
    if (standard_doctypes.includes(first.toLowerCase())) {
        return true;
    }
    return false;
}

function _force_popout_full_width() {
    if (!$('body').hasClass('smriti-popout-active')) return;
    
    // Target main page content containers
    var targets = $('.layout-main-section, .layout-main, .page-container, .sim-page, .smriti-billing-container, .page-content, .layout-main-section-wrapper, [id^="page-"]');
    if (!targets.length) return;
    
    targets.each(function() {
        var el = $(this);
        while (el.length && !el.is('body') && !el.is('html')) {
            var style = el.attr('style') || '';
            
            // Clean up old values to avoid duplicate bloating
            style = style.replace(/margin-left:[^;]+;?/g, '')
                         .replace(/margin-right:[^;]+;?/g, '')
                         .replace(/padding-left:[^;]+;?/g, '')
                         .replace(/padding-right:[^;]+;?/g, '')
                         .replace(/width:[^;]+;?/g, '')
                         .replace(/max-width:[^;]+;?/g, '')
                         .replace(/left:[^;]+;?/g, '')
                         .replace(/transform:[^;]+;?/g, '');
                         
            style += '; margin-left: 0px !important; margin-right: 0px !important; padding-left: 0px !important; padding-right: 0px !important; width: 100% !important; max-width: 100% !important; left: 0px !important; transform: none !important;';
            el.attr('style', style);
            el = el.parent();
        }
    });
}

function _check_global_popout_mode() {
    var urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('popout') === 'false') {
        sessionStorage.removeItem('smriti_popout_mode');
    }
    
    var isPopout = urlParams.get('popout') === 'true' || sessionStorage.getItem('smriti_popout_mode') === 'true';
    if (isPopout) {
        sessionStorage.setItem('smriti_popout_mode', 'true');
        $('body').addClass('smriti-popout-active');
        
        // Add custom vs doctype route helper class
        if (is_doctype_route()) {
            $('body').addClass('smriti-popout-doctype');
            $('body').removeClass('smriti-popout-custom-page');
        } else {
            $('body').addClass('smriti-popout-custom-page');
            $('body').removeClass('smriti-popout-doctype');
        }
        
        _render_popout_floating_controls();
        _force_popout_full_width();
    } else {
        $('body').removeClass('smriti-popout-active');
        $('body').removeClass('smriti-popout-doctype');
        $('body').removeClass('smriti-popout-custom-page');
        document.getElementById('smriti-popout-controls')?.remove();
    }
}

function _render_popout_floating_controls() {
    if (!$('body').hasClass('smriti-popout-active')) return;
    if (document.getElementById('smriti-popout-controls')) return;

    var controls = document.createElement('div');
    controls.id = 'smriti-popout-controls';
    controls.className = 'smriti-popout-controls-floating';
    
    controls.innerHTML = `
        <button class="smriti-popout-btn smriti-popout-fullscreen" title="Toggle Fullscreen">
            <span class="material-symbols-outlined">fullscreen</span>
        </button>
        <button class="smriti-popout-btn smriti-popout-close" title="Exit Popout / Close Window">
            <span class="material-symbols-outlined">close</span>
        </button>
    `;
    document.body.appendChild(controls);

    // Bind events
    $(controls).find('.smriti-popout-fullscreen').off('click').on('click', function() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.error(`Error attempting to enable full-screen mode: ${err.message}`);
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    });

    $(controls).find('.smriti-popout-close').off('click').on('click', function() {
        window.close();
    });
}

/* ── 10. Frappe lifecycle hooks ─────────────────────────────────────────── */
$(document).on('app_ready', function () {
    _patch_sidebar_prototype();
    _patch_frappe_boot();
    _patch_workspace_sidebar_controller();
    _monkey_patch_about();
    _redirect_to_smriti_home();
    _setup_smriti_layout_class();
    _render_smriti_sidebar_if_applicable();
    _do_scrub();
    _sidebar_lockdown();
    _setup_sidebar_toggle();
    _check_global_popout_mode();
});

$(document).on('page-change route-change', function () {
    _patch_sidebar_prototype();
    _patch_frappe_boot();
    _patch_workspace_sidebar_controller();
    _redirect_to_smriti_home();
    _setup_smriti_layout_class();
    _render_smriti_sidebar_if_applicable();
    _scrub_dom();
    _sidebar_lockdown();
    _setup_sidebar_toggle();
    _check_global_popout_mode();
    _force_popout_full_width();
});

/* Periodic safety net */
setInterval(function () {
    _check_global_popout_mode();
    _force_popout_full_width();
    if (!_is_smriti_user()) return;
    _patch_sidebar_prototype();
    _patch_frappe_boot();
    _setup_smriti_layout_class();
    _render_smriti_sidebar_if_applicable();
    _scrub_dom();
    _sidebar_lockdown();
    _monkey_patch_about(); /* re-attempt lock on each cycle */
}, 1500);

/* Periodic safety net for sidebar position & toggle button */
setInterval(function () {
    _setup_sidebar_toggle();
}, 1000);

/* Scan open modals frequently so Frappe About is replaced within 150 ms */
setInterval(_scan_modals, 150);

/* Rapid initial scrub — run at 100 ms, 300 ms, 700 ms, 1500 ms after DOMContentLoaded
   to catch Frappe's progressive hydration phases */
function _boot_scrub_sequence() {
    _do_scrub();
    _redirect_to_smriti_home();
    _setup_smriti_layout_class();
    _render_smriti_sidebar_if_applicable();
    _setup_sidebar_toggle();
    _check_global_popout_mode();
    _force_popout_full_width();
    [100, 300, 700, 1500, 3000].forEach(function (ms) {
        setTimeout(function () {
            _patch_sidebar_prototype();
            _patch_frappe_boot();
            _redirect_to_smriti_home();
            _setup_smriti_layout_class();
            _render_smriti_sidebar_if_applicable();
            _do_scrub();
            _setup_sidebar_toggle();
            _check_global_popout_mode();
            _force_popout_full_width();
        }, ms);
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _boot_scrub_sequence);
} else {
    _boot_scrub_sequence();
}

