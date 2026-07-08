# -*- coding: utf-8 -*-
# @file:    smriti_retail_os/core/forms/retail_forms/__init__.py
# @desc:    SMRITI Retail Form Presets — pre-built form definitions for retail operations.
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
from smriti_retail_os.core.forms.retail_forms.purchase_form import PurchaseForm  # noqa: F401
from smriti_retail_os.core.forms.retail_forms.customer_form import CustomerForm  # noqa: F401
from smriti_retail_os.core.forms.retail_forms.product_form import ProductForm    # noqa: F401
from smriti_retail_os.core.forms.retail_forms.grn_form import GRNForm            # noqa: F401

__all__ = ["PurchaseForm", "CustomerForm", "ProductForm", "GRNForm"]
