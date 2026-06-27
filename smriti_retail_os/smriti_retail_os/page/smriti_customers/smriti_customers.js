/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_customers/smriti_customers.js
 * @description: Page controller for SMRITI Customer Directory (Desk SPA).
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-17
 * @version: 1.8.6
 * @license: MIT
 */

frappe.pages['smriti-customers'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Customer Directory'),
        single_column: true
    });

    var smriti_customers = new SmritiCustomersController(wrapper, page);
}

class SmritiCustomersController {
    constructor(wrapper, page) {
        this.wrapper = $(wrapper);
        this.page = page;
        this.masterCustomersList = [];

        this.GST_STATE_CODES = {
            "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab", "04": "Chandigarh",
            "05": "Uttarakhand", "06": "Haryana", "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
            "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh", "13": "Nagaland", "14": "Manipur",
            "15": "Mizoram", "16": "Tripura", "17": "Meghalaya", "18": "Assam", "19": "West Bengal",
            "20": "Jharkhand", "21": "Odisha", "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
            "26": "Dadra and Nagar Haveli and Daman and Diu", "27": "Maharashtra", "29": "Karnataka",
            "30": "Goa", "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu", "34": "Puducherry",
            "35": "Andaman & Nicobar Islands", "36": "Telangana", "37": "Andhra Pradesh", "38": "Ladakh",
            "97": "Other Territory"
        };

        this.setup_layout();
        this.bind_actions();
        this.init();
    }

