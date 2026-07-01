# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/navigation/validator/__init__.py
# @description: Auto-registers all SMRITI Navigation Validator rules.
# @author: Jawahar R. Mallah
#

from smriti_retail_os.navigation.validator.base_validator import VALIDATOR_REGISTRY, BaseValidator
from smriti_retail_os.navigation.validator.duplicate_rule import DuplicateRule
from smriti_retail_os.navigation.validator.cycle_rule import CycleRule
from smriti_retail_os.navigation.validator.route_rule import RouteRule
from smriti_retail_os.navigation.validator.icon_rule import IconRule
from smriti_retail_os.navigation.validator.permission_rule import PermissionRule
from smriti_retail_os.navigation.validator.naming_rule import NamingRule
