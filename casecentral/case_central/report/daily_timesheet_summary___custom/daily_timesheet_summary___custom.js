// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Timesheet Summary - Custom"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("من تاريخ"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "to_date",
			label: __("إلى تاريخ"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "matter",
			label: __("الماتر"),
			fieldtype: "Link",
			options: "Matter",
		},
		{
			fieldname: "employee",
			label: __("الموظف"),
			fieldtype: "Link",
			options: "Employee",
		},
	],
};
