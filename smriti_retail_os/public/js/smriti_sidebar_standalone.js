/**
 * @file: smriti_retail_os/public/js/smriti_sidebar_standalone.js
 * @description: Frontend controller for standalone sidebar layout..
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
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
            { id: 'products', label: '├─ Products Catalog', url: '/products' },
            { id: 'item_master', label: '├─ Item Master', url: '/item_master' },
            { id: 'sizewise_item', label: '├─ Sizewise Creator', url: '/sizewise_item' },
            { id: 'customers', label: '├─ Customers', url: '/customers' },
            { id: 'suppliers', label: '├─ Suppliers', url: '/suppliers' }
        ]
    },
    {
        type: 'category',
        id: 'channel_stock',
        emoji: '🌐',
        label: 'Channel Stock',
        items: [
            { id: 'psa', label: '├─ Distributor Accounts', url: '/psa' },
            { id: 'psv_opening_balance', label: '├─ Opening Balances', url: '/psv-opening-balance' },
            { id: 'sales_upload', label: '├─ Sales Uploads', url: '/sales-upload' },
            { id: 'psv_audit', label: '├─ Stock Audits', url: '/stock-audit' },
            { id: 'psv_reorder', label: '└─ Reorder Report', url: '/reports?report=psv_reorder_report' }
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
            { id: 'sales_return', label: '├─ Sales Return', url: '/sales_return' },
            { id: 'delivery_challan', label: '└─ Delivery Challan', url: '/delivery_challan' }
        ]
    },
    {
        type: 'category',
        id: 'purchase',
        emoji: '📥',
        label: 'Purchase',
        items: [
            { id: 'purchase_ops', label: '├─ Purchase Manager', url: '/purchase' },
            { id: 'grn', label: '├─ GRN / Receipts', url: '/purchase_receipt' },
            { id: 'purchase_invoice', label: '└─ Purchase Invoice', url: '/purchase_invoice' }
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
            { id: 'print_templates', label: '├─ Print Templates', url: '/print_templates' },
            { id: 'stock_adjust', label: '└─ Stock Adjustments', url: '/inventory?tab=adjust' }
        ]
    },
    {
        type: 'category',
        id: 'finance',
        emoji: '💰',
        label: 'Finance',
        items: [
            { id: 'receipts', label: '├─ Receipts', url: '/payments?payment_type=Receive' },
            { id: 'payments', label: '├─ Payments', url: '/payments?payment_type=Pay' },
            { id: 'credit_notes', label: '└─ Credit Notes', url: '/sales_return?sidebar_id=credit_notes' }
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
        url: '/reports'
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
            { id: 'security', label: '├─ Security & Workflows', url: '/security' },
            { id: 'backup', label: '└─ Backup & Restore', url: '/backup' }
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

SMRITI.renderFlexibleSidebar = async function(activePageId) {
    const target = document.getElementById("smriti-sidebar-target");
    if (!target) return;

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

    const filteredSchema = JSON.parse(JSON.stringify(SMRITI.sidebarSchema));
    filteredSchema.forEach(cat => {
        if (cat.items) {
            cat.items = cat.items.filter(item => {
                if (business_type !== "Footwear") {
                    // FMCG / Others (hide footwear size attributes)
                    if (['sizewise_item', 'sizewise_invoice'].includes(item.id)) return false;
                }
                return true;
            });
        }
    });

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
    
    const isAdminAccount = loggedUser === 'Admin' || loggedUser === 'admin@erpnbook.com';
    
    filteredSchema.forEach(block => {
        if (block.type === 'link') {
            if (isAdminAccount && block.id === 'security') return;
            const activeCls = block.id === activePageId ? 'active' : '';
            menuHtml += `
                <a class="sidebar-item ${activeCls}" href="${block.url}">
                    <span class="emoji">${block.emoji}</span>
                    <span>${block.label}</span>
                    <button class="sidebar-popout-btn"
                        onclick="event.preventDefault();event.stopPropagation();openPopout('${block.url}')"
                        title="Open in new window">↗</button>
                </a>
            `;
        } else if (block.type === 'category') {
            const isCatOpen = localStorage.getItem(`smriti-sidebar-cat-${block.id}`) !== 'closed';
            const openCls = isCatOpen ? 'open' : '';
            
            // Check if any sub-item is active to highlight parent category
            let isSubActive = false;
            let subItemsHtml = '';
            
            block.items.forEach(sub => {
                if (isAdminAccount && sub.id === 'security') return;
                const subActiveCls = sub.id === activePageId ? 'active' : '';
                if (sub.id === activePageId) isSubActive = true;
                subItemsHtml += `
                    <a class="sidebar-sub-item ${subActiveCls}" href="${sub.url}">
                        <span>${sub.label}</span>
                        <button class="sidebar-popout-btn"
                            onclick="event.preventDefault();event.stopPropagation();openPopout('${sub.url}')"
                            title="Open in new window">↗</button>
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
