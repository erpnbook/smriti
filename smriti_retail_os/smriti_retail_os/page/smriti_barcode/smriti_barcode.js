// DEPRECATED: Compatibility wrapper for SMRITI Barcode Printer Desk route.
// Canonical implementation resides in: public/js/smriti_barcode.js
// Target removal: SMRITI v2.0

frappe.pages['smriti-barcode'].on_page_load = function(wrapper) {
    frappe.require([
        '/assets/smriti_retail_os/css/smriti-barcode.css',
        '/assets/smriti_retail_os/js/smriti_barcode.js'
    ], function() {
        if (typeof SmritiBarcodeController !== 'undefined') {
            var page = frappe.ui.make_app_page({
                parent: wrapper,
                title: __('SMRITI Barcode Printing'),
                single_column: true
            });
            new SmritiBarcodeController(wrapper, page);
        }
    });
};
