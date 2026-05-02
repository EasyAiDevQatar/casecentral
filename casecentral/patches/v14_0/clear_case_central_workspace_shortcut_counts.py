"""Disable Case Central shortcut counts that can trigger restricted reportview queries."""

from __future__ import annotations

import frappe


def execute():
	if not frappe.db.exists("Workspace", "Case Central"):
		return

	workspace = frappe.get_doc("Workspace", "Case Central")
	for shortcut in workspace.get("shortcuts", []):
		if shortcut.get("label") in {"Matter", "Customer", "Case"}:
			shortcut.stats_filter = ""

	workspace.save(ignore_permissions=True)
