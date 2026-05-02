"""Remove the obsolete Document Outward doctype from installed sites."""

from __future__ import annotations

import json

import frappe


def execute():
	remove_document_outward_from_workspaces()
	if frappe.db.exists("DocType", "Document Outward"):
		frappe.delete_doc("DocType", "Document Outward", force=True, ignore_permissions=True)


def remove_document_outward_from_workspaces():
	for workspace_name in frappe.get_all("Workspace", pluck="name"):
		workspace = frappe.get_doc("Workspace", workspace_name)
		changed = False

		links = [
			link
			for link in workspace.get("links", [])
			if link.get("link_to") != "Document Outward" and link.get("label") != "Document Outward"
		]
		if len(links) != len(workspace.get("links", [])):
			workspace.set("links", links)
			changed = True

		shortcuts = [
			shortcut
			for shortcut in workspace.get("shortcuts", [])
			if shortcut.get("link_to") != "Document Outward" and shortcut.get("label") != "Document Outward"
		]
		if len(shortcuts) != len(workspace.get("shortcuts", [])):
			workspace.set("shortcuts", shortcuts)
			changed = True

		if workspace.content:
			content = json.loads(workspace.content)
			filtered_content = [
				block
				for block in content
				if block.get("data", {}).get("shortcut_name") != "Document Outward"
				and block.get("data", {}).get("card_name") != "Document Outward"
			]
			if len(filtered_content) != len(content):
				workspace.content = json.dumps(filtered_content, separators=(",", ":"))
				changed = True

		if changed:
			workspace.save(ignore_permissions=True)
