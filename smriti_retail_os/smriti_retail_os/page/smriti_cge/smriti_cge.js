/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_cge/smriti_cge.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

frappe.pages['smriti-cge'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('CGE Studio'),
        single_column: true
    });

    if (window.SMRITI && typeof SMRITI.renderSidebar === 'function') {
        SMRITI.renderSidebar("masters"); // Render sidebar indicating masters/marketing context
    }

    window.smriti_cge = new SmritiCGEPage(wrapper);
};

class SmritiCGEPage {
    constructor(wrapper) {
        this.wrapper = $(wrapper);
        this.active_tab = 'dashboard';
        this.data = {
            campaigns: [],
            loyalty_rules: [],
            loyalty_tiers: [],
            promotions: [],
            wallet_ledger: []
        };
        this.init();
    }

    init() {
        this.setup_layout();
        this.bind_tabs();
        this.load_tab_data();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-cge-container">
                <!-- Header Component -->
                <div class="smriti-cge-header">
                    <div class="smriti-cge-branding">
                        <span class="material-symbols-outlined" style="font-size: 32px; color: #ffffff;">campaign</span>
                        <div class="smriti-cge-title-group">
                            <h1>Customer Growth Engine (CGE) Studio</h1>
                            <p>SMRITI Retail OS — Loyalty, Campaigns, and Promotions Console</p>
                        </div>
                    </div>
                    <!-- Tabs Navigation -->
                    <div class="smriti-cge-tabs-nav">
                        <button class="smriti-cge-tab-btn active" data-tab="dashboard">
                            <span class="material-symbols-outlined">analytics</span> Dashboard
                        </button>
                        <button class="smriti-cge-tab-btn" data-tab="promotions">
                            <span class="material-symbols-outlined">sell</span> Promotions
                        </button>
                        <button class="smriti-cge-tab-btn" data-tab="loyalty">
                            <span class="material-symbols-outlined">card_membership</span> Loyalty Studio
                        </button>
                        <button class="smriti-cge-tab-btn" data-tab="coupons">
                            <span class="material-symbols-outlined">local_activity</span> Coupons
                        </button>
                        <button class="smriti-cge-tab-btn" data-tab="wallet">
                            <span class="material-symbols-outlined">account_balance_wallet</span> Cashback Wallet
                        </button>
                    </div>
                </div>

                <!-- Tab content containers -->
                <div class="smriti-cge-tab-content active" id="cge-tab-dashboard">
                    <!-- Stat Cards Grid -->
                    <div class="smriti-cge-dashboard-grid" id="dashboard-metrics-container">
                        <div class="empty-state">
                            <span class="empty-icon"><span class="material-symbols-outlined">hourglass_empty</span></span>
                            <span class="empty-text">Loading metrics...</span>
                        </div>
                    </div>

                    <!-- Snapshot History Widget -->
                    <div class="smriti-cge-panel">
                        <div class="panel-header">
                            <span class="panel-title"><span class="material-symbols-outlined">history</span> Outstanding Liability Risk Log</span>
                        </div>
                        <div style="padding: 10px 0;" id="dashboard-recent-snapshots">
                            <!-- Populated dynamically -->
                            <div class="empty-state">
                                <span class="empty-text">No active risk flags raised. Real-time ledger checks in progress.</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="smriti-cge-tab-content" id="cge-tab-promotions">
                    <div class="smriti-cge-grid">
                        <div class="smriti-cge-panel">
                            <div class="panel-header">
                                <span class="panel-title"><span class="material-symbols-outlined">list_alt</span> Active Pricing Rules</span>
                            </div>
                            <div class="smriti-cge-list-wrapper" id="promotions-list">
                                <div class="empty-state"><span class="empty-text">Loading Pricing Rules...</span></div>
                            </div>
                        </div>
                        <div class="smriti-cge-panel">
                            <div class="panel-header">
                                <span class="panel-title"><span class="material-symbols-outlined">info</span> Promotion Info</span>
                            </div>
                            <div id="promotion-editor-container">
                                <div class="empty-state">
                                    <span class="empty-icon"><span class="material-symbols-outlined">touch_app</span></span>
                                    <span class="empty-text">Select a pricing rule from the left panel.</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="smriti-cge-tab-content" id="cge-tab-loyalty">
                    <div style="margin-bottom: 15px; display: flex; justify-content: flex-end; gap: 8px;">
                        <button class="btn btn-sm btn-primary" id="btn-new-loyalty-tier">New Loyalty Tier</button>
                        <button class="btn btn-sm btn-primary" id="btn-new-loyalty-rule">New Loyalty Rule</button>
                    </div>
                    <div class="smriti-cge-grid">
                        <div class="smriti-cge-panel">
                            <div class="panel-header">
                                <span class="panel-title"><span class="material-symbols-outlined">military_tech</span> Loyalty Tiers & Rules</span>
                            </div>
                            <div class="smriti-cge-list-wrapper" id="loyalty-list">
                                <div class="empty-state"><span class="empty-text">Loading Loyalty Rules...</span></div>
                            </div>
                        </div>
                        <div class="smriti-cge-panel">
                            <div class="panel-header">
                                <span class="panel-title"><span class="material-symbols-outlined">border_color</span> Rule Configuration</span>
                            </div>
                            <div id="loyalty-editor-container">
                                <div class="empty-state">
                                    <span class="empty-icon"><span class="material-symbols-outlined">touch_app</span></span>
                                    <span class="empty-text">Select a tier or loyalty rule to edit, or click New.</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="smriti-cge-tab-content" id="cge-tab-coupons">
                    <div style="margin-bottom: 15px; display: flex; justify-content: flex-end;">
                        <button class="btn btn-sm btn-primary" id="btn-new-coupon-campaign">New Coupon Campaign</button>
                    </div>
                    <div class="smriti-cge-grid">
                        <div class="smriti-cge-panel">
                            <div class="panel-header">
                                <span class="panel-title"><span class="material-symbols-outlined">campaign</span> Coupon Campaigns</span>
                            </div>
                            <div class="smriti-cge-list-wrapper" id="coupons-list">
                                <div class="empty-state"><span class="empty-text">Loading campaigns...</span></div>
                            </div>
                        </div>
                        <div class="smriti-cge-panel">
                            <div class="panel-header">
                                <span class="panel-title"><span class="material-symbols-outlined">account_balance</span> Campaign Budget Config</span>
                            </div>
                            <div id="coupons-editor-container">
                                <div class="empty-state">
                                    <span class="empty-icon"><span class="material-symbols-outlined">touch_app</span></span>
                                    <span class="empty-text">Select a campaign to configure budgets and utilization settings.</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="smriti-cge-tab-content" id="cge-tab-wallet">
                    <div style="margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid var(--smriti-glass-border);">
                        <div style="display: flex; gap: 8px; align-items: center; flex: 1;">
                            <label class="s-label" style="margin: 0; min-width: 100px;">Filter Customer</label>
                            <input type="text" id="wallet-customer-filter" class="form-control s-input" style="max-width: 250px;" placeholder="Search customer name...">
                        </div>
                        <button class="btn btn-sm btn-primary" id="btn-manual-wallet-adj">Manual Adjustment</button>
                    </div>
                    <div class="smriti-cge-panel" style="overflow-x: auto;">
                        <div class="panel-header">
                            <span class="panel-title"><span class="material-symbols-outlined">receipt_long</span> Wallet Ledger Entries</span>
                        </div>
                        <table class="smriti-cge-wallet-table">
                            <thead>
                                <tr>
                                    <th>Sequence ID</th>
                                    <th>Customer</th>
                                    <th>Wallet Type</th>
                                    <th>Transaction</th>
                                    <th>Amount</th>
                                    <th>Reference Invoice</th>
                                    <th>Journal Entry</th>
                                    <th>Audit Reason</th>
                                    <th>Created At</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="wallet-ledger-entries">
                                <tr>
                                    <td colspan="10" style="text-align: center; padding: 30px;">Loading Wallet Ledger...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `);

        // Bind button actions for creating new records
        const me = this;
        this.wrapper.find("#btn-new-loyalty-tier").on("click", () => me.show_loyalty_tier_editor(null));
        this.wrapper.find("#btn-new-loyalty-rule").on("click", () => me.show_loyalty_rule_editor(null));
        this.wrapper.find("#btn-new-coupon-campaign").on("click", () => me.show_campaign_editor(null));
        this.wrapper.find("#btn-manual-wallet-adj").on("click", () => me.show_wallet_adjustment_dialog());
        this.wrapper.find("#wallet-customer-filter").on("input", function() {
            const val = $(this).val().trim();
            me.load_wallet_ledger(val);
        });
    }

    bind_tabs() {
        const me = this;
        this.wrapper.find(".smriti-cge-tab-btn").on("click", function() {
            const tab = $(this).data("tab");
            me.wrapper.find(".smriti-cge-tab-btn").removeClass("active");
            $(this).addClass("active");
            me.wrapper.find(".smriti-cge-tab-content").removeClass("active");
            me.wrapper.find(`#cge-tab-${tab}`).addClass("active");
            me.active_tab = tab;
            me.load_tab_data();
        });
    }

    load_tab_data() {
        if (this.active_tab === 'dashboard') {
            this.load_dashboard();
        } else if (this.active_tab === 'promotions') {
            this.load_promotions();
        } else if (this.active_tab === 'loyalty') {
            this.load_loyalty();
        } else if (this.active_tab === 'coupons') {
            this.load_coupons();
        } else if (this.active_tab === 'wallet') {
            const filter = this.wrapper.find("#wallet-customer-filter").val();
            this.load_wallet_ledger(filter);
        }
    }

    // ──────────────────────────────────────────
    // Tab 1: Dashboard
    // ──────────────────────────────────────────
    load_dashboard() {
        const me = this;
        frappe.call({
            method: "smriti_retail_os.cge.api.cge_api.get_cge_liability_metrics",
            callback: function(r) {
                const metrics = r.message || { loyalty_liability: 0, cashback_liability: 0, coupon_exposure: 0, total_liability: 0, amber_threshold: 100000, red_threshold: 250000 };
                
                // Risk determination
                let risk_status = 'GREEN';
                let risk_class = 'green';
                let card_class_loyalty = '';
                let card_class_cashback = '';
                
                const amber_limit = flt(metrics.amber_threshold) || 100000.0;
                const red_limit = flt(metrics.red_threshold) || 250000.0;

                if (metrics.total_liability > red_limit) {
                    risk_status = 'RED RISK';
                    risk_class = 'red';
                    card_class_loyalty = 'risk-red';
                    card_class_cashback = 'risk-red';
                } else if (metrics.total_liability > amber_limit) {
                    risk_status = 'AMBER WARNING';
                    risk_class = 'amber';
                    card_class_loyalty = 'risk-amber';
                    card_class_cashback = 'risk-amber';
                }

                me.wrapper.find("#dashboard-metrics-container").html(`
                    <!-- Loyalty Exposure Card -->
                    <div class="smriti-cge-stat-card ${card_class_loyalty}">
                        <div class="smriti-cge-stat-header">
                            <span>Outstanding Loyalty Points</span>
                            <span class="material-symbols-outlined" style="color: var(--smriti-blue);">stars</span>
                        </div>
                        <div class="smriti-cge-stat-val">
                            ${parseFloat(metrics.loyalty_liability).toLocaleString()} <span style="font-size:14px; font-weight:400; color:var(--smriti-text-muted);">Points</span>
                        </div>
                        <div class="smriti-cge-stat-desc">Remaining points in active Loyalty Point Entries</div>
                    </div>

                    <!-- Cashback Wallet Exposure Card -->
                    <div class="smriti-cge-stat-card ${card_class_cashback}">
                        <div class="smriti-cge-stat-header">
                            <span>Cashback Wallet Liability</span>
                            <span class="material-symbols-outlined" style="color: #10B981;">account_balance_wallet</span>
                        </div>
                        <div class="smriti-cge-stat-val">
                            ₹${parseFloat(metrics.cashback_liability).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </div>
                        <div class="smriti-cge-stat-desc">Total wallet ledger balance exposure across all customers</div>
                    </div>

                    <!-- Active Campaign Budget Reserved Card -->
                    <div class="smriti-cge-stat-card">
                        <div class="smriti-cge-stat-header">
                            <span>Campaign Exposure</span>
                            <span class="material-symbols-outlined" style="color: #F59E0B;">toll</span>
                        </div>
                        <div class="smriti-cge-stat-val">
                            ₹${parseFloat(metrics.coupon_exposure).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </div>
                        <div class="smriti-cge-stat-desc">Reserved budgets from active coupon checkouts</div>
                    </div>

                    <!-- Risk Metric Card -->
                    <div class="smriti-cge-stat-card ${metrics.total_liability > red_limit ? 'risk-red' : (metrics.total_liability > amber_limit ? 'risk-amber' : '')}">
                        <div class="smriti-cge-stat-header">
                            <span>CGE Liability Risk Level</span>
                            <span class="smriti-cge-indicator ${risk_class}">${risk_status}</span>
                        </div>
                        <div class="smriti-cge-stat-val" style="font-size: 24px;">
                            ₹${parseFloat(metrics.total_liability).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </div>
                        <div class="smriti-cge-stat-desc">Combined outstanding liability score (Target limit: ₹${red_limit.toLocaleString('en-IN')})</div>
                    </div>
                `);

                // Outstanding snapshots check
                me.load_snapshots();
            }
        });
    }

    load_snapshots() {
        const me = this;
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "SMRITI Liability Snapshot",
                fields: ["snapshot_date", "loyalty_liability", "cashback_liability", "coupon_liability"],
                order_by: "snapshot_date desc",
                limit: 5
            },
            callback: function(r) {
                const logs = r.message || [];
                const container = me.wrapper.find("#dashboard-recent-snapshots");
                if (logs.length === 0) {
                    container.html(`
                        <div style="text-align: center; color: var(--smriti-text-muted); padding: 20px;">
                            No liability history logs found. Nightly cron will record statistics automatically.
                        </div>
                    `);
                    return;
                }

                let html = `
                    <table class="smriti-cge-wallet-table">
                        <thead>
                            <tr>
                                <th>Snapshot Date</th>
                                <th>Loyalty Exposure</th>
                                <th>Cashback Balance Exposure</th>
                                <th>Coupon Budget Reserved</th>
                                <th>Total Exposure</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                logs.forEach(l => {
                    const total = flt(l.loyalty_liability) + flt(l.cashback_liability) + flt(l.coupon_liability);
                    const risk_indicator = total > 250000 
                        ? '<span class="smriti-cge-indicator red">RED RISK</span>' 
                        : (total > 100000 ? '<span class="smriti-cge-indicator amber">AMBER WARNING</span>' : '<span class="smriti-cge-indicator green">STABLE</span>');

                    html += `
                        <tr>
                            <td><b>${l.snapshot_date}</b></td>
                            <td>${parseFloat(l.loyalty_liability).toLocaleString()} Pts</td>
                            <td>₹${parseFloat(l.cashback_liability).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                            <td>₹${parseFloat(l.coupon_liability).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                            <td><b>₹${total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</b></td>
                            <td>${risk_indicator}</td>
                        </tr>
                    `;
                });

                html += `</tbody></table>`;
                container.html(html);
            }
        });
    }


    // ──────────────────────────────────────────
    // Tab 2: Promotions
    // ──────────────────────────────────────────
    load_promotions() {
        const me = this;
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Pricing Rule",
                filters: { disable: 0 },
                fields: ["name", "title", "selling", "price_or_product_discount", "apply_on", "rate_or_discount", "discount_percentage", "discount_amount"],
                order_by: "creation desc"
            },
            callback: function(r) {
                me.data.promotions = r.message || [];
                me.render_promotions_list();
            }
        });
    }

    render_promotions_list() {
        const list_div = this.wrapper.find("#promotions-list");
        list_div.empty();

        if (this.data.promotions.length === 0) {
            list_div.html(`<div class="empty-state"><span class="empty-text">No active promotions found.</span></div>`);
            return;
        }

        const me = this;
        this.data.promotions.forEach(p => {
            const desc = p.rate_or_discount === 'Discount Percentage' 
                ? `${p.discount_percentage}% off` 
                : (p.rate_or_discount === 'Discount Amount' ? `₹${p.discount_amount} off` : 'Rate Override');

            list_div.append(`
                <div class="smriti-cge-card" data-name="${p.name}">
                    <div class="smriti-cge-card-header">
                        <span class="smriti-cge-card-title">${p.title || p.name}</span>
                        <span class="smriti-cge-card-badge">${p.apply_on}</span>
                    </div>
                    <div class="smriti-cge-card-details">
                        <span><b>Benefit:</b> ${desc}</span>
                        <span><b>Linked Doc:</b> ${p.name}</span>
                    </div>
                </div>
            `);
        });

        list_div.find(".smriti-cge-card").on("click", function() {
            const name = $(this).data("name");
            const promo = me.data.promotions.find(p => p.name === name);
            me.show_promotion_details(promo);
            list_div.find(".smriti-cge-card").removeClass("active");
            $(this).addClass("active");
        });
    }

    show_promotion_details(promo) {
        const container = this.wrapper.find("#promotion-editor-container");
        container.html(`
            <div class="editor-form-card">
                <h3>${promo.title || promo.name}</h3>
                <table class="smriti-cge-wallet-table" style="margin-top: 15px;">
                    <tbody>
                        <tr><td><b>System ID:</b></td><td>${promo.name}</td></tr>
                        <tr><td><b>Promotion Rule type:</b></td><td>${promo.price_or_product_discount}</td></tr>
                        <tr><td><b>Applies On:</b></td><td>${promo.apply_on}</td></tr>
                        <tr><td><b>Discount Calculation:</b></td><td>${promo.rate_or_discount}</td></tr>
                        <tr><td><b>Efficacy:</b></td><td>Active / Enabled</td></tr>
                    </tbody>
                </table>
                <p style="margin-top: 15px; font-size:12px; color: var(--smriti-text-muted);">
                    SMRITI Retail OS uses standard ERPNext Pricing Rules for promotional discounts. Direct modifications can be made in the system setting panel.
                </p>
                <div style="margin-top: 20px;">
                    <a href="/app/pricing-rule/${promo.name}" class="btn-smriti-action text-center" style="display:inline-flex;">
                        <span class="material-symbols-outlined" style="color:white; font-size:16px;">open_in_new</span> Edit Pricing Rule
                    </a>
                </div>
            </div>
        `);
    }

    // ──────────────────────────────────────────
    // Tab 3: Loyalty Studio
    // ──────────────────────────────────────────
    load_loyalty() {
        const me = this;
        // Fetch tiers and rules concurrently
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "SMRITI Loyalty Tier",
                fields: ["name", "tier_name", "min_points", "tier_multiplier", "active"],
                order_by: "min_points asc"
            },
            callback: function(r1) {
                me.data.loyalty_tiers = r1.message || [];
                
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "SMRITI Loyalty Rule",
                        fields: ["name", "rule_name", "rule_type", "dimension", "dimension_value", "rule_value", "priority", "status"],
                        order_by: "priority desc"
                    },
                    callback: function(r2) {
                        me.data.loyalty_rules = r2.message || [];
                        me.render_loyalty_list();
                    }
                });
            }
        });
    }

    render_loyalty_list() {
        const list_div = this.wrapper.find("#loyalty-list");
        list_div.empty();

        const me = this;
        
        // Add Section Header for Tiers
        list_div.append(`<div style="font-weight:700; color:var(--smriti-navy); font-size:12px; text-transform:uppercase; margin-bottom: 8px;">Loyalty Tiers</div>`);
        
        if (this.data.loyalty_tiers.length === 0) {
            list_div.append(`<div class="empty-state" style="padding:10px;"><span class="empty-text">No tiers configured.</span></div>`);
        } else {
            this.data.loyalty_tiers.forEach(t => {
                list_div.append(`
                    <div class="smriti-cge-card" data-type="tier" data-name="${t.name}" style="border-left: 4px solid var(--smriti-blue);">
                        <div class="smriti-cge-card-header">
                            <span class="smriti-cge-card-title">${t.tier_name}</span>
                            <span class="smriti-cge-card-badge">${t.active ? 'Active' : 'Inactive'}</span>
                        </div>
                        <div class="smriti-cge-card-details">
                            <span><b>Min Points:</b> ${t.min_points}</span>
                            <span><b>Earning Multiplier:</b> ${t.tier_multiplier}x</span>
                        </div>
                    </div>
                `);
            });
        }

        // Add Section Header for Rules
        list_div.append(`<div style="font-weight:700; color:var(--smriti-navy); font-size:12px; text-transform:uppercase; margin: 15px 0 8px 0;">Loyalty Rules</div>`);
        
        if (this.data.loyalty_rules.length === 0) {
            list_div.append(`<div class="empty-state" style="padding:10px;"><span class="empty-text">No custom rules configured.</span></div>`);
        } else {
            this.data.loyalty_rules.forEach(r => {
                list_div.append(`
                    <div class="smriti-cge-card" data-type="rule" data-name="${r.name}" style="border-left: 4px solid #10B981;">
                        <div class="smriti-cge-card-header">
                            <span class="smriti-cge-card-title">${r.rule_name}</span>
                            <span class="smriti-cge-card-badge">${r.status}</span>
                        </div>
                        <div class="smriti-cge-card-details">
                            <span><b>Type:</b> ${r.rule_type} | <b>Priority:</b> ${r.priority}</span>
                            <span><b>Dimension:</b> ${r.dimension} (${r.dimension_value})</span>
                            <span><b>Rule Value:</b> ${r.rule_value}</span>
                        </div>
                    </div>
                `);
            });
        }

        list_div.find(".smriti-cge-card").on("click", function() {
            const name = $(this).data("name");
            const type = $(this).data("type");
            list_div.find(".smriti-cge-card").removeClass("active");
            $(this).addClass("active");

            if (type === 'tier') {
                const tier = me.data.loyalty_tiers.find(t => t.name === name);
                me.show_loyalty_tier_editor(tier);
            } else {
                const rule = me.data.loyalty_rules.find(ru => ru.name === name);
                me.show_loyalty_rule_editor(rule);
            }
        });
    }

    show_loyalty_tier_editor(tier) {
        const container = this.wrapper.find("#loyalty-editor-container");
        const is_new = !tier;
        const data = tier || { tier_name: '', min_points: 0, tier_multiplier: 1.0, active: 1 };
        
        container.html(`
            <div class="editor-form-card">
                <h3>${is_new ? 'New Loyalty Tier' : 'Edit Tier: ' + data.tier_name}</h3>
                <div class="form-group" style="margin-top:15px;">
                    <label class="s-label">Tier Name</label>
                    <input type="text" id="tier-name-input" class="form-control s-input" value="${data.tier_name}">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="s-label">Min Points Requirement</label>
                        <input type="number" id="tier-min-points" class="form-control s-input" value="${data.min_points}">
                    </div>
                    <div class="form-group">
                        <label class="s-label">Collection Multiplier</label>
                        <input type="number" step="0.1" id="tier-multiplier" class="form-control s-input" value="${data.tier_multiplier}">
                    </div>
                </div>
                <div class="form-group">
                    <label class="s-label">Status</label>
                    <select id="tier-active" class="form-control s-input">
                        <option value="1" ${data.active == 1 ? 'selected' : ''}>Active</option>
                        <option value="0" ${data.active == 0 ? 'selected' : ''}>Inactive</option>
                    </select>
                </div>
                <div style="margin-top: 20px; display:flex; gap: 8px;">
                    <button class="btn-smriti-action" id="btn-save-tier" style="flex:1;">Save Tier</button>
                    ${!is_new ? `<button class="btn-smriti-action btn-danger" id="btn-delete-tier">Delete</button>` : ''}
                </div>
            </div>
        `);

        const me = this;
        this.wrapper.find("#btn-save-tier").on("click", function() {
            const tier_obj = {
                name: is_new ? null : tier.name,
                tier_name: me.wrapper.find("#tier-name-input").val().trim(),
                min_points: flt(me.wrapper.find("#tier-min-points").val()),
                tier_multiplier: flt(me.wrapper.find("#tier-multiplier").val()),
                active: parseInt(me.wrapper.find("#tier-active").val())
            };
            
            if (!tier_obj.tier_name) {
                frappe.show_alert({message: "Tier Name is required.", indicator: "red"});
                return;
            }

            frappe.call({
                method: "smriti_retail_os.cge.api.cge_api.save_loyalty_tier",
                args: { tier_data: tier_obj },
                freeze: true,
                callback: function() {
                    frappe.show_alert({message: "Tier saved successfully", indicator: "green"});
                    me.load_loyalty();
                }
            });
        });

        if (!is_new) {
            this.wrapper.find("#btn-delete-tier").on("click", function() {
                frappe.confirm("Are you sure you want to delete this Loyalty Tier?", () => {
                    frappe.call({
                        method: "frappe.client.delete",
                        args: { doctype: "SMRITI Loyalty Tier", name: tier.name },
                        callback: function() {
                            frappe.show_alert({message: "Tier deleted", indicator: "green"});
                            me.load_loyalty();
                            container.html(`<div class="empty-state"><span class="empty-text">Tier deleted. Select another.</span></div>`);
                        }
                    });
                });
            });
        }
    }

    show_loyalty_rule_editor(rule) {
        const container = this.wrapper.find("#loyalty-editor-container");
        const is_new = !rule;
        const data = rule || { rule_name: '', rule_type: 'Multiplier', dimension: 'Brand', dimension_value: '', rule_value: 1.0, priority: 10, status: 'Active', allow_stack: 1 };
        
        container.html(`
            <div class="editor-form-card">
                <h3>${is_new ? 'New Loyalty Rule' : 'Edit Rule: ' + data.rule_name}</h3>
                <div class="form-group" style="margin-top:15px;">
                    <label class="s-label">Rule Name</label>
                    <input type="text" id="rule-name-input" class="form-control s-input" value="${data.rule_name}">
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="s-label">Rule Type</label>
                        <select id="rule-type-input" class="form-control s-input">
                            <option value="Multiplier" ${data.rule_type === 'Multiplier' ? 'selected' : ''}>Multiplier</option>
                            <option value="Bonus Points" ${data.rule_type === 'Bonus Points' ? 'selected' : ''}>Bonus Points</option>
                            <option value="Cap" ${data.rule_type === 'Cap' ? 'selected' : ''}>Points Cap</option>
                            <option value="Exclusion" ${data.rule_type === 'Exclusion' ? 'selected' : ''}>Exclusion (No Points)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="s-label">Rule Value</label>
                        <input type="number" step="0.01" id="rule-val-input" class="form-control s-input" value="${data.rule_value}">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="s-label">Target Dimension</label>
                        <select id="rule-dimension" class="form-control s-input">
                            <option value="Brand" ${data.dimension === 'Brand' ? 'selected' : ''}>Brand</option>
                            <option value="Item Group" ${data.dimension === 'Item Group' ? 'selected' : ''}>Item Group</option>
                            <option value="Style" ${data.dimension === 'Style' ? 'selected' : ''}>Style Code</option>
                            <option value="Season" ${data.dimension === 'Season' ? 'selected' : ''}>Season</option>
                            <option value="Store" ${data.dimension === 'Store' ? 'selected' : ''}>Store (Warehouse)</option>
                            <option value="Customer Group" ${data.dimension === 'Customer Group' ? 'selected' : ''}>Customer Group</option>
                            <option value="Tier" ${data.dimension === 'Tier' ? 'selected' : ''}>Loyalty Tier</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="s-label">Dimension Value</label>
                        <input type="text" id="rule-dimension-value" class="form-control s-input" value="${data.dimension_value}" placeholder="Enter Brand Name, Tier, etc.">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="s-label">Priority</label>
                        <input type="number" id="rule-priority" class="form-control s-input" value="${data.priority}">
                    </div>
                    <div class="form-group">
                        <label class="s-label">Allow Rule Stacking</label>
                        <select id="rule-stack" class="form-control s-input">
                            <option value="1" ${data.allow_stack == 1 ? 'selected' : ''}>Yes</option>
                            <option value="0" ${data.allow_stack == 0 ? 'selected' : ''}>No (Priority Overrides)</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label class="s-label">Status</label>
                    <select id="rule-status" class="form-control s-input">
                        <option value="Active" ${data.status === 'Active' ? 'selected' : ''}>Active</option>
                        <option value="Inactive" ${data.status === 'Inactive' ? 'selected' : ''}>Inactive</option>
                    </select>
                </div>
                <div style="margin-top: 20px; display:flex; gap: 8px;">
                    <button class="btn-smriti-action" id="btn-save-rule" style="flex:1;">Save Rule</button>
                    ${!is_new ? `<button class="btn-smriti-action btn-danger" id="btn-delete-rule">Delete</button>` : ''}
                </div>
            </div>
        `);

        const me = this;
        this.wrapper.find("#btn-save-rule").on("click", function() {
            const rule_obj = {
                name: is_new ? null : rule.name,
                rule_name: me.wrapper.find("#rule-name-input").val().trim(),
                rule_type: me.wrapper.find("#rule-type-input").val(),
                rule_value: flt(me.wrapper.find("#rule-val-input").val()),
                dimension: me.wrapper.find("#rule-dimension").val(),
                dimension_value: me.wrapper.find("#rule-dimension-value").val().trim(),
                priority: parseInt(me.wrapper.find("#rule-priority").val()) || 10,
                allow_stack: parseInt(me.wrapper.find("#rule-stack").val()),
                status: me.wrapper.find("#rule-status").val()
            };
            
            if (!rule_obj.rule_name || !rule_obj.dimension_value) {
                frappe.show_alert({message: "Rule Name and Dimension Value are required.", indicator: "red"});
                return;
            }

            frappe.call({
                method: "smriti_retail_os.cge.api.cge_api.save_loyalty_rule",
                args: { rule_data: rule_obj },
                freeze: true,
                callback: function() {
                    frappe.show_alert({message: "Rule saved successfully", indicator: "green"});
                    me.load_loyalty();
                }
            });
        });

        if (!is_new) {
            this.wrapper.find("#btn-delete-rule").on("click", function() {
                frappe.confirm("Are you sure you want to delete this Loyalty Rule?", () => {
                    frappe.call({
                        method: "frappe.client.delete",
                        args: { doctype: "SMRITI Loyalty Rule", name: rule.name },
                        callback: function() {
                            frappe.show_alert({message: "Rule deleted", indicator: "green"});
                            me.load_loyalty();
                            container.html(`<div class="empty-state"><span class="empty-text">Rule deleted. Select another.</span></div>`);
                        }
                    });
                });
            });
        }
    }


    // ──────────────────────────────────────────
    // Tab 4: Coupons
    // ──────────────────────────────────────────
    load_coupons() {
        const me = this;
        frappe.call({
            method: "smriti_retail_os.cge.api.cge_api.get_campaigns_with_utilization",
            callback: function(r) {
                me.data.campaigns = r.message || [];
                me.render_coupons_list();
            }
        });
    }

    render_coupons_list() {
        const list_div = this.wrapper.find("#coupons-list");
        list_div.empty();

        if (this.data.campaigns.length === 0) {
            list_div.html(`<div class="empty-state"><span class="empty-text">No active campaigns configured.</span></div>`);
            return;
        }

        const me = this;
        this.data.campaigns.forEach(c => {
            const limit = flt(c.budget_limit);
            const consumed = flt(c.budget_consumed);
            const reserved = flt(c.budget_reserved);
            const total_exposure = consumed + reserved;
            const util = flt(c.utilization);
            
            // Determine progress bar style
            let bar_class = '';
            if (util >= 90) bar_class = 'danger';
            else if (util >= 70) bar_class = 'warning';

            list_div.append(`
                <div class="smriti-cge-card" data-name="${c.name}">
                    <div class="smriti-cge-card-header">
                        <span class="smriti-cge-card-title">${c.campaign_name}</span>
                        <span class="smriti-cge-card-badge">${c.status}</span>
                    </div>
                    <div class="smriti-cge-card-details">
                        <span><b>Type:</b> ${c.campaign_type}</span>
                        <span><b>Dates:</b> ${c.start_date || 'Open'} to ${c.end_date || 'Open'}</span>
                        <span><b>Limit:</b> ₹${limit.toLocaleString('en-IN')} | <b>Consumed:</b> ₹${consumed.toLocaleString('en-IN')}</span>
                    </div>
                    <!-- Utilization Progress Meter -->
                    <div class="smriti-cge-progress-container">
                        <div class="smriti-cge-progress-label">
                            <span>Budget Utilization</span>
                            <span>${util.toFixed(1)}%</span>
                        </div>
                        <div class="smriti-cge-progress-bar-bg">
                            <div class="smriti-cge-progress-bar-fill ${bar_class}" style="width: ${Math.min(100, util)}%;"></div>
                        </div>
                    </div>
                </div>
            `);
        });

        list_div.find(".smriti-cge-card").on("click", function() {
            const name = $(this).data("name");
            const camp = me.data.campaigns.find(c => c.name === name);
            me.show_campaign_editor(camp);
            list_div.find(".smriti-cge-card").removeClass("active");
            $(this).addClass("active");
        });
    }

    show_campaign_editor(campaign) {
        const container = this.wrapper.find("#coupons-editor-container");
        const is_new = !campaign;
        const data = campaign || { campaign_name: '', campaign_type: 'Discount Coupon', start_date: '', end_date: '', budget_limit: 10000, stop_on_limit: 1, status: 'Active' };

        container.html(`
            <div class="editor-form-card">
                <h3>${is_new ? 'New Coupon Campaign' : 'Edit Campaign: ' + data.campaign_name}</h3>
                
                <div class="form-group" style="margin-top:15px;">
                    <label class="s-label">Campaign Name</label>
                    <input type="text" id="camp-name-input" class="form-control s-input" value="${data.campaign_name}">
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label class="s-label">Campaign Type</label>
                        <select id="camp-type-input" class="form-control s-input">
                            <option value="Discount Coupon" ${data.campaign_type === 'Discount Coupon' ? 'selected' : ''}>Discount Coupon</option>
                            <option value="Cashback Promo" ${data.campaign_type === 'Cashback Promo' ? 'selected' : ''}>Cashback Promo</option>
                            <option value="Seasonal Drive" ${data.campaign_type === 'Seasonal Drive' ? 'selected' : ''}>Seasonal Drive</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="s-label">Budget Limit (₹)</label>
                        <input type="number" id="camp-budget-limit" class="form-control s-input" value="${data.budget_limit}">
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label class="s-label">Start Date</label>
                        <input type="date" id="camp-start" class="form-control s-input" value="${data.start_date || ''}">
                    </div>
                    <div class="form-group">
                        <label class="s-label">End Date</label>
                        <input type="date" id="camp-end" class="form-control s-input" value="${data.end_date || ''}">
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label class="s-label">Stop Coupon on Budget Overrun</label>
                        <select id="camp-stop-limit" class="form-control s-input">
                            <option value="1" ${data.stop_on_limit == 1 ? 'selected' : ''}>Yes (Hard Stop)</option>
                            <option value="0" ${data.stop_on_limit == 0 ? 'selected' : ''}>No (Allow Overdraft)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="s-label">Campaign Status</label>
                        <select id="camp-status" class="form-control s-input">
                            <option value="Active" ${data.status === 'Active' ? 'selected' : ''}>Active</option>
                            <option value="Inactive" ${data.status === 'Inactive' ? 'selected' : ''}>Inactive</option>
                        </select>
                    </div>
                </div>

                <div style="margin-top: 20px; display:flex; gap: 8px;">
                    <button class="btn-smriti-action" id="btn-save-camp" style="flex:1;">Save Campaign</button>
                    ${!is_new ? `<button class="btn-smriti-action btn-danger" id="btn-delete-camp">Delete</button>` : ''}
                </div>
            </div>
        `);

        const me = this;
        this.wrapper.find("#btn-save-camp").on("click", function() {
            const camp_obj = {
                name: is_new ? null : campaign.name,
                campaign_name: me.wrapper.find("#camp-name-input").val().trim(),
                campaign_type: me.wrapper.find("#camp-type-input").val(),
                budget_limit: flt(me.wrapper.find("#camp-budget-limit").val()),
                start_date: me.wrapper.find("#camp-start").val(),
                end_date: me.wrapper.find("#camp-end").val(),
                stop_on_limit: parseInt(me.wrapper.find("#camp-stop-limit").val()),
                status: me.wrapper.find("#camp-status").val()
            };

            if (!camp_obj.campaign_name) {
                frappe.show_alert({message: "Campaign Name is required.", indicator: "red"});
                return;
            }

            frappe.call({
                method: "smriti_retail_os.cge.api.cge_api.save_coupon_campaign",
                args: { campaign_data: camp_obj },
                freeze: true,
                callback: function() {
                    frappe.show_alert({message: "Campaign saved successfully", indicator: "green"});
                    me.load_coupons();
                }
            });
        });

        if (!is_new) {
            this.wrapper.find("#btn-delete-camp").on("click", function() {
                frappe.confirm("Are you sure you want to delete this Coupon Campaign?", () => {
                    frappe.call({
                        method: "frappe.client.delete",
                        args: { doctype: "SMRITI Coupon Campaign", name: campaign.name },
                        callback: function() {
                            frappe.show_alert({message: "Campaign deleted", indicator: "green"});
                            me.load_coupons();
                            container.html(`<div class="empty-state"><span class="empty-text">Campaign deleted. Select another.</span></div>`);
                        }
                    });
                });
            });
        }
    }


    // ──────────────────────────────────────────
    // Tab 5: Cashback Wallet
    // ──────────────────────────────────────────
    load_wallet_ledger(customer_filter = '') {
        const me = this;
        frappe.call({
            method: "smriti_retail_os.cge.api.cge_api.get_wallet_ledger",
            args: { customer: customer_filter || null, limit: 50 },
            callback: function(r) {
                me.data.wallet_ledger = r.message || [];
                me.render_wallet_ledger();
            }
        });
    }

    render_wallet_ledger() {
        const tbody = this.wrapper.find("#wallet-ledger-entries");
        tbody.empty();

        if (this.data.wallet_ledger.length === 0) {
            tbody.html(`<tr><td colspan="10" style="text-align:center; padding:30px; color:var(--smriti-text-muted);">No wallet transactions logged.</td></tr>`);
            return;
        }

        const me = this;
        this.data.wallet_ledger.forEach(l => {
            const tr_class = l.transaction_type === 'Credit' ? 'credit' : 'debit';
            const sign = l.transaction_type === 'Credit' ? '+' : '-';
            const formatted_date = frappe.datetime.str_to_user(l.creation);
            
            // Check reversal action availability
            let action_btn = '';
            if (!l.is_reversal && l.transaction_type === 'Debit') {
                // Check if already reversed in memory list
                const reversed = me.data.wallet_ledger.some(rx => rx.is_reversal && rx.reference_invoice === l.reference_invoice && rx.transaction_type === 'Credit');
                if (!reversed) {
                    action_btn = `<button class="btn btn-xs btn-danger btn-reverse-wl" data-seq="${l.name}">Reverse</button>`;
                } else {
                    action_btn = `<span style="font-size:10px; color: var(--smriti-text-muted);">Reversed</span>`;
                }
            } else if (l.is_reversal) {
                action_btn = `<span style="font-size:10px; color: var(--smriti-text-muted);">Reversal Record</span>`;
            }

            const audit_reason = `<b>${l.adjustment_reason_type || '-'}</b>${l.remarks ? '<br><span class="text-muted">' + l.remarks + '</span>' : ''}`;

            tbody.append(`
                <tr>
                    <td><b>${l.ledger_sequence}</b></td>
                    <td>${l.customer}</td>
                    <td>${l.wallet_type}</td>
                    <td><span class="transaction-badge ${tr_class}">${l.transaction_type}</span></td>
                    <td><b>${sign} ₹${parseFloat(l.amount).toFixed(2)}</b></td>
                    <td>${l.reference_invoice || '-'}</td>
                    <td><a href="/app/journal-entry/${l.journal_entry}">${l.journal_entry || '-'}</a></td>
                    <td>${audit_reason}</td>
                    <td>${formatted_date}</td>
                    <td>${action_btn}</td>
                </tr>
            `);
        });

        // Bind reversal buttons
        tbody.find(".btn-reverse-wl").on("click", function() {
            const seq = $(this).data("seq");
            me.show_reversal_dialog(seq);
        });
    }

    show_reversal_dialog(ledger_seq) {
        const me = this;
        const d = new frappe.ui.Dialog({
            title: __('Reverse Wallet Transaction'),
            fields: [
                {
                    label: __('Reason for Reversal'),
                    fieldname: 'reason',
                    fieldtype: 'Small Text',
                    reqd: 1
                }
            ],
            primary_action_label: __('Confirm Reversal'),
            primary_action(values) {
                frappe.call({
                    method: "smriti_retail_os.cge.api.cge_api.reverse_wallet_transaction",
                    args: {
                        ledger_seq: ledger_seq,
                        reason: values.reason
                    },
                    freeze: true,
                    callback: function(r) {
                        d.hide();
                        frappe.show_alert({message: "Reversal posted successfully", indicator: "green"});
                        me.load_tab_data();
                    }
                });
            }
        });
        d.show();
    }

    show_wallet_adjustment_dialog() {
        const me = this;
        const d = new frappe.ui.Dialog({
            title: __('Manual Wallet Adjustment'),
            fields: [
                {
                    label: __('Customer ID'),
                    fieldname: 'customer',
                    fieldtype: 'Link',
                    options: 'Customer',
                    reqd: 1
                },
                {
                    label: __('Wallet Type'),
                    fieldname: 'wallet_type',
                    fieldtype: 'Select',
                    options: ['Promo Cashback', 'Customer Refund', 'Manual Adjustment'],
                    default: 'Manual Adjustment',
                    reqd: 1
                },
                {
                    label: __('Transaction Type'),
                    fieldname: 'transaction_type',
                    fieldtype: 'Select',
                    options: ['Credit', 'Debit'],
                    default: 'Credit',
                    reqd: 1
                },
                {
                    label: __('Adjustment Category'),
                    fieldname: 'adjustment_reason_type',
                    fieldtype: 'Select',
                    options: ['Manual Credit', 'Manual Debit', 'Customer Complaint', 'Campaign Correction', 'System Recovery', 'Admin Adjustment'],
                    reqd: 1
                },
                {
                    label: __('Audit Remarks / Reason'),
                    fieldname: 'remarks',
                    fieldtype: 'Small Text',
                    reqd: 1
                },
                {
                    label: __('Adjustment Amount (₹)'),
                    fieldname: 'amount',
                    fieldtype: 'Currency',
                    reqd: 1
                }
            ],
            primary_action_label: __('Post Adjustment'),
            primary_action(values) {
                if (flt(values.amount) <= 0) {
                    frappe.show_alert({message: "Amount must be greater than zero", indicator: "red"});
                    return;
                }
                if (!values.remarks) {
                    frappe.show_alert({message: "Remarks / Reason is strictly required for audit trails.", indicator: "red"});
                    return;
                }
                frappe.call({
                    method: "smriti_retail_os.cge.api.cge_api.post_wallet_adjustment",
                    args: {
                        customer: values.customer,
                        wallet_type: values.wallet_type,
                        transaction_type: values.transaction_type,
                        amount: flt(values.amount),
                        remarks: values.remarks,
                        adjustment_reason_type: values.adjustment_reason_type
                    },
                    freeze: true,
                    callback: function(r) {
                        d.hide();
                        frappe.show_alert({message: "Adjustment transaction posted successfully", indicator: "green"});
                        me.load_tab_data();
                    }
                });
            }
        });
        d.show();
    }
}
