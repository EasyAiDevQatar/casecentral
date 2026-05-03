"""Disable Case Central shortcut counts that can trigger restricted reportview queries."""

from __future__ import annotations

import frappe


OBSOLETE_DOCTYPES = {"Caveat", "Document Outward"}


def execute():
	if not frappe.db.exists("Workspace", "Case Central"):
		return

	workspace = frappe.get_doc("Workspace", "Case Central")
	workspace.set(
		"links",
		[
			link
			for link in workspace.get("links", [])
			if link.get("link_to") not in OBSOLETE_DOCTYPES
			and link.get("label") not in OBSOLETE_DOCTYPES
		],
	)
	workspace.set(
		"shortcuts",
		[
			shortcut
			for shortcut in workspace.get("shortcuts", [])
			if shortcut.get("link_to") not in OBSOLETE_DOCTYPES
			and shortcut.get("label") not in OBSOLETE_DOCTYPES
		],
	)
	for shortcut in workspace.get("shortcuts", []):
		if shortcut.get("label") in {"Matter", "Customer", "Case"}:
			shortcut.stats_filter = ""

	workspace.save(ignore_permissions=True)
