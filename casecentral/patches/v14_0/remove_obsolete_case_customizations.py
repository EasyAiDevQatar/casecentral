"""Remove lawfirm custom fields / property setter that duplicated native Case layout."""

from __future__ import annotations

import frappe


def execute():
	for name in ("Case-case_sessions", "Case-case_sessions_section"):
		if frappe.db.exists("Custom Field", name):
			frappe.delete_doc("Custom Field", name, force=True, ignore_permissions=True)
	if frappe.db.exists("Property Setter", "Case-case_history-options"):
		frappe.delete_doc("Property Setter", "Case-case_history-options", force=True, ignore_permissions=True)
