# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/services/lookup_service.py
# @desc:    Universal Smart Lookup Service Layer. Maps abstract entities to DocTypes
#           and handles generic search, recents, validation, and Quick Create.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 4 (Business Logic)
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
from frappe import _
from frappe.utils import flt, cint, nowdate
from smriti_retail_os.repositories.lookup_repository import LookupRepository


ENTITY_MAP = {
    "Customer": {
        "doctype": "Customer",
        "search_fields": ["name", "customer_name", "mobile_no", "email_id"],
        "fields": ["name", "customer_name as title", "mobile_no", "email_id"],
        "title_field": "customer_name",
        "create_fields": ["customer_name", "mobile_no"]
    },
    "Supplier": {
        "doctype": "SMRITI Supplier",
        "search_fields": ["name", "supplier_name", "mobile_no", "email_id", "tax_id"],
        "fields": ["name", "supplier_name as title", "mobile_no", "email_id", "tax_id"],
        "title_field": "supplier_name",
        "create_fields": ["supplier_name", "mobile_no", "email_id"]
    },
    "Product": {
        "doctype": "Item",
        "search_fields": ["item_code", "item_name"],
        "fields": ["item_code as name", "item_name as title", "standard_rate"],
        "title_field": "item_name",
        "create_fields": ["item_code", "item_name", "standard_rate"]
    },
    "Warehouse": {
        "doctype": "Warehouse",
        "search_fields": ["name", "warehouse_name"],
        "fields": ["name", "warehouse_name as title"],
        "title_field": "warehouse_name",
        "create_fields": ["warehouse_name"]
    },
    "Employee": {
        "doctype": "Employee",
        "search_fields": ["name", "employee_name", "cell_number"],
        "fields": ["name", "employee_name as title", "cell_number"],
        "title_field": "employee_name",
        "create_fields": ["employee_name", "cell_number"]
    },
    "Salesperson": {
        "doctype": "Sales Person",
        "search_fields": ["name", "sales_person_name"],
        "fields": ["name", "sales_person_name as title"],
        "title_field": "sales_person_name",
        "create_fields": ["sales_person_name"]
    },
    "Brand": {
        "doctype": "Brand",
        "search_fields": ["name", "brand_name"],
        "fields": ["name", "brand_name as title"],
        "title_field": "brand_name",
        "create_fields": ["brand_name"]
    },
    "Category": {
        "doctype": "Item Group",
        "search_fields": ["name", "item_group_name"],
        "fields": ["name", "item_group_name as title"],
        "title_field": "item_group_name",
        "create_fields": ["item_group_name"]
    },
    "UOM": {
        "doctype": "UOM",
        "search_fields": ["name", "uom_name"],
        "fields": ["name", "uom_name as title"],
        "title_field": "uom_name",
        "create_fields": ["uom_name"]
    },
    "Tax Template": {
        "doctype": "Item Tax Template",
        "search_fields": ["name", "title"],
        "fields": ["name", "title"],
        "title_field": "title",
        "create_fields": ["title"]
    },
    "Payment Terms": {
        "doctype": "Payment Terms Template",
        "search_fields": ["name", "template_name"],
        "fields": ["name", "template_name as title"],
        "title_field": "template_name",
        "create_fields": ["template_name"]
    },
    "Currency": {
        "doctype": "Currency",
        "search_fields": ["name", "currency_name"],
        "fields": ["name", "currency_name as title"],
        "title_field": "currency_name",
        "create_fields": ["currency_name"]
    },
    "Company": {
        "doctype": "Company",
        "search_fields": ["name", "company_name"],
        "fields": ["name", "company_name as title"],
        "title_field": "company_name",
        "create_fields": ["company_name"]
    }
}


