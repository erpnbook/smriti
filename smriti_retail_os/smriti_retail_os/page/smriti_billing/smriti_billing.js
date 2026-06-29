/**
 * @file: smriti_retail_os/smriti_retail_os/page/smriti_billing/smriti_billing.js
 * @description: Thin wrapper loader for SMRITI POS Billing Terminal Desk page.
 *               Loads the canonical public assets dynamically to avoid duplication.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @version: 1.9.0
 * @sprint: Sprint 2 — Billing UI Consolidation
 */

frappe.pages['smriti-billing'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('SMRITI Retail Billing'),
        single_column: true
    });

    // Dynamically load canonical stylesheet and script assets
    frappe.require([
        "/assets/smriti_retail_os/css/smriti-billing.css",
        "/assets/smriti_retail_os/js/smriti_billing.js"
    ], function() {
        console.log("[SMRITI Billing Page Wrapper] Canonical assets loaded successfully. Mounting Billing Controller.");
        // Initialize the controller from the canonical script
        wrapper.smriti_billing = new SmritiBillingController(wrapper, page);
    });
}
