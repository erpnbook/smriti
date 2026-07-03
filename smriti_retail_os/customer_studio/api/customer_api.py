# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/customer_studio/api/customer_api.py
# @desc:    Whitelisted API boundaries for SMRITI Customer Studio.
#           Interacts exclusively with CustomerService.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _
from smriti_retail_os.customer_studio.service.customer_service import CustomerService
from smriti_retail_os.security_api import check_page_access


def _check_access():
    """Verifies that user is logged in and possesses Customer Directory access rights."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication required."), frappe.PermissionError)
    check_page_access("customers")


@frappe.whitelist()
def get_customers(limit=200):
    """Retrieves list of active customers for Grid."""
    _check_access()
    return CustomerService.get_customers(limit=limit)


@frappe.whitelist()
def get_customer_detail(customer_id):
    """Retrieves complete attributes of a customer for the editor form."""
    _check_access()
    if not customer_id:
        frappe.throw(_("Customer ID parameter is required."))
    return CustomerService.get_customer_detail(customer_id)


@frappe.whitelist()
def save_customer(customer_data, customer_id=None):
    """Creates a new customer or updates an existing one."""
    _check_access()
    if not customer_data:
        frappe.throw(_("Customer data is required."))
    
    return CustomerService.save_customer(customer_data, customer_id)


@frappe.whitelist()
def delete_customer(customer_id):
    """Disables the specified customer."""
    _check_access()
    if not customer_id:
        frappe.throw(_("Customer ID parameter is required."))
    return CustomerService.delete_customer(customer_id)