class LookupService:
    @staticmethod
    def get_config(entity):
        if entity not in ENTITY_MAP:
            frappe.throw(_("Entity type '{0}' is not supported by SMRITI Universal Lookup.").format(entity))
        return ENTITY_MAP[entity]

    @staticmethod
    def search(entity, text=None, filters=None, limit=20):
        config = LookupService.get_config(entity)
        doctype = config["doctype"]

        # Base Filters (disabled check where applicable)
        static_filters = {}
        meta = frappe.get_meta(doctype)
        if meta.has_field("disabled"):
            static_filters["disabled"] = 0

        if filters:
            static_filters.update(filters)

        # Or filters for search matches
        or_filters = []
        if text:
            for field in config["search_fields"]:
                or_filters.append([field, "like", f"%{text}%"])

        results = frappe.get_list(
            doctype,
            filters=static_filters,
            or_filters=or_filters,
            fields=config["fields"],
            limit_page_length=cint(limit) or 20
        )

        # Normalize results to standard output envelope {value, label}
        normalized = []
        for r in results:
            # We map name to 'value', and title to 'label'
            label = r.get("title") or r.get("name")
            normalized.append({
                "value": r.get("name"),
                "label": label,
                "detail": r
            })
        return normalized

    @staticmethod
    def recent(entity):
        config = LookupService.get_config(entity)
        doctype = config["doctype"]

        static_filters = {}
        meta = frappe.get_meta(doctype)
        if meta.has_field("disabled"):
            static_filters["disabled"] = 0

        results = frappe.get_list(
            doctype,
            filters=static_filters,
            fields=config["fields"],
            order_by="modified desc",
            limit_page_length=5
        )

        normalized = []
        for r in results:
            label = r.get("title") or r.get("name")
            normalized.append({
                "value": r.get("name"),
                "label": label,
                "detail": r
            })
        return normalized

    @staticmethod
    def validate(entity, value):
        config = LookupService.get_config(entity)
        doctype = config["doctype"]
        exists = frappe.db.exists(doctype, value)
        return {"exists": bool(exists), "value": value}

    @staticmethod
    def create(entity, data):
        config = LookupService.get_config(entity)
        doctype = config["doctype"]

        # Validate mandatory data presence
        if not data:
            frappe.throw(_("Creation payload is empty."))

        doc = LookupRepository.new_doc(doctype)

        # Entity specific setup to ensure document is valid
        if entity == "Customer":
            doc.customer_name = data.get("customer_name")
            doc.mobile_no = data.get("mobile_no")
            doc.customer_group = data.get("customer_group") or frappe.db.get_value("Customer Group", {"is_group": 0}, "name") or "Individual"
            doc.territory = data.get("territory") or frappe.db.get_value("Territory", {"is_group": 0}, "name") or "India"
            doc.customer_type = data.get("customer_type") or "Company"

        elif entity == "Supplier":
            doc.supplier_name = data.get("supplier_name")
            doc.mobile_no = data.get("mobile_no")
            doc.email_id = data.get("email_id")
            doc.supplier_type = data.get("supplier_type") or "Company"
            doc.supplier_group = data.get("supplier_group") or frappe.db.get_value("Supplier Group", {"is_group": 0}, "name") or "All Supplier Groups"

        elif entity == "Product":
            doc.item_code = data.get("item_code") or data.get("barcode")
            doc.item_name = data.get("item_name")
            doc.standard_rate = flt(data.get("standard_rate"))
            doc.stock_uom = data.get("uom") or "Nos"
            doc.item_group = data.get("item_group") or frappe.db.get_value("Item Group", {"is_group": 0}, "name") or "Products"
            
            # Resolve HSN for India Compliance
            try:
                default_hsn = frappe.db.get_single_value("SMRITI Settings", "default_hsn_code")
                if default_hsn:
                    doc.gst_hsn_code = default_hsn
            except Exception:
                pass

        elif entity == "Warehouse":
            doc.warehouse_name = data.get("warehouse_name")
            # Warehouse needs warehouse_type
            doc.warehouse_type = data.get("warehouse_type") or "Transit"
            doc.company = data.get("company") or frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")

        elif entity == "Employee":
            doc.employee_name = data.get("employee_name")
            doc.cell_number = data.get("cell_number")
            doc.date_of_joining = data.get("date_of_joining") or nowdate()
            doc.gender = data.get("gender") or "Male"

        elif entity == "Salesperson":
            doc.sales_person_name = data.get("sales_person_name")

        elif entity == "Brand":
            doc.brand_name = data.get("brand_name")

        elif entity == "Category":
            doc.item_group_name = data.get("item_group_name")
            doc.parent_item_group = data.get("parent_item_group") or "All Item Groups"

        elif entity == "UOM":
            doc.uom_name = data.get("uom_name")

        elif entity == "Tax Template":
            doc.title = data.get("title")

        elif entity == "Payment Terms":
            doc.template_name = data.get("template_name")

        elif entity == "Currency":
            doc.currency_name = data.get("currency_name")

        elif entity == "Company":
            doc.company_name = data.get("company_name")
            doc.default_currency = data.get("default_currency") or "INR"

        else:
            # Fallback for dynamic fields matching dictionary keys
            for key, val in data.items():
                if doc.meta.has_field(key):
                    doc.set(key, val)

        doc.insert(ignore_permissions=True)
        return {
            "value": doc.name,
            "label": doc.get(config["title_field"]) or doc.name,
            "detail": doc
        }
