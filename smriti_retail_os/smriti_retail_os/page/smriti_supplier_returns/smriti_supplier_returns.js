/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_supplier_returns/smriti_supplier_returns.js
 * @description: SMRITI Supplier Returns page controller.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-17
 * @version: 1.0.0
 * @license: MIT
 */

frappe.pages['smriti-supplier-returns'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Supplier Returns'),
        single_column: true
    });

    var controller = new SmritiSupplierReturnsController(wrapper, page);
}

class SmritiSupplierReturnsController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;
        this.masterReturnsList = [];
        this.activeReturnDoc = null;
        this.selectedGrnName = null;
        this.cartItems = [];
        this.warehousesList = [];
        this.defaultWarehouse = '';
        this.pinModalAction = null;

        this.setup_layout();
        this.bind_actions();
        this.init();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-supplier-returns-container">
                <!-- Topbar -->
                <div class="topbar">
                    <div class="topbar-breadcrumbs">
                        <span>SMRITI</span>
                        <span class="sep">/</span>
                        <span>Purchase</span>
                        <span class="sep">/</span>
                        <span class="active">${__('Supplier Returns')}</span>
                    </div>
                    <div class="topbar-right">
                        <button class="topbtn" id="btn-create-return" style="background:var(--primary-color); color:white; border-color:var(--primary-color);">
                            <span class="material-symbols-outlined">add</span> ${__('Create Return')}
                        </button>
                    </div>
                </div>

                <!-- Filter Bar -->
                <div class="filter-bar">
                    <input type="text" class="form-input search-input" id="smriti-sr-search" placeholder="${__('Search return no or supplier...')}">
                    <select class="form-input filter-select" id="smriti-sr-filter-status">
                        <option value="">${__('All Statuses')}</option>
                        <option value="Submitted">${__('Submitted')}</option>
                        <option value="Draft">${__('Draft')}</option>
                    </select>
                </div>

                <!-- Table -->
                <div class="table-wrap">
                    <table class="smriti-table">
                        <thead>
                            <tr>
                                <th>${__('Return Number')}</th>
                                <th>${__('Date & Time')}</th>
                                <th>${__('Supplier')}</th>
                                <th style="text-align:right;">${__('Grand Total')}</th>
                                <th style="text-align:center;">${__('Status')}</th>
                            </tr>
                        </thead>
                        <tbody id="smriti-returns-tbody">
                            <tr>
                                <td colspan="5" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">
                                    ${__('Loading Supplier Returns...')}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Details Drawer -->
                <div class="drawer-backdrop" id="smriti-sr-drawer-backdrop">
                    <div class="drawer" onclick="event.stopPropagation()">
                        <div class="drawer-header">
                            <div class="drawer-title" id="drw-id">${__('Return Details')}</div>
                            <button class="drawer-close" id="smriti-sr-drawer-close">&times;</button>
                        </div>
                        <div class="drawer-body">
                            <div class="section-card">
                                <div class="section-title">${__('General Details')}</div>
                                <div class="meta-row"><span class="meta-label">${__('Date & Time')}</span><span class="meta-value" id="drw-date"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Supplier')}</span><span class="meta-value" id="drw-supplier"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Status')}</span><span id="drw-status"></span></div>
                            </div>

                            <div class="section-card">
                                <div class="section-title">${__('Items Returned')}</div>
                                <table class="invoice-items-table">
                                    <thead>
                                        <tr>
                                            <th>${__('Product Description')}</th>
                                            <th style="text-align:center;">${__('Qty')}</th>
                                            <th style="text-align:right;">${__('Rate')}</th>
                                            <th style="text-align:right;">${__('Total')}</th>
                                        </tr>
                                    </thead>
                                    <tbody id="drw-items-tbody"></tbody>
                                </table>
                            </div>

                            <div class="section-card">
                                <div class="section-title">${__('Breakdown')}</div>
                                <div class="meta-row" style="border-top:1px solid var(--border-dark); padding-top:8px; margin-top:8px; font-size:1.05rem;"><span class="meta-label" style="color:var(--text-color); font-weight:700;">${__('Grand Total')}</span><span class="meta-value" id="drw-grand" style="color:var(--success-color); font-weight:800;"></span></div>
                            </div>
                        </div>
                        <div class="drawer-footer" id="drawer-footer-actions">
                            <button class="btn-print" id="btn-print-debit-note">
                                <span class="material-symbols-outlined">print</span> ${__('Print Debit Note')}
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Create Return Drawer (Modal) -->
                <div class="drawer-backdrop" id="smriti-sr-modal-backdrop">
                    <div class="drawer" style="max-width: 680px;" onclick="event.stopPropagation()">
                        <div class="drawer-header">
                            <div class="drawer-title">${__('Create Supplier Return')}</div>
                            <button class="drawer-close" id="smriti-sr-modal-close">&times;</button>
                        </div>
                        <div class="drawer-body">
                            <!-- Step 1: Select Purchase Receipt (GRN) -->
                            <div class="section-card" id="grn-select-section">
                                <div class="section-title">${__('Search & Select Original GRN')}</div>
                                <div style="position:relative; margin-bottom:12px;">
                                    <input type="text" class="form-input" id="grn-search-input" placeholder="${__('Search original GRN no. or supplier...')}" style="width:100%;">
                                    <div id="grn-search-results" style="position:absolute; left:0; right:0; top:40px; background:var(--card2-dark); border:1px solid var(--border2-dark); border-radius:var(--radius-sm-val); max-height:200px; overflow-y:auto; z-index:100; display:none; box-shadow:0 8px 16px rgba(0,0,0,0.5);"></div>
                                </div>
                                <div id="selected-grn-display" style="font-weight:600; font-size:0.85rem; display:none; background:rgba(99,102,241,0.08); padding:8px 12px; border-radius:var(--radius-sm-val); border:1px solid var(--border-dark);"></div>
                            </div>

                            <!-- Return Cart Section -->
                            <div class="section-card" id="cart-section" style="display:none;">
                                <div class="section-title">${__('Return Items List')}</div>
                                <div style="overflow-x:auto;">
                                    <table class="invoice-items-table" style="width:100%; min-width:450px;">
                                        <thead>
                                            <tr>
                                                <th>${__('Product Details')}</th>
                                                <th style="text-align:center; width:80px;">${__('Received')}</th>
                                                <th style="text-align:center; width:80px;">${__('Returned')}</th>
                                                <th style="text-align:center; width:80px;">${__('Return Qty')}</th>
                                                <th style="text-align:right; width:90px;">${__('Rate')}</th>
                                                <th style="text-align:right; width:90px;">${__('Total')}</th>
                                                <th style="text-align:center; width:120px;">${__('Warehouse')}</th>
                                            </tr>
                                        </thead>
                                        <tbody id="cart-items-tbody"></tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- Warehouse, Remarks & Summary -->
                            <div id="summary-section" style="display:none; grid-template-columns: 1fr 1fr; gap:16px;">
                                <div class="section-card">
                                    <div class="section-title">${__('Default Return Warehouse & Remarks')}</div>
                                    <div style="display:flex; flex-direction:column; gap:10px;">
                                        <div style="display:flex; flex-direction:column; gap:4px;">
                                            <label style="font-size:0.75rem; color:var(--text-muted-color); font-weight:600;">${__('Default Return Warehouse')}</label>
                                            <select class="form-input" id="modal-default-warehouse"></select>
                                        </div>
                                        <div style="display:flex; flex-direction:column; gap:4px;">
                                            <label style="font-size:0.75rem; color:var(--text-muted-color); font-weight:600;">${__('Remarks / Reason')}</label>
                                            <textarea class="form-input" id="modal-remarks" style="height:70px; resize:none; font-size:0.82rem;" placeholder="${__('Reason for return...')}"></textarea>
                                        </div>
                                    </div>
                                </div>
                                <div class="section-card" style="display:flex; flex-direction:column; justify-content:space-between;">
                                    <div class="section-title">${__('Return Summary')}</div>
                                    <div style="display:flex; flex-direction:column; gap:8px; flex:1; justify-content:center;">
                                        <div style="display:flex; justify-content:space-between; font-size:0.9rem;">
                                            <span class="meta-label">${__('Total Returned Items')}</span>
                                            <span class="meta-value" id="summary-total-qty">0</span>
                                        </div>
                                        <div style="display:flex; justify-content:space-between; font-size:1.05rem; border-top:1px solid var(--border-dark); padding-top:8px; margin-top:8px;">
                                            <span class="meta-label" style="font-weight:700; color:var(--text-color);">${__('Return Total')}</span>
                                            <span class="meta-value" id="summary-grand-total" style="color:var(--success-color); font-weight:800; font-size:1.15rem;">Rs. 0.00</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="drawer-footer" id="modal-footer" style="display:none;">
                            <button class="topbtn" style="flex:1; justify-content:center; padding:10px;" id="btn-modal-cancel">${__('Cancel')}</button>
                            <button class="btn-print" style="flex:1.5; background:var(--success-color);" id="btn-modal-submit">
                                <span class="material-symbols-outlined">check_circle</span> ${__('Submit Return')}
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Manager PIN Override Modal -->
                <div class="drawer-backdrop" id="smriti-pin-modal-backdrop" style="z-index:99999;">
                    <div class="drawer" style="max-width:360px; height:auto; margin:auto; border-radius:var(--radius-val); border:1px solid var(--border2-dark);" onclick="event.stopPropagation()">
                        <div class="drawer-header">
                            <div class="drawer-title">${__('Manager PIN Override')}</div>
                            <button class="drawer-close" id="smriti-pin-modal-close">&times;</button>
                        </div>
                        <div class="drawer-body" style="padding:20px; text-align:center;">
                            <div style="font-size:0.85rem; color:var(--text-muted-color); margin-bottom:16px;" id="pin-modal-message">${__('Enter SMRITI Manager PIN to authorize this action.')}</div>
                            <input type="password" class="form-input" id="manager-pin-input" placeholder="••••" style="width:120px; text-align:center; font-size:20px; letter-spacing:8px; padding:10px;" maxlength="8">
                        </div>
                        <div class="drawer-footer" style="padding:12px 20px;">
                            <button class="topbtn" style="flex:1; justify-content:center;" id="btn-pin-cancel">${__('Cancel')}</button>
                            <button class="btn-print" style="flex:1; background:var(--primary-color);" id="btn-pin-auth">${__('Authorize')}</button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_actions() {
        var me = this;
        this.wrapper.find("#btn-create-return").on("click", () => me.open_return_modal());
        this.wrapper.find("#smriti-sr-search").on("input", () => me.apply_filters());
        this.wrapper.find("#smriti-sr-filter-status").on("change", () => me.apply_filters());

        this.wrapper.find("#smriti-sr-drawer-close").on("click", () => me.close_drawer());
        this.wrapper.find("#smriti-sr-drawer-backdrop").on("click", () => me.close_drawer());
        this.wrapper.find("#btn-print-debit-note").on("click", () => me.print_receipt());

        this.wrapper.find("#smriti-sr-modal-close").on("click", () => me.close_return_modal());
        this.wrapper.find("#btn-modal-cancel").on("click", () => me.close_return_modal());
        this.wrapper.find("#smriti-sr-modal-backdrop").on("click", () => me.close_return_modal());

        this.wrapper.find("#grn-search-input").on("input", function() { me.handle_grn_search($(this).val()); });
        this.wrapper.find("#modal-default-warehouse").on("change", function() { me.update_cart_warehouses($(this).val()); });
        this.wrapper.find("#btn-modal-submit").on("click", () => me.save_return());

        // PIN modal
        this.wrapper.find("#smriti-pin-modal-close").on("click", () => me.close_pin_modal());
        this.wrapper.find("#btn-pin-cancel").on("click", () => me.close_pin_modal());
        this.wrapper.find("#btn-pin-auth").on("click", () => me.submit_pin_override());
        this.wrapper.find("#manager-pin-input").on("keydown", function(e) {
            if (e.key === 'Enter') me.submit_pin_override();
        });

        $(document).on("click", function(e) {
            if (!$(e.target).closest('#grn-search-input') && !$(e.target).closest('#grn-search-results')) {
                me.wrapper.find('#grn-search-results').hide();
            }
        });
    }

    init() {
        this.load_returns();
        this.load_warehouses();
    }

    load_returns() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Purchase Receipt',
                filters: { is_return: 1 },
                fields: ['name', 'posting_date', 'posting_time', 'supplier_name', 'grand_total', 'status', 'docstatus'],
                order_by: 'posting_date desc, posting_time desc',
                limit_page_length: 150
            },
            callback: function(r) {
                me.masterReturnsList = r.message || [];
                me.render_table(me.masterReturnsList);
            }
        });
    }

    load_warehouses() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Warehouse',
                filters: { is_group: 0 },
                fields: ['name', 'warehouse_name'],
                limit_page_length: 100
            },
            callback: function(r) {
                me.warehousesList = r.message || [];
                if (me.warehousesList.length) {
                    me.defaultWarehouse = me.warehousesList[0].name;
                }
                const whSelect = me.wrapper.find('#modal-default-warehouse');
                whSelect.empty();
                me.warehousesList.forEach(wh => {
                    whSelect.append(`<option value="${wh.name}">${wh.warehouse_name}</option>`);
                });
            }
        });
    }

    render_table(list) {
        var me = this;
        const tbody = this.wrapper.find('#smriti-returns-tbody');
        tbody.empty();

        if (!list.length) {
            tbody.html(`<tr><td colspan="5" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">${__('No supplier returns tracked.')}</td></tr>`);
            return;
        }

        list.forEach(pr => {
            const statusText = pr.docstatus === 1 ? 'Submitted' : 'Draft';
            const statusCls = statusText.toLowerCase();
            const tr = $(`
                <tr data-id="${pr.name}">
                    <td><span class="invoice-badge">${pr.name}</span></td>
                    <td>
                        <div style="font-weight:600;">${pr.posting_date}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted-color); margin-top:2px;">${pr.posting_time || ''}</div>
                    </td>
                    <td style="font-weight:600; color:var(--text-color);">${pr.supplier_name}</td>
                    <td style="text-align:right; font-weight:700; color:var(--success-color);">Rs. ${parseFloat(Math.abs(pr.grand_total)).toFixed(2)}</td>
                    <td style="text-align:center;">
                        <span class="status-badge ${statusCls}">${statusText}</span>
                    </td>
                </tr>
            `);
            tr.on("click", function() {
                me.load_return_details($(this).data("id"));
            });
            tbody.append(tr);
        });
    }

    apply_filters() {
        const q = this.wrapper.find('#smriti-sr-search').val().toLowerCase();
        const status = this.wrapper.find('#smriti-sr-filter-status').val();

        let filtered = this.masterReturnsList;

        if (q) {
            filtered = filtered.filter(pr => 
                pr.name.toLowerCase().includes(q) ||
                pr.supplier_name.toLowerCase().includes(q)
            );
        }
        if (status) {
            filtered = filtered.filter(pr => {
                const statusText = pr.docstatus === 1 ? 'Submitted' : 'Draft';
                return statusText === status;
            });
        }

        this.render_table(filtered);
    }

    load_return_details(returnId) {
        var me = this;
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Purchase Receipt',
                name: returnId
            },
            callback: function(r) {
                if (r.message) {
                    const doc = r.message;
                    me.activeReturnDoc = doc;

                    me.wrapper.find('#drw-id').text(doc.name);
                    me.wrapper.find('#drw-date').text(`${doc.posting_date} | ${doc.posting_time || ''}`);
                    me.wrapper.find('#drw-supplier').text(doc.supplier_name);
                    
                    const statusEl = me.wrapper.find('#drw-status');
                    const statusText = doc.docstatus === 1 ? 'Submitted' : 'Draft';
                    statusEl.attr('class', `status-badge ${statusText.toLowerCase()}`);
                    statusEl.text(statusText);

                    // Render Items
                    const tbody = me.wrapper.find('#drw-items-tbody');
                    tbody.empty();
                    doc.items.forEach(it => {
                        tbody.append(`
                            <tr>
                                <td>
                                    <div style="font-weight:600;color:var(--text-color);">${it.item_name}</div>
                                    <div style="font-size:0.75rem;color:var(--text-muted-color);margin-top:2px;">${it.item_code}</div>
                                </td>
                                <td style="text-align:center;font-weight:600;">${Math.abs(it.qty)}</td>
                                <td style="text-align:right;">Rs. ${parseFloat(it.rate).toFixed(2)}</td>
                                <td style="text-align:right;font-weight:600;">Rs. ${parseFloat(Math.abs(it.amount)).toFixed(2)}</td>
                            </tr>
                        `);
                    });

                    me.wrapper.find('#drw-grand').text(`Rs. ${parseFloat(Math.abs(doc.grand_total)).toFixed(2)}`);
                    me.wrapper.find('#smriti-sr-drawer-backdrop').addClass('open');
                }
            }
        });
    }

    print_receipt() {
        if (!this.activeReturnDoc) return;
        const url = `/printview?doctype=Purchase%20Receipt&name=${encodeURIComponent(this.activeReturnDoc.name)}`;
        window.open(url, '_blank');
    }

    close_drawer() {
        this.wrapper.find('#smriti-sr-drawer-backdrop').removeClass('open');
        this.activeReturnDoc = null;
    }

    open_return_modal() {
        this.selectedGrnName = null;
        this.cartItems = [];
        this.wrapper.find('#grn-search-input').val('');
        this.wrapper.find('#selected-grn-display').hide();
        this.wrapper.find('#cart-section').hide();
        this.wrapper.find('#summary-section').hide();
        this.wrapper.find('#modal-footer').hide();
        this.wrapper.find('#modal-remarks').val('');
        
        this.wrapper.find('#modal-default-warehouse').val(this.defaultWarehouse);
        this.wrapper.find('#smriti-sr-modal-backdrop').addClass('open');
    }

    close_return_modal() {
        this.wrapper.find('#smriti-sr-modal-backdrop').removeClass('open');
    }

    handle_grn_search(query) {
        var me = this;
        if (query.length < 2) {
            me.wrapper.find('#grn-search-results').hide();
            return;
        }
        frappe.call({
            method: 'smriti_retail_os.api.supplier_returns_api.get_submitted_receipts',
            args: { query: query },
            callback: function(r) {
                const resultsDiv = me.wrapper.find('#grn-search-results');
                resultsDiv.empty();
                const list = r.message || [];
                if (!list.length) {
                    resultsDiv.append(`<div style="padding:10px; color:var(--text-muted-color);">${__('No submitted GRNs found.')}</div>`);
                } else {
                    list.forEach(pr => {
                        const row = $(`
                            <div style="padding:10px; border-bottom:1px solid var(--border-dark); cursor:pointer; font-size:0.85rem;">
                                <span style="font-weight:700; color:var(--primary-lt-color);">${pr.name}</span> | 
                                <span>${pr.supplier_name}</span> | 
                                <span style="color:var(--success-color);">Rs. ${parseFloat(pr.grand_total).toFixed(2)}</span>
                                <div style="font-size:0.75rem; color:var(--text-muted-color);">${pr.posting_date}</div>
                            </div>
                        `);
                        row.on("click", function() {
                            resultsDiv.hide();
                            me.wrapper.find('#grn-search-input').val('');
                            me.select_grn(pr.name);
                        });
                        resultsDiv.append(row);
                    });
                }
                resultsDiv.show();
            }
        });
    }

    select_grn(grnName) {
        var me = this;
        frappe.call({
            method: 'smriti_retail_os.api.supplier_returns_api.get_receipt_details',
            args: { receipt_name: grnName },
            callback: function(r) {
                if (r.message) {
                    const details = r.message;
                    me.selectedGrnName = details.name;

                    const grnDisp = me.wrapper.find('#selected-grn-display');
                    grnDisp.html(`
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <strong>${__('Selected GRN:')}</strong> <span class="invoice-badge">${details.name}</span>
                                <span style="margin-left:8px; color:var(--text-muted-color);">${details.supplier_name}</span>
                            </div>
                            <button style="background:none; border:none; color:var(--danger-color); cursor:pointer;" class="btn-clear-grn">
                                <span class="material-symbols-outlined" style="font-size:18px;">close</span>
                            </button>
                        </div>
                    `);
                    grnDisp.find('.btn-clear-grn').on("click", function() { me.clear_selected_grn(); });
                    grnDisp.show();

                    me.cartItems = details.items.map(it => ({
                        ...it,
                        return_qty: 0,
                        warehouse: it.warehouse || me.defaultWarehouse
                    }));

                    me.render_cart();

                    me.wrapper.find('#cart-section').show();
                    me.wrapper.find('#summary-section').css('display', 'grid');
                    me.wrapper.find('#modal-footer').show();
                }
            }
        });
    }

    clear_selected_grn() {
        this.selectedGrnName = null;
        this.cartItems = [];
        this.wrapper.find('#selected-grn-display').hide();
        this.wrapper.find('#cart-section').hide();
        this.wrapper.find('#summary-section').hide();
        this.wrapper.find('#modal-footer').hide();
    }

    render_cart() {
        var me = this;
        const tbody = this.wrapper.find('#cart-items-tbody');
        tbody.empty();

        if (!this.cartItems.length) {
            tbody.html('<tr><td colspan="7" style="text-align:center; color:var(--text-muted-color); padding:20px 0;">No items found.</td></tr>');
            this.update_summary();
            return;
        }

        this.cartItems.forEach((item, index) => {
            const warehouseOptions = this.warehousesList.map(wh => `
                <option value="${wh.name}" ${wh.name === item.warehouse ? 'selected' : ''}>${wh.warehouse_name}</option>
            `).join('');

            const row = $(`
                <tr>
                    <td>
                        <div style="font-weight:600; color:var(--text-color);">${item.item_name}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted-color);">${item.item_code}</div>
                    </td>
                    <td style="text-align:center; font-weight:600;">${item.qty}</td>
                    <td style="text-align:center; color:var(--text-muted-color);">${item.returned_qty}</td>
                    <td style="text-align:center;">
                        <input type="number" class="form-input inp-qty" style="width:70px; text-align:center; padding:4px;" value="${item.return_qty}" min="0" step="any" max="${item.max_return}">
                    </td>
                    <td style="text-align:right;">Rs. ${parseFloat(item.rate).toFixed(2)}</td>
                    <td style="text-align:right; font-weight:600;">
                        Rs. ${(item.return_qty * item.rate).toFixed(2)}
                    </td>
                    <td>
                        <select class="form-input select-wh" style="width:100%; padding:4px; font-size:0.8rem;">
                            ${warehouseOptions}
                        </select>
                    </td>
                </tr>
            `);

            row.find('.inp-qty').on("change", function() { me.update_cart_item_qty(index, $(this).val()); });
            row.find('.select-wh').on("change", function() { me.cartItems[index].warehouse = $(this).val(); });

            tbody.append(row);
        });

        this.update_summary();
    }

    update_cart_warehouses(whVal) {
        this.cartItems.forEach(it => {
            it.warehouse = whVal;
        });
        this.render_cart();
    }

    update_cart_item_qty(index, val) {
        const returnQty = parseFloat(val);
        if (isNaN(returnQty) || returnQty < 0) return;
        
        const item = this.cartItems[index];
        if (returnQty > item.max_return) {
            frappe.show_alert({message: __('Cannot return more than remaining quantity (') + item.max_return + ')', indicator: 'red'});
            this.render_cart();
            return;
        }
        
        item.return_qty = returnQty;
        this.render_cart();
    }

    update_summary() {
        let totalQty = 0;
        let grandTotal = 0;
        this.cartItems.forEach(it => {
            totalQty += it.return_qty;
            grandTotal += it.return_qty * it.rate;
        });
        
        this.wrapper.find('#summary-total-qty').text(totalQty.toFixed(2));
        this.wrapper.find('#summary-grand-total').text(`Rs. ${grandTotal.toFixed(2)}`);
    }

    save_return(managerPin) {
        var me = this;
        const returning = this.cartItems.filter(it => it.return_qty > 0);
        if (!returning.length) {
            frappe.show_alert({message: __('Please specify a return quantity greater than 0 for at least one item.'), indicator: 'red'});
            return;
        }
        
        const itemsPayload = returning.map(it => ({
            receipt_item_name: it.receipt_item_name,
            qty: it.return_qty,
            warehouse: it.warehouse
        }));
        
        const remarks = this.wrapper.find('#modal-remarks').val();
        
        let args = {
            receipt_name: this.selectedGrnName,
            return_items: JSON.stringify(itemsPayload),
            remarks: remarks
        };
        if (managerPin) {
            args.manager_pin = managerPin;
        }

        frappe.call({
            method: 'smriti_retail_os.api.supplier_returns_api.submit_supplier_return',
            args: args,
            freeze: true,
            freeze_message: __('Submitting Supplier Return...'),
            callback: function(r) {
                frappe.show_alert({message: r.message.message, indicator: 'green'});
                me.close_pin_modal();
                me.close_return_modal();
                me.load_returns();
            },
            error: function(r) {
                const err = r.message || r.exc || '';
                if (err.includes('Access Denied') || err.includes('restricted to Cashiers') || (r.response && r.response._server_messages && r.response._server_messages.includes('restricted to Cashiers'))) {
                    me.open_pin_modal(__('Manager authorization required to submit supplier returns.'), function(pin) {
                        me.save_return(pin);
                    });
                }
            }
        });
    }

    open_pin_modal(msg, callback) {
        this.wrapper.find('#pin-modal-message').text(msg);
        this.wrapper.find('#manager-pin-input').val('');
        this.pinModalAction = callback;
        this.wrapper.find('#smriti-pin-modal-backdrop').addClass('open');
        this.wrapper.find('#manager-pin-input').focus();
    }

    close_pin_modal() {
        this.wrapper.find('#smriti-pin-modal-backdrop').removeClass('open');
        this.pinModalAction = null;
    }

    submit_pin_override() {
        const pin = this.wrapper.find('#manager-pin-input').val();
        if (!pin) {
            frappe.show_alert({message: __('PIN is required'), indicator: 'red'});
            return;
        }
        if (this.pinModalAction) {
            this.pinModalAction(pin);
        }
    }
}
