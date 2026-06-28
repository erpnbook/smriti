// DEPRECATED: Compatibility wrapper for SMRITI Desk Control Center route.
// Canonical implementation resides in: public/js/smriti_desk.js
// Target removal: SMRITI v2.0

frappe.pages['smriti-desk'].on_page_load = function(wrapper) {
    frappe.require('/assets/smriti_retail_os/js/smriti_desk.js', function() {
        if (typeof SmritiDeskPage !== 'undefined') {
            const page = frappe.ui.make_app_page({
                parent: wrapper,
                title: 'Control Center',
                single_column: true
            });
            if (window.SMRITI && typeof SMRITI.renderSidebar === 'function') {
                SMRITI.renderSidebar("desk");
            }
            window.smriti_desk = new SmritiDeskPage(wrapper);
        }
    });
};
