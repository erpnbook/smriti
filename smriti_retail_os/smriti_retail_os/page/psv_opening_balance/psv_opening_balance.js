/**
 * @file: smriti_retail_os/smriti_retail_os/page/psv_opening_balance/psv_opening_balance.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.0.0
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
frappe.pages['psv-opening-balance'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'PSV Opening Balance Import',
        single_column: true
    });

    $(page.main).html(`
        <div style="max-width:700px; margin:30px auto; padding:20px; background: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div class="alert alert-warning">
                <strong>⚠ One-Time Migration Utility.</strong>
                Use only during initial PSV deployment. 
                Each party+item can only receive one Opening Balance voucher to maintain audit integrity.
            </div>
            <div class="form-group">
                <label style="font-weight:600">Company</label>
                <div id="ob-company-field"></div>
            </div>
            <div class="form-group">
                <label style="font-weight:600">Party Stock Account</label>
                <div id="ob-party-field"></div>
            </div>
            <div class="form-group">
                <label style="font-weight:600">Upload Excel</label>
                <input type="file" id="ob-file" class="form-control" accept=".xlsx,.xls" style="border: 1px dashed #d1d8dd; padding: 20px; text-align: center;">
                <small class="text-muted">Columns: 1. Item Variant Code | 2. Opening Qty</small>
            </div>
            <div style="margin-top:20px; display:flex; gap:10px;">
                <button class="btn btn-primary" id="ob-preview">
                    <i class="fa fa-eye"></i> Preview Data
                </button>
                <button class="btn btn-success" id="ob-import" style="display:none;">
                    <i class="fa fa-check"></i> Confirm Import
                </button>
            </div>
            <div id="ob-preview-area" style="margin-top:30px; border-top: 1px solid #eee; padding-top: 20px;"></div>
        </div>
    `);

    // Setup Link Fields
    let company_field = frappe.ui.form.make_control({
        parent: page.main.find('#ob-company-field'),
        df: {
            fieldtype: 'Link',
            options: 'Company',
            fieldname: 'company',
            placeholder: 'Select Company',
            only_select: true
        },
        render_input: true
    });
    company_field.set_value(frappe.defaults.get_user_default("Company"));

    let party_field = frappe.ui.form.make_control({
        parent: page.main.find('#ob-party-field'),
        df: {
            fieldtype: 'Link',
            options: 'SMRITI Party Stock Account',
            fieldname: 'party_stock_account',
            placeholder: 'Select Party Stock Account',
            only_select: true,
            get_query: function() {
                return {
                    filters: { company: company_field.get_value() }
                };
            }
        },
        render_input: true
    });

    let parsedRows = [];

    $('#ob-preview').click(async function() {
        const file = document.getElementById('ob-file').files[0];
        if (!file) { frappe.msgprint(__('Please select an Excel file first.')); return; }
        
        const company = company_field.get_value();
        const party = party_field.get_value();
        if (!company || !party) { frappe.msgprint(__('Company and Party Stock Account are required.')); return; }

        // Upload file
        const fd = new FormData();
        fd.append('file', file, file.name);
        fd.append('is_private', 1);
        fd.append('folder', 'Home/Attachments');

        frappe.show_alert({message: __('Uploading and parsing...'), indicator: 'blue'});

        try {
            const up = await fetch('/api/method/upload_file', {
                method: 'POST',
                headers: { 'X-Frappe-CSRF-Token': frappe.csrf_token },
                body: fd
            });
            const upData = await up.json();
            const fileUrl = upData.message?.file_url;
            if (!fileUrl) { frappe.msgprint(__('Upload failed.')); return; }

            frappe.call({
                method: 'smriti_retail_os.utils.opening_balance.parse_opening_excel',
                args: { file_url: fileUrl },
                callback(r) {
                    parsedRows = r.message?.rows || [];
                    const errors = r.message?.errors || [];
                    
                    let html = `<h5 style="margin-bottom:15px;">${parsedRows.length} valid rows | ${errors.length} errors</h5>`;
                    
                    if (errors.length) {
                        html += `<div class="alert alert-danger" style="max-height:150px; overflow-y:auto; font-family:monospace; font-size:12px;">`;
                        errors.forEach(err => { html += `<div>${err}</div>`; });
                        html += `</div>`;
                    }

                    if (parsedRows.length > 0) {
                        html += `
                            <table class="table table-bordered table-condensed" style="font-size:13px;">
                                <thead style="background:#f8f9fa;">
                                    <tr><th>Item Variant</th><th style="text-align:right;">Opening Qty</th></tr>
                                </thead>
                                <tbody>
                        `;
                        parsedRows.slice(0, 50).forEach(r => {
                            html += `<tr><td>${r.item_code}</td><td style="text-align:right; font-weight:bold;">${r.qty}</td></tr>`;
                        });
                        if (parsedRows.length > 50) {
                            html += `<tr><td colspan="2" class="text-center text-muted">... and ${parsedRows.length - 50} more rows</td></tr>`;
                        }
                        html += `</tbody></table>`;
                        $('#ob-import').show();
                    } else {
                        $('#ob-import').hide();
                    }
                    
                    $('#ob-preview-area').html(html);
                }
            });
        } catch (e) {
            frappe.msgprint(__('Error uploading file.'));
        }
    });

    $('#ob-import').click(function() {
        const company = company_field.get_value();
        const party = party_field.get_value();
        
        frappe.confirm(
            __('Are you sure you want to import opening balances for {0}? This action is immutable.', [party]),
            function() {
                frappe.call({
                    method: 'smriti_retail_os.psv_service.process_opening_balance',
                    args: { 
                        company: company, 
                        party_stock_account: party, 
                        items: parsedRows 
                    },
                    freeze: true,
                    callback(r) {
                        frappe.show_alert({ message: __('Opening Balances imported successfully!'), indicator: 'green' });
                        $('#ob-import').hide();
                        $('#ob-preview-area').html('<div class="alert alert-success">Import Complete. Check Shadow Ledger for entries.</div>');
                        parsedRows = [];
                        document.getElementById('ob-file').value = "";
                    }
                });
            }
        );
    });
};
