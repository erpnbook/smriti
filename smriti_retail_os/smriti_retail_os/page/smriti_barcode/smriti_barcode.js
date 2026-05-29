/**
 * @file: smriti_retail_os/page/smriti-barcode/smriti-barcode.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */

frappe.pages['smriti-barcode'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Barcode Printing'),
        single_column: true
    });

    if (window.SMRITI && typeof SMRITI.renderSidebar === 'function') {
        SMRITI.renderSidebar("barcode");
    }

    var smriti_barcode = new SmritiBarcodeController(wrapper, page);
}

class SmritiBarcodeController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;

        // Controller state
        this.active_mode = "transaction"; // transaction or manual
        this.items = [];
        this.filters_cache = {
            brands: [],
            categories: [],
            sizes: []
        };

        this.selected_label_size = "50x25";

        this.init();
    }

    init() {
        var me = this;
        me.fetch_filters(() => {
            me.setup_layout();
            me.bind_mode_switching();
            me.bind_keyboard_shortcuts();
            me.bind_actions();
            me.render_mode_contents();
        });
    }

    fetch_filters(callback) {
        var me = this;
        frappe.call({
            method: "smriti_retail_os.barcode_api.get_barcode_filters",
            callback: function(r) {
                if (r.message) {
                    me.filters_cache = r.message;
                }
                if (callback) callback();
            }
        });
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-barcode-container dark-mode">
                <!-- Top Navbar: Mode selectors and shortcuts hint -->
                <div class="smriti-top-nav">
                    <div class="smriti-mode-selector">
                        <button class="smriti-mode-btn active" data-mode="transaction">📂 ${__('Transaction-Based')}</button>
                        <button class="smriti-mode-btn" data-mode="manual">🔍 ${__('Manual Bulk Selection')}</button>
                    </div>
                    <div class="smriti-shortcuts-hint">
                        <span><b>F2</b> Item Lookup | <b>F9</b> Print | <b>ESC</b> Focus</span>
                    </div>
                </div>

                <!-- Main Area split: inputs on left, preview on right -->
                <div class="smriti-grid">
                    <!-- Left Section: Forms & Item grids -->
                    <div class="smriti-main-panel">
                        <!-- Mode-specific settings card -->
                        <div class="smriti-header-fields-card" id="smriti-mode-settings-card">
                            <!-- Injected dynamically -->
                        </div>

                        <!-- Scanned/Loaded Items Grid -->
                        <div class="billing-table-wrapper" style="max-height: 400px; min-height: 220px;">
                            <table class="table table-bordered table-hover" id="smriti-barcode-table">
                                <thead id="smriti-barcode-table-head">
                                    <!-- Injected dynamically -->
                                </thead>
                                <tbody id="smriti-barcode-table-body">
                                    <!-- Injected dynamically -->
                                </tbody>
                            </table>
                            <div class="empty-state" id="smriti-barcode-empty-msg">
                                <span class="empty-icon">🖨️</span>
                                <span class="empty-text">${__('No items loaded. Load a transaction or apply manual filters above.')}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Right Section: Label preview & bottom print actions -->
                    <div class="smriti-side-panel">
                        <!-- Label Preview Card -->
                        <div class="summary-card">
                            <div class="summary-header">👁️ ${__('Label Preview Simulation')}</div>
                            <div class="smriti-label-preview-wrapper">
                                <div class="smriti-simulated-label" id="smriti-barcode-preview-box">
                                    <div class="sim-brand" id="sim-lbl-brand">BRAND</div>
                                    <div class="sim-name" id="sim-lbl-name">Select an item below to preview</div>
                                    <div class="sim-barcode" id="sim-lbl-barcode">1234567890123</div>
                                    <div class="sim-mrp" id="sim-lbl-mrp">MRP: Rs. 0.00</div>
                                    <div class="sim-details" id="sim-lbl-details">SIZE: L</div>
                                </div>
                            </div>
                        </div>

                        <!-- Printing Actions and variables -->
                        <div class="payment-drawer-card">
                            <div class="payment-drawer-header">⚙️ ${__('Printing Settings')}</div>
                            
                            <div class="summary-row" style="margin-bottom: 8px;">
                                <label class="s-label" style="display:inline-block; margin-bottom:0; line-height:30px;">📏 Label Size:</label>
                                <select class="form-control s-input" id="smriti-print-label-size" style="max-width: 140px; display:inline-block;">
                                    <option value="50x25">50 x 25 mm</option>
                                    <option value="50x30">50 x 30 mm</option>
                                    <option value="75x50">75 x 50 mm</option>
                                    <option value="100x50">100 x 50 mm</option>
                                    <option value="106x55">106.6 x 55.4 mm (TSPL)</option>
                                </select>
                            </div>

                            <div class="summary-divider"></div>
                            
                            <div class="summary-row">
                                <span class="summary-label">${__('Selected Lines')}:</span>
                                <span class="summary-val text-teal" id="smriti-lbl-stat-items">0 items</span>
                            </div>
                            <div class="summary-row">
                                <span class="summary-label">${__('Total Labels to Print')}:</span>
                                <span class="summary-val highlight" id="smriti-lbl-stat-labels">0</span>
                            </div>

                            <div class="summary-divider"></div>

                            <div class="row">
                                <div class="col-sm-6">
                                    <button class="btn btn-secondary btn-block" id="smriti-btn-preview-prn">📄 ${__('Preview ZPL')}</button>
                                </div>
                                <div class="col-sm-6">
                                    <button class="btn btn-success btn-block btn-checkout-save" id="smriti-btn-print-labels">🖨️ F9: ${__('Print')}</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_mode_switching() {
        var me = this;
        this.wrapper.find(".smriti-mode-btn").off("click").on("click", function() {
            const btn = $(this);
            me.wrapper.find(".smriti-mode-btn").removeClass("active");
            btn.addClass("active");

            me.active_mode = btn.data("mode");
            me.items = []; // Reset on mode switch
            me.render_mode_contents();
        });
    }

    bind_keyboard_shortcuts() {
        var me = this;
        $(document).off("keydown").on("keydown", function(e) {
            // F2: Item Search catalog lookup
            if (e.keyCode === 113) {
                e.preventDefault();
                me.trigger_catalog_lookup();
            }
            // F9: Print Labels
            else if (e.keyCode === 120) {
                e.preventDefault();
                me.trigger_print();
            }
            // ESC: Focus search/inputs
            else if (e.keyCode === 27) {
                e.preventDefault();
                $("#smriti-hdr-search").focus();
            }
        });
    }

    bind_actions() {
        var me = this;
        $("#smriti-print-label-size").off("change").on("change", function() {
            me.selected_label_size = $(this).val();
            // Update preview box size dynamically
            const sim = $("#smriti-barcode-preview-box");
            sim.removeClass("sz-50x25 sz-50x30 sz-75x50 sz-100x50 sz-106x55").addClass("sz-" + me.selected_label_size);
        });

        $("#smriti-btn-preview-prn").off("click").on("click", () => me.trigger_prn_preview_code());
        $("#smriti-btn-print-labels").off("click").on("click", () => me.trigger_print());
    }

    render_mode_contents() {
        this.render_mode_settings();
        this.render_table_headers();
        this.render_grid_rows();
        this.update_summary();
    }

    render_mode_settings() {
        const card = $("#smriti-mode-settings-card");
        card.empty();
        var me = this;

        if (this.active_mode === "transaction") {
            card.html(`
                <div class="row align-items-end">
                    <div class="col-sm-4">
                        <label class="s-label">📄 Document Type</label>
                        <select class="form-control s-input" id="smriti-hdr-doctype">
                            <option value="Purchase Receipt">Purchase Receipt</option>
                            <option value="Stock Entry">Stock Entry</option>
                        </select>
                    </div>
                    <div class="col-sm-5">
                        <label class="s-label">🎫 Document Name / Reference</label>
                        <input type="text" class="form-control s-input" id="smriti-hdr-docname" placeholder="Search reference number...">
                    </div>
                    <div class="col-sm-3">
                        <button class="btn btn-primary btn-block" id="smriti-btn-load-txn" style="height: auto; padding: 10px 0;">⚡ Load Items</button>
                    </div>
                </div>
            `);

            // Attach dynamic doc lookup / standard autocomplete if required
            // For now, load on load button click
            $("#smriti-btn-load-txn").off("click").on("click", () => me.load_transaction_items());

        } else if (this.active_mode === "manual") {
            let brand_opts = `<option value="">-- All Brands --</option>`;
            this.filters_cache.brands.forEach(b => {
                brand_opts += `<option value="${b}">${b}</option>`;
            });

            let group_opts = `<option value="">-- All Categories --</option>`;
            this.filters_cache.categories.forEach(c => {
                group_opts += `<option value="${c}">${c}</option>`;
            });

            let size_opts = `<option value="">-- All Sizes --</option>`;
            this.filters_cache.sizes.forEach(s => {
                size_opts += `<option value="${s}">${s}</option>`;
            });

            card.html(`
                <div class="row align-items-end">
                    <div class="col-sm-3">
                        <label class="s-label">🏷️ Brand</label>
                        <select class="form-control s-input" id="smriti-hdr-brand">${brand_opts}</select>
                    </div>
                    <div class="col-sm-3">
                        <label class="s-label">📂 Category</label>
                        <select class="form-control s-input" id="smriti-hdr-group">${group_opts}</select>
                    </div>
                    <div class="col-sm-2">
                        <label class="s-label">📏 Label Size</label>
                        <select class="form-control s-input" id="smriti-hdr-size">${size_opts}</select>
                    </div>
                    <div class="col-sm-2">
                        <label class="s-label">🔎 Search</label>
                        <input type="text" class="form-control s-input" id="smriti-hdr-search" placeholder="Code/Name...">
                    </div>
                    <div class="col-sm-2">
                        <button class="btn btn-primary btn-block" id="smriti-btn-apply-filters" style="height: auto; padding: 10px 0;">Apply</button>
                    </div>
                </div>
            `);

            $("#smriti-btn-apply-filters").off("click").on("click", () => me.load_manual_filtered_items());
        }
    }

    render_table_headers() {
        const thead = $("#smriti-barcode-table-head");
        thead.empty();

        if (this.active_mode === "transaction") {
            thead.html(`
                <tr>
                    <th style="width: 5%">#</th>
                    <th style="width: 20%">Barcode</th>
                    <th style="width: 30%">Item Details</th>
                    <th style="width: 15%">Brand</th>
                    <th style="width: 15%">MRP (INR)</th>
                    <th style="width: 15%">Print Qty</th>
                </tr>
            `);
        } else if (this.active_mode === "manual") {
            thead.html(`
                <tr>
                    <th style="width: 5%">
                        <input type="checkbox" id="smriti-chk-all" checked>
                    </th>
                    <th style="width: 20%">Barcode</th>
                    <th style="width: 25%">Item Details</th>
                    <th style="width: 15%">Brand</th>
                    <th style="width: 12%">MRP (INR)</th>
                    <th style="width: 10%">Size</th>
                    <th style="width: 13%">Print Qty</th>
                </tr>
            `);
        }
    }

    render_grid_rows() {
        var me = this;
        var tbody = $("#smriti-barcode-table-body");
        tbody.empty();

        if (this.items.length === 0) {
            $("#smriti-barcode-empty-msg").show();
            return;
        }
        $("#smriti-barcode-empty-msg").hide();

        this.items.forEach((it, idx) => {
            if (this.active_mode === "transaction") {
                tbody.append(`
                    <tr data-idx="${idx}" class="barcode-row">
                        <td>${idx + 1}</td>
                        <td class="font-weight-bold text-teal">${it.barcode}</td>
                        <td><b>${it.item_code}</b><br><small class="text-muted">${it.item_name}</small></td>
                        <td>${it.brand}</td>
                        <td>INR ${it.mrp.toFixed(2)}</td>
                        <td>
                            <input type="number" class="grid-qty-input form-control text-center" value="${it.print_qty}" min="1" style="max-width: 80px;">
                        </td>
                    </tr>
                `);
            } else if (this.active_mode === "manual") {
                const checked = it.selected !== false ? 'checked' : '';
                tbody.append(`
                    <tr data-idx="${idx}" class="barcode-row">
                        <td class="text-center">
                            <input type="checkbox" class="grid-select-chk" ${checked}>
                        </td>
                        <td class="font-weight-bold text-teal">${it.barcode}</td>
                        <td><b>${it.item_code}</b><br><small class="text-muted">${it.item_name}</small></td>
                        <td>${it.brand}</td>
                        <td>INR ${it.mrp.toFixed(2)}</td>
                        <td><span class="badge badge-secondary">${it.size}</span></td>
                        <td>
                            <input type="number" class="grid-qty-input form-control text-center" value="${it.print_qty}" min="1" style="max-width: 80px;">
                        </td>
                    </tr>
                `);
            }
        });

        // Binds
        tbody.find(".barcode-row").off("click").on("click", function(e) {
            if ($(e.target).is('input, checkbox')) return;
            const idx = $(this).data("idx");
            me.update_preview_sim(me.items[idx]);
        });

        tbody.find(".grid-qty-input").off("change").on("change", function() {
            const idx = $(this).closest("tr").data("idx");
            me.items[idx].print_qty = cint($(this).val());
            me.update_summary();
        });

        tbody.find(".grid-select-chk").off("change").on("change", function() {
            const idx = $(this).closest("tr").data("idx");
            me.items[idx].selected = $(this).prop("checked");
            me.update_summary();
        });

        $("#smriti-chk-all").off("change").on("change", function() {
            const chk = $(this).prop("checked");
            me.items.forEach(i => i.selected = chk);
            tbody.find(".grid-select-chk").prop("checked", chk);
            me.update_summary();
        });

        // Select the first item for preview initially
        me.update_preview_sim(this.items[0]);
    }

    update_preview_sim(item) {
        if (!item) {
            $("#sim-lbl-brand").text("BRAND");
            $("#sim-lbl-name").text("Select an item below to preview");
            $("#sim-lbl-barcode").text("1234567890123");
            $("#sim-lbl-mrp").text("MRP: Rs. 0.00");
            $("#sim-lbl-details").text("SIZE: L");
            return;
        }

        $("#sim-lbl-brand").text(item.brand.toUpperCase());
        $("#sim-lbl-name").text(item.item_name);
        $("#sim-lbl-barcode").text(item.barcode);
        $("#sim-lbl-mrp").text("MRP: Rs. " + item.mrp.toFixed(2));
        $("#sim-lbl-details").text("SIZE: " + item.size + " | " + item.item_code);
    }

    update_summary() {
        const selected_items = this.items.filter(i => this.active_mode === "transaction" || i.selected !== false);
        const lines = selected_items.length;
        const total_labels = selected_items.reduce((sum, i) => sum + i.print_qty, 0);

        $("#smriti-lbl-stat-items").text(lines + " items selected");
        $("#smriti-lbl-stat-labels").text(total_labels);
    }

    load_transaction_items() {
        var me = this;
        const doctype = $("#smriti-hdr-doctype").val();
        const docname = $("#smriti-hdr-docname").val().trim();

        if (!docname) {
            frappe.show_alert({message: __("Please enter Document Name/Reference."), indicator: 'orange'});
            return;
        }

        frappe.call({
            method: "smriti_retail_os.barcode_api.get_items_for_printing",
            args: {
                source_doctype: doctype,
                source_name: docname
            },
            freeze: true,
            freeze_message: __("Loading transaction lines..."),
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    me.items = r.message;
                    me.render_grid_rows();
                    me.update_summary();
                } else {
                    frappe.show_alert({message: __("No transacting items found or document missing."), indicator: 'red'});
                }
            }
        });
    }

    load_manual_filtered_items() {
        var me = this;
        const filters = {
            brand: $("#smriti-hdr-brand").val(),
            item_group: $("#smriti-hdr-group").val(),
            custom_barcode_size: $("#smriti-hdr-size").val(),
            search_text: $("#smriti-hdr-search").val().trim()
        };

        frappe.call({
            method: "smriti_retail_os.barcode_api.get_items_for_printing",
            args: {
                filters: JSON.stringify(filters)
            },
            freeze: true,
            freeze_message: __("Filtering item catalog..."),
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    me.items = r.message.map(i => {
                        i.selected = true; // Auto select in manual mode
                        return i;
                    });
                    me.render_grid_rows();
                    me.update_summary();
                } else {
                    frappe.show_alert({message: __("No matching items found."), indicator: 'orange'});
                }
            }
        });
    }

    trigger_prn_preview_code() {
        const selected = this.items.filter(i => this.active_mode === "transaction" || i.selected !== false);
        if (selected.length === 0) {
            frappe.show_alert({message: __("Please select or load items to print."), indicator: 'orange'});
            return;
        }

        frappe.call({
            method: "smriti_retail_os.barcode_api.generate_prn",
            args: {
                items: JSON.stringify(selected.map(i => {
                    i.label_size = this.selected_label_size;
                    return i;
                }))
            },
            callback: function(r) {
                if (r.message) {
                    frappe.msgprint({
                        title: __('Zebra ZPL / PRN Preview'),
                        message: `<pre style="background:#1f2937; color:#10b981; padding:15px; border-radius:6px; font-family:monospace; max-height:300px; overflow-y:auto;">${r.message}</pre>`,
                        wide: true
                    });
                }
            }
        });
    }

    trigger_print() {
        var me = this;
        const selected = this.items.filter(i => this.active_mode === "transaction" || i.selected !== false);
        if (selected.length === 0) {
            frappe.show_alert({message: __("No items selected for printing."), indicator: 'orange'});
            return;
        }

        frappe.call({
            method: "smriti_retail_os.barcode_api.generate_prn",
            args: {
                items: JSON.stringify(selected.map(i => {
                    i.label_size = me.selected_label_size;
                    return i;
                }))
            },
            freeze: true,
            freeze_message: __("Generating ZPL PRN file..."),
            callback: function(r) {
                if (r.message) {
                    me.download_prn_file(r.message);
                }
            }
        });
    }

    download_prn_file(prn_data) {
        const filename = `smriti_barcodes_${moment().format('YYYYMMDD_HHmmss')}.prn`;
        const blob = new Blob([prn_data], { type: 'text/plain' });
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        link.click();
        
        frappe.show_alert({
            message: __('PRN Barcode file downloaded successfully.'),
            indicator: 'green'
        });
    }

    trigger_catalog_lookup() {
        var me = this;
        var dialog = new frappe.ui.Dialog({
            title: __('F2: Item Catalog Search'),
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
                                            <button class="btn btn-xs btn-primary btn-select-search-print" data-code="${it.item_code}">Add</button>
                                        </td>
                                    </tr>
                                `;
                            });
                            rows_html += `</tbody></table>`;
                            dialog.fields_dict.results_html.$wrapper.html(rows_html);

                            dialog.$wrapper.find(".btn-select-search-print").off("click").on("click", function() {
                                const code = $(this).data("code");
                                const found = r.message.find(i => i.item_code === code);
                                
                                frappe.call({
                                    method: "smriti_retail_os.barcode_api.get_items_for_printing",
                                    args: {
                                        filters: JSON.stringify({ search_text: found.item_code })
                                    },
                                    callback: function(res) {
                                        if (res.message && res.message.length > 0) {
                                            const item_details = res.message[0];
                                            item_details.selected = true;
                                            me.items.push(item_details);
                                            me.render_grid_rows();
                                            me.update_summary();
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
}
