/**
 * @file: smriti_retail_os/smriti_retail_os/report/psv_stock_ageing/psv_stock_ageing.js
 * @description: Handles user login, registration, and JWT token generation.
 * @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
 * @date: 2026-05-28
 * @version: 1.8.6
 * @license: MIT
 * * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
 */
frappe.query_reports["PSV Stock Ageing"] = {
    filters: [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "party_stock_account",
            "label": __("Party Account"),
            "fieldtype": "Link",
            "options": "SMRITI Party Stock Account"
        }
    ]
};
