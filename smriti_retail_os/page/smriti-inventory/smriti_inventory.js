frappe.pages['smriti-inventory'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Inventory Operations'),
        single_column: true
    });

    if (window.SMRITI && typeof SMRITI.renderSidebar === 'function') {
        SMRITI.renderSidebar("inventory");
    }

    var smriti_inventory = new SmritiInventoryController(wrapper, page);
}

class SmritiInventoryController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;
        
        // Roles & Permissions
        this.user = frappe.session.user;
        this.roles = frappe.user_roles || [];
        this.is_manager = this.roles.includes("SMRITI Store Manager") || this.roles.includes("System Manager") || this.user === "Administrator";
        
        // Active states per tab
        this.active_tab = "grn"; // grn, transfer, adjustment, audit
        
        this.states = {
            grn: {
                supplier: "",
                invoice_no: "",
                items: []
            },
            transfer: {
                from_warehouse: "",
                to_warehouse: "",
                items: []
            },
            adjustment: {
                reason: "Stock Damaged",
                items: []
            },
            audit: {
                warehouse: "",
                items: []
            }
        };

        // Cache for dynamic dropdowns
        this.suppliers = [];
        this.warehouses = [];

        this.init();
    }

    init() {
        var me = this;
        // Fetch masters, then construct layout
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
            <div class="smriti-inventory-container dark-mode">
                <!-- Top Navbar: Tabs selector and role indicators -->
                <div class="smriti-top-nav">
                    <div class="smriti-tabs-bar">
                        <button class="smriti-tab-btn active" data-tab="grn"><span class="material-symbols-outlined" style="margin-right: 6px;">download</span>${__('Goods Receipt (GRN)')}</button>
                        <button class="smriti-tab-btn" data-tab="transfer"><span class="material-symbols-outlined" style="margin-right: 6px;">sync_alt</span>${__('Stock Transfer')}</button>
                        <button class="smriti-tab-btn" data-tab="adjustment"><span class="material-symbols-outlined" style="margin-right: 6px;">warning</span>${__('Stock Adjustment')}</button>
                        <button class="smriti-tab-btn" data-tab="audit"><span class="material-symbols-outlined" style="margin-right: 6px;">assignment</span>${__('Stock Audit')}</button>
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
                        <div class="smriti-header-fields-card" id="smriti-tab-header-fields">
                            <!-- Injected dynamically -->
                        </div>

                        <!-- Barcode Field -->
                        <div class="barcode-wrapper">
                            <div class="barcode-input-container">
                                <span class="scanner-icon"><span class="material-symbols-outlined">barcode_scanner</span></span>
                                <input type="text" id="smriti-inv-barcode-input" autocomplete="off" placeholder="${__('Scan Barcode or Type Code...')}">
                            </div>
                        </div>

                        <!-- Grid Table -->
                        <div class="billing-table-wrapper">
                            <table class="table table-bordered table-hover" id="smriti-inv-table">
                                <thead id="smriti-inv-table-head">
                                    <!-- Dynamic headers -->
                                </thead>
                                <tbody id="smriti-inv-table-body">
                                    <!-- Dynamic rows -->
                                </tbody>
                            </table>
                            <div class="empty-state" id="smriti-inv-empty-msg">
                                <span class="empty-icon"><span class="material-symbols-outlined">inventory_2</span></span>
                                <span class="empty-text">${__('No Scanned Items. Begin scanning or press F2 to search catalog.')}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Right Section: Totals & Commit Action -->
                    <div class="smriti-side-panel">
                        <!-- Quick Summary Card -->
                        <div class="summary-card">
                            <div class="summary-header"><span class="material-symbols-outlined" style="margin-right: 6px;">bar_chart</span> ${__('Session Summary')}</div>
                            <div class="summary-row">
                                <span class="summary-label">${__('Scanned Lines')}:</span>
                                <span class="summary-val" id="smriti-inv-stat-lines">0</span>
                            </div>
                            <div class="summary-row">
                                <span class="summary-label">${__('Total Quantities')}:</span>
                                <span class="summary-val highlight" id="smriti-inv-stat-qty">0</span>
                            </div>
                        </div>

                        <!-- Help Instructions -->
                        <div class="summary-card" style="margin-top: 15px;">
                            <div class="summary-header"><span class="material-symbols-outlined" style="margin-right: 6px;">keyboard</span> ${__('Keyboard Shortcuts')}</div>
                            <div class="summary-row"><span><b>F2</b>: Search Catalog</span></div>
                            <div class="summary-row"><span><b>F9</b>: Commit Transaction</span></div>
                            <div class="summary-row"><span><b>ESC</b>: Focus barcode / Clear</span></div>
                        </div>

                        <!-- Main Submit Button -->
                        <div class="payment-drawer-card" style="margin-top: 15px;">
                            <button class="btn btn-success btn-block btn-checkout-save" id="smriti-inv-btn-submit" ${!this.is_manager ? 'disabled' : ''}>
                                <span class="material-symbols-outlined" style="color: white; margin-right: 4px;">send</span> F9: ${__('Commit to ERPNext')}
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
            // F2: Fast Catalog Search
            if (e.keyCode === 113) { 
                e.preventDefault();
                me.trigger_catalog_search();
            }
            // F9: Commit Transaction
            else if (e.keyCode === 120) {
                e.preventDefault();
                me.commit_transaction();
            }
            // ESC: Focus Scanner or cancel
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

        $(this.wrapper).off("keypress", "#smriti-inv-barcode-input").on("keypress", "#smriti-inv-barcode-input", function(e) {
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
        $("#smriti-inv-btn-submit").off("click").on("click", () => me.commit_transaction());
    }

    focus_active_barcode() {
        $("#smriti-inv-barcode-input").focus();
    }

    render_active_tab_contents() {
        this.render_header_fields();
        this.render_table_headers();
        this.render_grid_rows();
        this.update_summary_stats();
    }

    render_header_fields() {
        const header_fields = $("#smriti-tab-header-fields");
        header_fields.empty();
        
        const state = this.states[this.active_tab];

        if (this.active_tab === "grn") {
            let supplier_opts = `<option value="">-- Select Supplier --</option>`;
            this.suppliers.forEach(s => {
                supplier_opts += `<option value="${s.name}" ${state.supplier === s.name ? 'selected' : ''}>${s.supplier_name}</option>`;
            });

            header_fields.html(`
                <div class="row">
                    <div class="col-sm-6">
                        <label class="s-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">person</span> Supplier</label>
                        <select class="form-control s-input" id="smriti-hdr-supplier">${supplier_opts}</select>
                    </div>
                    <div class="col-sm-6">
                        <label class="s-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">description</span> Supplier Invoice / Bill No.</label>
                        <input type="text" class="form-control s-input" id="smriti-hdr-invoice" placeholder="Invoice Number..." value="${state.invoice_no}">
                    </div>
                </div>
            `);

            // Bind values to state
            var me = this;
            $("#smriti-hdr-supplier").on("change", function() { me.states.grn.supplier = $(this).val(); });
            $("#smriti-hdr-invoice").on("input", function() { me.states.grn.invoice_no = $(this).val(); });

        } else if (this.active_tab === "transfer") {
            let warehouse_opts = `<option value="">-- Select Warehouse --</option>`;
            this.warehouses.forEach(w => {
                warehouse_opts += `<option value="${w.name}">${w.name}</option>`;
            });

            header_fields.html(`
                <div class="row">
                    <div class="col-sm-6">
                        <label class="s-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">unarchive</span> Source Warehouse (From)</label>
                        <select class="form-control s-input" id="smriti-hdr-from-wh">${warehouse_opts}</select>
                    </div>
                    <div class="col-sm-6">
                        <label class="s-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">archive</span> Target Warehouse (To)</label>
                        <select class="form-control s-input" id="smriti-hdr-to-wh">${warehouse_opts}</select>
                    </div>
                </div>
            `);

            // Pre-select saved states
            $("#smriti-hdr-from-wh").val(state.from_warehouse);
            $("#smriti-hdr-to-wh").val(state.to_warehouse);

            var me = this;
            $("#smriti-hdr-from-wh").on("change", function() { me.states.transfer.from_warehouse = $(this).val(); });
            $("#smriti-hdr-to-wh").on("change", function() { me.states.transfer.to_warehouse = $(this).val(); });

        } else if (this.active_tab === "adjustment") {
            const reasons = ["Stock Damaged", "Stock Deficit", "Stock Surplus", "Promotional Sample"];
            let reason_opts = "";
            reasons.forEach(r => {
                reason_opts += `<option value="${r}" ${state.reason === r ? 'selected' : ''}>${r}</option>`;
            });

            let warehouse_opts = `<option value="">-- Select Warehouse --</option>`;
            this.warehouses.forEach(w => {
                warehouse_opts += `<option value="${w.name}">${w.name}</option>`;
            });

            header_fields.html(`
                <div class="row">
                    <div class="col-sm-6">
                        <label class="s-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">help</span> Adjustment Reason</label>
                        <select class="form-control s-input" id="smriti-hdr-reason">${reason_opts}</select>
                    </div>
                    <div class="col-sm-6">
                        <label class="s-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">store</span> Target Warehouse</label>
                        <select class="form-control s-input" id="smriti-hdr-adj-wh">${warehouse_opts}</select>
                    </div>
                </div>
            `);

            $("#smriti-hdr-adj-wh").val(state.warehouse || "");

            var me = this;
            $("#smriti-hdr-reason").on("change", function() { me.states.adjustment.reason = $(this).val(); });
            $("#smriti-hdr-adj-wh").on("change", function() { me.states.adjustment.warehouse = $(this).val(); });

        } else if (this.active_tab === "audit") {
            let warehouse_opts = `<option value="">-- Select Warehouse --</option>`;
            this.warehouses.forEach(w => {
                warehouse_opts += `<option value="${w.name}">${w.name}</option>`;
            });

            header_fields.html(`
                <div class="row">
                    <div class="col-sm-12">
                        <label class="s-label"><span class="material-symbols-outlined" style="font-size: 16px; vertical-align: text-bottom; margin-right: 4px;">domain</span> Audit Warehouse</label>
                        <select class="form-control s-input" id="smriti-hdr-audit-wh">${warehouse_opts}</select>
                    </div>
                </div>
            `);

            $("#smriti-hdr-audit-wh").val(state.warehouse || "");

            var me = this;
            $("#smriti-hdr-audit-wh").on("change", function() { me.states.audit.warehouse = $(this).val(); });
        }
    }

    render_table_headers() {
        const thead = $("#smriti-inv-table-head");
        thead.empty();

        if (this.active_tab === "grn") {
            thead.html(`
                <tr>
                    <th style="width: 5%">#</th>
                    <th style="width: 30%">Item Details</th>
                    <th style="width: 15%">Expiry / Batch</th>
                    <th style="width: 15%">Qty</th>
                    <th style="width: 15%">Rate (INR)</th>
                    <th style="width: 17%">Total (INR)</th>
                    <th style="width: 3%"></th>
                </tr>
            `);
        } else if (this.active_tab === "transfer") {
            thead.html(`
                <tr>
                    <th style="width: 5%">#</th>
                    <th style="width: 50%">Item Details</th>
                    <th style="width: 15%">UOM</th>
                    <th style="width: 27%">Qty to Transfer</th>
                    <th style="width: 3%"></th>
                </tr>
            `);
        } else if (this.active_tab === "adjustment") {
            thead.html(`
                <tr>
                    <th style="width: 5%">#</th>
                    <th style="width: 50%">Item Details</th>
                    <th style="width: 15%">UOM</th>
                    <th style="width: 27%">Qty to Adjust</th>
                    <th style="width: 3%"></th>
                </tr>
            `);
        } else if (this.active_tab === "audit") {
            thead.html(`
                <tr>
                    <th style="width: 5%">#</th>
                    <th style="width: 40%">Item Details</th>
                    <th style="width: 15%">UOM</th>
                    <th style="width: 20%">System Qty</th>
                    <th style="width: 20%">Physical Count</th>
                    <th style="width: 3%"></th>
                </tr>
            `);
        }
    }

    render_grid_rows() {
        var me = this;
        var tbody = $("#smriti-inv-table-body");
        tbody.empty();

        const state = this.states[this.active_tab];
        if (state.items.length === 0) {
            $("#smriti-inv-empty-msg").show();
            return;
        }
        $("#smriti-inv-empty-msg").hide();

        state.items.forEach((it, idx) => {
            if (this.active_tab === "grn") {
                const total = it.qty * it.rate;
                const date_picker = it.has_batch_no 
                    ? `<input type="date" class="grid-expiry-input form-control" value="${it.expiry_date || ''}">` 
                    : `<span class="text-muted">No Batch</span>`;

                tbody.append(`
                    <tr data-idx="${idx}">
                        <td>${idx + 1}</td>
                        <td><b>${it.item_code}</b><br><small class="text-muted">${it.item_name}</small></td>
                        <td>${date_picker}</td>
                        <td><input type="number" class="grid-qty-input form-control text-center" value="${it.qty}" min="1"></td>
                        <td><input type="number" class="grid-rate-input form-control text-right" value="${it.rate}" min="0.01"></td>
                        <td class="text-right font-weight-bold text-teal">INR ${total.toFixed(2)}</td>
                        <td class="text-center"><button class="btn btn-xs btn-danger btn-remove-row">✕</button></td>
                    </tr>
                `);
            } else if (this.active_tab === "transfer") {
                tbody.append(`
                    <tr data-idx="${idx}">
                        <td>${idx + 1}</td>
                        <td><b>${it.item_code}</b><br><small class="text-muted">${it.item_name}</small></td>
                        <td><span class="badge badge-secondary">${it.stock_uom}</span></td>
                        <td><input type="number" class="grid-qty-input form-control text-center" value="${it.qty}" min="1"></td>
                        <td class="text-center"><button class="btn btn-xs btn-danger btn-remove-row">✕</button></td>
                    </tr>
                `);
            } else if (this.active_tab === "adjustment") {
                tbody.append(`
                    <tr data-idx="${idx}">
                        <td>${idx + 1}</td>
                        <td><b>${it.item_code}</b><br><small class="text-muted">${it.item_name}</small></td>
                        <td><span class="badge badge-secondary">${it.stock_uom}</span></td>
                        <td><input type="number" class="grid-qty-input form-control text-center" value="${it.qty}" min="1"></td>
                        <td class="text-center"><button class="btn btn-xs btn-danger btn-remove-row">✕</button></td>
                    </tr>
                `);
            } else if (this.active_tab === "audit") {
                const diff_class = it.qty === it.available_qty ? 'text-green' : 'text-orange';
                tbody.append(`
                    <tr data-idx="${idx}">
                        <td>${idx + 1}</td>
                        <td><b>${it.item_code}</b><br><small class="text-muted">${it.item_name}</small></td>
                        <td><span class="badge badge-secondary">${it.stock_uom}</span></td>
                        <td class="text-center font-weight-bold">${it.available_qty}</td>
                        <td><input type="number" class="grid-qty-input form-control text-center ${diff_class}" value="${it.qty}" min="0"></td>
                        <td class="text-center"><button class="btn btn-xs btn-danger btn-remove-row">✕</button></td>
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
        let active_wh = "";
        
        if (this.active_tab === "transfer") {
            active_wh = this.states.transfer.from_warehouse;
            if (!active_wh) {
                frappe.show_alert({message: __("Please select a Source Warehouse first."), indicator: 'orange'});
                return;
            }
        } else if (this.active_tab === "adjustment") {
            active_wh = this.states.adjustment.warehouse;
            if (!active_wh) {
                frappe.show_alert({message: __("Please select a Target Warehouse first."), indicator: 'orange'});
                return;
            }
        } else if (this.active_tab === "audit") {
            active_wh = this.states.audit.warehouse;
            if (!active_wh) {
                frappe.show_alert({message: __("Please select an Audit Warehouse first."), indicator: 'orange'});
                return;
            }
        }

        frappe.call({
            method: "smriti_retail_os.inventory_api.scan_item_for_inventory",
            args: { barcode: barcode, warehouse: active_wh },
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
                available_qty: item.available_qty,
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

        $("#smriti-inv-stat-lines").text(lines);
        $("#smriti-inv-stat-qty").text(total_qty);
    }

    trigger_catalog_search() {
        var me = this;
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
                                            <button class="btn btn-xs btn-primary btn-select-inv-item" data-code="${it.item_code}">Add</button>
                                        </td>
                                    </tr>
                                `;
                            });
                            rows_html += `</tbody></table>`;
                            dialog.fields_dict.results_html.$wrapper.html(rows_html);

                            dialog.$wrapper.find(".btn-select-inv-item").off("click").on("click", function() {
                                const code = $(this).data("code");
                                const found = r.message.find(i => i.item_code === code);
                                
                                // Fetch dynamic stock for selected item
                                let active_wh = "";
                                if (me.active_tab === "transfer") active_wh = me.states.transfer.from_warehouse;
                                else if (me.active_tab === "adjustment") active_wh = me.states.adjustment.warehouse;
                                else if (me.active_tab === "audit") active_wh = me.states.audit.warehouse;

                                frappe.call({
                                    method: "smriti_retail_os.inventory_api.scan_item_for_inventory",
                                    args: { barcode: found.item_code, warehouse: active_wh },
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
                message: __('Only Store Managers or System Managers are authorized to commit inventory records to ERPNext.'),
                indicator: 'red'
            });
            return;
        }

        const state = this.states[this.active_tab];
        if (state.items.length === 0) {
            frappe.show_alert({message: __("Scanned list is empty."), indicator: 'red'});
            return;
        }

        if (this.active_tab === "grn") {
            if (!state.supplier) {
                frappe.show_alert({message: __("Please select a Supplier."), indicator: 'red'});
                return;
            }
            if (!state.invoice_no) {
                frappe.show_alert({message: __("Please enter a Supplier Invoice number."), indicator: 'red'});
                return;
            }
            
            // Validate batch expiry dates are input
            const missing_expiry = state.items.some(i => i.has_batch_no && !i.expiry_date);
            if (missing_expiry) {
                frappe.msgprint({
                    title: __('Missing Batch Expiry'),
                    message: __('One or more batch-tracked items is missing an Expiry Date. Please select valid dates in the grid before submitting.'),
                    indicator: 'orange'
                });
                return;
            }

            frappe.call({
                method: "smriti_retail_os.inventory_api.create_grn",
                args: {
                    supplier: state.supplier,
                    invoice_no: state.invoice_no,
                    items: JSON.stringify(state.items)
                },
                freeze: true,
                freeze_message: __("Generating Purchase Receipt (GRN) in ERPNext..."),
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('GRN Submitted Successfully'),
                            message: r.message.message,
                            indicator: 'green'
                        });
                        me.clear_active_tab_state();
                    }
                }
            });

        } else if (this.active_tab === "transfer") {
            if (!state.from_warehouse || !state.to_warehouse) {
                frappe.show_alert({message: __("Please select both Source and Target Warehouses."), indicator: 'red'});
                return;
            }
            if (state.from_warehouse === state.to_warehouse) {
                frappe.show_alert({message: __("Source and Target Warehouses cannot be the same."), indicator: 'red'});
                return;
            }

            frappe.call({
                method: "smriti_retail_os.inventory_api.create_stock_transfer",
                args: {
                    from_warehouse: state.from_warehouse,
                    to_warehouse: state.to_warehouse,
                    items: JSON.stringify(state.items)
                },
                freeze: true,
                freeze_message: __("Generating Material Transfer Stock Entry..."),
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Transfer Submitted Successfully'),
                            message: r.message.message,
                            indicator: 'green'
                        });
                        me.clear_active_tab_state();
                    }
                }
            });

        } else if (this.active_tab === "adjustment") {
            if (!state.warehouse) {
                frappe.show_alert({message: __("Please select a Target Warehouse."), indicator: 'red'});
                return;
            }

            frappe.call({
                method: "smriti_retail_os.inventory_api.create_stock_adjustment",
                args: {
                    items: JSON.stringify(state.items),
                    reason: state.reason
                },
                freeze: true,
                freeze_message: __("Submitting Stock Adjustment Entry..."),
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Adjustment Submitted Successfully'),
                            message: r.message.message,
                            indicator: 'green'
                        });
                        me.clear_active_tab_state();
                    }
                }
            });

        } else if (this.active_tab === "audit") {
            if (!state.warehouse) {
                frappe.show_alert({message: __("Please select an Audit Warehouse."), indicator: 'red'});
                return;
            }

            frappe.call({
                method: "smriti_retail_os.inventory_api.create_stock_audit",
                args: {
                    items: JSON.stringify(state.items.map(i => {
                        return {
                            item_code: i.item_code,
                            warehouse: state.warehouse,
                            qty: i.qty
                        }
                    }))
                },
                freeze: true,
                freeze_message: __("Running Stock Reconciliation Audit..."),
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Audit Reconciled Successfully'),
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
        if (this.active_tab === "grn") {
            state.invoice_no = "";
            $("#smriti-hdr-invoice").val("");
        }
        this.render_active_tab_contents();
        this.focus_active_barcode();
    }
}
