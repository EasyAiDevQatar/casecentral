"""Restore the Case Central workspace from the standard workspace JSON."""

from __future__ import annotations

import json
from pathlib import Path

import frappe


def execute():
	workspace_path = (
		Path(frappe.get_app_path("casecentral"))
		/ "case_central"
		/ "workspace"
		/ "case_central"
		/ "case_central.json"
	)
	workspace_data = json.loads(workspace_path.read_text())

	if frappe.db.exists("Workspace", "Case Central"):
		frappe.delete_doc("Workspace", "Case Central", force=True, ignore_permissions=True)
		frappe.db.commit()

	workspace = frappe.get_doc(workspace_data)
	workspace.flags.ignore_links = True
	workspace.flags.ignore_validate_update_after_submit = True
	workspace.flags.ignore_version = True
	workspace.flags.ignore_mandatory = True
	workspace.name = "Case Central"
	workspace.label = "Case Central"
	workspace.module = "Case Central"
	workspace.public = 1
	workspace.is_hidden = 0
	workspace.for_user = ""
	workspace.parent_page = ""

	workspace.insert(ignore_permissions=True)
