# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/forms/retail_forms/customer_form.py
# @desc:    SMRITI Customer Form.
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
from smriti_retail_os.core.forms.form_engine import SmritiForm
from smriti_retail_os.core.forms.field import (
    TextField, SelectField, LookupField, NumberField,
    CurrencyField, TextAreaField, SectionBreak
)


class CustomerForm(SmritiForm):
    """SMRITI Customer Form."""

    MODEL = "Customer"
    TITLE = "Customer"

    FIELDS = [
        SectionBreak("Customer Details"),
        TextField(  "customer_name",   "Customer Name",   required=True, max_length=140),
        SelectField("customer_type",   "Type",
                    options=["Individual", "Company"], default="Individual"),
        LookupField("customer_group",  "Customer Group",  model="CustomerGroup"),
        LookupField("territory",       "Territory",       model="Territory"),
        TextField(  "mobile_no",       "Mobile Number",   max_length=15),
        TextField(  "email_id",        "Email",           max_length=140),

        SectionBreak("Credit & Tax"),
        CurrencyField("credit_limit",  "Credit Limit",    default=0, min_value=0),
        TextField(  "gstin",           "GSTIN",           max_length=15),

        SectionBreak("Notes", collapsible=True),
        TextAreaField("customer_details", "Customer Notes", rows=3),
    ]
