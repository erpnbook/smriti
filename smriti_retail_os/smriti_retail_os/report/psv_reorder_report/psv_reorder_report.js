/**
 * @file: smriti_retail_os/smriti_retail_os/report/psv_reorder_report/psv_reorder_report.js
 * @description: Frontend filters for the PSV Reorder Recommendation Report.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-06-09
 * @version: 1.8.6
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
frappe.query_reports["PSV Reorder Report"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "zone",
			label: __("Zone"),
			fieldtype: "Select",
			options: "\nNorth\nSouth\nEast\nWest\nCentral"
		},
		{
			fieldname: "priority",
			label: __("Priority"),
			fieldtype: "Select",
			options: "\nCritical\nHigh\nMedium\nLow"
		},
		{
			fieldname: "show_zero",
			label: __("Show Zero Recommendations"),
			fieldtype: "Check",
			default: 0
		}
	]
};
