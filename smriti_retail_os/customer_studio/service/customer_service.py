# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/customer_studio/service/customer_service.py
# @desc:    Business Logic / Service Layer for SMRITI Customer Studio.
#           Coordinates validation and interacts with CustomerRepository.
# @author:  Jawahar R. Mallah
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from smriti_retail_os.customer_studio.repository.customer_repository import CustomerRepository


class CustomerService:
    """
    Implements business rules and validation logic for SMRITI Customers.
    """

    @staticmethod
    def get_customers(filters=None, fields=None, order_by="creation desc", limit=200):
        """Fetches active customers using repository."""
        return CustomerRepository.get_list(filters, fields, order_by, limit)

    @staticmethod
    def get_customer_detail(customer_id):
        """Gets complete customer details."""
        return CustomerRepository.get_detail(customer_id)

    @staticmethod
    def save_customer(customer_data, customer_id=None):
        """
        Validates customer details and creates or updates a customer.
        - Enforces mobile number presence and 10-digit numeric constraint.
        """
        if not customer_data.get("customer_name"):
            frappe.throw(_("Customer Name is required."))

        mobile = customer_data.get("mobile_no")
        if not mobile:
            frappe.throw(_("Mobile Number is required."))
        # Basic 10-digit verification for India compliance
        clean_mobile = "".join(filter(str.isdigit, str(mobile)))
        if len(clean_mobile) < 10:
            frappe.throw(_("Mobile number must contain at least 10 digits."))

        # Set default groups
        if not customer_data.get("customer_group"):
            customer_data["customer_group"] = "Individual"
        if not customer_data.get("territory"):
            customer_data["territory"] = "All Territories"

        if customer_id:
            return CustomerRepository.update(customer_id, customer_data)
        else:
            # Verify unique name
            if smriti.db.exists("Customer", customer_data["customer_name"]):
                frappe.throw(_("Customer with name {0} already exists.").format(customer_data["customer_name"]))
            return CustomerRepository.create(customer_data)

    @staticmethod
    def delete_customer(customer_id):
        """Soft deletes customer by disabling them."""
        return CustomerRepository.delete(customer_id)
