# Copyright (c) 2023, 4C Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

# Fields aligned with Case Sessions; next_date is intentionally excluded from mirror.
_SESSION_TO_HISTORY_FIELDS = (
	"registration_no",
	"business_on_date",
	"court",
	"litigation_degree",
	"case_number",
	"chamber",
	"case_subject",
	"case_location",
	"client",
	"client_capacity",
	"opponent",
	"opponent_capacity",
	"previous_decision",
	"decision",
	"attendance_location",
	"defense_summary",
	"attachments",
	"tokeel_no",
	"tokeel_image",
	"agent",
)


class Case(Document):
	def validate(self):
		self.populate_session_defaults()
		self.sync_case_history_from_sessions()

	def populate_session_defaults(self):
		"""Keep session rows aligned with case-level client and case details."""
		client_name = self.get("customer_name")
		client_capacity = self.get("representing")
		case_number = self.get("case_no")
		tokeel_no = self.get("custom_tokeel_no")
		tokeel_image = self.get("custom_tokeel_image")

		for table_field in ("case_sessions", "case_history"):
			for row in self.get(table_field) or []:
				if client_name:
					row.client = client_name
				if client_capacity:
					row.client_capacity = client_capacity
				if case_number:
					row.case_number = case_number
				row.tokeel_no = tokeel_no or ""
				row.tokeel_image = tokeel_image or ""

	def sync_case_history_from_sessions(self):
		"""Move due Case Sessions (next_date == today) into Case History."""
		current_date = getdate(today())
		for row in list(self.get("case_sessions") or []):
			if not row.get("next_date") or getdate(row.get("next_date")) != current_date:
				continue
			entry = {fieldname: row.get(fieldname) for fieldname in _SESSION_TO_HISTORY_FIELDS}
			self.append("case_history", entry)
			self.remove(row)

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
