/**
 * @file: smriti_retail_os/page/smriti-loyalty/smriti-loyalty.js
 * @description: Page controller for SMRITI Loyalty & Promotions Page..
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI Retail OS — Loyalty Management Page Controller
   ============================================================ */

frappe.pages['smriti-loyalty'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Loyalty & Promotions'),
        single_column: true
    });

    if (window.SMRITI && typeof SMRITI.renderSidebar === 'function') {
        SMRITI.renderSidebar("loyalty");
    }

    window.smriti_loyalty = new SmritiLoyaltyPage(wrapper);
};

class SmritiLoyaltyPage {
    constructor(wrapper) {
        this.wrapper = $(wrapper);
        this.schemes = [];
        this.active_scheme = null;
        this.init();
    }

    init() {
        var me = this;
        me.setup_layout();
        me.load_schemes();
        me.bind_actions();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-loyalty-container dark-mode">
                <!-- Top Navbar -->
                <div class="smriti-top-nav">
                    <div class="smriti-status-indicators">
                        <span class="user-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">admin_panel_settings</span> Store Manager Console</span>
                    </div>
                    <div class="smriti-shortcuts-hint">
                        <span><b>F2</b> Search Customer | <b>ESC</b> Clear / Focus</span>
                    </div>
                </div>

                <!-- Main Layout Grid -->
                <div class="smriti-grid">
                    
                    <!-- Left Column: Schemes List -->
                    <div class="smriti-panel" style="flex: 1.2;">
                        <div class="panel-header">
                            <span class="panel-title"><span class="material-symbols-outlined">card_giftcard</span> Active Schemes</span>
                            <button class="btn btn-primary btn-xs" id="smriti-btn-new-scheme"><span class="material-symbols-outlined" style="font-size: 14px; color: white;">add</span> New</button>
                        </div>
                        <div class="schemes-list-wrapper" id="smriti-schemes-list">
                            <!-- Dynamic Cards -->
                            <div class="empty-state">
                                <span class="empty-icon"><span class="material-symbols-outlined">hourglass_empty</span></span>
                                <span class="empty-text">Loading Active Schemes...</span>
                            </div>
                        </div>
                    </div>

                    <!-- Middle Column: Details & Rules Editor -->
                    <div class="smriti-panel" style="flex: 1.8;">
                        <div class="panel-header">
                            <span class="panel-title"><span class="material-symbols-outlined">edit_note</span> Scheme Editor</span>
                        </div>
                        <div class="scheme-editor-wrapper" id="smriti-scheme-editor">
                            <div class="empty-state" style="padding: 60px 20px;">
                                <span class="empty-icon" style="color: #64748b;"><span class="material-symbols-outlined">touch_app</span></span>
                                <span class="empty-text">Select an active loyalty scheme or click "New" to create one.</span>
                            </div>
                        </div>
                    </div>

                    <!-- Right Column: Customer Enroller -->
                    <div class="smriti-panel" style="flex: 1.5;">
                        <div class="panel-header">
                            <span class="panel-title"><span class="material-symbols-outlined">person_add</span> Enroll Customers</span>
                        </div>
                        <div class="enroll-wrapper">
                            <div class="search-box-card">
                                <label class="s-label">Quick Search Customer</label>
                                <div class="barcode-input-container" style="margin-bottom: 12px;">
                                    <span class="scanner-icon"><span class="material-symbols-outlined">search</span></span>
                                    <input type="text" id="smriti-cust-search-input" placeholder="Type name or mobile..." autocomplete="off">
                                </div>
                            </div>
                            <div class="cust-results-wrapper" id="smriti-cust-results">
                                <div class="empty-state" style="padding: 40px 10px;">
                                    <span class="empty-icon" style="font-size: 32px;"><span class="material-symbols-outlined">group</span></span>
                                    <span class="empty-text">Search customer to assign them to a loyalty scheme.</span>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        `);
    }

    load_schemes() {
        var me = this;
        frappe.call({
            method: "smriti_retail_os.loyalty_api.get_loyalty_schemes",
            callback: function(r) {
                me.schemes = r.message || [];
                me.render_schemes_list();
            }
        });
    }

    render_schemes_list() {
        const list_div = $("#smriti-schemes-list");
        list_div.empty();

        if (this.schemes.length === 0) {
            list_div.html(`
                <div class="empty-state">
                    <span class="empty-icon"><span class="material-symbols-outlined">sentiment_dissatisfied</span></span>
                    <span class="empty-text">No active loyalty schemes configured in the system.</span>
                </div>
            `);
            return;
        }

        var me = this;
        this.schemes.forEach(sc => {
            const rules = sc.collection_rules || [];
            const rule_desc = rules.length > 0 
                ? `${rules[0].tier_name}: 1 Pt per ₹${(1/rules[0].collection_factor).toFixed(0)} spent` 
                : 'No earning rules configured';

            const active_class = me.active_scheme && me.active_scheme.name === sc.name ? 'active' : '';

            list_div.append(`
                <div class="scheme-card ${active_class}" data-name="${sc.name}">
                    <div class="scheme-card-header">
                        <span class="scheme-card-title">${sc.loyalty_program_name}</span>
                        <span class="scheme-card-badge">${sc.auto_opt_in ? 'Auto Enroll' : 'Manual'}</span>
                    </div>
                    <div class="scheme-card-details">
                        <span class="detail-row"><b>Conversion:</b> 1 Pt = ₹${parseFloat(sc.conversion_factor).toFixed(2)}</span>
                        <span class="detail-row"><b>Earning:</b> ${rule_desc}</span>
                    </div>
                </div>
            `);
        });

        // Binds
        list_div.find(".scheme-card").off("click").on("click", function() {
            const name = $(this).data("name");
            const sc = me.schemes.find(s => s.name === name);
            me.active_scheme = sc;
            me.render_schemes_list();
            me.render_editor();
        });
    }

    render_editor() {
        const editor_div = $("#smriti-scheme-editor");
        editor_div.empty();

        if (!this.active_scheme) return;

        const sc = this.active_scheme;
        const rules = sc.collection_rules || [{ tier_name: "Regular", min_spent: 0, collection_factor: 1 }];
        const rule = rules[0] || { tier_name: "Regular", min_spent: 0, collection_factor: 1 };
        
        // Calculate standard retail earning: 1 point per X INR spent (X = 1/collection_factor)
        const earning_amt = rule.collection_factor > 0 ? (1 / rule.collection_factor) : 100;

        editor_div.html(`
            <div class="editor-form-card">
                <div class="row">
                    <div class="col-md-12 form-group">
                        <label class="s-label">Scheme Name</label>
                        <input type="text" class="form-control s-input" id="smriti-edt-name" value="${sc.loyalty_program_name || ''}">
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 form-group">
                        <label class="s-label">Redemption Factor (Value per Point)</label>
                        <div class="input-group">
                            <span class="input-group-addon" style="background: rgba(255,255,255,0.02); color: #cbd5e1; border: 1px solid rgba(255,255,255,0.08);">₹</span>
                            <input type="number" step="0.01" class="form-control s-input" id="smriti-edt-conversion" value="${sc.conversion_factor || 1.0}">
                        </div>
                        <small class="text-muted">1 Point = ₹X discount at checkout</small>
                    </div>
                    <div class="col-md-6 form-group">
                        <label class="s-label">Auto Enroll Customers</label>
                        <div class="toggle-switch-wrapper" style="margin-top: 8px;">
                            <input type="checkbox" id="smriti-edt-auto" ${sc.auto_opt_in ? 'checked' : ''}>
                            <span class="toggle-label" style="margin-left: 8px;">Enable Auto-enrollment</span>
                        </div>
                    </div>
                </div>
                
                <hr style="border-top: 1px solid rgba(255,255,255,0.08); margin: 15px 0;">
                <span class="section-title-sm"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">currency_exchange</span> Earning / Collection Rules</span>
                
                <div class="row" style="margin-top: 10px;">
                    <div class="col-md-6 form-group">
                        <label class="s-label">Earning Tier Name</label>
                        <input type="text" class="form-control s-input" id="smriti-edt-tier" value="${rule.tier_name || 'Regular'}">
                    </div>
                    <div class="col-md-6 form-group">
                        <label class="s-label">Points Earning Ratio</label>
                        <div class="input-group">
                            <span class="input-group-addon" style="background: rgba(255,255,255,0.02); color: #cbd5e1; border: 1px solid rgba(255,255,255,0.08);">1 Pt per ₹</span>
                            <input type="number" class="form-control s-input" id="smriti-edt-earning-ratio" value="${earning_amt.toFixed(0)}">
                        </div>
                        <small class="text-muted">E.g., enter 10 to give 1 Pt per ₹10 spent</small>
                    </div>
                </div>

                <div class="row" style="margin-top: 20px;">
                    <div class="col-md-12">
                        <button class="btn btn-success btn-block btn-checkout-save" id="smriti-btn-save-scheme">
                            <span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px; color: white;">save</span> Save Scheme
                        </button>
                    </div>
                </div>
            </div>
        `);

        var me = this;
        $("#smriti-btn-save-scheme").off("click").on("click", function() {
            me.save_scheme_action();
        });
    }

    save_scheme_action() {
        var me = this;
        const name = $("#smriti-edt-name").val().trim();
        const conversion = flt($("#smriti-edt-conversion").val());
        const auto = $("#smriti-edt-auto").is(":checked") ? 1 : 0;
        const tier = $("#smriti-edt-tier").val().trim() || "Regular";
        const ratio = flt($("#smriti-edt-earning-ratio").val()) || 10.0;
        const collection_factor = ratio > 0 ? (1 / ratio) : 0.1;

        if (!name) {
            frappe.show_alert({message: "Scheme Name is required.", indicator: 'red'});
            return;
        }

        frappe.call({
            method: "smriti_retail_os.loyalty_api.save_loyalty_scheme",
            args: {
                doc_name: me.active_scheme.name.startsWith("new-") ? null : me.active_scheme.name,
                loyalty_program_name: name,
                conversion_factor: conversion,
                auto_opt_in: auto,
                tier_name: tier,
                min_spent: 0,
                collection_factor: collection_factor
            },
            freeze: true,
            freeze_message: "Saving Loyalty Scheme...",
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.show_alert({message: r.message.message, indicator: 'green'});
                    me.active_scheme = null;
                    me.load_schemes();
                    $("#smriti-scheme-editor").html(`
                        <div class="empty-state" style="padding: 60px 20px;">
                            <span class="empty-icon" style="color: #64748b;"><span class="material-symbols-outlined">done_all</span></span>
                            <span class="empty-text">Saved Successfully! Select a scheme from the left to view.</span>
                        </div>
                    `);
                }
            }
        });
    }

    bind_actions() {
        var me = this;
        
        // F2: Focus Customer Search or clear
        $(document).off("keydown").on("keydown", function(e) {
            if (e.keyCode === 113) { // F2
                e.preventDefault();
                $("#smriti-cust-search-input").focus().select();
            } else if (e.keyCode === 27) { // ESC
                e.preventDefault();
                $("#smriti-cust-search-input").val("").blur();
                me.render_search_results([]);
            }
        });

        // Search Input change
        $("#smriti-cust-search-input").off("input").on("input", function() {
            const val = $(this).val().trim();
            if (val.length >= 3) {
                me.search_customers(val);
            } else {
                me.render_search_results([]);
            }
        });

        // New Scheme button
        $("#smriti-btn-new-scheme").off("click").on("click", function() {
            me.active_scheme = {
                name: "new-" + frappe.utils.get_random(5),
                loyalty_program_name: "New Loyalty Program",
                conversion_factor: 1.0,
                auto_opt_in: 1,
                collection_rules: [{ tier_name: "Regular", min_spent: 0, collection_factor: 0.1 }]
            };
            me.render_schemes_list();
            me.render_editor();
        });
    }

    search_customers(query) {
        var me = this;
        frappe.call({
            method: "smriti_retail_os.billing_api.search_customer",
            args: { query: query },
            callback: function(r) {
                me.render_search_results(r.message || []);
            }
        });
    }

    render_search_results(cust_list) {
        const results_div = $("#smriti-cust-results");
        results_div.empty();

        if (cust_list.length === 0) {
            results_div.html(`
                <div class="empty-state" style="padding: 40px 10px;">
                    <span class="empty-icon" style="font-size: 32px;"><span class="material-symbols-outlined">group_off</span></span>
                    <span class="empty-text">No matching customers found.</span>
                </div>
            `);
            return;
        }

        var me = this;
        
        let select_opts = `<option value="">-- Choose Program --</option>`;
        this.schemes.forEach(sc => {
            select_opts += `<option value="${sc.name}">${sc.loyalty_program_name}</option>`;
        });

        cust_list.forEach(cust => {
            const prog = cust.loyalty_program || '<span style="color: #ef4444;">Not Enrolled</span>';
            
            results_div.append(`
                <div class="customer-enroll-row" data-id="${cust.name}">
                    <div class="cust-info">
                        <span class="cust-row-name">${cust.customer_name}</span>
                        <span class="cust-row-detail">Mobile: ${cust.primary_mobile_no || '-'} | Program: <b>${prog}</b></span>
                    </div>
                    <div class="cust-actions">
                        <select class="form-control s-input select-enroll-prog" style="max-width: 140px; font-size:11px; padding: 2px 4px; display:inline-block; height: 26px; vertical-align:middle;">
                            ${select_opts}
                        </select>
                        <button class="btn btn-xs btn-primary btn-enroll-action" style="height: 26px; padding: 2px 8px; margin-left:4px; vertical-align:middle;">Enroll</button>
                    </div>
                </div>
            `);
        });

        // Binds
        results_div.find(".btn-enroll-action").off("click").on("click", function() {
            const row = $(this).closest(".customer-enroll-row");
            const customer = row.data("id");
            const program = row.find(".select-enroll-prog").val();

            if (!program) {
                frappe.show_alert({message: "Please select a loyalty program.", indicator: 'red'});
                return;
            }

            frappe.call({
                method: "smriti_retail_os.loyalty_api.enroll_customer",
                args: {
                    customer: customer,
                    program_name: program
                },
                freeze: true,
                freeze_message: "Enrolling Customer...",
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({message: r.message.message, indicator: 'green'});
                        // Re-trigger search to show updated status
                        const query = $("#smriti-cust-search-input").val().trim();
                        if (query) me.search_customers(query);
                    }
                }
            });
        });
    }
}
