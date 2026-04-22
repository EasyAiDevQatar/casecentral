"""Move rows mirrored in tabCase Sessions (parentfield=case_history) into tabCase History.

Used when Case History child used the Case Sessions DocType via property setter; after consolidation
each mirror row belongs in tabCase History only.
"""

from __future__ import annotations

import frappe

_META_AND_DATA_COLS = [
	"name",
	"creation",
	"modified",
	"owner",
	"modified_by",
	"docstatus",
	"idx",
	"parent",
	"parentfield",
	"parenttype",
	"registration_no",
	"business_on_date",
	"court",
	"litigation_degree",
	"case_number",
	"chamber",
	"case_subject",
	"client",
	"client_capacity",
	"opponent",
	"opponent_capacity",
	"previous_decision",
	"decision",
	"next_date",
	"facts_summary",
	"defense_summary",
	"attachments_note",
	"agent",
]


def execute():
	if not frappe.db.has_table("tabCase Sessions") or not frappe.db.has_table("tabCase History"):
		return

	n_mirrored = frappe.db.sql(
		"""
		SELECT COUNT(*) FROM `tabCase Sessions`
		WHERE parentfield = 'case_history'
		"""
	)[0][0]
	if n_mirrored:
		h_cols = set(frappe.db.get_table_columns("tabCase History"))
		s_cols = set(frappe.db.get_table_columns("tabCase Sessions"))
		cols = [c for c in _META_AND_DATA_COLS if c in h_cols and c in s_cols]
		if cols:
			quoted = ", ".join(f"`{c}`" for c in cols)
			frappe.db.sql(
				f"""
				INSERT INTO `tabCase History` ({quoted})
				SELECT {quoted}
				FROM `tabCase Sessions`
				WHERE parentfield = 'case_history'
				"""
			)
			frappe.db.sql(
				"""
				DELETE FROM `tabCase Sessions`
				WHERE parentfield = 'case_history'
				"""
			)
