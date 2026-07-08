# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/forms/validator.py
# @desc:    SMRITI Form Engine — Validation engine.
#           Validates form data against field definitions and business rules.
#           Returns a ValidationResult, never raises exceptions directly.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ── Validation Result ──────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    """
    Result of a form validation run.

    Attributes:
        ok (bool):           True if all validations passed
        errors (dict):       {field_name: [error_message, ...]}
        global_errors (list): Form-level errors not tied to a specific field

    Usage:
        result = validator.validate(form, data)
        if not result.ok:
            for field_name, messages in result.errors.items():
                print(f"{field_name}: {'; '.join(messages)}")
    """
    ok: bool = True
    errors: Dict[str, List[str]] = field(default_factory=dict)
    global_errors: List[str] = field(default_factory=list)

    def add_field_error(self, field_name: str, message: str):
        """Add a field-level error and mark the result as failed."""
        self.ok = False
        self.errors.setdefault(field_name, []).append(message)

    def add_global_error(self, message: str):
        """Add a form-level error not tied to a specific field."""
        self.ok = False
        self.global_errors.append(message)

    def merge(self, other: "ValidationResult"):
        """Merge another result into this one."""
        if not other.ok:
            self.ok = False
            for fname, msgs in other.errors.items():
                for msg in msgs:
                    self.add_field_error(fname, msg)
            for msg in other.global_errors:
                self.add_global_error(msg)

    def to_dict(self) -> dict:
        return {
            "ok":            self.ok,
            "errors":        self.errors,
            "global_errors": self.global_errors,
        }


# ── Built-in Validation Rules ──────────────────────────────────────────────────

class FormValidator:
    """
    SMRITI Form Validator.

    Validates form data against field definitions and an optional set
    of business rules. Returns a ValidationResult — never raises exceptions.

    Usage:
        validator = FormValidator()
        validator.add_rule(ValidationRule.custom("grand_total",
            lambda v, d: (float(v or 0) > 0, "Total must be greater than zero")))

        result = validator.validate(form.fields, data)
        if not result.ok:
            smriti.errors.raise_validation("Validation Failed",
                "; ".join(result.global_errors or ["Please fix the highlighted fields."]))
    """

    def __init__(self):
        self._custom_rules: List["ValidationRule"] = []

    def add_rule(self, rule: "ValidationRule") -> "FormValidator":
        """Add a custom validation rule."""
        self._custom_rules.append(rule)
        return self

    def validate(self, fields, data: dict) -> ValidationResult:
        """
        Validate form data against field definitions and custom rules.

        Args:
            fields (list): List of SmritiField definitions (from SmritiForm.fields)
            data (dict):   Form data {fieldname: value}

        Returns:
            ValidationResult
        """
        result = ValidationResult()

        for f in fields:
            # Skip section breaks and hidden fields
            if not hasattr(f, "name"):
                continue
            if getattr(f, "hidden", False):
                continue

            value = data.get(f.name)

            # Required check
            if getattr(f, "required", False) and _is_empty(value):
                result.add_field_error(f.name,
                    f"{f.label} is required. Please fill in this field.")

            # Type-specific checks
            from smriti_retail_os.core.forms.field import (
                NumberField, CurrencyField, TableField, TextField, TextAreaField
            )
            if isinstance(f, (NumberField, CurrencyField)) and not _is_empty(value):
                try:
                    num = float(value)
                    if hasattr(f, "min_value") and f.min_value is not None and num < f.min_value:
                        result.add_field_error(f.name,
                            f"{f.label} must be at least {f.min_value}.")
                    if hasattr(f, "max_value") and f.max_value is not None and num > f.max_value:
                        result.add_field_error(f.name,
                            f"{f.label} must not exceed {f.max_value}.")
                except (TypeError, ValueError):
                    result.add_field_error(f.name,
                        f"{f.label} must be a number.")

            if isinstance(f, (TextField, TextAreaField)) and not _is_empty(value):
                if hasattr(f, "max_length") and len(str(value)) > f.max_length:
                    result.add_field_error(f.name,
                        f"{f.label} must not exceed {f.max_length} characters.")

            if isinstance(f, TableField) and getattr(f, "min_rows", 0) > 0:
                rows = value if isinstance(value, list) else []
                if len(rows) < f.min_rows:
                    result.add_field_error(f.name,
                        f"{f.label} must have at least {f.min_rows} row(s).")

        # Custom rules
        for rule in self._custom_rules:
            rule_result = rule.evaluate(data)
            result.merge(rule_result)

        return result


# ── Validation Rule ────────────────────────────────────────────────────────────

class ValidationRule:
    """
    A single validation rule for FormValidator.

    Use the class methods to create common rule types without subclassing.
    """

    def __init__(self, evaluator: Callable[[dict], ValidationResult]):
        self._evaluator = evaluator

    def evaluate(self, data: dict) -> ValidationResult:
        return self._evaluator(data)

    # ── Factory methods ─────────────────────────────────────────────────────

    @classmethod
    def required(cls, field_name: str, label: str) -> "ValidationRule":
        """Field must not be empty."""
        def check(data):
            r = ValidationResult()
            if _is_empty(data.get(field_name)):
                r.add_field_error(field_name, f"{label} is required.")
            return r
        return cls(check)

    @classmethod
    def min_value(cls, field_name: str, label: str, minimum: float) -> "ValidationRule":
        """Numeric field must be >= minimum."""
        def check(data):
            r = ValidationResult()
            v = data.get(field_name)
            if not _is_empty(v):
                try:
                    if float(v) < minimum:
                        r.add_field_error(field_name,
                            f"{label} must be at least {minimum}.")
                except (TypeError, ValueError):
                    r.add_field_error(field_name, f"{label} must be a number.")
            return r
        return cls(check)

    @classmethod
    def regex(cls, field_name: str, label: str, pattern: str,
              message: str = None) -> "ValidationRule":
        """Field value must match the regex pattern."""
        compiled = re.compile(pattern)
        def check(data):
            r = ValidationResult()
            v = data.get(field_name)
            if not _is_empty(v) and not compiled.match(str(v)):
                r.add_field_error(field_name,
                    message or f"{label} has an invalid format.")
            return r
        return cls(check)

    @classmethod
    def custom(cls, field_name: str,
               fn: Callable[[Any, dict], Tuple[bool, str]]) -> "ValidationRule":
        """
        Custom rule with access to full form data.

        Args:
            field_name (str): Field to report errors on
            fn: Callable(value, all_data) -> (is_valid: bool, error_message: str)

        Example:
            ValidationRule.custom("qty_ordered",
                lambda v, d: (float(v or 0) > 0, "Quantity must be greater than zero"))
        """
        def check(data):
            r = ValidationResult()
            value = data.get(field_name)
            is_valid, message = fn(value, data)
            if not is_valid:
                r.add_field_error(field_name, message)
            return r
        return cls(check)

    @classmethod
    def global_rule(cls, fn: Callable[[dict], Optional[str]]) -> "ValidationRule":
        """
        Form-level rule (not tied to a single field).
        fn(data) returns an error string if invalid, None if valid.

        Example:
            ValidationRule.global_rule(
                lambda d: "Grand total must be positive." if float(d.get("grand_total") or 0) <= 0 else None)
        """
        def check(data):
            r = ValidationResult()
            msg = fn(data)
            if msg:
                r.add_global_error(msg)
            return r
        return cls(check)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _is_empty(value: Any) -> bool:
    """True if value is None, empty string, empty list, or empty dict."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    return False
