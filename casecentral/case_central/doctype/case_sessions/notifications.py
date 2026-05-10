# Copyright (c) 2026, Case Central and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, getdate, today


def notify_upcoming_sessions():
	"""Create desk Notification Log for assignees when a Case session's next_date is tomorrow."""
	target = getdate(add_days(today(), 1))
	run_day = today()

	rows = frappe.db.sql(
		"""
		select distinct cs.parent as case_name
		from `tabCase Sessions` cs
		where cs.parenttype = 'Case'
			and cs.parentfield = 'case_sessions'
			and cs.next_date = %(target)s
		""",
		{"target": target},
		as_dict=True,
	)

	cache = frappe.cache()

	for row in rows:
		case_name = row.case_name
		if not case_name:
			continue

		assignees = frappe.get_all(
			"ToDo",
			pluck="allocated_to",
			filters={
				"reference_type": "Case",
				"reference_name": case_name,
				"status": ("!=", "Cancelled"),
				"allocated_to": ("is", "set"),
			},
			distinct=True,
		)

		for user in assignees:
			if not user or user == "Guest":
				continue

			cache_key = f"case_hearing_notif:{case_name}:{user}:{run_day}"
			if cache.get_value(cache_key):
				continue

			subject = frappe._("Hearing tomorrow — Case {0}").format(case_name)

			notification = frappe.get_doc(
				{
					"doctype": "Notification Log",
					"for_user": user,
					"type": "Alert",
					"document_type": "Case",
					"document_name": case_name,
					"subject": subject,
					"email_content": subject,
				}
			)
			notification.insert(ignore_permissions=True)
			cache.set_value(cache_key, 1, expires_in_sec=86400)

			frappe.publish_realtime(
				event="notification",
				message={"count": frappe.db.count("Notification Log", {"read": 0, "for_user": user})},
				user=user,
			)

	frappe.db.commit()
