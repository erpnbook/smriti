# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/navigation/validator/base_validator.py
# @description: Base interface and registration for SMRITI Navigation Validator rules.
# @author: Jawahar R. Mallah
#

VALIDATOR_REGISTRY = []

class BaseValidator(object):
    rule_id = ""
    severity = ""
    title = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register rule instance automatically if it is a concrete class defining a rule_id
        if cls.rule_id:
            # Avoid duplicate registrations
            if not any(r.rule_id == cls.rule_id for r in VALIDATOR_REGISTRY):
                VALIDATOR_REGISTRY.append(cls())

    def validate(self, nav_config):
        """
        Evaluates navigation configuration.
        Returns list of structured warning dicts.
        """
        raise NotImplementedError("Subclasses must implement validate method")
