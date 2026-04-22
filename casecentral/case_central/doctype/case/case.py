# Copyright (c) 2023, 4C Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

# Fields aligned with Case Sessions; next_date is intentionally excluded from mirror.
_SESSION_TO_HISTORY_FIELDS = (
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
	"facts_summary",
	"defense_summary",
	"attachments_note",
	"agent",
)


class Case(Document):
	def validate(self):
		self.sync_case_history_from_sessions()

	def sync_case_history_from_sessions(self):
		"""Mirror Case Sessions into Case History (same fields as sessions; excludes next session date)."""
		self.set("case_history", [])
		for row in self.get("case_sessions") or []:
			entry = {fieldname: row.get(fieldname) for fieldname in _SESSION_TO_HISTORY_FIELDS}
			self.append("case_history", entry)

	def on_update(self):
		next_hearing = frappe.db.sql(
			"""
			select next_date from `tabCase Sessions`
			where parent=%s and parenttype=%s and parentfield='case_sessions'
				and next_date is not null
			order by business_on_date desc
			limit 1
			""",
			(self.name, self.doctype),
		)
		next_val = next_hearing[0][0] if next_hearing else None
		frappe.db.set_value(self.doctype, self.name, "next_hearing_date", next_val)
		self.reload()

@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.

	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions

	conditions = get_event_conditions("Case", filters)

	data = frappe.db.sql(
		"""
		select
			name, concat(name, CHAR(13), registration_number) as title, status, next_hearing_date
		from
			`tabCase`
		where status="InProgress"
			and (next_hearing_date between %(start)s and %(end)s)
			{conditions}
		""".format(
			conditions=conditions
		),
		{"start": start, "end": end},
		as_dict=True
	)
	return data
