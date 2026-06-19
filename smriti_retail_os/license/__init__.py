# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/license/__init__.py
# @description: SMRITI License package initialisation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/license/__init__.py
# @description: SMRITI License module — convenience re-exports.
# @authority: docs/architecture/licensing/SMRITI_LICENSE_ARCHITECTURE_V1.md
#

from smriti_retail_os.license.manager import check_feature, get_license_summary

__all__ = ["check_feature", "get_license_summary"]
