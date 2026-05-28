/**
 * @file: smriti_retail_os/public/js/smriti_purchase.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

/* ============================================================
   SMRITI Retail OS — Purchase Management Page Controller
   ============================================================ */

frappe.pages['smriti-purchase'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'SMRITI Purchase Management',
        single_column: true
    });
    window.smriti_purchase = new SmritiPurchasePage(wrapper);
};

class SmritiPurchasePage {
    constructor(wrapper) {
        this.wrapper = $(wrapper);
        
        // Roles & Permissions
        this.user = frappe.session.user;
        this.roles = frappe.user_roles || [];
        this.is_manager = this.roles.includes("SMRITI Store Manager") || this.roles.includes("System Manager") || this.user === "Administrator";
        
        // State variables
        this.active_tab = "po"; // po, grn
        this.states = {
            po: {
                supplier: "",
                items: []
            },
            grn: {
                purchase_mode: "direct", // direct, against_po
                supplier: "",
                po_name: "",
                items: []
            }
        };

        // Cache lists
        this.suppliers = [];
        this.warehouses = [];
        this.open_pos = []; // Filtered open POs for selected supplier

        this.init();
    }

    init() {
        var me = this;
        me.fetch_masters(() => {
            me.setup_layout();
            me.bind_tab_switching();
            me.bind_keyboard_shortcuts();
            me.bind_actions();
            me.render_active_tab_contents();
            me.focus_active_barcode();
        });
    }