    setup_layout() {
        this.wrapper.find(".layout-main-section").html(`
            <div class="smriti-customers-container">
                <!-- Topbar -->
                <div class="topbar">
                    <div class="topbar-breadcrumbs">
                        <span>SMRITI</span>
                        <span class="sep">/</span>
                        <span class="active">${__('Customer Directory')}</span>
                    </div>

                    <div class="topbar-right">
                        <button class="topbtn" id="smriti-cust-btn-add" style="border-color: var(--primary-color); color: var(--primary-lt-color);">
                            <span class="material-symbols-outlined">person_add</span> ${__('Quick Add Customer')}
                        </button>
                    </div>
                </div>

                <!-- Filter Bar -->
                <div class="filter-bar">
                    <input type="text" class="form-input search-input" id="smriti-cust-search" placeholder="${__('Search by customer name or phone...')}">
                    <select class="form-input filter-select" id="smriti-cust-filter-group">
                        <option value="">${__('All Groups')}</option>
                    </select>
                </div>

                <!-- Directory Table -->
                <div class="table-wrap">
                    <table class="smriti-table">
                        <thead>
                            <tr>
                                <th>${__('Customer Details')}</th>
                                <th>${__('Mobile Number')}</th>
                                <th>${__('Customer Group')}</th>
                                <th>${__('Territory')}</th>
                                <th>${__('System Identifier')}</th>
                                <th style="text-align:right;">${__('Actions')}</th>
                            </tr>
                        </thead>
                        <tbody id="smriti-customers-tbody">
                            <tr>
                                <td colspan="6" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">
                                    ${__('Loading customers...')}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Customer Form Modal -->
                <div class="modal-backdrop" id="smriti-customer-modal">
                    <div class="modal" onclick="event.stopPropagation()">
                        <div class="modal-header">
                            <div class="modal-title">
                                <span class="material-symbols-outlined">person_add</span> 
                                <span id="smriti-modal-action-title">${__('Quick Add Customer')}</span>
                            </div>
                            <button class="modal-close" id="smriti-cust-modal-close">&times;</button>
                        </div>
                        <div class="modal-body" style="max-height: 75vh; overflow-y: auto; padding-right: 6px;">
                            <input type="hidden" id="cust-name-id" value="">
                            
                            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--primary-lt-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 12px; display:flex; align-items:center; gap:6px;">
                                <span class="material-symbols-outlined" style="font-size:16px;">contact_page</span> 1. General Profile
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                                <div class="form-group">
                                    <label class="form-label">${__('Customer Name *')}</label>
                                    <input type="text" class="form-input" id="cust-name" placeholder="e.g. Rahul Sharma">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Customer Type')}</label>
                                    <select class="form-input" id="cust-type">
                                        <option value="Individual">${__('Individual')}</option>
                                        <option value="Company">${__('Company')}</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Mobile Number')}</label>
                                    <input type="text" class="form-input" id="cust-mobile" placeholder="e.g. 9876543210">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Email Address')}</label>
                                    <input type="email" class="form-input" id="cust-email" placeholder="e.g. rahul@gmail.com">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Customer Group')}</label>
                                    <select class="form-input" id="cust-group"></select>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Territory')}</label>
                                    <select class="form-input" id="cust-territory"></select>
                                </div>
                            </div>

                            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--primary-lt-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 12px; display:flex; align-items:center; gap:6px;">
                                <span class="material-symbols-outlined" style="font-size:16px;">payments</span> 2. Tax Compliance & Override
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                                <div class="form-group">
                                    <label class="form-label">${__('GSTIN / Tax ID')}</label>
                                    <input type="text" class="form-input" id="cust-gstin" placeholder="e.g. 29AABCR1718E1ZL">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('GST Category')}</label>
                                    <select class="form-input" id="cust-gst-category">
                                        <option value="Unregistered">${__('Unregistered')}</option>
                                        <option value="Registered Regular" selected>${__('Registered Regular')}</option>
                                        <option value="Composition">${__('Composition')}</option>
                                        <option value="Overseas">${__('Overseas')}</option>
                                        <option value="SEZ">${__('SEZ')}</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('PAN (Tax ID)')}</label>
                                    <input type="text" class="form-input" id="cust-pan" placeholder="e.g. ABCDE1234F">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Tax Inclusive Override')}</label>
                                    <select class="form-input" id="cust-tax-override">
                                        <option value="Default" selected>${__('Default (Standard Pricing)')}</option>
                                        <option value="Inclusive">${__('Force Tax Inclusive')}</option>
                                        <option value="Exclusive">${__('Force Tax Exclusive')}</option>
                                    </select>
                                </div>
                            </div>

                            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--primary-lt-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 12px; display:flex; align-items:center; gap:6px;">
                                <span class="material-symbols-outlined" style="font-size:16px;">home</span> 3. Billing Address Details (Bill To)
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                                <div class="form-group" style="grid-column: span 2;">
                                    <label class="form-label">${__('Address Line 1')}</label>
                                    <input type="text" class="form-input" id="bill-line1" placeholder="e.g. Flat 402, Green Glen Layout">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Address Line 2 (Optional)')}</label>
                                    <input type="text" class="form-input" id="bill-line2" placeholder="e.g. Bellandur">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('City')}</label>
                                    <input type="text" class="form-input" id="bill-city" placeholder="e.g. Bangalore">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('State')}</label>
                                    <input type="text" class="form-input" id="bill-state" placeholder="e.g. Karnataka">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Pincode')}</label>
                                    <input type="text" class="form-input" id="bill-pincode" placeholder="e.g. 560103">
                                </div>
                            </div>

                            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--primary-lt-color); border-bottom: 1px solid var(--border-dark); padding-bottom: 4px; margin-bottom: 12px; display:flex; align-items:center; justify-content:space-between;">
                                <span style="display:flex; align-items:center; gap:6px;">
                                    <span class="material-symbols-outlined" style="font-size:16px;">local_shipping</span> 4. Shipping Address Details (Ship To)
                                </span>
                                <label style="font-size: 0.72rem; display:inline-flex; align-items:center; gap:4px; cursor:pointer;">
                                    <input type="checkbox" id="same-as-billing" style="accent-color:var(--primary-color);"> ${__('Same as Billing')}
                                </label>
                            </div>
                            <div id="shipping-address-section" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 10px;">
                                <div class="form-group" style="grid-column: span 2;">
                                    <label class="form-label">${__('Address Line 1')}</label>
                                    <input type="text" class="form-input" id="ship-line1" placeholder="e.g. Flat 402, Green Glen Layout">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Address Line 2 (Optional)')}</label>
                                    <input type="text" class="form-input" id="ship-line2" placeholder="e.g. Bellandur">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('City')}</label>
                                    <input type="text" class="form-input" id="ship-city" placeholder="e.g. Bangalore">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('State')}</label>
                                    <input type="text" class="form-input" id="ship-state" placeholder="e.g. Karnataka">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">${__('Pincode')}</label>
                                    <input type="text" class="form-input" id="ship-pincode" placeholder="e.g. 560103">
                                </div>
                            </div>

                            <button class="btn-submit" id="btn-save" style="margin-top: 15px;">
                                <span class="material-symbols-outlined">save</span> ${__('Save Customer Record')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_actions() {
        var me = this;
        this.wrapper.find("#smriti-cust-btn-add").on("click", () => me.open_add_customer_modal());
        this.wrapper.find("#smriti-cust-modal-close").on("click", () => me.close_customer_modal());
        this.wrapper.find("#smriti-customer-modal").on("click", () => me.close_customer_modal());
        
        this.wrapper.find("#smriti-cust-search").on("input", function() {
            me.apply_filters();
        });

        this.wrapper.find("#smriti-cust-filter-group").on("change", function() {
            me.apply_filters();
        });

        this.wrapper.find("#same-as-billing").on("change", function() {
            me.toggle_same_as_billing($(this).is(":checked"));
        });

        this.wrapper.find("#cust-gstin").on("change", function() {
            me.auto_resolve_state($(this).val(), 'bill');
        });

        this.wrapper.find("#btn-save").on("click", () => me.save_customer_detail());
    }

    init() {
        this.load_customers();
        this.load_filter_options();
        this.load_dropdown_options();
    }

    load_customers() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Customer',
                fields: ['name', 'customer_name', 'mobile_no', 'customer_group', 'territory'],
                order_by: 'creation desc',
                limit_page_length: 200
            },
            callback: function(r) {
                me.masterCustomersList = r.message || [];
                me.render_table(me.masterCustomersList);
            }
        });
    }

    load_filter_options() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Customer Group',
                fields: ['name'],
                order_by: 'name asc',
                limit_page_length: 100
            },
            callback: function(r) {
                const grpSel = me.wrapper.find('#smriti-cust-filter-group');
                grpSel.html(`<option value="">${__('All Groups')}</option>`);
                if (r.message) {
                    r.message.forEach(g => {
                        grpSel.append(`<option value="${g.name}">${g.name}</option>`);
                    });
                }
            }
        });
    }

    load_dropdown_options() {
        var me = this;
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Customer Group',
                fields: ['name'],
                order_by: 'name asc',
                limit_page_length: 100
            },
            callback: function(r) {
                const grpSel = me.wrapper.find('#cust-group');
                grpSel.empty();
                if (r.message) {
                    r.message.forEach(g => {
                        grpSel.append(`<option value="${g.name}">${g.name}</option>`);
                    });
                }
            }
        });

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Territory',
                fields: ['name'],
                order_by: 'name asc',
                limit_page_length: 100
            },
            callback: function(r) {
                const terrSel = me.wrapper.find('#cust-territory');
                terrSel.empty();
                if (r.message) {
                    r.message.forEach(t => {
                        terrSel.append(`<option value="${t.name}">${t.name}</option>`);
                    });
                }
            }
        });
    }

    render_table(list) {
        var me = this;
        const tbody = this.wrapper.find('#smriti-customers-tbody');
        tbody.empty();

        if (!list.length) {
            tbody.html(`<tr><td colspan="6" style="text-align:center; color: var(--text-sub-color); padding:40px 0;">${__('No customers found.')}</td></tr>`);
            return;
        }

        list.forEach(c => {
            const tr = $(`
                <tr>
                    <td>
                        <div style="font-weight:600; color:var(--text-color);">${c.customer_name}</div>
                    </td>
                    <td style="font-weight:600; color:var(--primary-lt-color);">${c.mobile_no || 'N/A'}</td>
                    <td style="color:var(--text-muted-color);">${c.customer_group}</td>
                    <td style="color:var(--text-muted-color);">${c.territory || 'N/A'}</td>
                    <td><span class="customer-id-badge">${c.name}</span></td>
                    <td style="text-align:right;">
                        <button class="topbtn btn-edit-customer" data-id="${c.name}" title="${__('Edit Customer Details')}" style="padding:4px 8px;">
                            <span class="material-symbols-outlined" style="font-size:16px;">edit</span>
                        </button>
                    </td>
                </tr>
            `);
            tr.find(".btn-edit-customer").on("click", function() {
                me.open_edit_customer_modal($(this).data("id"));
            });
            tbody.append(tr);
        });
    }

    apply_filters() {
        const q = this.wrapper.find('#smriti-cust-search').val().toLowerCase();
        const grp = this.wrapper.find('#smriti-cust-filter-group').val();

        let filtered = this.masterCustomersList;

        if (q) {
            filtered = filtered.filter(c => 
                c.customer_name.toLowerCase().includes(q) ||
                (c.mobile_no || '').includes(q) ||
                c.name.toLowerCase().includes(q)
            );
        }
        if (grp) {
            filtered = filtered.filter(c => c.customer_group === grp);
        }

        this.render_table(filtered);
    }

    open_add_customer_modal() {
        this.wrapper.find('#smriti-modal-action-title').text(__('Quick Add Customer'));
        this.wrapper.find('#cust-name-id').val("");
        this.wrapper.find('#cust-name').val("");
        this.wrapper.find('#cust-type').val("Individual");
        this.wrapper.find('#cust-mobile').val("");
        this.wrapper.find('#cust-email').val("");
        
        // Select first or default customer group
        this.wrapper.find('#cust-group').val("Individual");
        this.wrapper.find('#cust-territory').val("All Territories");
        
        this.wrapper.find('#cust-gstin').val("");
        this.wrapper.find('#cust-gst-category').val("Registered Regular");
        this.wrapper.find('#cust-pan').val("");
        this.wrapper.find('#cust-tax-override').val("Default");
        
        // Clear Address
        this.wrapper.find('#bill-line1').val("");
        this.wrapper.find('#bill-line2').val("");
        this.wrapper.find('#bill-city').val("");
        this.wrapper.find('#bill-state').val("");
        this.wrapper.find('#bill-pincode').val("");
        
        this.wrapper.find('#same-as-billing').prop('checked', false);
        this.toggle_same_as_billing(false);
        
        this.wrapper.find('#ship-line1').val("");
        this.wrapper.find('#ship-line2').val("");
        this.wrapper.find('#ship-city').val("");
        this.wrapper.find('#ship-state').val("");
        this.wrapper.find('#ship-pincode').val("");

        this.wrapper.find('#smriti-customer-modal').addClass('open');
        this.wrapper.find('#cust-name').focus();
    }

    open_edit_customer_modal(name) {
        var me = this;
        frappe.show_alert({message: __('Fetching customer details...'), indicator: 'blue'});
        
        frappe.call({
            method: 'smriti_retail_os.master_api.get_customer_detail',
            args: { name: name },
            callback: function(r) {
                if (r.message) {
                    const c = r.message;
                    me.wrapper.find('#smriti-modal-action-title').text(__('Edit Customer: ') + c.customer_name);
                    me.wrapper.find('#cust-name-id').val(c.name);
                    me.wrapper.find('#cust-name').val(c.customer_name);
                    me.wrapper.find('#cust-type').val(c.customer_type || "Individual");
                    me.wrapper.find('#cust-mobile').val(c.mobile_no || "");
                    me.wrapper.find('#cust-email').val(c.email_id || "");
                    me.wrapper.find('#cust-group').val(c.customer_group || "Individual");
                    me.wrapper.find('#cust-territory').val(c.territory || "All Territories");
                    me.wrapper.find('#cust-gstin').val(c.tax_id || "");
                    me.wrapper.find('#cust-gst-category').val(c.gst_category || "Registered Regular");
                    me.wrapper.find('#cust-pan').val(c.pan || "");
                    me.wrapper.find('#cust-tax-override').val(c.custom_tax_inclusive_override || "Default");
                    
                    // Parse Billing Address Text
                    const billLines = (c.custom_address_text || "").split('\n');
                    me.wrapper.find('#bill-line1').val(billLines[0] || "");
                    me.wrapper.find('#bill-line2').val(billLines[1] || "");
                    me.wrapper.find('#bill-city').val(billLines[2] || "");
                    me.wrapper.find('#bill-state').val(billLines[3] || "");
                    me.wrapper.find('#bill-pincode').val(billLines[4] || "");

                    // Parse Shipping Address Text
                    const shipLines = (c.custom_shipping_address_text || "").split('\n');
                    me.wrapper.find('#ship-line1').val(shipLines[0] || "");
                    me.wrapper.find('#ship-line2').val(shipLines[1] || "");
                    me.wrapper.find('#ship-city').val(shipLines[2] || "");
                    me.wrapper.find('#ship-state').val(shipLines[3] || "");
                    me.wrapper.find('#ship-pincode').val(shipLines[4] || "");

                    const isSame = c.custom_address_text && c.custom_address_text === c.custom_shipping_address_text;
                    me.wrapper.find('#same-as-billing').prop('checked', isSame);
                    me.toggle_same_as_billing(isSame);

                    me.wrapper.find('#smriti-customer-modal').addClass('open');
                }
            }
        });
    }

    close_customer_modal() {
        this.wrapper.find('#smriti-customer-modal').removeClass('open');
    }

    toggle_same_as_billing(isSame) {
        const shipSection = this.wrapper.find('#shipping-address-section');
        if (isSame) {
            shipSection.css({
                'opacity': '0.5',
                'pointer-events': 'none'
            });
            // Sync values
            this.wrapper.find('#ship-line1').val(this.wrapper.find('#bill-line1').val());
            this.wrapper.find('#ship-line2').val(this.wrapper.find('#bill-line2').val());
            this.wrapper.find('#ship-city').val(this.wrapper.find('#bill-city').val());
            this.wrapper.find('#ship-state').val(this.wrapper.find('#bill-state').val());
            this.wrapper.find('#ship-pincode').val(this.wrapper.find('#bill-pincode').val());
        } else {
            shipSection.css({
                'opacity': '1',
                'pointer-events': 'all'
            });
        }
    }

    auto_resolve_state(gstin, prefix) {
        if (!gstin || gstin.trim().length < 2) return;
        const code = gstin.trim().substring(0, 2);
        const state = this.GST_STATE_CODES[code];
        if (state) {
            const el = this.wrapper.find(`#${prefix}-state`);
            if (el.length) {
                el.val(state);
                el.addClass('retrieval-glowing');
                setTimeout(() => { el.removeClass('retrieval-glowing'); }, 2000);
            }
        }
    }

