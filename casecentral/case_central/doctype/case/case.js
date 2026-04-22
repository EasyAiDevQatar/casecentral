// Copyright (c) 2023, 4C Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Case', {
	refresh: function(frm) {
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
			if (grid) {
				grid.update_docfield_property('next_date', 'hidden', 1);
			}
		}
		hide_case_history_next_date();
		setTimeout(hide_case_history_next_date, 200);
	},
	after_save: function(frm) {
		if(frm.doc.status == "Pending" && frm.doc.registration_number) {
			frm.doc.status = "InProgress";
		}
		if(frm.doc.status=="Pending" || frm.doc.status=="InProgress") {
			frm.doc.documents_handover = 0;
		}
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
	},
	case_year: function(frm){
		set_registration_number(frm);
	}
});

var set_registration_number = function(frm) {
	if (frm.doc.case_type_abbr && frm.doc.case_no && frm.doc.case_year) {
		frm.set_value("registration_number", frm.doc.case_type_abbr + "_" + frm.doc.case_no + "_" + frm.doc.case_year);
	} else {
		frm.set_value("registration_number", "");
	}
}