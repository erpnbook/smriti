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
        url: '/smriti'
    },
    {
        type: 'category',
        id: 'masters',
        emoji: '📦',
        label: 'Masters',
        items: [
            { type: 'subheader', label: 'Product Masters' },
            { id: 'products', label: '├─ Product Catalog', url: '/products' },
            { id: 'item_master', label: '├─ Item Master', url: '/item_master' },
            { id: 'sizewise_item', label: '├─ Sizewise Creator', url: '/sizewise_item' },
            { id: 'brand_master', label: '├─ Brand Master', url: '/smriti-coming-soon?feature=Brand+Master&progress=60&eta=Q3+2026' },
            { id: 'item_group', label: '├─ Item Group', url: '/smriti-coming-soon?feature=Item+Group&progress=45&eta=Q3+2026' },
            { id: 'category_hierarchy', label: '├─ Category Hierarchy', url: '/smriti-coming-soon?feature=Category+Hierarchy&progress=50&eta=Q3+2026' },
            { id: 'season_collection', label: '├─ Season / Collection', url: '/smriti-coming-soon?feature=Season+/+Collection&progress=40&eta=Q3+2026' },
            { id: 'uom_master', label: '└─ UOM Master', url: '/smriti-coming-soon?feature=UOM+Master&progress=70&eta=Q3+2026' },
            
            { type: 'subheader', label: 'Party Masters' },
            { id: 'customers', label: '├─ Customers', url: '/customers' },
            { id: 'customer_group', label: '├─ Customer Group', url: '/smriti-coming-soon?feature=Customer+Group&progress=30&eta=Q4+2026' },
            { id: 'territory_zone', label: '├─ Territory / Zone', url: '/smriti-coming-soon?feature=Territory+/+Zone&progress=20&eta=Q4+2026' },
            { id: 'suppliers', label: '├─ Suppliers', url: '/suppliers' },
            { id: 'supplier_group', label: '├─ Supplier Group', url: '/smriti-coming-soon?feature=Supplier+Group&progress=30&eta=Q4+2026' },
            { id: 'salespersons', label: '└─ Salespersons', url: '/smriti-coming-soon?feature=Salespersons&progress=15&eta=Q4+2026' },
            
            { type: 'subheader', label: 'Compliance Masters' },
            { id: 'hsn_master', label: '├─ HSN Master', url: '/smriti-coming-soon?feature=HSN+Master&progress=75&eta=Q3+2026' },
            { id: 'tax_templates', label: '├─ Tax Templates', url: '/smriti-coming-soon?feature=Tax+Templates&progress=65&eta=Q3+2026' },
            { id: 'gst_configuration', label: '└─ GST Configuration', url: '/smriti-coming-soon?feature=GST+Configuration&progress=80&eta=Q3+2026' },
            
            { type: 'subheader', label: 'System Masters' },
            { id: 'warehouses', label: '├─ Warehouses', url: '/smriti-coming-soon?feature=Warehouses&progress=70&eta=Q3+2026' },
            { id: 'payment_terms', label: '├─ Payment Terms', url: '/smriti-coming-soon?feature=Payment+Terms&progress=50&eta=Q4+2026' },
            { id: 'shipping_courier', label: '├─ Shipping / Courier', url: '/smriti-coming-soon?feature=Shipping+/+Courier&progress=40&eta=Q4+2026' },
            { id: 'reason_codes', label: '└─ Reason Codes', url: '/smriti-coming-soon?feature=Reason+Codes&progress=85&eta=Q3+2026' }
        ]
    },
    {
        type: 'category',
        id: 'pricing',
        emoji: '💰',
        label: 'Pricing',
        items: [
            { id: 'price_lists', label: '├─ Price Lists', url: '/smriti-coming-soon?feature=Price+Lists&progress=80&eta=Q3+2026' },
            { id: 'customer_pricing', label: '├─ Customer Pricing', url: '/smriti-coming-soon?feature=Customer+Pricing&progress=65&eta=Q3+2026' },
            { id: 'scheme_discount', label: '├─ Scheme / Discount', url: '/smriti-coming-soon?feature=Scheme+/+Discount&progress=50&eta=Q4+2026' },
            { id: 'promotions', label: '├─ Promotions', url: '/smriti-coming-soon?feature=Promotions&progress=45&eta=Q4+2026' },
            { id: 'price_revision', label: '├─ Price Revision', url: '/smriti-coming-soon?feature=Price+Revision&progress=30&eta=Q4+2026' },
            { id: 'price_audit', label: '└─ Price Audit History', url: '/smriti-coming-soon?feature=Price+Audit+History&progress=25&eta=Q4+2026' }
        ]
    },
    {
        type: 'category',
        id: 'channel_stock',
        emoji: '🌐',
        label: 'Party Stock Visibility',
        items: [
            { id: 'psv_dashboard', label: '├─ PSV Dashboard', url: '/psv-dashboard' },
            { id: 'psa', label: '├─ Distributor Accounts', url: '/psa' },
            { id: 'psv_opening_balance', label: '├─ Opening Balances', url: '/psv-opening-balance' },
            { id: 'sales_upload', label: '├─ Sales Uploads', url: '/sales-upload' },
            { id: 'psv_audit', label: '├─ Stock Audits', url: '/stock-audit' },
            { id: 'replenishment_insights', label: '└─ Replenishment Insights', url: '/smriti-coming-soon?feature=Replenishment+Insights&progress=35&eta=Q4+2026' }
        ]
    },
    {
        type: 'category',
        id: 'sales',
        emoji: '🛒',
        label: 'Sales',
        items: [
            { id: 'day_open', label: '├─ Day Open', url: '/shift' },
            { id: 'sales_order', label: '├─ Sales Order', url: '/smriti-coming-soon?feature=Sales+Order&progress=80&eta=Q3+2026' },
            { id: 'proforma_invoice', label: '├─ Proforma Invoice', url: '/smriti-coming-soon?feature=Proforma+Invoice&progress=70&eta=Q3+2026' },
            { id: 'billing', label: '├─ POS Billing', url: '/billing' },
            { id: 'sales_invoices', label: '├─ Tax Invoice', url: '/sales_invoices' },
            { id: 'sales_return', label: '├─ Sales Return', url: '/sales_return' },
            { id: 'delivery_challan', label: '├─ Delivery Challan', url: '/delivery_challan' },
            { id: 'customer_outward', label: '├─ Customer Outward', url: '/smriti-coming-soon?feature=Customer+Outward&progress=45&eta=Q4+2026' },
            { id: 'day_close', label: '└─ Day Close', url: '/shift' }
        ]
    },
    {
        type: 'category',
        id: 'purchase',
        emoji: '📥',
        label: 'Purchase',
        items: [
            { id: 'purchase_order', label: '├─ Purchase Order', url: '/smriti-coming-soon?feature=Purchase+Order&progress=85&eta=Q3+2026' },
            { id: 'grn', label: '├─ GRN / Receipts', url: '/purchase_receipt' },
            { id: 'purchase_invoice', label: '├─ Purchase Invoice', url: '/purchase_invoice' },
            { id: 'landed_cost', label: '├─ Landed Cost Voucher', url: '/smriti-coming-soon?feature=Landed+Cost+Voucher&progress=30&eta=Q4+2026' },
            { id: 'supplier_return', label: '├─ Supplier Return', url: '/smriti-coming-soon?feature=Supplier+Return&progress=50&eta=Q3+2026' },
            { id: 'cost_adjustments', label: '└─ Cost Adjustments', url: '/smriti-coming-soon?feature=Cost+Adjustments&progress=40&eta=Q4+2026' }
        ]
    },
    {
        type: 'category',
        id: 'inventory',
        emoji: '🏬',
        label: 'Inventory',
        items: [
            { id: 'inventory_ops', label: '├─ Stock Ledger', url: '/inventory' },
            { id: 'stock_transfer', label: '├─ Stock Transfer', url: '/inventory?tab=transfer' },
            { id: 'stock_adjust', label: '├─ Stock Adjustment', url: '/inventory?tab=adjust' },
            { id: 'stock_audit_wh', label: '├─ Stock Audit', url: '/smriti-coming-soon?feature=Stock+Audit&progress=60&eta=Q3+2026' },
            { id: 'barcode', label: '├─ Barcode Center', url: '/barcode' },
            { id: 'print_templates', label: '├─ Print Templates', url: '/print_templates' },
            { id: 'batch_management', label: '├─ Batch Management', url: '/smriti-coming-soon?feature=Batch+Management&progress=50&eta=Q4+2026' },
            { id: 'reorder_planning', label: '└─ Reorder Planning', url: '/smriti-coming-soon?feature=Reorder+Planning&progress=45&eta=Q4+2026' }
        ]
    },
    {
        type: 'category',
        id: 'intelligence',
        emoji: '📊',
        label: 'Intelligence',
        items: [
            { id: 'exec_dashboard', label: '├─ Executive Dashboard', url: '/smriti-coming-soon?feature=Executive+Dashboard&progress=30&eta=Q4+2026', feature_flag: 'exec_dashboard_enabled' },
            { id: 'gmroi', label: '├─ GMROI', url: '/smriti-coming-soon?feature=GMROI&progress=40&eta=Q4+2026', feature_flag: 'gmroi_enabled' },
            { id: 'sell_through', label: '├─ Sell Through', url: '/smriti-coming-soon?feature=Sell+Through&progress=35&eta=Q4+2026', feature_flag: 'sell_through_enabled' },
            { id: 'coverage_days', label: '├─ Coverage Days', url: '/smriti-coming-soon?feature=Coverage+Days&progress=20&eta=Q4+2026', feature_flag: 'coverage_days_enabled' },
            { id: 'inventory_aging', label: '├─ Inventory Aging', url: '/smriti-coming-soon?feature=Inventory+Aging&progress=25&eta=Q4+2026', feature_flag: 'inventory_aging_enabled' },
            { id: 'capital_locked', label: '├─ Capital Locked', url: '/smriti-coming-soon?feature=Capital+Locked&progress=15&eta=Q4+2026', feature_flag: 'capital_locked_enabled' },
            { id: 'dead_stock', label: '└─ Dead Stock Recovery', url: '/smriti-coming-soon?feature=Dead+Stock+Recovery&progress=10&eta=Q4+2026', feature_flag: 'dead_stock_enabled' }
        ]
    },
    {
        type: 'category',
        id: 'ai_hub',
        emoji: '🤖',
        label: 'AI Hub',
        items: [
            { id: 'demand_forecast', label: '├─ Demand Forecast', url: '/smriti-coming-soon?feature=Demand+Forecast&progress=30&eta=Q4+2026', feature_flag: 'demand_forecast_enabled' },
            { id: 'slow_mover', label: '├─ Slow Mover Detection', url: '/smriti-coming-soon?feature=Slow+Mover+Detection&progress=35&eta=Q4+2026', feature_flag: 'slow_mover_enabled' },
            { id: 'purchase_suggestions', label: '├─ Purchase Suggestions', url: '/smriti-coming-soon?feature=Purchase+Suggestions&progress=40&eta=Q4+2026', feature_flag: 'purchase_suggestions_enabled' },
            { id: 'promo_suggestions', label: '├─ Promotion Suggestions', url: '/smriti-coming-soon?feature=Promotion+Suggestions&progress=45&eta=Q4+2026', feature_flag: 'promo_suggestions_enabled' },
            { id: 'stock_risk_alerts', label: '└─ Stock Risk Alerts', url: '/smriti-coming-soon?feature=Stock+Risk+Alerts&progress=50&eta=Q4+2026', feature_flag: 'stock_risk_alerts_enabled' }
        ]
    },
    {
        type: 'category',
        id: 'reports',
        emoji: '📑',
        label: 'Reports',
        items: [
            { id: 'sales_reports', label: '├─ Sales Reports', url: '/reports?category=Sales' },
            { id: 'purchase_reports', label: '├─ Purchase Reports', url: '/reports?category=Purchase' },
            { id: 'inventory_reports', label: '├─ Inventory Reports', url: '/reports?category=Inventory' },
            { id: 'psv_reports', label: '├─ PSV Reports', url: '/reports?category=PSV' },
            { id: 'pricing_reports', label: '├─ Pricing Reports', url: '/reports?category=Pricing' },
            { id: 'saved_reports', label: '└─ Saved Reports', url: '/reports?category=Saved' }
        ]
    },
    {
        type: 'category',
        id: 'integrations',
        emoji: '🔄',
        label: 'Integrations',
        items: [
            { id: 'tally_sync', label: '├─ TallyPrime Sync', url: '/smriti-coming-soon?feature=TallyPrime+Sync&progress=85&eta=Q3+2026' },
            { id: 'export_center', label: '├─ Export Center', url: '/smriti-coming-soon?feature=Export+Center&progress=60&eta=Q3+2026' },
            { id: 'import_center', label: '├─ Import Center', url: '/smriti-coming-soon?feature=Import+Center&progress=70&eta=Q3+2026' },
            { id: 'sync_history', label: '├─ Sync History', url: '/smriti-coming-soon?feature=Sync+History&progress=40&eta=Q3+2026' },
            { id: 'integration_settings', label: '└─ Integration Settings', url: '/smriti-coming-soon?feature=Integration+Settings&progress=50&eta=Q3+2026' }
        ]
    },
    {
        type: 'category',
        id: 'admin',
        emoji: '⚙️',
        label: 'Administration',
        items: [
            { id: 'users', label: '├─ Users', url: '/smriti-coming-soon?feature=Users+Management&progress=80&eta=Q3+2026' },
            { id: 'roles', label: '├─ Roles', url: '/smriti-coming-soon?feature=Roles+Management&progress=75&eta=Q3+2026' },
            { id: 'security', label: '├─ Security & Workflow', url: '/security' },
            { id: 'audit_logs', label: '├─ Audit Logs', url: '/smriti-coming-soon?feature=Audit+Logs&progress=90&eta=Q3+2026' },
            { id: 'activity_logs', label: '├─ Activity Logs', url: '/smriti-coming-soon?feature=Activity+Logs&progress=85&eta=Q3+2026' },
            { id: 'backup', label: '├─ Backup Center', url: '/backup' },
            { id: 'configure', label: '└─ System Settings', url: '/configure' }
        ]
    },
    {
        type: 'link',
        id: 'help',
        emoji: '🆘',
        label: 'Help Desk',
        url: '/smriti-coming-soon?feature=Help+Desk&progress=80&eta=Q3+2026'
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

    // Feature Flag Policy
    function isFeatureEnabled(flag) {
        if (!flag) return true;
        const SMRITI_FEATURE_FLAGS = {
            "intelligence_enabled": false,
            "ai_hub_enabled": false,
            "coverage_days_enabled": false,
            "exec_dashboard_enabled": false,
            "gmroi_enabled": false,
            "sell_through_enabled": false,
            "inventory_aging_enabled": false,
            "capital_locked_enabled": false,
            "dead_stock_enabled": false,
            "demand_forecast_enabled": false,
            "slow_mover_enabled": false,
            "purchase_suggestions_enabled": false,
            "promo_suggestions_enabled": false,
            "stock_risk_alerts_enabled": false
        };
        return !!SMRITI_FEATURE_FLAGS[flag];
    }

    const filteredSchema = JSON.parse(JSON.stringify(SMRITI.sidebarSchema));
    const renderedSchema = [];

    filteredSchema.forEach(cat => {
        // Exclude category by feature flag
        if (cat.feature_flag && !isFeatureEnabled(cat.feature_flag)) {
            return;
        }

        if (cat.type === 'category') {
            if (cat.items) {
                cat.items = cat.items.filter(item => {
                    // Exclude items by feature flag
                    if (item.feature_flag && !isFeatureEnabled(item.feature_flag)) {
                        return false;
                    }
                    if (business_type !== "Footwear") {
                        // FMCG / Others (hide footwear size attributes)
                        if (['sizewise_item', 'sizewise_invoice'].includes(item.id)) return false;
                    }
                    return true;
                });
            }
            // AUTO-HIDE POLICY: Hide category if no child items or only subheaders are rendered
            const hasClickableItems = cat.items && cat.items.some(item => item.type !== 'subheader');
            if (!hasClickableItems) {
                return;
            }
        } else if (cat.type === 'link') {
            // Exclude links by feature flag
            if (cat.feature_flag && !isFeatureEnabled(cat.feature_flag)) {
                return;
            }
        }
        renderedSchema.push(cat);
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
    
    renderedSchema.forEach(block => {
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
                
                if (sub.type === 'subheader') {
                    subItemsHtml += `
                        <div class="sidebar-sub-header smriti-side-sub-header">
                            <span>${sub.label}</span>
                        </div>
                    `;
                    return;
                }
                
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
