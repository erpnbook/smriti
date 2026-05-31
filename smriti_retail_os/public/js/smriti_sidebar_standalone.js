/**
 * @file: smriti_retail_os/public/js/smriti_sidebar_standalone.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
/**
 * @file: smriti_retail_os/public/js/smriti_sidebar_standalone.js
 * @description: Dynamic Flexible Layout Sidebar Engine for SMRITI Standalone Pages
 * @author: Antigravity <antigravity@google.com>
 * @version: 1.0.0
 * @license: MIT
 */

window.SMRITI = window.SMRITI || {};

// Define all navigation items grouped by collapsible folders
SMRITI.sidebarSchema = [
    {
        type: 'link',
        id: 'desk',
        emoji: '🏠',
        label: 'Dashboard',
        url: '/desk'
    },
    {
        type: 'category',
        id: 'masters',
        emoji: '📦',
        label: 'Masters',
        items: [
            { id: 'item_master', label: '├─ Item Master', url: '/item_master' },
            { id: 'sizewise_item', label: '├─ Sizewise Creator', url: '/sizewise_item' },
            { id: 'customers', label: '├─ Customers', url: '/customers' },
            { id: 'suppliers', label: '└─ Suppliers', url: '/suppliers' }
        ]
    },
    {
        type: 'category',
        id: 'sales',
        emoji: '🛒',
        label: 'Sales',
        items: [
            { id: 'billing', label: '├─ POS Billing', url: '/billing' },
            { id: 'sales_invoices', label: '├─ Billing Invoices', url: '/sales_invoices' },
            { id: 'sizewise_invoice', label: '├─ Sizewise Tax Invoice', url: '/sizewise_invoice' },
            { id: 'sales_return', label: '├─ Sales Return', url: '#' },
            { id: 'delivery_challan', label: '└─ Delivery Challan', url: '#' }
        ]
    },
    {
        type: 'category',
        id: 'purchase',
        emoji: '📥',
        label: 'Purchase',
        items: [
            { id: 'purchase_ops', label: '├─ Purchase Manager', url: '/purchase' },
            { id: 'grn', label: '├─ GRN / Receipts', url: '#' },
            { id: 'purchase_invoice', label: '└─ Purchase Invoice', url: '#' }
        ]
    },
    {
        type: 'category',
        id: 'inventory',
        emoji: '🏬',
        label: 'Inventory',
        items: [
            { id: 'inventory_ops', label: '├─ Stock Operations', url: '/inventory' },
            { id: 'barcode', label: '├─ Barcode Center', url: '/barcode' },
            { id: 'stock_adjust', label: '└─ Stock Adjustments', url: '#' }
        ]
    },
    {
        type: 'category',
        id: 'finance',
        emoji: '💰',
        label: 'Finance',
        items: [
            { id: 'receipts', label: '├─ Receipts', url: '#' },
            { id: 'payments', label: '├─ Payments', url: '#' },
            { id: 'credit_notes', label: '└─ Credit Notes', url: '#' }
        ]
    },
    {
        type: 'link',
        id: 'eway_bill',
        emoji: '🚚',
        label: 'E-way Bills',
        url: '/eway_bill'
    },
    {
        type: 'link',
        id: 'reports',
        emoji: '📊',
        label: 'Reports',
        url: '#'
    },
    {
        type: 'category',
        id: 'ai_hub',
        emoji: '🤖',
        label: 'AI Hub',
        items: [
            { id: 'ai_forecast', label: '├─ Demand Forecasts', url: '#' },
            { id: 'ai_audits', label: '└─ Cashier Performance', url: '#' }
        ]
    },
    {
        type: 'category',
        id: 'admin',
        emoji: '⚙️',
        label: 'Administration',
        items: [
            { id: 'shift', label: '├─ Shifts / Register', url: '/shift' },
            { id: 'configure', label: '├─ Config Portal', url: '/configure' },
            { id: 'backup', label: '└─ Backup & Restore', url: '#' }
        ]
    },
    {
        type: 'link',
        id: 'help',
        emoji: '❓',
        label: 'Help Desk',
        url: '#'
    }
];

SMRITI.renderFlexibleSidebar = function(activePageId) {
    const target = document.getElementById("smriti-sidebar-target");
    if (!target) return;

    // 1. Resolve active layout preferences from localStorage
    const app = document.getElementById("app");
    
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
    
    SMRITI.sidebarSchema.forEach(block => {
        if (block.type === 'link') {
            const activeCls = block.id === activePageId ? 'active' : '';
            menuHtml += `
                <a class="sidebar-item ${activeCls}" href="${block.url}">
                    <span class="emoji">${block.emoji}</span>
                    <span>${block.label}</span>
                    <button class="popout-btn" title="Open in Popout Window" onclick="SMRITI.triggerPopout(event, '${block.url}')">
                        <span class="material-symbols-outlined" style="font-size:16px;">open_in_new</span>
                    </button>
                </a>
            `;
        } else if (block.type === 'category') {
            const isCatOpen = localStorage.getItem(`smriti-sidebar-cat-${block.id}`) !== 'closed';
            const openCls = isCatOpen ? 'open' : '';
            
            // Check if any sub-item is active to highlight parent category
            let isSubActive = false;
            let subItemsHtml = '';
            
            block.items.forEach(sub => {
                const subActiveCls = sub.id === activePageId ? 'active' : '';
                if (sub.id === activePageId) isSubActive = true;
                subItemsHtml += `
                    <a class="sidebar-sub-item ${subActiveCls}" href="${sub.url}">
                        ${sub.label}
                    </a>
                `;
            });

            const headerActiveCls = isSubActive ? 'active-header' : '';
            
            menuHtml += `
                <div class="sidebar-category ${openCls}" id="cat-block-${block.id}">
                    <div class="category-header ${headerActiveCls}" onclick="SMRITI.toggleCategory('${block.id}')">
                        <span class="emoji">${block.emoji}</span>
                        <span>${block.label}</span>
                        <span class="material-symbols-outlined arrow">chevron_right</span>
                    </div>
                    <div class="category-body">
                        ${subItemsHtml}
                    </div>
                </div>
            `;
        }
    });
    
    menuHtml += '</div>';

    // 5. Generate User Footer Info
    const cashierLabel = loggedUser ? loggedUser.split('@')[0] : 'Manager';
    const firstLetter = cashierLabel.charAt(0).toUpperCase();

    const footerHtml = `
        <div class="sidebar-footer">
            <div class="sidebar-user">
                <div class="sidebar-avatar">${firstLetter}</div>
                <div class="sidebar-info">
                    <span class="sidebar-name">${cashierLabel}</span>
                    <span class="sidebar-role">Store Manager</span>
                </div>
            </div>
            <button class="sidebar-logout" onclick="doLogout()">
                <span class="material-symbols-outlined" style="font-size:16px;">logout</span>
                <span>Sign Out</span>
            </button>
        </div>
    `;

    // Inject everything
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
SMRITI.triggerPopout = function(e, url) {
    e.preventDefault();
    e.stopPropagation();
    
    let popout_url = url;
    if (popout_url.indexOf('?') === -1) {
        popout_url += '?popout=true';
    } else if (popout_url.indexOf('popout=true') === -1) {
        popout_url += '&popout=true';
    }
    
    window.open(popout_url, "smriti-popout-window", "width=1200,height=800,resizable=yes,scrollbars=yes");
};
