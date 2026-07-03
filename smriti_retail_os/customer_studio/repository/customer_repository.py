# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/customer_studio/repository/customer_repository.py
# @desc:    Data Access Repository Layer for SMRITI Customer Studio.
#           Encapsulates all database reads and writes to ERPNext Customer-related doctypes.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _


class CustomerRepository:
    """
    Isolates direct database access for SMRITI Customer and partner operations.
    Follows Rule 4 of SMRITI Constitution (Repository Layer Isolation).
    """

    @staticmethod
    def get_list(filters=None, fields=None, order_by="creation desc", limit=200):
        """Queries active customers from DB."""
        if filters is None:
            filters = {}
        filters["disabled"] = 0

        if fields is None:
            fields = ["name", "customer_name", "mobile_no", "customer_group", "territory"]

        return frappe.get_list(
            "Customer",
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit_page_length=int(limit)
        )

    @staticmethod
    def get_detail(customer_id):
        """Retrieves detailed attributes of a customer."""
        if not frappe.db.exists("Customer", customer_id):
            frappe.throw(_("Customer {0} does not exist.").format(customer_id), frappe.DoesNotExistError)

        doc = frappe.get_doc("Customer", customer_id)
        
        # Fetch associated primary address if exists
        billing_address = ""
        shipping_address = ""
        address_list = frappe.get_all(
            "Address",
            filters={"links.link_doctype": "Customer", "links.link_name": customer_id},
            fields=["name", "address_title", "address_line1", "address_line2", "city", "state", "pincode"]
        )
        if address_list:
            billing_address = address_list[0]
            if len(address_list) > 1:
                shipping_address = address_list[1]
            else:
                shipping_address = address_list[0]

        return {
            "customer_id": doc.name,
            "customer_name": doc.customer_name,
            "customer_type": doc.customer_type or "Individual",
            "mobile_no": doc.mobile_no or "",
            "email_id": doc.email_id or "",
            "customer_group": doc.customer_group or "Individual",
            "territory": doc.territory or "All Territories",
            "billing_address": billing_address,
            "shipping_address": shipping_address
        }

    @staticmethod
    def create(customer_data):
        """Creates a new Customer Doc and links Address."""
        cust = frappe.new_doc("Customer")
        cust.customer_name = customer_data["customer_name"]
        cust.customer_type = customer_data.get("customer_type", "Individual")
        cust.mobile_no = customer_data.get("mobile_no", "")
        cust.email_id = customer_data.get("email_id", "")
        cust.customer_group = customer_data.get("customer_group", "Individual")
        cust.territory = customer_data.get("territory", "All Territories")
        
        cust.insert(ignore_permissions=True)

        # Create primary address if provided
        if customer_data.get("address_line1"):
            addr = frappe.new_doc("Address")
            addr.address_title = customer_data["customer_name"]
            addr.address_type = "Billing"
            addr.address_line1 = customer_data["address_line1"]
            addr.address_line2 = customer_data.get("address_line2", "")
            addr.city = customer_data.get("city", "")
            addr.state = customer_data.get("state", "")
            addr.pincode = customer_data.get("pincode", "")
            addr.append("links", {"link_doctype": "Customer", "link_name": cust.name})
            addr.insert(ignore_permissions=True)

        return cust.name

    @staticmethod
    def update(customer_id, customer_data):
        """Updates attributes of an existing Customer doc."""
        if not frappe.db.exists("Customer", customer_id):
            frappe.throw(_("Customer {0} not found.").format(customer_id), frappe.DoesNotExistError)

        doc = frappe.get_doc("Customer", customer_id)
        if "customer_name" in customer_data:
            doc.customer_name = customer_data["customer_name"]
        if "customer_type" in customer_data:
            doc.customer_type = customer_data["customer_type"]
        if "mobile_no" in customer_data:
            doc.mobile_no = customer_data["mobile_no"]
        if "email_id" in customer_data:
            doc.email_id = customer_data["email_id"]
        if "customer_group" in customer_data:
            doc.customer_group = customer_data["customer_group"]
        if "territory" in customer_data:
            doc.territory = customer_data["territory"]

        doc.save(ignore_permissions=True)
        return doc.name

    @staticmethod
    def delete(customer_id):
        """Disables/Soft-deletes the Customer."""
        if not frappe.db.exists("Customer", customer_id):
            return False
        frappe.db.set_value("Customer", customer_id, "disabled", 1)
        frappe.db.commit()
        return True
