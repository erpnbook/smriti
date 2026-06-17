/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_sales_return/smriti_sales_return.js
 * @description: SMRITI Sales Returns & Credit Notes page controller.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-17
 * @version: 1.0.0
 * @license: MIT
 */

frappe.pages['smriti-sales-return'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Sales Returns & Credit Notes'),
        single_column: true
    });

    var controller = new SmritiSalesReturnController(wrapper, page);
}

class SmritiSalesReturnController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;
        this.masterReturnsList = [];
        this.activeReturnDoc = null;
        this.returnMode = 'single';
        this.selectedCustomer = { name: 'Walk-In Customer', customer_name: 'Walk-In Customer' };
        this.selectedBills = [];
        this.cartItems = [];
        this.warehousesList = [];
        this.defaultWarehouse = '';
        this.editingReturnName = null;
        this.pinModalAction = null;

        this.setup_layout();
        this.bind_actions();
        this.init();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-sales-return-container">
                <!-- Topbar -->
                <div class="topbar">
                    <div class="topbar-breadcrumbs">
                        <span>SMRITI</span>
                        <span class="sep">/</span>
                        <span class="active">${__('Sales Returns & Credit Notes')}</span>
                    </div>
                    <div class="topbar-right">
                        <button class="topbtn" id="btn-create-return" style="background:var(--primary-color); color:white; border-color:var(--primary-color);">
                            <span class="material-symbols-outlined">add</span> ${__('Create Return')}
                        </button>
                    </div>
                </div>

                <!-- Filter Bar -->
                <div class="filter-bar">
                    <input type="text" class="form-input search-input" id="smriti-ret-search" placeholder="${__('Search return no or customer...')}">
                    <select class="form-input filter-select" id="smriti-ret-filter-status">
                        <option value="">${__('All Statuses')}</option>
                        <option value="Paid">${__('Paid')}</option>
                        <option value="Unpaid">${__('Unpaid')}</option>
                        <option value="Draft">${__('Draft')}</option>
                        <option value="Cancelled">${__('Cancelled')}</option>
                    </select>
                </div>

                <!-- Table -->
                <div class="table-wrap">
                    <table class="smriti-table">
                        <thead>
                            <tr>
                                <th>${__('Return Number')}</th>
                                <th>${__('Date & Time')}</th>
                                <th>${__('Customer')}</th>
                                <th style="text-align:right;">${__('Grand Total')}</th>
                                <th style="text-align:right;">${__('Outstanding')}</th>
                                <th style="text-align:center;">${__('Status')}</th>
                            </tr>
                        </thead>
                        <tbody id="smriti-returns-tbody">
                            <tr>
                                <td colspan="6" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">
                                    ${__('Loading Sales Returns...')}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Details Drawer -->
                <div class="drawer-backdrop" id="smriti-ret-drawer-backdrop">
                    <div class="drawer" onclick="event.stopPropagation()">
                        <div class="drawer-header">
                            <div class="drawer-title" id="drw-id">${__('Return Details')}</div>
                            <button class="drawer-close" id="smriti-ret-drawer-close">&times;</button>
                        </div>
                        <div class="drawer-body">
                            <div class="section-card">
                                <div class="section-title">${__('General Details')}</div>
                                <div class="meta-row"><span class="meta-label">${__('Date & Time')}</span><span class="meta-value" id="drw-date"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Customer')}</span><span class="meta-value" id="drw-customer"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Outstanding')}</span><span class="meta-value" id="drw-outstanding" style="color:var(--danger-color);"></span></div>
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
                                <div class="meta-row"><span class="meta-label">${__('Net Amount')}</span><span class="meta-value" id="drw-net"></span></div>
                                <div class="meta-row"><span class="meta-label">${__('Taxes & Charges')}</span><span class="meta-value" id="drw-tax"></span></div>
                                <div class="meta-row" style="border-top:1px solid var(--border-dark); padding-top:8px; margin-top:8px; font-size:1.05rem;"><span class="meta-label" style="color:var(--text-color); font-weight:700;">${__('Grand Total')}</span><span class="meta-value" id="drw-grand" style="color:var(--success-color); font-weight:800;"></span></div>
                            </div>
                        </div>
                        <div class="drawer-footer" id="drawer-footer-actions" style="display:flex; flex-direction:column; gap:8px;"></div>
                    </div>
                </div>

                <!-- Create/Edit Return Modal -->
                <div class="drawer-backdrop" id="smriti-ret-modal-backdrop">
                    <div class="drawer" style="max-width: 680px;" onclick="event.stopPropagation()">
                        <div class="drawer-header">
                            <div class="drawer-title" id="modal-title">${__('Create Sales Return')}</div>
                            <button class="drawer-close" id="smriti-ret-modal-close">&times;</button>
                        </div>
                        <div class="drawer-body">
                            <!-- Step 1: Mode Selection -->
                            <div class="section-card" id="mode-selection-section">
                                <div class="section-title">${__('Return Mode')}</div>
                                <div style="display: flex; gap: 12px; margin-bottom: 12px;">
                                    <label style="flex:1; display:flex; flex-direction:column; gap:6px; padding:12px; border:1px solid var(--border-dark); border-radius:var(--radius-sm-val); cursor:pointer; background:rgba(255,255,255,0.02);" id="label-mode-single">
                                        <input type="radio" name="return-mode" id="mode-single" value="single" checked style="align-self:flex-start;">
                                        <span style="font-weight:700; font-size:0.9rem;">${__('Against Single Bill')}</span>
                                        <span style="font-size:0.75rem; color:var(--text-muted-color);">${__('Return items from a specific invoice')}</span>
                                    </label>
                                    <label style="flex:1; display:flex; flex-direction:column; gap:6px; padding:12px; border:1px solid var(--border-dark); border-radius:var(--radius-sm-val); cursor:pointer; background:rgba(255,255,255,0.02);" id="label-mode-multiple">
                                        <input type="radio" name="return-mode" id="mode-multiple" value="multiple" style="align-self:flex-start;">
                                        <span style="font-weight:700; font-size:0.9rem;">${__('Against Multiple Bills')}</span>
                                        <span style="font-size:0.75rem; color:var(--text-muted-color);">${__('Return items from multiple invoices')}</span>
                                    </label>
                                    <label style="flex:1; display:flex; flex-direction:column; gap:6px; padding:12px; border:1px solid var(--border-dark); border-radius:var(--radius-sm-val); cursor:pointer; background:rgba(255,255,255,0.02);" id="label-mode-standalone">
                                        <input type="radio" name="return-mode" id="mode-standalone" value="standalone" style="align-self:flex-start;">
                                        <span style="font-weight:700; font-size:0.9rem;">${__('Without Bill (Standalone)')}</span>
                                        <span style="font-size:0.75rem; color:var(--text-muted-color);">${__('Return items without prior invoice')}</span>
                                    </label>
                                </div>
                            </div>

                            <!-- Customer Search (Standalone mode only) -->
                            <div class="section-card" id="customer-select-section" style="display:none;">
                                <div class="section-title">${__('Customer Selection')}</div>
                                <div style="position:relative;">
                                    <input type="text" class="form-input" id="cust-search-input" placeholder="${__('Search customer name or mobile...')}" style="width:100%;">
                                    <div id="cust-search-results" style="position:absolute; left:0; right:0; top:40px; background:var(--card2-dark); border:1px solid var(--border2-dark); border-radius:var(--radius-sm-val); max-height:200px; overflow-y:auto; z-index:100; display:none; box-shadow:0 8px 16px rgba(0,0,0,0.5);"></div>
                                </div>
                                <div style="margin-top:10px; font-weight:600; font-size:0.85rem;" id="selected-customer-display">${__('Selected Customer: Walk-In Customer')}</div>
                            </div>

                            <!-- Invoice Search (Single/Multiple modes) -->
                            <div class="section-card" id="bill-select-section">
                                <div class="section-title" id="bill-select-title">${__('Select Original Bill')}</div>
                                <div style="position:relative; margin-bottom:12px;">
                                    <input type="text" class="form-input" id="bill-search-input" placeholder="${__('Search original bill no. or customer...')}" style="width:100%;">
                                    <div id="bill-search-results" style="position:absolute; left:0; right:0; top:40px; background:var(--card2-dark); border:1px solid var(--border2-dark); border-radius:var(--radius-sm-val); max-height:200px; overflow-y:auto; z-index:100; display:none; box-shadow:0 8px 16px rgba(0,0,0,0.5);"></div>
                                </div>
                                <div id="selected-bills-list" style="display:flex; flex-direction:column; gap:6px;"></div>
                            </div>

                            <!-- Standalone Item Search (Standalone mode only) -->
                            <div class="section-card" id="item-search-section" style="display:none;">
                                <div class="section-title">${__('Search & Add Items')}</div>
                                <div style="position:relative;">
                                    <input type="text" class="form-input" id="item-search-input" placeholder="${__('Search item code, name, or barcode...')}" style="width:100%;">
                                    <div id="item-search-results" style="position:absolute; left:0; right:0; top:40px; background:var(--card2-dark); border:1px solid var(--border2-dark); border-radius:var(--radius-sm-val); max-height:200px; overflow-y:auto; z-index:100; display:none; box-shadow:0 8px 16px rgba(0,0,0,0.5);"></div>
                                </div>
                            </div>

                            <!-- Return Cart Section -->
                            <div class="section-card">
                                <div class="section-title">${__('Return Items List')}</div>
                                <div style="overflow-x:auto;">
                                    <table class="invoice-items-table" style="width:100%; min-width:450px;">
                                        <thead>
                                            <tr>
                                                <th>${__('Product Details')}</th>
                                                <th style="text-align:center; width:80px;">${__('Qty')}</th>
                                                <th style="text-align:right; width:90px;">${__('Rate')}</th>
                                                <th style="text-align:right; width:90px;">${__('Total')}</th>
                                                <th style="text-align:center; width:120px;">${__('Warehouse')}</th>
                                                <th style="text-align:center; width:40px;"></th>
                                            </tr>
                                        </thead>
                                        <tbody id="cart-items-tbody">
                                            <tr><td colspan="6" style="text-align:center; color:var(--text-muted-color); padding:20px 0;">${__('No items selected for return.')}</td></tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- Warehouse, Remarks & Summary -->
                            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                                <div class="section-card">
                                    <div class="section-title">${__('Target Warehouse & Remarks')}</div>
                                    <div style="display:flex; flex-direction:column; gap:10px;">
                                        <div style="display:flex; flex-direction:column; gap:4px;">
                                            <label style="font-size:0.75rem; color:var(--text-muted-color); font-weight:600;">${__('Default Return Warehouse')}</label>
                                            <select class="form-input" id="modal-default-warehouse"></select>
                                        </div>
                                        <div style="display:flex; flex-direction:column; gap:4px;">
                                            <label style="font-size:0.75rem; color:var(--text-muted-color); font-weight:600;">${__('Remarks')}</label>
                                            <textarea class="form-input" id="modal-remarks" style="height:70px; resize:none; font-size:0.82rem;" placeholder="${__('Reason for return...')}"></textarea>
                                        </div>
                                    </div>
                                </div>
                                <div class="section-card" style="display:flex; flex-direction:column; justify-content:space-between;">
                                    <div class="section-title">${__('Return Summary')}</div>
                                    <div style="display:flex; flex-direction:column; gap:8px; flex:1; justify-content:center;">
                                        <div style="display:flex; justify-content:space-between; font-size:0.9rem;">
                                            <span class="meta-label">${__('Total Items')}</span>
                                            <span class="meta-value" id="summary-total-qty">0</span>
                                        </div>
                                        <div style="display:flex; justify-content:space-between; font-size:1.05rem; border-top:1px solid var(--border-dark); padding-top:8px; margin-top:8px;">
                                            <span class="meta-label" style="font-weight:700; color:var(--text-color);">${__('Refund Total')}</span>
                                            <span class="meta-value" id="summary-grand-total" style="color:var(--success-color); font-weight:800; font-size:1.15rem;">Rs. 0.00</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="drawer-footer">
                            <button class="topbtn" style="flex:1; justify-content:center; padding:10px;" id="btn-modal-cancel">${__('Cancel')}</button>
                            <button class="btn-print" style="flex:1.2; background:var(--accent-color); color:var(--bg-dark);" id="btn-modal-draft">
                                <span class="material-symbols-outlined">drafts</span> ${__('Save Draft')}
                            </button>
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
        this.wrapper.find("#smriti-ret-search").on("input", () => me.apply_filters());
        this.wrapper.find("#smriti-ret-filter-status").on("change", () => me.apply_filters());

        this.wrapper.find("#smriti-ret-drawer-close").on("click", () => me.close_drawer());
        this.wrapper.find("#smriti-ret-drawer-backdrop").on("click", () => me.close_drawer());

        this.wrapper.find("#smriti-ret-modal-close").on("click", () => me.close_return_modal());
        this.wrapper.find("#btn-modal-cancel").on("click", () => me.close_return_modal());
        this.wrapper.find("#smriti-ret-modal-backdrop").on("click", () => me.close_return_modal());

        // Mode radio selections
        this.wrapper.find("#label-mode-single").on("click", () => me.set_return_mode('single'));
        this.wrapper.find("#label-mode-multiple").on("click", () => me.set_return_mode('multiple'));
        this.wrapper.find("#label-mode-standalone").on("click", () => me.set_return_mode('standalone'));

        // Searches
        this.wrapper.find("#cust-search-input").on("input", function() { me.handle_customer_search($(this).val()); });
        this.wrapper.find("#bill-search-input").on("input", function() { me.handle_bill_search($(this).val()); });
        this.wrapper.find("#item-search-input").on("input", function() { me.handle_item_search($(this).val()); });

        this.wrapper.find("#modal-default-warehouse").on("change", function() { me.update_cart_warehouses($(this).val()); });

        // Save / Submit buttons
        this.wrapper.find("#btn-modal-draft").on("click", () => me.save_return(true));
        this.wrapper.find("#btn-modal-submit").on("click", () => me.save_return(false));

        // PIN modal
        this.wrapper.find("#smriti-pin-modal-close").on("click", () => me.close_pin_modal());
        this.wrapper.find("#btn-pin-cancel").on("click", () => me.close_pin_modal());
        this.wrapper.find("#btn-pin-auth").on("click", () => me.submit_pin_override());
        this.wrapper.find("#manager-pin-input").on("keydown", function(e) {
            if (e.key === 'Enter') me.submit_pin_override();
        });

        // Click outside search results to close
        $(document).on("click", function(e) {
            if (!$(e.target).closest('#cust-search-input') && !$(e.target).closest('#cust-search-results')) {
                me.wrapper.find('#cust-search-results').hide();
            }
            if (!$(e.target).closest('#bill-search-input') && !$(e.target).closest('#bill-search-results')) {
                me.wrapper.find('#bill-search-results').hide();
            }
            if (!$(e.target).closest('#item-search-input') && !$(e.target).closest('#item-search-results')) {
                me.wrapper.find('#item-search-results').hide();
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
                doctype: 'Sales Invoice',
                filters: { is_return: 1 },
                fields: ['name', 'posting_date', 'posting_time', 'customer_name', 'grand_total', 'outstanding_amount', 'status', 'docstatus'],
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
            tbody.html(`<tr><td colspan="6" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">${__('No sales returns tracked.')}</td></tr>`);
            return;
        }

        list.forEach(inv => {
            const statusCls = inv.status.toLowerCase();
            const tr = $(`
                <tr data-id="${inv.name}">
                    <td><span class="invoice-badge">${inv.name}</span></td>
                    <td>
                        <div style="font-weight:600;">${inv.posting_date}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted-color); margin-top:2px;">${inv.posting_time || ''}</div>
                    </td>
                    <td style="font-weight:600; color:var(--text-color);">${inv.customer_name}</td>
                    <td style="text-align:right; font-weight:700; color:var(--success-color);">Rs. ${parseFloat(inv.grand_total).toFixed(2)}</td>
                    <td style="text-align:right; font-weight:600; color:${parseFloat(inv.outstanding_amount) > 0 ? 'var(--danger-color)' : 'var(--text-muted-color)'};">Rs. ${parseFloat(inv.outstanding_amount).toFixed(2)}</td>
                    <td style="text-align:center;">
                        <span class="status-badge ${statusCls}">${inv.status}</span>
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
        const q = this.wrapper.find('#smriti-ret-search').val().toLowerCase();
        const status = this.wrapper.find('#smriti-ret-filter-status').val();

        let filtered = this.masterReturnsList;

        if (q) {
            filtered = filtered.filter(inv => 
                inv.name.toLowerCase().includes(q) ||
                inv.customer_name.toLowerCase().includes(q)
            );
        }
        if (status) {
            filtered = filtered.filter(inv => inv.status === status);
        }

        this.render_table(filtered);
    }

    load_return_details(returnId) {
        var me = this;
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Sales Invoice',
                name: returnId
            },
            callback: function(r) {
                if (r.message) {
                    const doc = r.message;
                    me.activeReturnDoc = doc;

                    me.wrapper.find('#drw-id').text(doc.name);
                    me.wrapper.find('#drw-date').text(`${doc.posting_date} | ${doc.posting_time || ''}`);
                    me.wrapper.find('#drw-customer').text(doc.customer_name);
                    me.wrapper.find('#drw-outstanding').text(`Rs. ${parseFloat(doc.outstanding_amount).toFixed(2)}`);
                    
                    const statusEl = me.wrapper.find('#drw-status');
                    statusEl.attr('class', `status-badge ${doc.status.toLowerCase()}`);
                    statusEl.text(doc.status);

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
                                <td style="text-align:right;font-weight:600;">Rs. ${parseFloat(it.amount).toFixed(2)}</td>
                            </tr>
                        `);
                    });

                    me.wrapper.find('#drw-net').text(`Rs. ${parseFloat(doc.net_total).toFixed(2)}`);
                    me.wrapper.find('#drw-tax').text(`Rs. ${parseFloat(doc.total_taxes_and_charges || 0).toFixed(2)}`);
                    me.wrapper.find('#drw-grand').text(`Rs. ${parseFloat(doc.grand_total).toFixed(2)}`);

                    // Set up action buttons in footer
                    const footer = me.wrapper.find('#drawer-footer-actions');
                    footer.empty();
                    
                    footer.append(`
                        <button class="btn-print" id="btn-print-credit-note">
                            <span class="material-symbols-outlined">print</span> ${__('Print Credit Note')}
                        </button>
                    `);
                    me.wrapper.find("#btn-print-credit-note").on("click", () => me.print_receipt());

                    if (doc.docstatus === 0) {
                        footer.append(`
                            <button class="btn-print" style="background:var(--accent-color); color:var(--bg-dark);" id="btn-edit-return">
                                <span class="material-symbols-outlined">edit</span> ${__('Edit Return')}
                            </button>
                            <button class="btn-print" style="background:var(--danger-color);" id="btn-delete-return">
                                <span class="material-symbols-outlined">delete</span> ${__('Delete Draft')}
                            </button>
                        `);
                        me.wrapper.find("#btn-edit-return").on("click", () => me.edit_draft_return(doc.name));
                        me.wrapper.find("#btn-delete-return").on("click", () => me.delete_return_prompt(doc.name, true));
                    } else if (doc.docstatus === 1) {
                        footer.append(`
                            <button class="btn-print" style="background:var(--danger-color);" id="btn-cancel-return">
                                <span class="material-symbols-outlined">cancel</span> ${__('Cancel Return')}
                            </button>
                        `);
                        me.wrapper.find("#btn-cancel-return").on("click", () => me.delete_return_prompt(doc.name, false));
                    }

                    me.wrapper.find('#smriti-ret-drawer-backdrop').addClass('open');
                }
            }
        });
    }

    print_receipt() {
        if (!this.activeReturnDoc) return;
        const url = `/printview?doctype=Sales%20Invoice&name=${encodeURIComponent(this.activeReturnDoc.name)}`;
        window.open(url, '_blank');
    }

    close_drawer() {
        this.wrapper.find('#smriti-ret-drawer-backdrop').removeClass('open');
        this.activeReturnDoc = null;
    }

    open_return_modal() {
        this.editingReturnName = null;
        this.wrapper.find('#modal-title').text(__('Create Sales Return'));
        this.wrapper.find('#mode-selection-section').show();

        this.selectedBills = [];
        this.cartItems = [];
        this.selectedCustomer = { name: 'Walk-In Customer', customer_name: 'Walk-In Customer' };
        this.wrapper.find('#selected-customer-display').text(__('Selected Customer: Walk-In Customer'));
        this.wrapper.find('#modal-remarks').val('');
        this.wrapper.find('#bill-search-input').val('');
        this.wrapper.find('#cust-search-input').val('');
        this.wrapper.find('#item-search-input').val('');
        this.wrapper.find('#selected-bills-list').empty();

        this.wrapper.find('#mode-single').prop('checked', true);
        this.set_return_mode('single');

        this.wrapper.find('#modal-default-warehouse').val(this.defaultWarehouse);
        this.wrapper.find('#smriti-ret-modal-backdrop').addClass('open');
    }

    close_return_modal() {
        this.wrapper.find('#smriti-ret-modal-backdrop').removeClass('open');
    }

    set_return_mode(mode) {
        this.returnMode = mode;
        this.selectedBills = [];
        this.cartItems = [];

        this.wrapper.find('#selected-bills-list').empty();
        this.wrapper.find('#bill-search-input').val('');
        this.wrapper.find('#cust-search-input').val('');
        this.wrapper.find('#item-search-input').val('');

        if (mode === 'standalone') {
            this.wrapper.find('#customer-select-section').show();
            this.wrapper.find('#bill-select-section').hide();
            this.wrapper.find('#item-search-section').show();
        } else {
            this.wrapper.find('#customer-select-section').hide();
            this.wrapper.find('#bill-select-section').show();
            this.wrapper.find('#item-search-section').hide();

            const title = mode === 'single' ? __('Select Original Bill') : __('Select Original Bills (Multiple)');
            this.wrapper.find('#bill-select-title').text(title);
        }

        this.render_cart();
    }

    handle_customer_search(query) {
        var me = this;
        if (query.length < 2) {
            me.wrapper.find('#cust-search-results').hide();
            return;
        }
        frappe.call({
            method: 'smriti_retail_os.billing_api.search_customer',
            args: { query: query },
            callback: function(r) {
                const resultsDiv = me.wrapper.find('#cust-search-results');
                resultsDiv.empty();
                const list = r.message || [];
                if (!list.length) {
                    resultsDiv.append(`<div style="padding:10px; color:var(--text-muted-color);">${__('No customers found.')}</div>`);
                } else {
                    list.forEach(c => {
                        const row = $(`
                            <div style="padding:10px; border-bottom:1px solid var(--border-dark); cursor:pointer; font-size:0.85rem;">
                                <span style="font-weight:700;">${c.customer_name}</span> | 
                                <span style="color:var(--text-muted-color);">${c.mobile_no || 'No Mobile'}</span>
                            </div>
                        `);
                        row.on("click", function() {
                            me.selectedCustomer = c;
                            me.wrapper.find('#selected-customer-display').text(__('Selected Customer: ') + c.customer_name);
                            resultsDiv.hide();
                            me.wrapper.find('#cust-search-input').val('');
                        });
                        resultsDiv.append(row);
                    });
                }
                resultsDiv.show();
            }
        });
    }

    handle_bill_search(query) {
        var me = this;
        if (query.length < 2) {
            me.wrapper.find('#bill-search-results').hide();
            return;
        }
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Sales Invoice',
                filters: {
                    docstatus: 1,
                    is_return: 0
                },
                or_filters: {
                    name: ['like', '%' + query + '%'],
                    customer_name: ['like', '%' + query + '%']
                },
                fields: ['name', 'posting_date', 'customer_name', 'grand_total'],
                limit_page_length: 10
            },
            callback: function(r) {
                const resultsDiv = me.wrapper.find('#bill-search-results');
                resultsDiv.empty();
                const list = r.message || [];
                if (!list.length) {
                    resultsDiv.append(`<div style="padding:10px; color:var(--text-muted-color);">${__('No invoices found.')}</div>`);
                } else {
                    list.forEach(inv => {
                        const row = $(`
                            <div style="padding:10px; border-bottom:1px solid var(--border-dark); cursor:pointer; font-size:0.85rem;">
                                <span style="font-weight:700; color:var(--primary-lt-color);">${inv.name}</span> | 
                                <span>${inv.customer_name}</span> | 
                                <span style="color:var(--success-color);">Rs. ${parseFloat(inv.grand_total).toFixed(2)}</span>
                                <div style="font-size:0.75rem; color:var(--text-muted-color);">${inv.posting_date}</div>
                            </div>
                        `);
                        row.on("click", function() {
                            resultsDiv.hide();
                            me.wrapper.find('#bill-search-input').val('');
                            me.select_bill(inv.name);
                        });
                        resultsDiv.append(row);
                    });
                }
                resultsDiv.show();
            }
        });
    }

    select_bill(invoiceName) {
        var me = this;
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Sales Invoice',
                name: invoiceName
            },
            callback: function(r) {
                if (r.message) {
                    const doc = r.message;
                    if (me.returnMode === 'single') {
                        me.selectedBills = [doc];
                        me.cartItems = [];
                        me.selectedCustomer = { name: doc.customer, customer_name: doc.customer_name };
                    } else {
                        if (me.selectedBills.find(b => b.name === doc.name)) {
                            frappe.show_alert({message: __('Invoice already selected'), indicator: 'blue'});
                            return;
                        }
                        me.selectedBills.push(doc);
                    }

                    doc.items.forEach(it => {
                        const existing = me.cartItems.find(item => item.item_code === it.item_code && item.sales_invoice === doc.name);
                        if (!existing) {
                            me.cartItems.push({
                                item_code: it.item_code,
                                item_name: it.item_name,
                                stock_uom: it.uom,
                                qty: it.qty,
                                rate: it.rate,
                                mrp: it.price_list_rate || it.rate,
                                warehouse: it.warehouse || me.defaultWarehouse,
                                original_qty: it.qty,
                                sales_invoice: doc.name,
                                sales_invoice_item: it.name
                            });
                        }
                    });

                    me.render_selected_bills_list();
                    me.render_cart();
                }
            }
        });
    }

    render_selected_bills_list() {
        var me = this;
        const billsListDiv = this.wrapper.find('#selected-bills-list');
        billsListDiv.empty();
        this.selectedBills.forEach(b => {
            const row = $(`
                <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.03); padding:6px 12px; border-radius:var(--radius-sm-val); border:1px solid var(--border-dark);">
                    <div>
                        <span class="invoice-badge">${b.name}</span>
                        <span style="font-size:0.8rem; margin-left:8px; color:var(--text-muted-color);">${b.customer_name}</span>
                    </div>
                    <button style="background:none; border:none; color:var(--danger-color); cursor:pointer;" class="btn-remove-bill">
                        <span class="material-symbols-outlined" style="font-size:18px;">close</span>
                    </button>
                </div>
            `);
            row.find('.btn-remove-bill').on("click", function() {
                me.remove_selected_bill(b.name);
            });
            billsListDiv.append(row);
        });
    }

    remove_selected_bill(invoiceName) {
        var me = this;
        this.selectedBills = this.selectedBills.filter(b => b.name !== invoiceName);
        this.cartItems = [];
        this.selectedBills.forEach(doc => {
            doc.items.forEach(it => {
                me.cartItems.push({
                    item_code: it.item_code,
                    item_name: it.item_name,
                    stock_uom: it.uom,
                    qty: it.qty,
                    rate: it.rate,
                    mrp: it.price_list_rate || it.rate,
                    warehouse: it.warehouse || me.defaultWarehouse,
                    original_qty: it.qty,
                    sales_invoice: doc.name,
                    sales_invoice_item: it.name
                });
            });
        });
        this.render_selected_bills_list();
        this.render_cart();
    }

    handle_item_search(query) {
        var me = this;
        if (query.length < 2) {
            me.wrapper.find('#item-search-results').hide();
            return;
        }
        frappe.call({
            method: 'smriti_retail_os.billing_api.search_items',
            args: { query: query },
            callback: function(r) {
                const resultsDiv = me.wrapper.find('#item-search-results');
                resultsDiv.empty();
                const list = r.message || [];
                if (!list.length) {
                    resultsDiv.append(`<div style="padding:10px; color:var(--text-muted-color);">${__('No items found.')}</div>`);
                } else {
                    list.forEach(it => {
                        const row = $(`
                            <div style="padding:10px; border-bottom:1px solid var(--border-dark); cursor:pointer; font-size:0.85rem;">
                                <span style="font-weight:700; color:var(--primary-lt-color);">${it.item_code}</span> | 
                                <span>${it.item_name}</span> | 
                                <span style="color:var(--success-color);">Rs. ${parseFloat(it.rate).toFixed(2)}</span>
                            </div>
                        `);
                        row.on("click", function() {
                            me.add_standalone_item(it);
                            resultsDiv.hide();
                            me.wrapper.find('#item-search-input').val('');
                        });
                        resultsDiv.append(row);
                    });
                }
                resultsDiv.show();
            }
        });
    }

    add_standalone_item(it) {
        const existing = this.cartItems.find(item => item.item_code === it.item_code);
        if (existing) {
            existing.qty += 1;
        } else {
            this.cartItems.push({
                item_code: it.item_code,
                item_name: it.item_name,
                stock_uom: it.stock_uom,
                qty: 1,
                rate: it.rate,
                mrp: it.mrp,
                warehouse: this.defaultWarehouse
            });
        }
        this.render_cart();
    }

    render_cart() {
        var me = this;
        const tbody = this.wrapper.find('#cart-items-tbody');
        tbody.empty();

        if (!this.cartItems.length) {
            tbody.html(`<tr><td colspan="6" style="text-align:center; color:var(--text-muted-color); padding:20px 0;">${__('No items selected for return.')}</td></tr>`);
            this.update_summary();
            return;
        }

        this.cartItems.forEach((item, index) => {
            const warehouseOptions = this.warehousesList.map(wh => `
                <option value="${wh.name}" ${wh.name === item.warehouse ? 'selected' : ''}>${wh.warehouse_name}</option>
            `).join('');
            
            const origQtyHtml = item.original_qty ? `
                <div style="font-size:0.75rem; color:var(--text-muted-color); margin-top:2px;">
                    Original Qty: ${item.original_qty} (${item.sales_invoice})
                </div>
            ` : '';
            
            const removeButton = this.returnMode === 'standalone' ? `
                <button style="background:none; border:none; color:var(--danger-color); cursor:pointer;" class="btn-remove-item">
                    <span class="material-symbols-outlined" style="font-size:18px;">delete</span>
                </button>
            ` : '';

            const row = $(`
                <tr>
                    <td>
                        <div style="font-weight:600; color:var(--text-color);">${item.item_name}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted-color);">${item.item_code}</div>
                        ${origQtyHtml}
                    </td>
                    <td style="text-align:center;">
                        <input type="number" class="form-input inp-qty" style="width:70px; text-align:center; padding:4px;" value="${item.qty}" min="0.1" step="any" 
                            ${item.original_qty ? `max="${item.original_qty}"` : ''}>
                    </td>
                    <td style="text-align:right;">
                        <input type="number" class="form-input inp-rate" style="width:80px; text-align:right; padding:4px;" value="${parseFloat(item.rate).toFixed(2)}" step="any">
                    </td>
                    <td style="text-align:right; font-weight:600;">
                        Rs. ${(item.qty * item.rate).toFixed(2)}
                    </td>
                    <td>
                        <select class="form-input select-wh" style="width:100%; padding:4px; font-size:0.8rem;">
                            ${warehouseOptions}
                        </select>
                    </td>
                    <td style="text-align:center;">
                        ${removeButton}
                    </td>
                </tr>
            `);

            row.find('.inp-qty').on("change", function() { me.update_cart_item_qty(index, $(this).val()); });
            row.find('.inp-rate').on("change", function() { me.update_cart_item_rate(index, $(this).val()); });
            row.find('.select-wh').on("change", function() { me.cartItems[index].warehouse = $(this).val(); });
            row.find('.btn-remove-item').on("click", function() {
                me.cartItems.splice(index, 1);
                me.render_cart();
            });

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
        const qty = parseFloat(val);
        if (isNaN(qty) || qty <= 0) return;
        
        const item = this.cartItems[index];
        if (item.original_qty && qty > item.original_qty) {
            frappe.show_alert({message: __('Cannot return more than original quantity (') + item.original_qty + ')', indicator: 'red'});
            this.render_cart();
            return;
        }
        
        item.qty = qty;
        this.render_cart();
    }

    update_cart_item_rate(index, val) {
        const rate = parseFloat(val);
        if (isNaN(rate) || rate < 0) return;
        this.cartItems[index].rate = rate;
        this.render_cart();
    }

    update_summary() {
        let totalQty = 0;
        let grandTotal = 0;
        this.cartItems.forEach(it => {
            totalQty += it.qty;
            grandTotal += it.qty * it.rate;
        });
        
        this.wrapper.find('#summary-total-qty').text(totalQty.toFixed(2));
        this.wrapper.find('#summary-grand-total').text(`Rs. ${grandTotal.toFixed(2)}`);
    }

    save_return(draft) {
        var me = this;
        if (!this.cartItems.length) {
            frappe.show_alert({message: __('Please select at least one item to return.'), indicator: 'red'});
            return;
        }
        
        const itemsPayload = this.cartItems.map(it => ({
            item_code: it.item_code,
            qty: it.qty,
            rate: it.rate,
            mrp: it.mrp,
            stock_uom: it.stock_uom,
            warehouse: it.warehouse,
            sales_invoice: it.sales_invoice || null,
            sales_invoice_item: it.sales_invoice_item || null
        }));
        
        const remarks = this.wrapper.find('#modal-remarks').val();
        
        if (this.editingReturnName) {
            frappe.call({
                method: 'smriti_retail_os.billing_api.update_sales_return',
                args: {
                    name: me.editingReturnName,
                    items: JSON.stringify(itemsPayload),
                    remarks: remarks,
                    draft: draft ? 1 : 0
                },
                freeze: true,
                freeze_message: __('Saving Sales Return...'),
                callback: function(r) {
                    frappe.show_alert({message: r.message.message, indicator: 'green'});
                    me.close_return_modal();
                    me.load_returns();
                }
            });
        } else {
            frappe.call({
                method: 'smriti_retail_os.billing_api.create_custom_sales_return',
                args: {
                    customer: me.selectedCustomer.name,
                    items: JSON.stringify(itemsPayload),
                    return_against_invoice: (me.returnMode === 'single' && me.selectedBills.length) ? me.selectedBills[0].name : null,
                    remarks: remarks,
                    draft: draft ? 1 : 0
                },
                freeze: true,
                freeze_message: __('Creating Sales Return...'),
                callback: function(r) {
                    frappe.show_alert({message: r.message.message, indicator: 'green'});
                    me.close_return_modal();
                    me.load_returns();
                }
            });
        }
    }

    edit_draft_return(returnName) {
        var me = this;
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Sales Invoice',
                name: returnName
            },
            callback: function(r) {
                if (r.message) {
                    const doc = r.message;
                    me.editingReturnName = returnName;
                    me.wrapper.find('#modal-title').text(__('Edit Draft Return: ') + returnName);
                    
                    me.wrapper.find('#mode-selection-section').hide();
                    me.wrapper.find('#customer-select-section').hide();
                    me.wrapper.find('#bill-select-section').hide();
                    me.wrapper.find('#item-search-section').hide();
                    
                    me.wrapper.find('#modal-remarks').val(doc.remarks || '');
                    me.selectedCustomer = { name: doc.customer, customer_name: doc.customer_name };
                    
                    me.cartItems = doc.items.map(it => ({
                        item_code: it.item_code,
                        item_name: it.item_name,
                        stock_uom: it.uom,
                        qty: Math.abs(it.qty),
                        rate: it.rate,
                        mrp: it.price_list_rate || it.rate,
                        warehouse: it.warehouse,
                        original_qty: null,
                        sales_invoice: it.return_against || null,
                        sales_invoice_item: it.sales_invoice_item || null
                    }));
                    
                    me.render_cart();
                    me.close_drawer();
                    me.wrapper.find('#smriti-ret-modal-backdrop').addClass('open');
                }
            }
        });
    }

    delete_return_prompt(name, isDraft) {
        var me = this;
        const actionText = isDraft ? __('delete draft') : __('cancel submitted');
        frappe.confirm(
            __('Are you sure you want to {0} sales return {1}?', [actionText, name]),
            function() {
                me.delete_return(name);
            }
        );
    }

    delete_return(name, pin) {
        var me = this;
        let args = { name: name };
        if (pin) {
            args.manager_pin = pin;
        }

        frappe.call({
            method: 'smriti_retail_os.billing_api.delete_sales_return',
            args: args,
            callback: function(r) {
                frappe.show_alert({message: r.message.message, indicator: 'green'});
                me.close_pin_modal();
                me.close_drawer();
                me.load_returns();
            },
            error: function(r) {
                const err = r.message || r.exc || '';
                if (err.includes('PIN override is required') || (r.response && r.response._server_messages && r.response._server_messages.includes('PIN override is required'))) {
                    me.open_pin_modal(err || __('PIN override is required to cancel/delete return'), function(inputPin) {
                        me.delete_return(name, inputPin);
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
