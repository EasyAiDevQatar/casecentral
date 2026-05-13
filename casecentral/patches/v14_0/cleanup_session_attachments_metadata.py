"""Remove obsolete nested session_attachments metadata after additional_attachments rollout."""

from __future__ import annotations

import frappe


def execute():
	for parent in ("Case Sessions", "Case History"):
		frappe.db.delete("DocField", {"parent": parent, "fieldname": "session_attachments"})
		frappe.db.delete("Custom Field", {"dt": parent, "fieldname": "session_attachments"})

	for name in frappe.get_all(
		"Custom Field",
		pluck="name",
		filters={"fieldname": "session_attachments"},
	):
		frappe.delete_doc("Custom Field", name, force=True, ignore_permissions=True)

	for name in frappe.get_all(
		"Property Setter",
		pluck="name",
		filters={"field_name": "session_attachments"},
	):
		frappe.delete_doc("Property Setter", name, force=True, ignore_permissions=True)

	if frappe.db.exists("DocType", "Case Session Attachment"):
		frappe.delete_doc("DocType", "Case Session Attachment", force=True, ignore_permissions=True)

	for doctype in ("Case", "Case Sessions", "Case History"):
		frappe.clear_cache(doctype=doctype)

	frappe.db.commit()
