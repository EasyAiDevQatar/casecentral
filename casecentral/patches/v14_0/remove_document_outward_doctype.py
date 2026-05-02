"""Remove the obsolete Document Outward doctype from installed sites."""

from __future__ import annotations

import frappe


def execute():
	if frappe.db.exists("DocType", "Document Outward"):
		frappe.delete_doc("DocType", "Document Outward", force=True, ignore_permissions=True)
