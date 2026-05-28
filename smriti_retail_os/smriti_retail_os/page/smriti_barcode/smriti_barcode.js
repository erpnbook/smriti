/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_barcode/smriti_barcode.js
 * @description: Barcode Printing — template-driven ZPL/TSPL, USB download, LAN direct-send.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 2.0.0
 * @license: MIT
 * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
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
};

class SmritiBarcodeController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;

        // Controller state
        this.active_mode        = "transaction"; // transaction | manual
        this.items              = [];
        this.filters_cache      = { brands: [], categories: [], sizes: [], print_templates: [] };
        this.selected_label_size = "50x25";
        this.selected_template   = "";   // SMRITI Print Template name
        this.lan_printer_ip      = localStorage.getItem("smriti_printer_ip")  || "";
        this.lan_printer_port    = localStorage.getItem("smriti_printer_port") || "9100";

        this.init();
    }

    // -----------------------------------------------------------------------
    // INIT
    // -----------------------------------------------------------------------

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
                    // Pre-select first template if available
                    if (r.message.print_templates && r.message.print_templates.length > 0) {
                        me.selected_template = r.message.print_templates[0].name;
                    }
                }
                if (callback) callback();
            }
        });
    }

    // -----------------------------------------------------------------------
    // LAYOUT
    // -----------------------------------------------------------------------

    setup_layout() {
        var me = this;

        // Build template options for the print settings card
        let tmpl_opts = `<option value="">-- Built-in (Auto) --</option>`;
        (me.filters_cache.print_templates || []).forEach(t => {
            const sel = (t.name === me.selected_template) ? "selected" : "";
            tmpl_opts += `<option value="${t.name}" ${sel}>${t.template_name} (${t.label_size} · ${t.printer_language})</option>`;
        });

        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-barcode-container dark-mode">

                <!-- Top Navbar -->
                <div class="smriti-top-nav">
                    <div class="smriti-mode-selector">
                        <button class="smriti-mode-btn active" data-mode="transaction">📂 ${__('Transaction-Based')}</button>
                        <button class="smriti-mode-btn" data-mode="manual">🔍 ${__('Manual Bulk Selection')}</button>
                    </div>
                    <div class="smriti-shortcuts-hint">
                        <span><b>F2</b> Item Lookup | <b>F9</b> Print / Download | <b>F8</b> Send to LAN Printer | <b>ESC</b> Focus</span>
                    </div>
                </div>

                <!-- Main Split Grid -->
                <div class="smriti-grid">

                    <!-- Left: Forms & Item Grid -->
                    <div class="smriti-main-panel">

                        <!-- Mode-specific settings card -->
                        <div class="smriti-header-fields-card" id="smriti-mode-settings-card"></div>

                        <!-- Item Grid -->
                        <div class="billing-table-wrapper" style="max-height: 400px; min-height: 220px;">
                            <table class="table table-bordered table-hover" id="smriti-barcode-table">
                                <thead id="smriti-barcode-table-head"></thead>
                                <tbody id="smriti-barcode-table-body"></tbody>
                            </table>
                            <div class="empty-state" id="smriti-barcode-empty-msg">
                                <span class="empty-icon">🖨️</span>
                                <span class="empty-text">${__('No items loaded. Load a transaction or apply manual filters above.')}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Preview + Print Settings -->
                    <div class="smriti-side-panel">

                        <!-- Label Preview Simulation -->
                        <div class="summary-card">
                            <div class="summary-header">👁️ ${__('Label Preview Simulation')}</div>
                            <div class="smriti-label-preview-wrapper">
                                <div class="smriti-simulated-label sz-50x25" id="smriti-barcode-preview-box">
                                    <div class="sim-brand" id="sim-lbl-brand">BRAND</div>
                                    <div class="sim-name" id="sim-lbl-name">Select an item below to preview</div>
                                    <div class="sim-barcode" id="sim-lbl-barcode">1234567890123</div>
                                    <div class="sim-mrp" id="sim-lbl-mrp">MRP: Rs. 0.00</div>
                                    <div class="sim-details" id="sim-lbl-details">SIZE: L</div>
                                </div>
                            </div>
                        </div>

                        <!-- Print Settings -->
                        <div class="payment-drawer-card">
                            <div class="payment-drawer-header">⚙️ ${__('Printing Settings')}
                                <button class="btn btn-xs btn-info pull-right" id="smriti-btn-field-map" title="Show PRN field mapping reference">
                                    📖 ${__('Field Map')}
                                </button>
                            </div>

                            <!-- Label Size -->
                            <div class="summary-row" style="margin-bottom:8px;">
                                <label class="s-label" style="display:inline-block;margin-bottom:0;line-height:30px;min-width:90px;">📏 ${__('Label Size')}:</label>
                                <select class="form-control s-input" id="smriti-print-label-size" style="max-width:145px;display:inline-block;">
                                    <option value="50x25">50 × 25 mm</option>
                                    <option value="50x30">50 × 30 mm</option>
                                    <option value="75x50">75 × 50 mm</option>
                                    <option value="100x50">100 × 50 mm</option>
                                    <option value="106x55">106.6 × 55.4 mm (TSPL)</option>
                                </select>
                            </div>

                            <!-- PRN Template -->
                            <div class="summary-row" style="margin-bottom:8px;">
                                <label class="s-label" style="display:inline-block;margin-bottom:0;line-height:30px;min-width:90px;">🖨️ ${__('Template')}:</label>
                                <select class="form-control s-input" id="smriti-print-template" style="max-width:195px;display:inline-block;">
                                    ${tmpl_opts}
                                </select>
                            </div>

                            <div class="summary-divider"></div>

                            <!-- Stats -->
                            <div class="summary-row">
                                <span class="summary-label">${__('Selected Lines')}:</span>
                                <span class="summary-val text-teal" id="smriti-lbl-stat-items">0 items</span>
                            </div>
                            <div class="summary-row">
                                <span class="summary-label">${__('Total Labels to Print')}:</span>
                                <span class="summary-val highlight" id="smriti-lbl-stat-labels">0</span>
                            </div>

                            <div class="summary-divider"></div>

                            <!-- Action Buttons Row 1 -->
                            <div class="row" style="margin-bottom:8px;">
                                <div class="col-sm-6">
                                    <button class="btn btn-secondary btn-block" id="smriti-btn-preview-prn">📄 ${__('Preview ZPL')}</button>
                                </div>
                                <div class="col-sm-6">
                                    <button class="btn btn-success btn-block btn-checkout-save" id="smriti-btn-print-labels">⬇️ F9: ${__('Download PRN')}</button>
                                </div>
                            </div>

                            <!-- LAN Printer Section -->
                            <div class="smriti-lan-printer-section">
                                <div class="lan-header">🌐 ${__('Direct LAN Printer')}
                                    <span class="lan-hint">${__('(Raw TCP/IP — port 9100)')}</span>
                                </div>
                                <div class="lan-inputs">
                                    <input type="text" class="form-control s-input" id="smriti-printer-ip"
                                        placeholder="192.168.1.100"
                                        value="${frappe.utils.escape_html(me.lan_printer_ip)}"
                                        title="Printer IP Address">
                                    <input type="number" class="form-control s-input lan-port" id="smriti-printer-port"
                                        placeholder="9100"
                                        value="${frappe.utils.escape_html(me.lan_printer_port)}"
                                        title="Printer Port (default 9100)">
                                </div>
                                <button class="btn btn-primary btn-block" id="smriti-btn-lan-print" style="margin-top:6px;">
                                    🚀 F8: ${__('Send to Printer')}
                                </button>
                                <div class="lan-status" id="smriti-lan-status"></div>
                            </div>

                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    // -----------------------------------------------------------------------
    // BINDINGS
    // -----------------------------------------------------------------------

    bind_mode_switching() {
        var me = this;
        this.wrapper.find(".smriti-mode-btn").off("click").on("click", function() {
            const btn = $(this);
            me.wrapper.find(".smriti-mode-btn").removeClass("active");
            btn.addClass("active");
            me.active_mode = btn.data("mode");
            me.items = [];
            me.render_mode_contents();
        });
    }

    bind_keyboard_shortcuts() {
        var me = this;
        $(document).off("keydown.smriti_barcode").on("keydown.smriti_barcode", function(e) {
            // F2: Item Search
            if (e.keyCode === 113) {
                e.preventDefault();
                me.trigger_catalog_lookup();
            }
            // F9: Download PRN
            else if (e.keyCode === 120) {
                e.preventDefault();
                me.trigger_print();
            }
            // F8: LAN Print
            else if (e.keyCode === 119) {
                e.preventDefault();
                me.trigger_lan_print();
            }
            // ESC: Focus search
            else if (e.keyCode === 27) {
                e.preventDefault();
                $("#smriti-hdr-search, #smriti-hdr-docname").first().focus();
            }
        });
    }

    bind_actions() {
        var me = this;

        // Label size change → update preview size class
        $("#smriti-print-label-size").off("change").on("change", function() {
            me.selected_label_size = $(this).val();
            const sim = $("#smriti-barcode-preview-box");
            sim.removeClass("sz-50x25 sz-50x30 sz-75x50 sz-100x50 sz-106x55")
               .addClass("sz-" + me.selected_label_size);
        });

        // Template change
        $("#smriti-print-template").off("change").on("change", function() {
            me.selected_template = $(this).val();
        });

        // LAN IP/port persistence
        $("#smriti-printer-ip").off("change").on("change", function() {
            me.lan_printer_ip = $(this).val().trim();
            localStorage.setItem("smriti_printer_ip", me.lan_printer_ip);
        });
        $("#smriti-printer-port").off("change").on("change", function() {
            me.lan_printer_port = $(this).val().trim();
            localStorage.setItem("smriti_printer_port", me.lan_printer_port);
        });

        // Buttons
        $("#smriti-btn-preview-prn").off("click").on("click",    () => me.trigger_prn_preview_code());
        $("#smriti-btn-print-labels").off("click").on("click",   () => me.trigger_print());
        $("#smriti-btn-lan-print").off("click").on("click",      () => me.trigger_lan_print());
        $("#smriti-btn-field-map").off("click").on("click",      () => me.show_field_mapping_dialog());
    }

    // -----------------------------------------------------------------------
    // RENDER
    // -----------------------------------------------------------------------

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
                        <label class="s-label">📄 ${__('Document Type')}</label>
                        <select class="form-control s-input" id="smriti-hdr-doctype">
                            <option value="Purchase Receipt">Purchase Receipt</option>
                            <option value="Stock Entry">Stock Entry</option>
                        </select>
                    </div>
                    <div class="col-sm-5">
                        <label class="s-label">🎫 ${__('Document Name / Reference')}</label>
                        <input type="text" class="form-control s-input" id="smriti-hdr-docname" placeholder="e.g. MAT-PRE-2026-00001">
                    </div>
                    <div class="col-sm-3">
                        <button class="btn btn-primary btn-block" id="smriti-btn-load-txn" style="height:auto;padding:10px 0;">⚡ ${__('Load Items')}</button>
                    </div>
                </div>
            `);
            $("#smriti-btn-load-txn").off("click").on("click", () => me.load_transaction_items());

        } else if (this.active_mode === "manual") {
            let brand_opts = `<option value="">-- ${__('All Brands')} --</option>`;
            this.filters_cache.brands.forEach(b => { brand_opts += `<option value="${b}">${b}</option>`; });

            let group_opts = `<option value="">-- ${__('All Categories')} --</option>`;
            this.filters_cache.categories.forEach(c => { group_opts += `<option value="${c}">${c}</option>`; });

            card.html(`
                <div class="row align-items-end">
                    <div class="col-sm-3">
                        <label class="s-label">🏷️ ${__('Brand')}</label>
                        <select class="form-control s-input" id="smriti-hdr-brand">${brand_opts}</select>
                    </div>
                    <div class="col-sm-3">
                        <label class="s-label">📂 ${__('Category')}</label>
                        <select class="form-control s-input" id="smriti-hdr-group">${group_opts}</select>
                    </div>
                    <div class="col-sm-2">
                        <label class="s-label">🔎 ${__('Search')}</label>
                        <input type="text" class="form-control s-input" id="smriti-hdr-search" placeholder="${__('Code / Name...')}">
                    </div>
                    <div class="col-sm-2">
                        <label class="s-label">📏 ${__('Barcode Size')}</label>
                        <select class="form-control s-input" id="smriti-hdr-size">
                            <option value="">-- ${__('All')} --</option>
                            <option value="50x25">50×25</option>
                            <option value="106x55">106×55</option>
                        </select>
                    </div>
                    <div class="col-sm-2">
                        <button class="btn btn-primary btn-block" id="smriti-btn-apply-filters" style="height:auto;padding:10px 0;">${__('Apply')}</button>
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
                    <th style="width:4%">#</th>
                    <th style="width:20%">${__('Barcode')}</th>
                    <th style="width:28%">${__('Item Details')}</th>
                    <th style="width:12%">${__('Brand')}</th>
                    <th style="width:12%">${__('Size / Color')}</th>
                    <th style="width:12%">${__('MRP (INR)')}</th>
                    <th style="width:12%">${__('Print Qty')}</th>
                </tr>
            `);
        } else {
            thead.html(`
                <tr>
                    <th style="width:4%"><input type="checkbox" id="smriti-chk-all" checked></th>
                    <th style="width:18%">${__('Barcode')}</th>
                    <th style="width:26%">${__('Item Details')}</th>
                    <th style="width:12%">${__('Brand')}</th>
                    <th style="width:12%">${__('Size / Color')}</th>
                    <th style="width:12%">${__('MRP (INR)')}</th>
                    <th style="width:16%">${__('Print Qty')}</th>
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
            const size_color = [it.size, it.color].filter(Boolean).join(" / ") || "—";

            if (this.active_mode === "transaction") {
                tbody.append(`
                    <tr data-idx="${idx}" class="barcode-row">
                        <td>${idx + 1}</td>
                        <td class="font-weight-bold text-teal">${it.barcode}</td>
                        <td><b>${it.item_code}</b><br><small class="text-muted">${it.item_name}</small></td>
                        <td>${it.brand}</td>
                        <td><span class="badge badge-secondary">${size_color}</span></td>
                        <td>₹ ${it.mrp.toFixed(2)}</td>
                        <td>
                            <input type="number" class="grid-qty-input form-control text-center"
                                value="${it.print_qty}" min="1" style="max-width:75px;">
                        </td>
                    </tr>
                `);
            } else {
                const checked = it.selected !== false ? 'checked' : '';
                tbody.append(`
                    <tr data-idx="${idx}" class="barcode-row">
                        <td class="text-center"><input type="checkbox" class="grid-select-chk" ${checked}></td>
                        <td class="font-weight-bold text-teal">${it.barcode}</td>
                        <td><b>${it.item_code}</b><br><small class="text-muted">${it.item_name}</small></td>
                        <td>${it.brand}</td>
                        <td><span class="badge badge-secondary">${size_color}</span></td>
                        <td>₹ ${it.mrp.toFixed(2)}</td>
                        <td>
                            <input type="number" class="grid-qty-input form-control text-center"
                                value="${it.print_qty}" min="1" style="max-width:75px;">
                        </td>
                    </tr>
                `);
            }
        });

        // Row click → preview
        tbody.find(".barcode-row").off("click").on("click", function(e) {
            if ($(e.target).is('input')) return;
            const idx = $(this).data("idx");
            me.update_preview_sim(me.items[idx]);
        });

        // Qty change
        tbody.find(".grid-qty-input").off("change").on("change", function() {
            const idx = $(this).closest("tr").data("idx");
            me.items[idx].print_qty = cint($(this).val());
            me.update_summary();
        });

        // Individual checkbox
        tbody.find(".grid-select-chk").off("change").on("change", function() {
            const idx = $(this).closest("tr").data("idx");
            me.items[idx].selected = $(this).prop("checked");
            me.update_summary();
        });

        // Select-all checkbox
        $("#smriti-chk-all").off("change").on("change", function() {
            const chk = $(this).prop("checked");
            me.items.forEach(i => i.selected = chk);
            tbody.find(".grid-select-chk").prop("checked", chk);
            me.update_summary();
        });

        // Auto-preview first row
        me.update_preview_sim(this.items[0]);
    }

    // -----------------------------------------------------------------------
    // PREVIEW SIMULATION
    // -----------------------------------------------------------------------

    update_preview_sim(item) {
        if (!item) {
            $("#sim-lbl-brand").text("BRAND");
            $("#sim-lbl-name").text("Select an item below to preview");
            $("#sim-lbl-barcode").text("1234567890123");
            $("#sim-lbl-mrp").text("MRP: Rs. 0.00");
            $("#sim-lbl-details").text("SIZE: L");
            return;
        }

        const size_color = [item.size, item.color].filter(Boolean).join(" / ") || "—";
        $("#sim-lbl-brand").text((item.brand || "BRAND").toUpperCase());
        $("#sim-lbl-name").text(item.item_name || item.item_code);
        $("#sim-lbl-barcode").text(item.barcode);
        $("#sim-lbl-mrp").text("MRP: Rs. " + item.mrp.toFixed(2));
        $("#sim-lbl-details").text("SIZE: " + size_color + " | " + item.item_code);
    }

    update_summary() {
        const selected = this.get_selected_items();
        const total_labels = selected.reduce((s, i) => s + (i.print_qty || 1), 0);
        $("#smriti-lbl-stat-items").text(selected.length + " " + __("items selected"));
        $("#smriti-lbl-stat-labels").text(total_labels);
    }

    get_selected_items() {
        if (this.active_mode === "transaction") {
            return this.items;
        }
        return this.items.filter(i => i.selected !== false);
    }

    // -----------------------------------------------------------------------
    // LOAD ITEMS
    // -----------------------------------------------------------------------

    load_transaction_items() {
        var me = this;
        const doctype = $("#smriti-hdr-doctype").val();
        const docname = $("#smriti-hdr-docname").val().trim();

        if (!docname) {
            frappe.show_alert({ message: __("Please enter Document Name / Reference."), indicator: 'orange' });
            return;
        }

        frappe.call({
            method: "smriti_retail_os.barcode_api.get_items_for_printing",
            args: { source_doctype: doctype, source_name: docname },
            freeze: true,
            freeze_message: __("Loading transaction lines…"),
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    me.items = r.message;
                    me.render_grid_rows();
                    me.update_summary();
                } else {
                    frappe.show_alert({ message: __("No items found in this document."), indicator: 'red' });
                }
            }
        });
    }

    load_manual_filtered_items() {
        var me = this;
        const filters = {
            brand:               $("#smriti-hdr-brand").val(),
            item_group:          $("#smriti-hdr-group").val(),
            custom_barcode_size: $("#smriti-hdr-size").val(),
            search_text:         $("#smriti-hdr-search").val().trim()
        };

        frappe.call({
            method: "smriti_retail_os.barcode_api.get_items_for_printing",
            args: { filters: JSON.stringify(filters) },
            freeze: true,
            freeze_message: __("Filtering item catalog…"),
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    me.items = r.message.map(i => { i.selected = true; return i; });
                    me.render_grid_rows();
                    me.update_summary();
                } else {
                    frappe.show_alert({ message: __("No matching items found."), indicator: 'orange' });
                }
            }
        });
    }

    // -----------------------------------------------------------------------
    // PRN PREVIEW
    // -----------------------------------------------------------------------

    trigger_prn_preview_code() {
        const selected = this.get_selected_items();
        if (selected.length === 0) {
            frappe.show_alert({ message: __("Please load or select items first."), indicator: 'orange' });
            return;
        }

        frappe.call({
            method: "smriti_retail_os.barcode_api.generate_prn",
            args: {
                items: JSON.stringify(selected.map(i => {
                    i.label_size = this.selected_label_size;
                    return i;
                })),
                template_name: this.selected_template
            },
            callback: function(r) {
                if (r.message) {
                    frappe.msgprint({
                        title: __('ZPL / TSPL PRN Preview'),
                        message: `<pre style="background:#0f1117;color:#10b981;padding:15px;border-radius:8px;
                                  font-family:'Fira Mono','Consolas',monospace;font-size:12px;
                                  max-height:350px;overflow-y:auto;white-space:pre-wrap;word-break:break-all;">${
                                  frappe.utils.escape_html(r.message)
                                  }</pre>`,
                        wide: true
                    });
                }
            }
        });
    }

    // -----------------------------------------------------------------------
    // DOWNLOAD PRN (USB / File method)
    // -----------------------------------------------------------------------

    trigger_print() {
        var me = this;
        const selected = this.get_selected_items();
        if (selected.length === 0) {
            frappe.show_alert({ message: __("No items selected for printing."), indicator: 'orange' });
            return;
        }

        frappe.call({
            method: "smriti_retail_os.barcode_api.generate_prn",
            args: {
                items: JSON.stringify(selected.map(i => {
                    i.label_size = me.selected_label_size;
                    return i;
                })),
                template_name: me.selected_template
            },
            freeze: true,
            freeze_message: __("Generating PRN file…"),
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
            message: __('✅ PRN file downloaded. Send to printer via USB or raw print queue.'),
            indicator: 'green'
        });

        // Show quick USB instructions tip
        this.show_usb_tip_once();
    }

    show_usb_tip_once() {
        if (localStorage.getItem("smriti_prn_usb_tip_shown")) return;
        localStorage.setItem("smriti_prn_usb_tip_shown", "1");
        frappe.msgprint({
            title: __('💡 How to send PRN to USB Printer'),
            message: `
                <div style="font-family:inherit;line-height:1.7;">
                    <b>Windows (CMD / PowerShell):</b><br>
                    <code style="background:#1f2937;color:#10b981;padding:4px 8px;border-radius:4px;display:inline-block;margin:4px 0;">
                        copy /b smriti_barcodes_*.prn \\\\&lt;ComputerName&gt;\\&lt;PrinterShare&gt;
                    </code>
                    <br><br>
                    <b>Linux / Mac Terminal:</b><br>
                    <code style="background:#1f2937;color:#10b981;padding:4px 8px;border-radius:4px;display:inline-block;margin:4px 0;">
                        lp -d &lt;printer_name&gt; smriti_barcodes_*.prn
                    </code>
                    <br><br>
                    <b>Or use the 🌐 LAN Printer</b> section on the right to send directly over the network (no file needed).
                </div>`,
            wide: false
        });
    }

    // -----------------------------------------------------------------------
    // LAN DIRECT PRINT
    // -----------------------------------------------------------------------

    trigger_lan_print() {
        var me = this;
        const ip   = $("#smriti-printer-ip").val().trim();
        const port = $("#smriti-printer-port").val().trim() || "9100";

        if (!ip) {
            frappe.show_alert({ message: __("Enter the printer IP address first."), indicator: 'orange' });
            $("#smriti-printer-ip").focus();
            return;
        }

        const selected = this.get_selected_items();
        if (selected.length === 0) {
            frappe.show_alert({ message: __("No items selected for printing."), indicator: 'orange' });
            return;
        }

        // Persist
        me.lan_printer_ip   = ip;
        me.lan_printer_port = port;
        localStorage.setItem("smriti_printer_ip",   ip);
        localStorage.setItem("smriti_printer_port", port);

        const status_el = $("#smriti-lan-status");
        status_el.html(`<span class="lan-sending">⏳ ${__('Sending to')} ${ip}:${port}…</span>`);

        frappe.call({
            method: "smriti_retail_os.barcode_api.send_to_network_printer",
            args: {
                items: JSON.stringify(selected.map(i => {
                    i.label_size = me.selected_label_size;
                    return i;
                })),
                template_name: me.selected_template,
                printer_ip:    ip,
                printer_port:  port
            },
            freeze: true,
            freeze_message: __("Sending to printer…"),
            callback: function(r) {
                if (r.message && r.message.success) {
                    status_el.html(`<span class="lan-success">✅ ${r.message.message}</span>`);
                    frappe.show_alert({
                        message: r.message.message,
                        indicator: 'green'
                    });
                } else {
                    status_el.html(`<span class="lan-error">❌ ${__('Failed — check IP and port')}</span>`);
                }
            },
            error: function(r) {
                const msg = r && r._server_messages
                    ? JSON.parse(r._server_messages)[0]
                    : __("Connection failed");
                status_el.html(`<span class="lan-error">❌ ${frappe.utils.escape_html(msg)}</span>`);
            }
        });
    }

    // -----------------------------------------------------------------------
    // FIELD MAPPING HELPER DIALOG
    // -----------------------------------------------------------------------

    show_field_mapping_dialog() {
        frappe.call({
            method: "smriti_retail_os.barcode_api.get_field_mapping_reference",
            callback: function(r) {
                if (!r.message) return;

                const rows = r.message.map(m => `
                    <tr>
                        <td><code class="prn-token">${frappe.utils.escape_html(m.placeholder)}</code></td>
                        <td>${frappe.utils.escape_html(m.item_master_field)}</td>
                        <td><span class="prn-example">${frappe.utils.escape_html(m.example)}</span></td>
                        <td class="text-muted" style="font-size:12px;">${frappe.utils.escape_html(m.description)}</td>
                    </tr>
                `).join("");

                frappe.msgprint({
                    title: __('📖 PRN Template — Item Master Field Mapping'),
                    message: `
                        <div style="font-family:inherit;">
                            <p style="margin-bottom:10px;color:#9ca3af;font-size:13px;">
                                Use these <b style="color:#10b981;">{placeholder}</b> tokens in your
                                <b>SMRITI Print Template → Raw PRN Template</b> field.
                                The system automatically replaces them with live Item Master data at print time.
                            </p>
                            <div style="overflow-x:auto;">
                            <table class="table table-bordered" style="font-size:13px;min-width:650px;">
                                <thead>
                                    <tr style="background:#1f2937;color:#e5e7eb;">
                                        <th style="width:16%">Placeholder Token</th>
                                        <th style="width:28%">Item Master Field Source</th>
                                        <th style="width:12%">Example Value</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>${rows}</tbody>
                            </table>
                            </div>
                            <div style="margin-top:12px;padding:10px;background:#0f1117;border-radius:6px;">
                                <b style="color:#f59e0b;">📝 Example ZPL Snippet:</b><br>
                                <pre style="color:#10b981;font-size:11px;margin-top:6px;white-space:pre-wrap;">^XA
^FO20,10^BCN,60,Y,N,N^FD{barcode}^FS
^FO20,80^ADN,18,10^FD{item_name}^FS
^FO20,100^ADN,18,10^FDMRP: Rs.{mrp}^FS
^FO20,120^ADN,14,8^FD{brand} | Sz:{size} | {color}^FS
^XZ</pre>
                                <b style="color:#f59e0b;">📝 Example TSPL Snippet:</b><br>
                                <pre style="color:#10b981;font-size:11px;margin-top:6px;white-space:pre-wrap;">SIZE 50 mm, 25 mm
GAP 2 mm, 0 mm
CLS
TEXT 10,5,"3",0,1,1,"{brand}"
TEXT 10,30,"2",0,1,1,"{item_name}"
BARCODE 10,60,"128",50,1,0,2,4,"{barcode}"
TEXT 10,120,"2",0,1,1,"MRP: Rs.{mrp}  Size:{size}"
TEXT 10,145,"1",0,1,1,"Color:{color}  Style:{style}  Pkd:{pkd_date}"
PRINT 1,1</pre>
                            </div>
                        </div>
                    `,
                    wide: true
                });
            }
        });
    }

    // -----------------------------------------------------------------------
    // ITEM CATALOG LOOKUP (F2)
    // -----------------------------------------------------------------------

    trigger_catalog_lookup() {
        var me = this;
        var dialog = new frappe.ui.Dialog({
            title: __('F2 — Item Catalog Search'),
            fields: [
                {
                    label: __('Search by Code / Name / Barcode'),
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
            if (val.length < 2) return;
            frappe.call({
                method: "smriti_retail_os.billing_api.search_items",
                args: { query: val },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let html = `<table class="table table-bordered table-condensed table-hover"><thead>
                            <tr><th>${__('Code')}</th><th>${__('Name')}</th><th>${__('Brand')}</th><th>${__('Rate')}</th><th></th></tr>
                            </thead><tbody>`;
                        r.message.forEach(it => {
                            html += `
                                <tr>
                                    <td><b>${it.item_code}</b></td>
                                    <td>${it.item_name}</td>
                                    <td>${it.brand || '—'}</td>
                                    <td>₹ ${it.rate}</td>
                                    <td><button class="btn btn-xs btn-primary btn-catalog-add" data-code="${it.item_code}">
                                        + ${__('Add')}</button></td>
                                </tr>`;
                        });
                        html += `</tbody></table>`;
                        dialog.fields_dict.results_html.$wrapper.html(html);

                        dialog.$wrapper.find(".btn-catalog-add").off("click").on("click", function() {
                            const code = $(this).data("code");
                            frappe.call({
                                method: "smriti_retail_os.barcode_api.get_items_for_printing",
                                args: { filters: JSON.stringify({ search_text: code }) },
                                callback: function(res) {
                                    if (res.message && res.message.length > 0) {
                                        const item = res.message[0];
                                        item.selected = true;
                                        me.items.push(item);
                                        me.render_grid_rows();
                                        me.update_summary();
                                    }
                                    dialog.hide();
                                }
                            });
                        });
                    } else {
                        dialog.fields_dict.results_html.$wrapper.html(
                            `<p class="text-muted">${__('No matching items found.')}</p>`
                        );
                    }
                }
            });
        });

        dialog.show();
        setTimeout(() => dialog.fields_dict.query.$wrapper.find("input").focus(), 200);
    }
}
