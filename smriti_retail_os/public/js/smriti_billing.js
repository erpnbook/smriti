frappe.pages['smriti-billing'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Retail Billing'),
        single_column: true
    });

    var smriti_billing = new SmritiBillingController(wrapper, page);
}

class SmritiBillingController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;
        
        // Billing State
        this.cashier = frappe.session.user;
        this.active_customer = "Walk-In Customer";
        this.items = []; 
        this.held_invoices = [];
        this.current_invoice_name = null;
        this.active_price_list = "Standard Selling";
        this.redeemed_loyalty = 0;
        this.loyalty_conversion_factor = 0.0;
        this.loyalty_balance_points = 0;
        
        this.setup_layout();
        this.bind_keyboard_shortcuts();
        this.bind_actions();
        this.fetch_loyalty_details();
        this.focus_barcode();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-billing-container">
                <!-- Top Navbar: Status indicators -->
                <div class="smriti-top-nav">
                    <div class="smriti-cashier-badge">
                        <span class="badge-dot green"></span>
                        <span class="badge-label">${__('Cashier')}: <b>${this.cashier}</b></span>
                    </div>
                    <div class="smriti-active-invoice">
                        <span class="invoice-number">${__('Invoice')}: <b id="smriti-invoice-id">NEW BILL</b></span>
                    </div>
                    <div class="smriti-shortcuts-hint">
                        <span><b>F2</b> Search | <b>F3</b> Customer | <b>F4</b> Hold | <b>F5</b> Recall | <b>F6</b> Checkout</span>
                    </div>
                </div>

                <!-- Main Billing Grid -->
                <div class="smriti-grid">
                    <!-- Left Section: Barcode Field & Cart Table -->
                    <div class="smriti-main-panel">
                        <div class="barcode-wrapper">
                            <div class="barcode-input-container">
                                <span class="scanner-icon"><span class="material-symbols-outlined">barcode_scanner</span></span>
                                <input type="text" id="smriti-barcode-input" autocomplete="off" placeholder="${__('Scan Barcode or Type Code...')}">
                            </div>
                            <button class="btn btn-secondary btn-scan-camera" id="smriti-btn-scan-camera" title="Use Camera to Scan Barcode" style="padding: 0 15px; border: 1px solid var(--smriti-glass-border); border-radius: 8px; background: rgba(17, 24, 39, 0.8); color: white; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease;">
                                <span class="material-symbols-outlined">photo_camera</span>
                            </button>
                        </div>

                        <!-- Item Grid Table -->
                        <div class="billing-table-wrapper">
                            <table class="table table-bordered table-hover" id="smriti-billing-table">
                                <thead>
                                    <tr>
                                        <th style="width: 5%">${__('#')}</th>
                                        <th style="width: 35%">${__('Item Details')}</th>
                                        <th style="width: 10%">${__('UOM')}</th>
                                        <th style="width: 10%">${__('Qty')}</th>
                                        <th style="width: 12%">${__('Rate (INR)')}</th>
                                        <th style="width: 10%">${__('GST %')}</th>
                                        <th style="width: 15%">${__('Amount (INR)')}</th>
                                        <th style="width: 3%"></th>
                                    </tr>
                                </thead>
                                <tbody id="smriti-item-grid-body">
                                    <!-- Dynamic rows -->
                                </tbody>
                            </table>
                            <div class="empty-state" id="smriti-empty-state-msg">
                                <span class="empty-icon"><span class="material-symbols-outlined">shopping_cart</span></span>
                                <span class="empty-text">${__('Cart is Empty. Scan an item or press F2 to search.')}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Right Section: Customer Details, Totals & Pay drawer -->
                    <div class="smriti-side-panel">
                        <!-- Customer Details Card -->
                        <div class="customer-card">
                            <div class="customer-header">
                                <span class="cust-title"><span class="material-symbols-outlined">person</span> ${__('Customer')}</span>
                                <button class="btn btn-secondary btn-xs" id="smriti-btn-cust-lookup">F3: ${__('Lookup')}</button>
                            </div>
                            <div class="customer-details">
                                <span class="cust-name" id="smriti-cust-name">${this.active_customer}</span>
                                <span class="cust-loyalty" id="smriti-cust-loyalty">${__('Redeem Points')}: <input type="number" id="redeem-points-input" value="0" min="0" style="max-width: 60px; display: inline-block; padding: 2px 5px; background: rgba(31,41,55,0.6); border: 1px solid rgba(255,255,255,0.08); color: white; border-radius: 4px;"></span>
                            </div>
                        </div>

                        <!-- Calculation Panel -->
                        <div class="summary-card">
                            <div class="summary-row">
                                <span class="summary-label">${__('Total Items')}:</span>
                                <span class="summary-val" id="smriti-total-items-qty">0</span>
                            </div>
                            <div class="summary-row">
                                <span class="summary-label">${__('Subtotal (Net)')}:</span>
                                <span class="summary-val" id="smriti-subtotal-net">INR 0.00</span>
                            </div>
                            <div class="summary-row">
                                <span class="summary-label">${__('GST Tax')}:</span>
                                <span class="summary-val" id="smriti-subtotal-tax">INR 0.00</span>
                            </div>
                            <hr class="summary-divider">
                            <div class="summary-row grand-total-row">
                                <span class="summary-label">${__('GRAND TOTAL')}:</span>
                                <span class="summary-val highlight" id="smriti-grand-total">INR 0.00</span>
                            </div>
                        </div>

                        <!-- Payment Split Drawer -->
                        <div class="payment-drawer-card">
                            <div class="payment-drawer-header"><span class="material-symbols-outlined">payments</span> ${__('F6: Split Payments')}</div>
                            <div class="payment-fields">
                                <div class="payment-field-row">
                                    <label><span class="material-symbols-outlined">payments</span> ${__('Cash')}:</label>
                                    <input type="number" id="pay-cash-input" value="0" min="0">
                                </div>
                                <div class="payment-field-row">
                                    <label><span class="material-symbols-outlined">qr_code_2</span> ${__('UPI / QR')}:</label>
                                    <input type="number" id="pay-upi-input" value="0" min="0">
                                </div>
                                <div class="payment-field-row">
                                    <label><span class="material-symbols-outlined">credit_card</span> ${__('Card')}:</label>
                                    <input type="number" id="pay-card-input" value="0" min="0">
                                </div>
                            </div>
                            <div class="payment-alert-box" id="pay-drawer-alert">
                                <span>Pending: <b id="pay-pending-total">INR 0.00</b></span>
                            </div>
                            <button class="btn btn-success btn-block btn-checkout-save" id="smriti-btn-checkout"><span class="material-symbols-outlined" style="color: white; margin-right: 4px;">print</span> F9: ${__('Submit & Print')}</button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_keyboard_shortcuts() {
        var me = this;
        $(document).off("keydown").on("keydown", function(e) {
            // F2: Fast Search Item
            if (e.keyCode === 113) { 
                e.preventDefault();
                me.trigger_fast_item_search();
            }
            // F3: Customer Search
            else if (e.keyCode === 114) {
                e.preventDefault();
                me.trigger_customer_lookup();
            }
            // F4: Hold Bill (Draft POS Invoice)
            else if (e.keyCode === 115) {
                e.preventDefault();
                me.hold_bill_action();
            }
            // F5: Recall Held Draft Invoices
            else if (e.keyCode === 116) {
                e.preventDefault();
                me.recall_held_bills_list();
            }
            // F6: Focus Payment Cash field
            else if (e.keyCode === 117) {
                e.preventDefault();
                $("#pay-cash-input").focus().select();
            }
            // F9: Save & Thermal print
            else if (e.keyCode === 120) {
                e.preventDefault();
                me.checkout_and_save_invoice();
            }
            else {
                if (!$(e.target).is('input, textarea, select, button')) {
                    me.focus_barcode();
                }
            }
        });

        $("#smriti-barcode-input").off("keypress").on("keypress", function(e) {
            if (e.which === 13) { 
                const val = $(this).val().trim();
                if (val) {
                    me.add_barcode_item(val);
                    $(this).val(""); 
                }
            }
        });

        $("#pay-cash-input, #pay-upi-input, #pay-card-input, #redeem-points-input").off("input").on("input", function() {
            me.update_totals();
        });
    }

    bind_actions() {
        var me = this;
        $("#smriti-btn-cust-lookup").off("click").on("click", () => me.trigger_customer_lookup());
        $("#smriti-btn-scan-camera").off("click").on("click", () => me.trigger_camera_scanner());
        $("#smriti-btn-checkout").off("click").on("click", () => me.checkout_and_save_invoice());
    }

    focus_barcode() {
        $("#smriti-barcode-input").focus();
    }

    add_barcode_item(barcode) {
        var me = this;
        frappe.call({
            method: "smriti_retail_os.billing_api.add_item_by_barcode",
            args: { barcode: barcode, price_list: me.active_price_list },
            callback: function(r) {
                if (r.message) {
                    me.add_item_to_cart(r.message);
                } else {
                    frappe.show_alert({
                        message: __('Barcode "{0}" not found.').format(barcode),
                        indicator: 'red'
                    });
                }
            }
        });
    }

    add_item_to_cart(item) {
        const existing = this.items.find(i => i.item_code === item.item_code);
        if (existing) {
            existing.qty += 1;
        } else {
            this.items.push({
                item_code: item.item_code,
                item_name: item.item_name,
                stock_uom: item.stock_uom,
                qty: 1,
                rate: item.rate,
                mrp: item.mrp,
                gst_percentage: item.gst_percentage,
                tax_template: item.tax_template
            });
        }
        this.render_grid_rows();
        this.update_totals();
    }

    render_grid_rows() {
        var me = this;
        var tbody = $("#smriti-item-grid-body");
        tbody.empty();

        if (this.items.length === 0) {
            $("#smriti-empty-state-msg").show();
            return;
        }
        $("#smriti-empty-state-msg").hide();

        this.items.forEach((it, idx) => {
            const row_total = (it.qty * it.rate);
            tbody.append(`
                <tr data-idx="${idx}">
                    <td>${idx + 1}</td>
                    <td>
                        <b style="color: #0f766e;">${it.item_code}</b> - ${it.item_name}
                    </td>
                    <td><span class="badge badge-secondary">${it.stock_uom}</span></td>
                    <td>
                        <input type="number" class="grid-qty-input form-control text-center" value="${it.qty}" min="1" style="max-width: 70px;">
                    </td>
                    <td>
                        <input type="number" class="grid-rate-input form-control text-right" value="${it.rate}" min="0.01" style="max-width: 100px;">
                    </td>
                    <td>${it.gst_percentage}%</td>
                    <td class="text-right font-weight-bold" style="color: #0d9488;">INR ${row_total.toFixed(2)}</td>
                    <td class="text-center">
                        <button class="btn btn-xs btn-danger btn-remove-row" style="padding: 2px 6px;">✕</button>
                    </td>
                </tr>
            `);
        });

        tbody.find(".grid-qty-input").off("change").on("change", function() {
            const idx = $(this).closest("tr").data("idx");
            me.items[idx].qty = flt($(this).val());
            me.render_grid_rows();
            me.update_totals();
        });

        tbody.find(".grid-rate-input").off("change").on("change", function() {
            const idx = $(this).closest("tr").data("idx");
            const new_rate = flt($(this).val());
            
            me.trigger_manager_override("Price Change Override", () => {
                me.items[idx].rate = new_rate;
                me.render_grid_rows();
                me.update_totals();
            }, () => {
                me.render_grid_rows();
            });
        });

        tbody.find(".btn-remove-row").off("click").on("click", function() {
            const idx = $(this).closest("tr").data("idx");
            me.trigger_manager_override("Void Row Override", () => {
                me.items.splice(idx, 1);
                me.render_grid_rows();
                me.update_totals();
            });
        });
    }

    update_totals() {
        let total_items = 0;
        let subtotal_net = 0;
        let subtotal_tax = 0;

        this.items.forEach(it => {
            total_items += it.qty;
            const net_row_amount = (it.qty * it.rate);
            const gst_factor = (it.gst_percentage / 100);
            const row_tax = (net_row_amount * gst_factor);
            
            subtotal_net += net_row_amount;
            subtotal_tax += row_tax;
        });

        const grand_total = (subtotal_net + subtotal_tax);
        
        // Calculate loyalty discount
        const points = cint($("#redeem-points-input").val()) || 0;
        const conversion = this.loyalty_conversion_factor || 0.0;
        const loyalty_discount = points * conversion;
        const final_due = Math.max(0, grand_total - loyalty_discount);

        $("#smriti-total-items-qty").text(total_items);
        $("#smriti-subtotal-net").text("INR " + subtotal_net.toFixed(2));
        $("#smriti-subtotal-tax").text("INR " + subtotal_tax.toFixed(2));
        $("#smriti-grand-total").text("INR " + final_due.toFixed(2));

        const cash_paid = flt($("#pay-cash-input").val());
        const upi_paid = flt($("#pay-upi-input").val());
        const card_paid = flt($("#pay-card-input").val());
        const total_paid = (cash_paid + upi_paid + card_paid);
        
        const pending = (final_due - total_paid);

        if (pending > 0) {
            $("#pay-drawer-alert").removeClass("reconciled").addClass("pending");
            $("#pay-pending-total").text("INR " + pending.toFixed(2));
        } else {
            $("#pay-drawer-alert").removeClass("pending").addClass("reconciled");
            $("#pay-pending-total").text("PAID / NO DUE");
        }
    }

    // --- Hold / Recall (Extension-based via standard Draft POS Invoice) ---

    hold_bill_action() {
        var me = this;
        if (this.items.length === 0) {
            frappe.show_alert({message: __("No items to put on hold."), indicator: 'orange'});
            return;
        }

        frappe.call({
            method: "smriti_retail_os.billing_api.hold_bill",
            args: {
                cashier: me.cashier,
                customer: me.active_customer,
                items: JSON.stringify(me.items)
            },
            freeze: true,
            freeze_message: __("Putting current active bill on hold..."),
            callback: function(r) {
                if (r.message) {
                    frappe.show_alert({message: r.message.message, indicator: 'green'});
                    me.items = []; 
                    me.current_invoice_name = null;
                    $("#smriti-invoice-id").text("NEW BILL");
                    me.render_grid_rows();
                    me.update_totals();
                    me.focus_barcode();
                }
            }
        });
    }

    recall_held_bills_list() {
        var me = this;
        frappe.call({
            method: "smriti_retail_os.billing_api.recall_bill",
            args: { cashier: me.cashier },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    me.show_recall_dialog(r.message);
                } else {
                    frappe.show_alert({message: __("No held draft bills found for cashier: ") + me.cashier, indicator: 'orange'});
                }
            }
        });
    }

    show_recall_dialog(held_list) {
        var me = this;
        var dialog = new frappe.ui.Dialog({
            title: __('F5: Recall Held Draft Bills'),
            fields: [
                {
                    fieldname: 'held_invoices_table',
                    fieldtype: 'HTML'
                }
            ]
        });

        let table_html = `
            <table class="table table-condensed table-hover">
                <thead>
                    <tr>
                        <th>${__('Draft Name')}</th>
                        <th>${__('Customer')}</th>
                        <th>${__('Hold Time')}</th>
                        <th>${__('Grand Total')}</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
        `;

        held_list.forEach(inv => {
            table_html += `
                <tr>
                    <td><b>${inv.name}</b></td>
                    <td>${inv.customer}</td>
                    <td>${frappe.datetime.global_date_format(inv.custom_hold_time)}</td>
                    <td>INR ${inv.grand_total.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-xs btn-primary btn-select-held" data-id="${inv.name}">Recall</button>
                    </td>
                </tr>
            `;
        });
        table_html += `</tbody></table>`;

        dialog.fields_dict.held_invoices_table.$wrapper.html(table_html);

        dialog.$wrapper.find(".btn-select-held").off("click").on("click", function() {
            const name = $(this).data("id");
            me.load_held_draft(name);
            dialog.hide();
        });

        dialog.show();
    }

    load_held_draft(invoice_name) {
        var me = this;
        frappe.call({
            method: "smriti_retail_os.billing_api.load_held_invoice",
            args: { invoice_name: invoice_name },
            freeze: true,
            freeze_message: __("Recalling draft invoice: ") + invoice_name,
            callback: function(r) {
                if (r.message) {
                    me.items = r.message.items || [];
                    me.active_customer = r.message.customer;
                    me.current_invoice_name = r.message.invoice_name;
                    
                    $("#smriti-invoice-id").html(`<span style="color: #ea580c;">RECALLED: ${me.current_invoice_name}</span>`);
                    $("#smriti-cust-name").text(me.active_customer);

                    me.render_grid_rows();
                    me.fetch_loyalty_details();
                    me.update_totals();
                    me.focus_barcode();
                }
            }
        });
    }

    checkout_and_save_invoice() {
        var me = this;
        if (this.items.length === 0) {
            frappe.show_alert({message: __("Cart is empty."), indicator: 'red'});
            return;
        }

        const subtotal_net = this.items.reduce((s, it) => s + (it.qty * it.rate), 0);
        const subtotal_tax = this.items.reduce((s, it) => s + (it.qty * it.rate * (it.gst_percentage / 100)), 0);
        const grand_total = (subtotal_net + subtotal_tax);

        const cash_paid = flt($("#pay-cash-input").val());
        const upi_paid = flt($("#pay-upi-input").val());
        const card_paid = flt($("#pay-card-input").val());
        const total_paid = (cash_paid + upi_paid + card_paid);

        if (total_paid < grand_total) {
            frappe.msgprint({
                title: __('Payment Incomplete'),
                message: __('Total paid must be equal to or greater than Grand Total. Please adjust payments.'),
                indicator: 'red'
            });
            return;
        }

        const payments = [
            { mode_of_payment: "Cash", amount: cash_paid },
            { mode_of_payment: "UPI", amount: upi_paid },
            { mode_of_payment: "Card", amount: card_paid }
        ].filter(p => p.amount > 0);

        const loyalty_points = cint($("#redeem-points-input").val()) || 0;

        frappe.call({
            method: "smriti_retail_os.billing_api.submit_bill",
            args: {
                cashier: me.cashier,
                customer: me.active_customer,
                items: JSON.stringify(me.items),
                payments: JSON.stringify(payments),
                loyalty_points: loyalty_points,
                invoice_name: me.current_invoice_name
            },
            freeze: true,
            freeze_message: __("Submitting Billing through India Compliance..."),
            callback: function(r) {
                if (r.message) {
                    frappe.show_alert({message: __("Invoice submitted successfully!"), indicator: 'green'});
                    
                    // Trigger browser print format window for standard download
                    frappe.show_alert({message: __("Print receipt triggered: ") + r.message.invoice, indicator: 'green'});
                    window.open(r.message.print_url, '_blank');

                    // Reset screen
                    me.items = [];
                    me.current_invoice_name = null;
                    me.redeemed_loyalty = 0;
                    me.loyalty_conversion_factor = 0.0;
                    me.loyalty_balance_points = 0;
                    $("#smriti-invoice-id").text("NEW BILL");
                    $("#pay-cash-input").val(0);
                    $("#pay-upi-input").val(0);
                    $("#pay-card-input").val(0);
                    $("#redeem-points-input").val(0);

                    me.render_grid_rows();
                    me.fetch_loyalty_details();
                    me.update_totals();
                    me.focus_barcode();
                }
            }
        });
    }

    trigger_customer_lookup() {
        var me = this;
        var dialog = new frappe.ui.Dialog({
            title: __('F3: Customer Mobile Search'),
            fields: [
                {
                    label: __('Search Customer'),
                    fieldname: 'query',
                    fieldtype: 'Data',
                    reqd: 1,
                    description: __('Query mobile number or name.')
                },
                {
                    fieldname: 'results_html',
                    fieldtype: 'HTML'
                }
            ]
        });

        dialog.fields_dict.query.$wrapper.find("input").on("input", function() {
            const val = $(this).val().trim();
            if (val.length >= 3) {
                frappe.call({
                    method: "smriti_retail_os.billing_api.search_customer",
                    args: { query: val },
                    callback: function(r) {
                        if (r.message && r.message.length > 0) {
                            let rows_html = `<table class="table table-bordered table-condensed table-hover"><thead><tr><th>Name</th><th>Mobile</th><th>Program</th><th></th></tr></thead><tbody>`;
                            r.message.forEach(cust => {
                                rows_html += `
                                    <tr>
                                        <td><b>${cust.customer_name}</b></td>
                                        <td>${cust.primary_mobile_no || '-'}</td>
                                        <td>${cust.loyalty_program || '-'}</td>
                                        <td>
                                            <button class="btn btn-xs btn-primary btn-select-customer" data-id="${cust.name}">Select</button>
                                        </td>
                                    </tr>
                                `;
                            });
                            rows_html += `</tbody></table>`;
                            dialog.fields_dict.results_html.$wrapper.html(rows_html);

                            dialog.$wrapper.find(".btn-select-customer").off("click").on("click", function() {
                                const id = $(this).data("id");
                                me.active_customer = id;
                                $("#smriti-cust-name").text(me.active_customer);
                                me.fetch_loyalty_details();
                                dialog.hide();
                            });
                        } else {
                            dialog.fields_dict.results_html.$wrapper.html(`<span class="text-muted">No customers found.</span>`);
                        }
                    }
                });
            }
        });

        dialog.show();
    }

    trigger_fast_item_search() {
        var me = this;
        var dialog = new frappe.ui.Dialog({
            title: __('F2: Fast Catalog Search'),
            fields: [
                {
                    label: __('Search Catalog'),
                    fieldname: 'query',
                    fieldtype: 'Data',
                    reqd: 1,
                    description: __('Query item code, name, brand, or group.')
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
                    args: { query: val, price_list: me.active_price_list },
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
                                            <button class="btn btn-xs btn-primary btn-select-search-item" data-code="${it.item_code}">Add</button>
                                        </td>
                                    </tr>
                                `;
                            });
                            rows_html += `</tbody></table>`;
                            dialog.fields_dict.results_html.$wrapper.html(rows_html);

                            dialog.$wrapper.find(".btn-select-search-item").off("click").on("click", function() {
                                const code = $(this).data("code");
                                const found = r.message.find(i => i.item_code === code);
                                me.add_item_to_cart(found);
                                dialog.hide();
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

    trigger_manager_override(action_name, success_callback, cancel_callback) {
        var me = this;
        var dialog = new frappe.ui.Dialog({
            title: `<span class="material-symbols-outlined" style="vertical-align: text-top; margin-right: 6px; color: #e11d48;">lock</span> Security Override Needed`,
            fields: [
                {
                    label: __('Manager PIN Code'),
                    fieldname: 'pin',
                    fieldtype: 'Password',
                    reqd: 1,
                    description: __('Action: ') + action_name
                }
            ],
            primary_action_label: __('Authorize'),
            primary_action: function(data) {
                frappe.call({
                    method: "smriti_retail_os.billing_api.validate_manager_override",
                    args: {
                        pin: data.pin,
                        action_type: action_name,
                        invoice_name: me.current_invoice_name
                    },
                    callback: function(r) {
                        if (r.message && r.message.authorized) {
                            frappe.show_alert({message: `Override approved by: ${r.message.manager}`, indicator: 'green'});
                            success_callback();
                            dialog.hide();
                        } else {
                            frappe.msgprint({
                                title: __('Authentication Failed'),
                                message: r.message ? r.message.message : __('Invalid PIN Code.'),
                                indicator: 'red'
                            });
                        }
                    }
                });
            }
        });
        
        dialog.on_cancel = function() {
            if (cancel_callback) cancel_callback();
        };

        dialog.show();
    }

    fetch_loyalty_details() {
        var me = this;
        if (!me.active_customer || me.active_customer === "Walk-In Customer") {
            $("#smriti-cust-loyalty").hide();
            $("#redeem-points-input").val(0).prop("max", 0);
            me.loyalty_conversion_factor = 0.0;
            me.loyalty_balance_points = 0;
            return;
        }

        frappe.call({
            method: "smriti_retail_os.loyalty_api.get_loyalty_details",
            args: { customer: me.active_customer },
            callback: function(r) {
                if (r.message && r.message.enrolled) {
                    const ld = r.message;
                    me.loyalty_conversion_factor = ld.conversion_factor;
                    me.loyalty_balance_points = ld.loyalty_points;

                    $("#smriti-cust-loyalty").show().html(`
                        ${__('Loyalty Balance')}: <b style="color: #0d9488;">${ld.loyalty_points} Pts</b> (Value: <b>₹${ld.redeem_amount.toFixed(2)}</b>)<br>
                        ${__('Redeem')}: <input type="number" id="redeem-points-input" value="0" min="0" max="${ld.loyalty_points}" style="max-width: 60px; display: inline-block; padding: 2px 5px; background: rgba(31,41,55,0.6); border: 1px solid rgba(255,255,255,0.08); color: white; border-radius: 4px; margin-top:4px;"> Pts
                    `);

                    // Re-bind input events
                    $("#redeem-points-input").off("input").on("input", function() {
                        let pts = cint($(this).val());
                        if (pts > ld.loyalty_points) {
                            pts = ld.loyalty_points;
                            $(this).val(pts);
                        }
                        me.update_totals();
                    });
                } else {
                    $("#smriti-cust-loyalty").show().html(`
                        <span class="text-muted" style="font-size:11px;">Not Enrolled in Loyalty Program</span>
                    `);
                    $("#redeem-points-input").val(0).prop("max", 0);
                    me.loyalty_conversion_factor = 0.0;
                    me.loyalty_balance_points = 0;
                }
                me.update_totals();
            }
        });
    }

    trigger_camera_scanner() {
        var me = this;
        
        var dialog = new frappe.ui.Dialog({
            title: `<span class="material-symbols-outlined" style="vertical-align: text-top; margin-right: 6px; color: #6366f1;">photo_camera</span> Live Camera Barcode Scanner`,
            fields: [
                {
                    fieldname: 'camera_html',
                    fieldtype: 'HTML'
                }
            ],
            primary_action_label: __('Close'),
            primary_action: function() {
                dialog.hide();
            }
        });

        dialog.fields_dict.camera_html.$wrapper.html(`
            <div style="position: relative; text-align: center; background: #000; border-radius: 8px; overflow: hidden; max-width: 480px; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
                <video id="smriti-scanner-video" width="100%" height="auto" autoplay playsinline style="display: block; border-radius: 8px; transform: scaleX(1);"></video>
                <div style="position: absolute; border: 2px dashed #e94560; top: 20%; bottom: 20%; left: 10%; right: 10%; pointer-events: none; border-radius: 8px; box-shadow: 0 0 0 9999px rgba(0,0,0,0.4); animation: scan-pulse 2s infinite alternate;"></div>
                <div id="smriti-scanner-status" style="position: absolute; bottom: 10px; left: 0; right: 0; color: white; background: rgba(0,0,0,0.7); padding: 5px; font-size: 11px;">Initializing camera stream...</div>
            </div>
            <style>
                @keyframes scan-pulse {
                    0% { border-color: #e94560; }
                    100% { border-color: #6366f1; }
                }
            </style>
        `);

        dialog.show();

        const video = document.getElementById("smriti-scanner-video");
        const status = document.getElementById("smriti-scanner-status");
        let stream = null;
        let active = true;

        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(s => {
                stream = s;
                video.srcObject = s;
                status.textContent = "Camera active. Point at barcode to scan...";
                
                // Initialize barcode detection loop
                startDetection();
            })
            .catch(err => {
                console.error(err);
                status.textContent = "Camera access denied or unavailable: " + err.message;
                status.style.color = "#ef4444";
            });

        function startDetection() {
            if (!active) return;
            
            if ('BarcodeDetector' in window) {
                const barcodeDetector = new BarcodeDetector({
                    formats: ['ean_13', 'code_128', 'code_39', 'qr']
                });
                
                function detect() {
                    if (!active) return;
                    barcodeDetector.detect(video)
                        .then(barcodes => {
                            if (barcodes.length > 0) {
                                const code = barcodes[0].rawValue;
                                me.add_barcode_item(code);
                                active = false;
                                stopCamera();
                                dialog.hide();
                                frappe.show_alert({message: `Scanned: ${code}`, indicator: 'green'});
                            } else {
                                requestAnimationFrame(detect);
                            }
                        })
                        .catch(err => {
                            console.error(err);
                            requestAnimationFrame(detect);
                        });
                }
                
                // Delay slightly to let camera adjust focus
                setTimeout(() => {
                    detect();
                }, 500);
            } else {
                status.textContent = "Native scanner not supported. Please use physical scanner.";
                status.style.color = "#ef4444";
            }
        }

        function stopCamera() {
            active = false;
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        }

        dialog.on_cancel = function() {
            stopCamera();
        };
    }
}