    save_customer_detail() {
        var me = this;
        const name = this.wrapper.find('#cust-name').val().trim();
        const mobile = this.wrapper.find('#cust-mobile').val().trim();
        const custId = this.wrapper.find('#cust-name-id').val();

        if (!name) {
            frappe.show_alert({message: __('Please enter the Customer Name.'), indicator: 'red'});
            return;
        }

        const btn = this.wrapper.find('#btn-save');
        btn.prop('disabled', true);

        // Construct addresses texts
        const billText = [
            this.wrapper.find('#bill-line1').val().trim(),
            this.wrapper.find('#bill-line2').val().trim(),
            this.wrapper.find('#bill-city').val().trim(),
            this.wrapper.find('#bill-state').val().trim(),
            this.wrapper.find('#bill-pincode').val().trim()
        ].join('\n');

        let shipText = billText;
        if (!this.wrapper.find('#same-as-billing').is(':checked')) {
            shipText = [
                this.wrapper.find('#ship-line1').val().trim(),
                this.wrapper.find('#ship-line2').val().trim(),
                this.wrapper.find('#ship-city').val().trim(),
                this.wrapper.find('#ship-state').val().trim(),
                this.wrapper.find('#ship-pincode').val().trim()
            ].join('\n');
        }

        frappe.call({
            method: 'smriti_retail_os.master_api.save_customer_detail',
            args: {
                customer_name: name,
                customer_type: this.wrapper.find('#cust-type').val(),
                customer_group: this.wrapper.find('#cust-group').val(),
                territory: this.wrapper.find('#cust-territory').val(),
                mobile_no: mobile,
                email_id: this.wrapper.find('#cust-email').val().trim(),
                tax_id: this.wrapper.find('#cust-gstin').val().trim(),
                gst_category: this.wrapper.find('#cust-gst-category').val(),
                pan: this.wrapper.find('#cust-pan').val().trim().toUpperCase(),
                custom_address_text: billText,
                custom_shipping_address_text: shipText,
                custom_tax_inclusive_override: this.wrapper.find('#cust-tax-override').val(),
                name: custId || null
            },
            freeze: true,
            freeze_message: __('Saving Customer Record...'),
            callback: function(r) {
                if (r.message) {
                    frappe.show_alert({message: __('Customer record saved successfully!'), indicator: 'green'});
                    me.close_customer_modal();
                    me.load_customers();
                }
                btn.prop('disabled', false);
            },
            error: function() {
                btn.prop('disabled', false);
            }
        });
    }
}
