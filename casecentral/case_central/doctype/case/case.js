// Copyright (c) 2023, 4C Solutions and contributors
// For license information, please see license.txt

const SESSION_CHILD_DOCTYPES = ["Case Sessions", "Case History"];

function sanitize_case_grid_user_settings(frm) {
	if (!frm || frm.doc.doctype !== "Case") {
		return;
	}

	const settings = frappe.model.user_settings[frm.doctype];
	const grid_view = settings && settings.GridView;
	if (!grid_view) {
		return;
	}

	let updated = false;
	SESSION_CHILD_DOCTYPES.forEach((child_doctype) => {
		if (!grid_view[child_doctype]) {
			return;
		}

		const rows = grid_view[child_doctype].filter(
			(row) => row && row.fieldname && frappe.meta.get_docfield(child_doctype, row.fieldname)
		);

		if (rows.length !== grid_view[child_doctype].length) {
			grid_view[child_doctype] = rows;
			updated = true;
		}
	});

	if (updated) {
		frappe.model.user_settings.save(frm.doctype, "GridView", grid_view);
	}
}

frappe.ui.form.on('Case', {
	onload: function(frm) {
		if (frappe.session.user === "Guest") {
			return;
		}

		frappe.model.user_settings.get(frm.doctype).then((settings) => {
			frappe.model.user_settings[frm.doctype] = settings || {};
			sanitize_case_grid_user_settings(frm);
		});
	},
	matter: function(frm) {
		apply_session_defaults(frm);
	},
	customer: function(frm) {
		apply_session_defaults(frm);
	},
	custom_tokeel_no: function(frm) {
		apply_session_defaults(frm);
	},
	custom_tokeel_image: function(frm) {
		apply_session_defaults(frm);
	},
	refresh: function(frm) {
		sanitize_case_grid_user_settings(frm);

		frm.set_query('nature_of_case', () => {
			if (frm.doc.service) {
				return {
					filters: {
						'service': frm.doc.service
					}
				};
			}
		});

		// Case History mirrors sessions without next session date; hide it in this grid only.
		function hide_case_history_next_date() {
			const grid = frm.fields_dict.case_history && frm.fields_dict.case_history.grid;
			if (grid && grid.meta) {
				grid.update_docfield_property('next_date', 'hidden', 1);
			}
		}
		hide_case_history_next_date();
		setTimeout(hide_case_history_next_date, 200);
		apply_session_defaults(frm);
	},
	after_save: function(frm) {
		if(frm.doc.status == "Pending" && frm.doc.registration_number) {
			frm.doc.status = "InProgress";
		}
		if(frm.doc.status=="Pending" || frm.doc.status=="InProgress") {
			frm.doc.documents_handover = 0;
		}
	},
	customer_name: function(frm) {
		apply_session_defaults(frm);
	},
	representing: function(frm) {
		apply_session_defaults(frm);
	},
	petitioner: function(frm){
		if (frm.doc.petitioner && frm.doc.respondent) {
			frm.set_value("case_title", frm.doc.petitioner + " V/s " + frm.doc.respondent);
		}
	},
	respondent: function(frm){
		if (frm.doc.petitioner && frm.doc.respondent) {
			frm.set_value("case_title", frm.doc.petitioner + " V/s " + frm.doc.respondent);
		}
	},
	ecase_type: function(frm){
		var ct_str = frm.doc.ecase_type.split("-")[0].trim().replace(/\./g, "");
		frm.set_value("case_type_abbr", ct_str);
		set_registration_number(frm);
	},
	case_no: function(frm){
		set_registration_number(frm);
		apply_session_defaults(frm);
	},
	case_year: function(frm){
		set_registration_number(frm);
	},
	case_sessions_add: function(frm, cdt, cdn) {
		apply_defaults_to_session_row(frm, locals[cdt][cdn]);
		frm.refresh_field('case_sessions');
	},
	case_history_add: function(frm, cdt, cdn) {
		apply_defaults_to_session_row(frm, locals[cdt][cdn]);
		frm.refresh_field('case_history');
	}
});

var set_registration_number = function(frm) {
	if (frm.doc.case_type_abbr && frm.doc.case_no && frm.doc.case_year) {
		frm.set_value("registration_number", frm.doc.case_type_abbr + "_" + frm.doc.case_no + "_" + frm.doc.case_year);
	} else {
		frm.set_value("registration_number", "");
	}
}

var apply_session_defaults = function(frm) {
	['case_sessions', 'case_history'].forEach(function(table_field) {
		const field = frm.fields_dict[table_field];
		if (!field || !field.df || !field.grid) {
			return;
		}

		(frm.doc[table_field] || []).forEach(function(row) {
			apply_defaults_to_session_row(frm, row);
		});
		field.refresh();
	});
}

var apply_defaults_to_session_row = function(frm, row) {
	if (!row) return;

	if (frm.doc.customer_name) {
		row.client = frm.doc.customer_name;
	}
	if (frm.doc.representing) {
		row.client_capacity = frm.doc.representing;
	}
	if (frm.doc.case_no) {
		row.case_number = frm.doc.case_no;
	}
	if (frm.doc.custom_tokeel_no !== undefined) {
		row.tokeel_no = frm.doc.custom_tokeel_no || '';
	}
	if (frm.doc.custom_tokeel_image !== undefined) {
		row.tokeel_image = frm.doc.custom_tokeel_image || '';
	}
}