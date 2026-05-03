"""Remove obsolete Caveat and Document Outward doctypes from installed sites."""

from __future__ import annotations

import json

import frappe


OBSOLETE_DOCTYPES = {"Caveat", "Document Outward"}


def execute():
	remove_obsolete_doctypes_from_workspaces()
	for doctype in OBSOLETE_DOCTYPES:
		if frappe.db.exists("DocType", doctype):
			frappe.delete_doc("DocType", doctype, force=True, ignore_permissions=True)


def remove_obsolete_doctypes_from_workspaces():
	for workspace_name in frappe.get_all("Workspace", pluck="name"):
		workspace = frappe.get_doc("Workspace", workspace_name)
		changed = False

		links = [
			link
			for link in workspace.get("links", [])
			if link.get("link_to") not in OBSOLETE_DOCTYPES
			and link.get("label") not in OBSOLETE_DOCTYPES
		]
		if len(links) != len(workspace.get("links", [])):
			workspace.set("links", links)
			changed = True

		shortcuts = [
			shortcut
			for shortcut in workspace.get("shortcuts", [])
			if shortcut.get("link_to") not in OBSOLETE_DOCTYPES
			and shortcut.get("label") not in OBSOLETE_DOCTYPES
		]
		if len(shortcuts) != len(workspace.get("shortcuts", [])):
			workspace.set("shortcuts", shortcuts)
			changed = True

		if workspace.content:
			content = json.loads(workspace.content)
			filtered_content = [
				block
				for block in content
				if block.get("data", {}).get("shortcut_name") not in OBSOLETE_DOCTYPES
				and block.get("data", {}).get("card_name") not in OBSOLETE_DOCTYPES
			]
			if len(filtered_content) != len(content):
				workspace.content = json.dumps(filtered_content, separators=(",", ":"))
				changed = True

		if changed:
			workspace.save(ignore_permissions=True)
