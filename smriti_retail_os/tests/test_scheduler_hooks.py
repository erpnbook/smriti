# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_scheduler_hooks.py
# @description: Regression gate that verifies every doc_events and
#   scheduler_events hook string in hooks.py resolves to a real, callable
#   attribute via Frappe's OWN resolution function (frappe.utils.get_attr),
#   so this test fails exactly when a live scheduler tick or `bench migrate`
#   would fail — no guessing at Frappe's internals required.
#
#   Root cause this guards against (KI-003): a hook string of the form
#   "module.path.ClassName.method_name" makes frappe.utils.get_attr treat
#   everything before the LAST dot as the module path — i.e.
#   "module.path.ClassName" — and try to import it as a module. Since
#   ClassName is a class, not a submodule, this fails at every
#   `bench migrate` / scheduler tick with:
#     "... is not a valid method: No module named '...ClassName';
#      '...module.path' is not a package"
#
#   Hook STRINGS are extracted via `ast` (no execution of hooks.py's other
#   top-level side effects required), but resolving each string still
#   requires a real Frappe + app environment, since these hooks import
#   frappe/erpnext transitively. Run via `bench run-tests`, matching the
#   rest of the suite (see README.md section 6, Testing).
#
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.1.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import ast
import os
import unittest

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS_PATH = os.path.join(APP_ROOT, "hooks.py")

# Hook dict names to check. Add new hook-bearing dicts here as the app grows
# (e.g. "override_whitelisted_methods") if they should also be gated.
HOOK_DICT_NAMES = {"doc_events", "scheduler_events"}

try:
	import frappe
	from frappe.utils import get_attr as frappe_get_attr
	FRAPPE_AVAILABLE = True
except ImportError:
	FRAPPE_AVAILABLE = False


def _literal_strings(node):
	"""
	Recursively pull every string literal out of an AST node (dict, list,
	nested dict-of-lists, etc.) without executing any code.
	"""
	found = []
	if isinstance(node, ast.Constant) and isinstance(node.value, str):
		found.append(node.value)
	elif isinstance(node, ast.Dict):
		for value in node.values:
			found.extend(_literal_strings(value))
	elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
		for elt in node.elts:
			found.extend(_literal_strings(elt))
	return found


def _extract_hook_strings(source, dict_names):
	"""Parse `source` and return all string literals assigned to any of
	the top-level variable names in `dict_names`."""
	tree = ast.parse(source, filename=HOOKS_PATH)
	strings = []
	for node in ast.walk(tree):
		if isinstance(node, ast.Assign):
			targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
			if any(name in dict_names for name in targets):
				strings.extend(_literal_strings(node.value))
	return strings


def _looks_like_dotted_python_path(value):
	"""
	doc_events/scheduler_events values are always dotted Python paths to a
	callable (e.g. "app.module.func"). Filter out anything that clearly
	isn't one (cron key strings like "*/30 * * * *", etc.) so we only
	validate real hook targets.
	"""
	if not isinstance(value, str) or "." not in value:
		return False
	if any(ch in value for ch in ("*", "/", " ")):
		return False
	return all(part.isidentifier() for part in value.split("."))


@unittest.skipUnless(
	FRAPPE_AVAILABLE,
	"Requires a live Frappe environment (run via `bench run-tests`). "
	"Hook targets import frappe/erpnext transitively, so this cannot be "
	"meaningfully checked outside a bench.",
)
class TestSchedulerAndDocEventHooksResolve(unittest.TestCase):
	"""
	Verifies every doc_events / scheduler_events hook string in hooks.py
	resolves to a real callable via Frappe's actual frappe.utils.get_attr —
	the same function Frappe itself uses at scheduler-tick and migrate time.
	This is a static, pre-runtime check: it does not execute the hooks, only
	confirms they CAN be resolved and called.
	"""

	@classmethod
	def setUpClass(cls):
		with open(HOOKS_PATH, "r", encoding="utf-8") as f:
			source = f.read()
		all_strings = _extract_hook_strings(source, HOOK_DICT_NAMES)
		cls.hook_paths = sorted(
			set(s for s in all_strings if _looks_like_dotted_python_path(s))
		)
		assert cls.hook_paths, (
			"No hook paths were extracted from hooks.py — the AST parser "
			"likely needs updating for a new hooks.py structure. Do not "
			"let this test silently pass with zero coverage."
		)

	def test_every_hook_path_resolves_to_a_callable(self):
		"""
		The actual regression gate. This would have failed on:
        "smriti_retail_os.negative_stock.service.recovery_service.
         SMRITINegativeStockRecoveryService.run_scheduler_safety_net"
		prior to the KI-003 fix, with the exact same error Frappe raises
		in production.
		"""
		failures = []
		for path in self.hook_paths:
			try:
				method = frappe_get_attr(path)
			except Exception as e:  # noqa: BLE001 - report ALL resolution failures
				failures.append(f"{path}\n    -> {type(e).__name__}: {e}")
				continue
			if not callable(method):
				failures.append(f"{path}\n    -> resolved but not callable ({type(method).__name__})")

		self.assertEqual(
			failures, [],
			"One or more scheduler/doc_event hooks in hooks.py do not "
			"resolve via frappe.utils.get_attr (this WILL fail at "
			"`bench migrate` / scheduler tick time):\n\n"
			+ "\n\n".join(failures),
		)