    fetch_masters(callback) {
        var me = this;
        // 1. Fetch Suppliers
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Supplier",
                filters: { disabled: 0 },
                fields: ["name", "supplier_name"],
                limit_page_length: 200
            },
            callback: function(r) {
                if (r.message) {
                    me.suppliers = r.message;
                }
                
                // 2. Fetch Warehouses
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Warehouse",
                        filters: { disabled: 0, is_group: 0 },
                        fields: ["name"],
                        limit_page_length: 200
                    },
                    callback: function(res) {
                        if (res.message) {
                            me.warehouses = res.message;
                        }
                        if (callback) callback();
                    }
                });
            }
        });
    }

    setup_layout() {
        const role_badge = this.is_manager 
            ? `<span class="smriti-badge badge-mgr"><span class="material-symbols-outlined" style="font-size: 14px; margin-right: 4px; color: white;">admin_panel_settings</span>Store Manager</span>` 
            : `<span class="smriti-badge badge-csh"><span class="material-symbols-outlined" style="font-size: 14px; margin-right: 4px; color: #475467;">visibility</span>Cashier (Read Only)</span>`;

        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-purchase-container dark-mode">
                <!-- Top Navbar: Tabs selector and role indicators -->
                <div class="smriti-top-nav">
                    <div class="smriti-tabs-bar">
                        <button class="smriti-tab-btn active" data-tab="po"><span class="material-symbols-outlined" style="margin-right: 6px;">list_alt</span>${__('Purchase Order (PO)')}</button>
                        <button class="smriti-tab-btn" data-tab="grn"><span class="material-symbols-outlined" style="margin-right: 6px;">shopping_cart</span>${__('Purchase Entry (GRN)')}</button>
                    </div>
                    <div class="smriti-status-indicators">
                        <span class="user-label">User: <b>${this.user}</b></span>
                        ${role_badge}
                    </div>
                </div>

                <!-- Active Area -->
                <div class="smriti-grid">
                    <!-- Left Section: Scanner + Dynamic forms + Grid table -->
                    <div class="smriti-main-panel">
                        <!-- Dynamic Header Fields per Tab -->
                        <div class="smriti-header-fields-card" id="smriti-pur-header-fields">
                            <!-- Injected dynamically -->
                        </div>

                        <!-- Barcode Field -->
                        <div class="barcode-wrapper" id="smriti-pur-barcode-wrapper">
                            <div class="barcode-input-container">
                                <span class="scanner-icon"><span class="material-symbols-outlined">barcode_scanner</span></span>
                                <input type="text" id="smriti-pur-barcode-input" autocomplete="off" placeholder="${__('Scan Barcode or Type Code...')}">
                            </div>
                        </div>

                        <!-- Grid Table -->
                        <div class="billing-table-wrapper">
                            <table class="table table-bordered table-hover" id="smriti-pur-table">
                                <thead id="smriti-pur-table-head">
                                    <!-- Dynamic headers -->
                                </thead>
                                <tbody id="smriti-pur-table-body">
                                    <!-- Dynamic rows -->
                                </tbody>
                            </table>
                            <div class="empty-state" id="smriti-pur-empty-msg">
                                <span class="empty-icon"><span class="material-symbols-outlined">shopping_bag</span></span>
                                <span class="empty-text">${__('No Scanned Items. Begin scanning, select a PO, or press F2 to search catalog.')}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Right Section: Totals & Commit Action -->
                    <div class="smriti-side-panel">
                        <!-- Quick Summary Card -->
                        <div class="summary-card">
                            <div class="summary-header"><span class="material-symbols-outlined" style="margin-right: 6px;">receipt</span> ${__('Purchase Summary')}</div>
                            <div class="summary-row">
                                <span class="summary-label">${__('Total Lines')}:</span>
                                <span class="summary-val" id="smriti-pur-stat-lines">0</span>
                            </div>
                            <div class="summary-row">
                                <span class="summary-label">${__('Total Items')}:</span>
                                <span class="summary-val" id="smriti-pur-stat-qty">0</span>
                            </div>
                            <hr style="border-top: 1px solid var(--smriti-glass-border); margin: 8px 0;">
                            <div class="summary-row">
                                <span class="summary-label">${__('Total Value')}:</span>
                                <span class="summary-val highlight" id="smriti-pur-stat-total">₹0.00</span>
                            </div>
                        </div>

                        <!-- Help Instructions -->
                        <div class="summary-card">
                            <div class="summary-header"><span class="material-symbols-outlined" style="margin-right: 6px;">keyboard</span> ${__('Keyboard Shortcuts')}</div>
                            <div class="summary-row"><span><b>F2</b>: Search Catalog</span></div>
                            <div class="summary-row"><span><b>F9</b>: Commit Transaction</span></div>
                            <div class="summary-row"><span><b>ESC</b>: Focus barcode / Clear</span></div>
                        </div>

                        <!-- Main Submit Button -->
                        <div class="payment-drawer-card">
                            <button class="btn btn-success btn-block btn-checkout-save" id="smriti-pur-btn-submit" ${!this.is_manager ? 'disabled' : ''}>
                                <span class="material-symbols-outlined" style="color: white; margin-right: 4px;">send</span> F9: ${__('Commit Purchase')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_tab_switching() {
        var me = this;
        this.wrapper.find(".smriti-tab-btn").off("click").on("click", function() {
            const btn = $(this);
            me.wrapper.find(".smriti-tab-btn").removeClass("active");
            btn.addClass("active");
            
            me.active_tab = btn.data("tab");
            me.render_active_tab_contents();
            me.focus_active_barcode();
        });
    }

    bind_keyboard_shortcuts() {
        var me = this;
        $(document).off("keydown").on("keydown", function(e) {
            // F2: Catalog Search
            if (e.keyCode === 113) { 
                e.preventDefault();
                me.trigger_catalog_search();
            }
            // F9: Commit Transaction
            else if (e.keyCode === 120) {
                e.preventDefault();
                me.commit_transaction();
            }
            // ESC: Focus barcode input or clear
            else if (e.keyCode === 27) {
                e.preventDefault();
                me.focus_active_barcode();
            }
            else {
                if (!$(e.target).is('input, textarea, select, button')) {
                    me.focus_active_barcode();
                }
            }
        });

        $(this.wrapper).off("keypress", "#smriti-pur-barcode-input").on("keypress", "#smriti-pur-barcode-input", function(e) {
            if (e.which === 13) { 
                const val = $(this).val().trim();
                if (val) {
                    me.process_barcode_scan(val);
                    $(this).val(""); 
                }
            }
        });
    }

    bind_actions() {
        var me = this;
        $("#smriti-pur-btn-submit").off("click").on("click", () => me.commit_transaction());
    }

    focus_active_barcode() {
        $("#smriti-pur-barcode-input").focus();
    }

    render_active_tab_contents() {
        this.render_header_fields();
        this.render_table_headers();
        this.render_grid_rows();
        this.update_summary_stats();
    }

    render_header_fields() {
        const header_fields = $("#smriti-pur-header-fields");
        header_fields.empty();
        
        const state = this.states[this.active_tab];
        let supplier_opts = `<option value="">-- Select Supplier --</option>`;
        this.suppliers.forEach(s => {
            supplier_opts += `<option value="${s.name}" ${state.supplier === s.name ? 'selected' : ''}>${s.supplier_name}</option>`;
        });

        if (this.active_tab === "po") {
            // Purchase Order form header
            header_fields.html(`
                <div class="row">
                    <div class="col-sm-12">
                        <label class="s-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">person</span> Supplier</label>
                        <select class="form-control s-input" id="smriti-hdr-supplier">${supplier_opts}</select>
                    </div>
                </div>
            `);

            // Bind values to state
            var me = this;
            $("#smriti-hdr-supplier").on("change", function() {
                me.states.po.supplier = $(this).val();
            });

            // Show barcode scanner for PO creation
            $("#smriti-pur-barcode-wrapper").show();

        } else if (this.active_tab === "grn") {
            // Purchase Entry Form Header
            const mode = state.purchase_mode;
            const is_direct = mode === "direct";
            
            let po_opts = `<option value="">-- Select Purchase Order --</option>`;
            this.open_pos.forEach(po => {
                po_opts += `<option value="${po.name}" ${state.po_name === po.name ? 'selected' : ''}>${po.name} (Total: ₹${parseFloat(po.grand_total).toFixed(2)})</option>`;
            });

            header_fields.html(`
                <div class="pur-toggle-container">
                    <button class="pur-toggle-btn ${is_direct ? 'active' : ''}" data-mode="direct">Direct Purchase (No PO)</button>
                    <button class="pur-toggle-btn ${!is_direct ? 'active' : ''}" data-mode="against_po">Against Purchase Order</button>
                </div>
                <div class="row">
                    <div class="col-sm-6">
                        <label class="s-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">person</span> Supplier</label>
                        <select class="form-control s-input" id="smriti-hdr-supplier">${supplier_opts}</select>
                    </div>
                    <div class="col-sm-6" id="po-select-wrapper" style="display: ${is_direct ? 'none' : 'block'};">
                        <label class="s-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">link</span> Open Purchase Order</label>
                        <select class="form-control s-input" id="smriti-hdr-po">${po_opts}</select>
                    </div>
                </div>
            `);

            // Hide barcode scanner if in PO mode (or keep it as fallback)
            if (is_direct) {
                $("#smriti-pur-barcode-wrapper").show();
            } else {
                $("#smriti-pur-barcode-wrapper").hide();
            }

            var me = this;
            // Bind Mode switcher buttons
            header_fields.find(".pur-toggle-btn").on("click", function() {
                const target_mode = $(this).data("mode");
                me.states.grn.purchase_mode = target_mode;
                
                // Clear state item list when switching modes
                me.states.grn.items = [];
                me.states.grn.po_name = "";
                me.render_active_tab_contents();
            });

            $("#smriti-hdr-supplier").on("change", function() {
                const supplier = $(this).val();
                me.states.grn.supplier = supplier;
                me.states.grn.po_name = "";
                me.states.grn.items = [];

                if (supplier && mode === "against_po") {
                    me.load_open_pos_for_supplier(supplier);
                } else {
                    me.open_pos = [];
                    me.render_active_tab_contents();
                }
            });

            $("#smriti-hdr-po").on("change", function() {
                const po_name = $(this).val();
                me.states.grn.po_name = po_name;
                if (po_name) {
                    me.load_po_details_to_grid(po_name);
                } else {
                    me.states.grn.items = [];
                    me.render_active_tab_contents();
                }
            });
        }
    }

    load_open_pos_for_supplier(supplier) {
        var me = this;
        frappe.call({
            method: "smriti_retail_os.purchase_api.get_open_purchase_orders",
            args: { supplier: supplier },
            callback: function(r) {
                me.open_pos = r.message || [];
                me.render_active_tab_contents();
            }
        });
    }

    load_po_details_to_grid(po_name) {
        var me = this;
        frappe.call({
            method: "smriti_retail_os.purchase_api.get_po_details",
            args: { po_name: po_name },
            freeze: true,
            freeze_message: __("Loading PO Items..."),
            callback: function(r) {
                if (r.message) {
                    me.states.grn.items = r.message.items || [];
                    me.render_active_tab_contents();
                }
            }
        });
    }

    render_table_headers() {
        const thead = $("#smriti-pur-table-head");
        thead.empty();

        if (this.active_tab === "po") {
            thead.html(`
                <tr>
                    <th style="width: 5%">#</th>
                    <th style="width: 45%">Item Details</th>
                    <th style="width: 15%">Qty</th>
                    <th style="width: 15%">Rate (INR)</th>
                    <th style="width: 17%">Total (INR)</th>
                    <th style="width: 3%"></th>
                </tr>
            `);
        } else if (this.active_tab === "grn") {
            thead.html(`
                <tr>
                    <th style="width: 5%">#</th>
                    <th style="width: 35%">Item Details</th>
                    <th style="width: 15%">Expiry / Batch</th>
                    <th style="width: 13%">Qty</th>
                    <th style="width: 14%">Rate (INR)</th>
                    <th style="width: 15%">Total (INR)</th>
                    <th style="width: 3%"></th>
                </tr>
            `);
        }
    }

    render_grid_rows() {
        var me = this;
        var tbody = $("#smriti-pur-table-body");
        tbody.empty();

        const state = this.states[this.active_tab];
        if (state.items.length === 0) {
            $("#smriti-pur-empty-msg").show();
            return;
        }
        $("#smriti-pur-empty-msg").hide();

        state.items.forEach((it, idx) => {
            const total = it.qty * it.rate;

            if (this.active_tab === "po") {
                tbody.append(`
                    <tr data-idx="${idx}">
                        <td>${idx + 1}</td>
                        <td><b>${it.item_code}</b><br><small class="text-muted">${it.item_name}</small></td>
                        <td><input type="number" class="grid-qty-input form-control text-center" value="${it.qty}" min="1"></td>
                        <td><input type="number" class="grid-rate-input form-control text-right" value="${it.rate}" min="0.01"></td>
                        <td class="text-right font-weight-bold text-teal">INR ${total.toFixed(2)}</td>
                        <td class="text-center"><button class="btn btn-xs btn-danger btn-remove-row">✕</button></td>
                    </tr>
                `);
            } else if (this.active_tab === "grn") {
                const date_picker = it.has_batch_no 
                    ? `<input type="date" class="grid-expiry-input form-control" value="${it.expiry_date || ''}">` 
                    : `<span class="text-muted">No Batch</span>`;

                tbody.append(`
                    <tr data-idx="${idx}">
                        <td>${idx + 1}</td>
                        <td>
                            <b>${it.item_code}</b><br><small class="text-muted">${it.item_name}</small>
                            ${it.po_qty ? `<br><small class="text-info">PO: ${it.po_qty} | Received: ${it.received_qty}</small>` : ''}
                        </td>
                        <td>${date_picker}</td>
                        <td><input type="number" class="grid-qty-input form-control text-center" value="${it.qty}" min="0.01"></td>
                        <td><input type="number" class="grid-rate-input form-control text-right" value="${it.rate}" min="0.01"></td>
                        <td class="text-right font-weight-bold text-teal">INR ${total.toFixed(2)}</td>
                        <td class="text-center">
                            <!-- If against PO, do not allow removing items, only set Qty to 0 if not received -->
                            ${state.purchase_mode === 'against_po' ? '' : '<button class="btn btn-xs btn-danger btn-remove-row">✕</button>'}
                        </td>
                    </tr>
                `);
            }
        });

        // Binds
        tbody.find(".grid-qty-input").off("change").on("change", function() {
            const idx = $(this).closest("tr").data("idx");
            state.items[idx].qty = flt($(this).val());
            me.render_grid_rows();
            me.update_summary_stats();
        });

        tbody.find(".grid-rate-input").off("change").on("change", function() {
            const idx = $(this).closest("tr").data("idx");
            state.items[idx].rate = flt($(this).val());
            me.render_grid_rows();
            me.update_summary_stats();
        });

        tbody.find(".grid-expiry-input").off("change").on("change", function() {
            const idx = $(this).closest("tr").data("idx");
            state.items[idx].expiry_date = $(this).val();
        });

        tbody.find(".btn-remove-row").off("click").on("click", function() {
            const idx = $(this).closest("tr").data("idx");
            state.items.splice(idx, 1);
            me.render_grid_rows();
            me.update_summary_stats();
        });
    }

    process_barcode_scan(barcode) {
        var me = this;
        frappe.call({
            method: "smriti_retail_os.inventory_api.scan_item_for_inventory",
            args: { barcode: barcode },
            callback: function(r) {
                if (r.message) {
                    me.add_scanned_item_to_grid(r.message);
                } else {
                    frappe.show_alert({message: __("Barcode not found in catalog."), indicator: 'red'});
                }
            }
        });
    }

    add_scanned_item_to_grid(item) {
        const state = this.states[this.active_tab];
        const existing = state.items.find(i => i.item_code === item.item_code);
        
        if (existing) {
            existing.qty += 1;
        } else {
            const new_item = {
                item_code: item.item_code,
                item_name: item.item_name,
                stock_uom: item.stock_uom,
                qty: 1,
                rate: item.rate,
                has_batch_no: item.has_batch_no,
                expiry_date: ""
            };
            state.items.push(new_item);
        }
        this.render_grid_rows();
        this.update_summary_stats();
    }

    update_summary_stats() {
        const state = this.states[this.active_tab];
        const lines = state.items.length;
        const total_qty = state.items.reduce((sum, i) => sum + i.qty, 0);
        const total_val = state.items.reduce((sum, i) => sum + (i.qty * i.rate), 0);

        $("#smriti-pur-stat-lines").text(lines);
        $("#smriti-pur-stat-qty").text(total_qty);
        $("#smriti-pur-stat-total").text('₹' + total_val.toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }));
    }

    trigger_catalog_search() {
        var me = this;
        // Do not allow adding manual items if we are in PO mode and Against PO is selected
        if (this.active_tab === "grn" && this.states.grn.purchase_mode === "against_po") {
            frappe.show_alert({message: __("Cannot manually add items in Against PO mode. Adjust quantities in grid."), indicator: 'orange'});
            return;
        }

        var dialog = new frappe.ui.Dialog({
            title: __('F2: Item Catalog Lookup'),
            fields: [
                {
                    label: __('Search Item'),
                    fieldname: 'query',
                    fieldtype: 'Data',
                    reqd: 1
                },
                {
                    fieldname: 'results_html',
                    fieldtype: 'HTML'
                }
            ]
        });

        dialog.fields_dict.query.$wrapper.find("input").on("input", function() {
            const val = $(this).val().trim();
            if (val.length >= 2) {
                frappe.call({
                    method: "smriti_retail_os.billing_api.search_items",
                    args: { query: val },
                    callback: function(r) {
                        if (r.message && r.message.length > 0) {
                            let rows_html = `<table class="table table-bordered table-condensed table-hover"><thead><tr><th>Code</th><th>Name</th><th>Brand</th><th>Rate</th><th></th></tr></thead><tbody>`;
                            r.message.forEach(it => {
                                rows_html += `
                                    <tr>
                                        <td><b>${it.item_code}</b></td>
                                        <td>${it.item_name}</td>
                                        <td>${it.brand || '-'}</td>
                                        <td>INR ${it.rate}</td>
                                        <td>
                                            <button class="btn btn-xs btn-primary btn-select-pur-item" data-code="${it.item_code}">Add</button>
                                        </td>
                                    </tr>
                                `;
                            });
                            rows_html += `</tbody></table>`;
                            dialog.fields_dict.results_html.$wrapper.html(rows_html);

                            dialog.$wrapper.find(".btn-select-pur-item").off("click").on("click", function() {
                                const code = $(this).data("code");
                                const found = r.message.find(i => i.item_code === code);
                                
                                frappe.call({
                                    method: "smriti_retail_os.inventory_api.scan_item_for_inventory",
                                    args: { barcode: found.item_code },
                                    callback: function(res) {
                                        if (res.message) {
                                            me.add_scanned_item_to_grid(res.message);
                                        }
                                        dialog.hide();
                                    }
                                });
                            });
                        } else {
                            dialog.fields_dict.results_html.$wrapper.html(`<span class="text-muted">No items found.</span>`);
                        }
                    }
                });
            }
        });

        dialog.show();
    }

    commit_transaction() {
        var me = this;
        
        if (!this.is_manager) {
            frappe.msgprint({
                title: __('Access Denied'),
                message: __('Only Store Managers or System Managers are authorized to commit purchase transactions.'),
                indicator: 'red'
            });
            return;
        }

        const state = this.states[this.active_tab];
        if (state.items.length === 0) {
            frappe.show_alert({message: __("Purchase item list is empty."), indicator: 'red'});
            return;
        }

        if (!state.supplier) {
            frappe.show_alert({message: __("Please select a Supplier."), indicator: 'red'});
            return;
        }

        if (this.active_tab === "po") {
            // Create Purchase Order
            frappe.call({
                method: "smriti_retail_os.purchase_api.create_purchase_order",
                args: {
                    supplier: state.supplier,
                    items: JSON.stringify(state.items)
                },
                freeze: true,
                freeze_message: __("Submitting Purchase Order..."),
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('PO Created Successfully'),
                            message: r.message.message,
                            indicator: 'green'
                        });
                        me.clear_active_tab_state();
                    }
                }
            });

        } else if (this.active_tab === "grn") {
            if (state.purchase_mode === "against_po" && !state.po_name) {
                frappe.show_alert({message: __("Please select an open Purchase Order."), indicator: 'red'});
                return;
            }

            // Check for missing batch expiry dates
            const missing_expiry = state.items.some(i => i.has_batch_no && !i.expiry_date && i.qty > 0);
            if (missing_expiry) {
                frappe.msgprint({
                    title: __('Missing Batch Expiry'),
                    message: __('One or more batch-tracked items is missing an Expiry Date. Please select valid dates in the grid before submitting.'),
                    indicator: 'orange'
                });
                return;
            }

            // Filter out items with 0 qty to receive
            const active_items = state.items.filter(i => i.qty > 0);
            if (active_items.length === 0) {
                frappe.show_alert({message: __("Quantity to receive must be greater than zero for at least one item."), indicator: 'red'});
                return;
            }

            frappe.call({
                method: "smriti_retail_os.purchase_api.create_purchase_receipt",
                args: {
                    supplier: state.supplier,
                    items: JSON.stringify(active_items),
                    po_name: state.purchase_mode === "against_po" ? state.po_name : null
                },
                freeze: true,
                freeze_message: __("Submitting Purchase Receipt..."),
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Purchase Submitted Successfully'),
                            message: r.message.message,
                            indicator: 'green'
                        });
                        me.clear_active_tab_state();
                    }
                }
            });
        }
    }

    clear_active_tab_state() {
        const state = this.states[this.active_tab];
        state.items = [];
        state.supplier = "";
        
        if (this.active_tab === "grn") {
            state.po_name = "";
            this.open_pos = [];
        }

        $("#smriti-hdr-supplier").val("");
        this.render_active_tab_contents();
        this.focus_active_barcode();
    }
}
