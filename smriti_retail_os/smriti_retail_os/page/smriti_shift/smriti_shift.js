// DEPRECATED: Compatibility wrapper for SMRITI Shift Desk route.
// Canonical implementation resides in: public/js/smriti_shift.js
// Target removal: SMRITI v2.0

frappe.pages['smriti-shift'].on_page_load = function(wrapper) {
    frappe.require('/assets/smriti_retail_os/js/smriti_shift.js', function() {
        if (typeof SmritiShiftPage !== 'undefined') {
            const page = frappe.ui.make_app_page({
                parent: wrapper,
                title: 'SMRITI Day Open / Close',
                single_column: true
            });
            window.smriti_shift = new SmritiShiftPage(wrapper);
        }
    });
};
