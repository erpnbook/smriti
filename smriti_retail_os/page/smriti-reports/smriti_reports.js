frappe.pages["smriti-reports"].on_page_load = function (wrapper) {
    frappe.ui.make_app_page({
        parent: wrapper,
        title: "Reports",
        single_column: true
    });

    if (window.SMRITI && typeof SMRITI.renderSidebar === 'function') {
        SMRITI.renderSidebar("reports");
    }

    // Main logic is in public/js/smriti_reports.js (loaded globally)
    if (window.SMRITIReports) {
        window.SMRITIReports.init(wrapper);
    } else {
        frappe.require("/assets/smriti_retail_os/js/smriti_reports.js", function () {
            window.SMRITIReports && window.SMRITIReports.init(wrapper);
        });
    }
};
