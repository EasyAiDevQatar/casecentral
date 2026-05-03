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
		workspace = frappe.get_doc("Workspace", "Case Central")
		workspace.update(workspace_data)
	else:
		workspace = frappe.get_doc(workspace_data)

	workspace.name = "Case Central"
	workspace.label = "Case Central"
	workspace.module = "Case Central"
	workspace.public = 1
	workspace.is_hidden = 0
	workspace.for_user = ""
	workspace.parent_page = ""
	workspace.save(ignore_permissions=True)
