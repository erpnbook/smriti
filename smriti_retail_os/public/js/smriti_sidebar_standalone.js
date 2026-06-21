/**
 * @file: smriti_retail_os/public/js/smriti_sidebar_standalone.js
 * @description: Frontend controller for standalone sidebar layout.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-12
 * @version: 1.9.1
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */


window.SMRITI = window.SMRITI || {};

// Define all navigation items grouped by collapsible folders
SMRITI.sidebarSchema = [];


SMRITI.renderFlexibleSidebar = async function(activePageId) {
    const target = document.getElementById("smriti-sidebar-target");
    if (!target) return;

    // Ensure nav config is loaded
    if (typeof SMRITI_NAV === 'undefined') {
        await new Promise((resolve, reject) => {
            const script = document.createElement('script');
            // Cache-bust: version 2.0.0 forces fresh load after route changes
            script.src = '/assets/smriti_retail_os/js/smriti_nav_config.js?v=2.0.4';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    let business_type = "Footwear";
    try {
        if (window.frappe && frappe.boot && frappe.boot.smriti_business_type) {
            business_type = frappe.boot.smriti_business_type;
        } else {
            const res = await fetch("/api/method/smriti_retail_os.company_api.get_business_type");
            const data = await res.json();
            if (data.message) business_type = data.message;
        }
    } catch(e) {}

    // Site Config feature flags check
    const siteConfig = {
        "ai_hub_enabled": true,
        "intelligence_enabled": true,
        "cge_enabled": true
    };

    try {
        if (window.frappe && frappe.boot && frappe.boot.smriti_site_config) {
            Object.assign(siteConfig, frappe.boot.smriti_site_config);
        } else {
            const res = await fetch("/api/method/smriti_retail_os.boot.get_smriti_session_info");
            const data = await res.json();
            if (data.message && data.message.smriti_site_config) {
                Object.assign(siteConfig, data.message.smriti_site_config);
            }
        }
    } catch(e) {
        console.error("[SMRITI] Failed to load site config:", e);
    }

    // Role restrictions for sections
    let user_roles = ["SMRITI Store Manager"];
    const activeUser = window.loggedUser || (window.frappe && frappe.session && frappe.session.user) || "";
    if (activeUser === 'Admin' || activeUser === 'admin@erpnbook.com' || (window.frappe && frappe.user_roles && frappe.user_roles.includes("System Manager"))) {
        user_roles = ["System Manager"];
    } else if (window.frappe && frappe.user_roles) {
        user_roles = frappe.user_roles;
    }
    const isAdminAccount = activeUser === 'Admin' || activeUser === 'admin@erpnbook.com';
    
    function hasRoleAccess(sectionId) {
        const SECTION_ROLE_RESTRICTIONS = {
            "cge": ["System Manager", "SMRITI Store Manager", "SMRITI Auditor"],
            "psv": ["System Manager", "SMRITI Store Manager"],
            "finance": ["System Manager", "SMRITI Store Manager"],
            "administration": ["System Manager", "SMRITI Store Manager"]
        };
        const allowed = SECTION_ROLE_RESTRICTIONS[sectionId];
        if (!allowed) return true;
        return allowed.some(role => user_roles.includes(role));
    }

    // SECTION EMOJIS
    const SECTION_EMOJIS = {
        "masters": "📦",
        "cge": "📈",
        "psv": "🌐",
        "sales": "🛒",
        "purchase": "📥",
        "inventory": "🏬",
        "finance": "💰",
        "reports": "📑",
        "administration": "⚙️",
        "help_desk": "🆘",
        "ai_hub": "🤖"
    };

    function isItemActive(item, activePageId) {
        if (item.id === activePageId) return true;
        const pathname = window.location.pathname;
        if (item.route && item.route === pathname) return true;
        if (item.route && pathname.startsWith(item.route + "/")) return true;
        return false;
    }

    // 1. Resolve active layout preferences from localStorage
    const app = document.getElementById("app");
    if (app) {
        const pos = localStorage.getItem("smriti-sidebar-position") || "left";
        if (pos === "right") {
            app.classList.add("sidebar-position-right");
        } else {
            app.classList.remove("sidebar-position-right");
        }

        const layout = localStorage.getItem("smriti-sidebar-layout") || "vertical";
        if (layout === "top") {
            app.classList.add("sidebar-layout-top");
        } else {
            app.classList.remove("sidebar-layout-top");
        }

        const collapsed = localStorage.getItem("smriti-sidebar-collapsed") === "true";
        if (collapsed) {
            app.classList.add("sidebar-collapsed");
        } else {
            app.classList.remove("sidebar-collapsed");
        }
    }

    // 2. Generate Brand Header
    const brandHtml = `
        <div class="sidebar-brand">
            <div class="sidebar-logo"><span class="material-symbols-outlined">local_shipping</span></div>
            <span class="sidebar-title">SMRITI OS</span>
        </div>
    `;

    // 3. Generate Layout Controls Toolbar
    const controlsHtml = `
        <div class="sidebar-layout-controls">
            <button class="layout-ctrl-btn" onclick="SMRITI.toggleSidebarPosition()" title="Swap Position (Left / Right)">
                <span class="material-symbols-outlined">swap_horiz</span>
            </button>
            <button class="layout-ctrl-btn" onclick="SMRITI.toggleSidebarLayout()" title="Transform Layout (Sidebar / Top Bar)">
                <span class="material-symbols-outlined">splitscreen</span>
            </button>
            <button class="layout-ctrl-btn" onclick="SMRITI.toggleSidebarCollapse()" title="Collapse / Expand Sidebar">
                <span class="material-symbols-outlined">menu_open</span>
            </button>
        </div>
    `;

    // 4. Generate Scrollable Menu Items
    let menuHtml = '<div class="sidebar-menu">';

    const navConfig = typeof SMRITI_NAV !== 'undefined' ? SMRITI_NAV : { sections: [] };

    navConfig.sections.forEach(section => {
        // 1. Hidden sections never render
        if (section.status === "hidden") return;

        // 2. Feature flag check
        const flagKey = section.id + "_enabled";
        if (siteConfig.hasOwnProperty(flagKey) && !siteConfig[flagKey]) return;

        // 3. Role Access check
        if (!hasRoleAccess(section.id)) return;

        // 4. Filter non-hidden items
        const visibleItems = (section.items || []).filter(item => item.status !== "hidden");

        // 5. Auto-hide section if no visible items
        if (visibleItems.length === 0) return;

        const isCatOpen = localStorage.getItem(`smriti-sidebar-cat-${section.id}`) !== 'closed';
        const openCls = isCatOpen ? 'open' : '';

        let isSubActive = false;
        let subItemsHtml = '';

        visibleItems.forEach(item => {
            if (isAdminAccount && (item.id === 'security' || item.id === 'security_workflows')) return;

            if (item.type === "header") {
                subItemsHtml += `
                    <div class="sidebar-sub-header" style="opacity: 0.7; margin-top: 8px; padding-left: 8px; font-weight: 800; font-size: 11px; color: var(--smriti-color-text-muted);">
                        ${item.label}
                    </div>
                `;
                return;
            }

            const isItemActiveFlag = isItemActive(item, activePageId);
            if (isItemActiveFlag) isSubActive = true;

            const subActiveCls = isItemActiveFlag ? 'active' : '';

            let item_url = "";
            let item_onclick = "";
            let item_style = "";
            let badge_html = "";

            if (item.status === "active") {
                item_url = item.standalone_route || item.route;
                item_style = "opacity: 1; cursor: pointer;";
            } else if (item.status === "coming_soon") {
                const comingSoonUrl = "/coming-soon?feature=" +
                    encodeURIComponent(item.label) +
                    "&progress=" + (item.progress || 0) +
                    "&eta=" + encodeURIComponent(item.eta || "Coming Soon");
                item_url = comingSoonUrl;
                item_style = "opacity: 0.6; cursor: pointer;";
                badge_html = `<span class="smriti-soon-badge" style="margin-left:auto; background:#EFF6FF; color:#2563EB; font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px;">Soon</span>`;
            } else if (item.status === "disabled") {
                item_url = "#";
                item_style = "opacity: 0.4; cursor: not-allowed;";
                item_onclick = "event.preventDefault();";
            }

            subItemsHtml += `
                <a class="sidebar-sub-item ${subActiveCls}" data-nav-id="${item.id}" data-status="${item.status}" style="${item_style}" href="${item_url}" ${item_onclick ? `onclick="${item_onclick}"` : ''}>
                    <span>${item.label}</span>
                    ${badge_html}
                    ${item.status === 'active' ? `
                    <button class="sidebar-popout-btn" onclick="event.preventDefault(); event.stopPropagation(); openPopout('${item_url}');" title="Open in new window">↗</button>
                    ` : ''}
                </a>
            `;
        });

        const headerActiveCls = isSubActive ? 'active-header' : '';
        const emoji = SECTION_EMOJIS[section.id] || "📁";

        menuHtml += `
            <div class="sidebar-category ${openCls}" id="cat-block-${section.id}" data-nav-id="${section.id}">
                <div class="category-header ${headerActiveCls}" onclick="SMRITI.toggleCategory('${section.id}')">
                    <span class="emoji">${emoji}</span>
                    <span>${section.label}</span>
                    <span class="material-symbols-outlined arrow">chevron_right</span>
                </div>
                <div class="category-body">
                    ${subItemsHtml}
                </div>
            </div>
        `;
    });
    
    menuHtml += '</div>';

    // 5. Generate User Footer Info
    const cashierLabel = activeUser ? activeUser.split('@')[0] : 'Manager';
    const firstLetter = cashierLabel.charAt(0).toUpperCase();
    
    let roleLabel = "Cashier";
    if (user_roles.includes("System Manager")) {
        roleLabel = "System Manager";
    } else if (user_roles.includes("SMRITI Store Manager")) {
        roleLabel = "Store Manager";
    }

    const footerHtml = `
        <div class="sidebar-footer">
            <div class="sidebar-user">
                <div class="sidebar-avatar">${firstLetter}</div>
                <div class="sidebar-info">
                    <span class="sidebar-name">${cashierLabel}</span>
                    <span class="sidebar-role">${roleLabel}</span>
                </div>
            </div>
            <button class="sidebar-logout" onclick="doLogout()">
                <span class="material-symbols-outlined" style="font-size:16px;">logout</span>
                <span>Sign Out</span>
            </button>
        </div>
    `;

    target.innerHTML = brandHtml + controlsHtml + menuHtml + footerHtml;
};


// ── Accordion Folders Expand/Collapse ────────────────────────────────
SMRITI.toggleCategory = function(catId) {
    const block = document.getElementById(`cat-block-${catId}`);
    if (!block) return;
    
    block.classList.toggle("open");
    const isOpen = block.classList.contains("open");
    localStorage.setItem(`smriti-sidebar-cat-${catId}`, isOpen ? "open" : "closed");
};

// ── Swap Position Shifting ──────────────────────────────────────────
SMRITI.toggleSidebarPosition = function() {
    const app = document.getElementById("app");
    const isRight = app.classList.toggle("sidebar-position-right");
    localStorage.setItem("smriti-sidebar-position", isRight ? "right" : "left");
    toast(isRight ? 'Sidebar docked to Right' : 'Sidebar docked to Left', 'info');
};

// ── Transform Navigation Layout ──────────────────────────────────────
SMRITI.toggleSidebarLayout = function() {
    const app = document.getElementById("app");
    const isTop = app.classList.toggle("sidebar-layout-top");
    localStorage.setItem("smriti-sidebar-layout", isTop ? "top" : "vertical");
    toast(isTop ? 'Transformed to Top Navigation Header' : 'Transformed to Vertical Sidebar', 'info');
};

// ── Expand/Collapse Sidebar Width ────────────────────────────────────
SMRITI.toggleSidebarCollapse = function() {
    const app = document.getElementById("app");
    const isCollapsed = app.classList.toggle("sidebar-collapsed");
    localStorage.setItem("smriti-sidebar-collapsed", isCollapsed ? "true" : "false");
};

// ── Popout click handler helper ─────────────────────────────────────
function openPopout(url) {
    const w = 1400, h = 900;
    const left = Math.round((screen.width - w) / 2);
    const top  = Math.round((screen.height - h) / 2);
    window.open(
        url + (url.includes('?') ? '&' : '?') + 'popout=true',
        '_blank',
        `width=${w},height=${h},left=${left},top=${top},toolbar=no,menubar=no,location=no,status=no,scrollbars=yes,resizable=yes`
    );
}

function _initPopoutMode() {
    if (!new URLSearchParams(window.location.search).get('popout')) return;
    document.body.classList.add('popout-mode');
    const toolbar = document.createElement('div');
    toolbar.className = 'popout-toolbar';
    toolbar.innerHTML = `
        <span style="font-size:0.75rem;opacity:0.5;padding:0 4px;">SMRITI</span>
        <button onclick="_popoutFitWidth()" title="Fit to width">⛶ Fit Width</button>
        <button onclick="_popoutFullscreen()" id="popout-fs-btn">⤢ Fullscreen</button>
        <button onclick="window.close()" style="color:var(--danger)">✕ Close</button>
    `;
    document.body.appendChild(toolbar);
}

function _popoutFitWidth() {
    const main = document.querySelector('.main-content, main, .content, .page-content');
    if (main) { main.style.maxWidth = '100%'; main.style.padding = '8px'; }
    document.querySelectorAll('table').forEach(t => t.style.width = '100%');
}

function _popoutFullscreen() {
    const btn = document.getElementById('popout-fs-btn');
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
        btn.textContent = '⤡ Exit Fullscreen';
    } else {
        document.exitFullscreen();
        btn.textContent = '⤢ Fullscreen';
    }
}

document.addEventListener('DOMContentLoaded', _initPopoutMode);

SMRITI.triggerPopout = function(e, url) {
    e.preventDefault();
    e.stopPropagation();
    openPopout(url);
};


SMRITI.injectLabelStudioShortcut = function() {
    const topbarRight = document.querySelector(".topbar-right");
    if (!topbarRight) return;
    
    if (document.getElementById("label-studio-shortcut")) return;
    
    const btn = document.createElement("button");
    btn.id = "label-studio-shortcut";
    btn.className = "topbtn";
    btn.title = "Label Studio";
    btn.innerHTML = `<span class="material-symbols-outlined">qr_code_scanner</span><span>Label Studio</span>`;
    
    btn.addEventListener("click", function() {
        window.location.href = "/barcode-center";
    });
    
    topbarRight.insertBefore(btn, topbarRight.firstChild);
};
