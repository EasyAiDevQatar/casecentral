"""Remove obsolete Case Central workspace cards and their links."""

from __future__ import annotations

import json

import frappe


OBSOLETE_LABELS = {
	"Quality Management",
	"Quality Goal",
	"Quality Review",
	"Books and Journals",
	"Book",
	"Book Type",
	"Lend Book",
	"Setup",
	"Branch",
	"Matter Template",
	"Case Central Settings",
}


def execute():
	if not frappe.db.exists("Workspace", "Case Central"):
		return

	workspace = frappe.get_doc("Workspace", "Case Central")

	workspace.set(
		"links",
		[
			link
			for link in workspace.get("links", [])
			if link.get("label") not in OBSOLETE_LABELS
			and link.get("link_to") not in OBSOLETE_LABELS
		],
	)

	if workspace.content:
		content = json.loads(workspace.content)
		workspace.content = json.dumps(
			[
				block
				for block in content
				if block.get("data", {}).get("card_name") not in OBSOLETE_LABELS
				and block.get("data", {}).get("shortcut_name") not in OBSOLETE_LABELS
			],
			separators=(",", ":"),
		)

	workspace.save(ignore_permissions=True)
