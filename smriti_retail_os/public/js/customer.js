/**
 * @file: smriti_retail_os/public/js/customer.js
 * @description: Form controller for SMRITI Customer Master customizations..
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.8.6
 * @license: GPL-3.0-only
 * SPDX-License-Identifier: GPL-3.0-only
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
        frm.set_df_property('primary_mobile_no', 'description', 'Enter 10-digit mobile number');
    },
    refresh: function(frm) {
        const is_smriti = frappe.user.has_role("SMRITI Store Manager") || frappe.user.has_role("SMRITI Cashier");
        if (is_smriti) {
            // 1. Hide Advanced Tabs
            const tabs_to_hide = [
                'accounting_tab', 'sales_team_tab', 'portal_users_tab', 
                'more_info_tab', 'connections_tab', 'tax_tab'
            ];
            tabs_to_hide.forEach(tab => frm.toggle_display(tab, false));

            // 2. Make custom SMRITI fields prominent
            frm.toggle_display('custom_address_text', true);
            frm.toggle_display('custom_birthday', true);
            frm.toggle_display('custom_anniversary', true);

            // 3. Render a beautiful dynamic GSTIN validation box if GSTIN is present
            if (frm.doc.tax_id) {
                frm.trigger('validate_gstin_client');
            }
        }
    },
    tax_id: function(frm) {
        // Trigger validation when GSTIN (tax_id) changes
        if (frm.doc.tax_id) {
            frm.trigger('validate_gstin_client');
        }
    },
    primary_mobile_no: function(frm) {
        if (frm.doc.primary_mobile_no) {
            const clean_num = frm.doc.primary_mobile_no.replace(/\D/g, '');
            if (clean_num.length !== 10) {
                frappe.msgprint({
                    title: __('Invalid Mobile Number'),
                    message: __('Please enter a valid 10-digit mobile number.'),
                    indicator: 'red'
                });
            } else {
                frm.set_value('primary_mobile_no', clean_num);
            }
        }
    },
    validate_gstin_client: function(frm) {
        const gstin = frm.doc.tax_id;
        if (!gstin || gstin.length !== 15) return;

        frappe.call({
            method: 'india_compliance.gst_india.doctype.gstin.gstin.get_gstin_status',
            args: {
                gstin: gstin,
                force_update: true
            },
            freeze: true,
            freeze_message: __('Validating GSTIN via India Compliance...'),
            callback: function(r) {
                if (r.message) {
                    const status = r.message.status || 'Unknown';
                    const legal_name = r.message.legal_name || 'N/A';
                    const state = r.message.state_jurisdiction || 'N/A';
                    
                    const badge_color = status === 'Active' ? '#0d9488' : '#e11d48';
                    const bg_color = status === 'Active' ? 'rgba(13, 148, 136, 0.1)' : 'rgba(225, 29, 72, 0.1)';
                    const border_color = status === 'Active' ? 'rgba(13, 148, 136, 0.3)' : 'rgba(225, 29, 72, 0.3)';

                    // Render dynamic information box in field description or a separate HTML area if we want.
                    frm.set_df_property('tax_id', 'description', 
                        `<div style="padding: 10px; margin-top: 5px; background: ${bg_color}; border: 1px solid ${border_color}; border-radius: 6px;">
                            <span style="font-weight: 700; color: ${badge_color};">GSTIN: ${status}</span><br>
                            <span style="font-size: 0.9em; color: #4b5563;"><b>Legal Name:</b> ${legal_name}</span><br>
                            <span style="font-size: 0.9em; color: #4b5563;"><b>Jurisdiction:</b> ${state}</span>
                         </div>`
                    );
                } else {
                    frm.set_df_property('tax_id', 'description', 
                        `<span style="color: #e11d48; font-weight: 600;">GSTIN check digit or structure validation failed.</span>`
                    );
                }
            }
        });
    }
});
