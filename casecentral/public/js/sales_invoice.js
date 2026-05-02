frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
		if (cint(frm.doc.docstatus==0) && cur_frm.page.current_view_name!=="pos" && !frm.doc.is_return) {
            frm.add_custom_button(__('Legal Services'), function() {
                get_legal_services_to_invoice(frm);
            },__("Get Items From"));
			autofill_from_matter(frm);
        }
    },
	matter: function(frm) {
		autofill_from_matter(frm);
	}
});

var autofill_from_matter = function(frm) {
	if (!frm.doc.matter || frm.doc.docstatus !== 0) return;

	frappe.db.get_doc("Matter", frm.doc.matter).then((matter_data) => {
		if (matter_data.customer && !frm.doc.customer) {
			frm.set_value("customer", matter_data.customer);
		}

		if ((frm.doc.items || []).length) return;

		const service_rates = (matter_data.legal_service_rates || []).filter((row) => row.legal_service);
		if (service_rates.length) {
			add_legal_service_rate_items(frm, service_rates);
			return;
		}

		if (matter_data.service) {
			get_invoice_item_for_service(matter_data.service).then((service_item) => {
				add_invoice_item(frm, service_item);
			});
		}
	});
};

var add_legal_service_rate_items = function(frm, service_rates) {
	const item_promises = service_rates.map((rate_row) => {
		return get_invoice_item_for_service(rate_row.legal_service).then((service_item) => {
			if (!service_item) return null;
			return {
				item_code: service_item.item_code,
				rate: rate_row.rate || service_item.rate,
				description: rate_row.description || service_item.description
			};
		});
	});

	Promise.all(item_promises).then((items) => {
		const add_promises = items
			.filter(Boolean)
			.map((service_item) => add_invoice_item(frm, service_item, false));
		Promise.all(add_promises).then(() => frm.refresh_field("items"));
	});
};

var add_invoice_item = function(frm, service_item, refresh=true) {
	if (!service_item || !service_item.item_code) return Promise.resolve();

	const row = frm.add_child("items");
	row.qty = 1;
	return frappe.model.set_value(row.doctype, row.name, "item_code", service_item.item_code).then(() => {
		const set_values = [frappe.model.set_value(row.doctype, row.name, "qty", 1)];
		if (service_item.rate) {
			set_values.push(frappe.model.set_value(row.doctype, row.name, "rate", service_item.rate));
		}
		if (service_item.description) {
			set_values.push(
				frappe.model.set_value(row.doctype, row.name, "description", service_item.description)
			);
		}
		return Promise.all(set_values).then(() => {
			if (refresh) {
				frm.refresh_field("items");
			}
		});
	});
};

var get_invoice_item_for_service = function(service) {
	return frappe.db.get_value("Legal Service", service, ["item", "item_code", "rate", "description"]).then((legal_service) => {
		const service_data = legal_service.message || {};
		const item_code = service_data.item || service_data.item_code;
		if (item_code) {
			return {
				item_code: item_code,
				rate: service_data.rate,
				description: service_data.description
			};
		}

		return frappe.db.get_value("Item", service, "name").then((item_check) => {
			if (!item_check.message || !item_check.message.name) return null;
			return { item_code: item_check.message.name };
		});
	});
};

var get_legal_services_to_invoice = function(frm) {
	var me = this;
    let selected_matter = '';
	var dialog = new frappe.ui.Dialog({
		title: __("Get Items from Legal Services"),
		fields:[
			{
				fieldtype: 'Link',
				options: 'Matter',
				label: 'Matter',
				fieldname: "matter",
				reqd: true
			},
			{ fieldtype: 'Section Break'	},
			{ fieldtype: 'HTML', fieldname: 'results_area' }
		]
	});
	var $wrapper;
	var $results;
	var $placeholder;
	dialog.set_values({
		'matter': frm.doc.matter
	});
	dialog.fields_dict["matter"].df.onchange = () => {
		var matter = dialog.fields_dict.matter.input.value;
		if(matter && matter!=selected_matter){
			selected_matter = matter;
			var method = "casecentral.utils.get_legal_services_to_invoice";
			var args = {matter: matter, company: frm.doc.company};
			var columns = (["service", "reference_name", "reference_type"]);
			get_legal_service_items(frm, $results, $placeholder, method, args, columns);
		}
		else if(!matter){
			selected_matter = '';
			$results.empty();
			$results.append($placeholder);
		}
	}
	$wrapper = dialog.fields_dict.results_area.$wrapper.append(`<div class="results"
		style="border: 1px solid #d1d8dd; border-radius: 3px; height: 300px; overflow: auto;"></div>`);
	$results = $wrapper.find('.results');
	$placeholder = $(`<div class="multiselect-empty-state">
				<span class="text-center" style="margin-top: -40px;">
					<i class="fa fa-2x fa-heartbeat text-extra-muted"></i>
					<p class="text-extra-muted">No billable Legal Services found</p>
				</span>
			</div>`);
	$results.on('click', '.list-item--head :checkbox', (e) => {
		$results.find('.list-item-container .list-row-check')
			.prop("checked", ($(e.target).is(':checked')));
	});
	set_primary_action(frm, dialog, $results);
	dialog.show();
};

var get_legal_service_items = function(frm, $results, $placeholder, method, args, columns) {
	var me = this;
	$results.empty();
	frappe.call({
		method: method,
		args: args,
		callback: function(data) {
			if(data.message){
				$results.append(make_list_row(columns));
				for(let i=0; i<data.message.length; i++){
					$results.append(make_list_row(columns, data.message[i]));
				}
			}else {
				$results.append($placeholder);
			}
		}
	});
}

var make_list_row= function(columns, result={}) {
	var me = this;
	// Make a head row by default (if result not passed)
	let head = Object.keys(result).length === 0;
	let contents = ``;
	columns.forEach(function(column) {
		contents += `<div class="list-item__content ellipsis">
			${
				head ? `<span class="ellipsis">${__(frappe.model.unscrub(column))}</span>`

				:(column !== "name" ? `<span class="ellipsis">${__(result[column])}</span>`
					: `<a class="list-id ellipsis">
						${__(result[column])}</a>`)
			}
		</div>`;
	})

	let $row = $(`<div class="list-item">
		<div class="list-item__content" style="flex: 0 0 10px;">
			<input type="checkbox" class="list-row-check" ${result.checked ? 'checked' : ''}>
		</div>
		${contents}
	</div>`);

	$row = list_row_data_items(head, $row, result);
	return $row;
};

var set_primary_action= function(frm, dialog, $results) {
	var me = this;
	dialog.set_primary_action(__('Add'), function() {
		let checked_values = get_checked_values($results);
		if(checked_values.length > 0){
            if ( !frm.doc.matter ) {
                frm.set_value("matter", dialog.fields_dict.matter.input.value);
            }
			frm.set_value("items", []);
			add_to_item_line(frm, checked_values);
			dialog.hide();
		}
		else {
			frappe.msgprint(__("Please select Legal Service"));
		}
	});
};

var get_checked_values= function($results) {
	return $results.find('.list-item-container').map(function() {
		let checked_values = {};
		if ($(this).find('.list-row-check:checkbox:checked').length > 0 ) {
			checked_values['dn'] = $(this).attr('data-dn');
			checked_values['dt'] = $(this).attr('data-dt');
			checked_values['item'] = $(this).attr('data-item');
			if($(this).attr('data-rate') != 'undefined'){
				checked_values['rate'] = $(this).attr('data-rate');
			}
			else{
				checked_values['rate'] = false;
			}
			if($(this).attr('data-income-account') != 'undefined'){
				checked_values['income_account'] = $(this).attr('data-income-account');
			}
			else{
				checked_values['income_account'] = false;
			}
			if($(this).attr('data-qty') != 'undefined'){
				checked_values['qty'] = $(this).attr('data-qty');
			}
			else{
				checked_values['qty'] = false;
			}
			if($(this).attr('data-description') != 'undefined'){
				checked_values['description'] = $(this).attr('data-description');
			}
			else{
				checked_values['description'] = false;
			}
			return checked_values;
		}
	}).get();
};

var list_row_data_items = function(head, $row, result) {
    head ? $row.addClass('list-item--head')
        : $row = $(`<div class="list-item-container"
            data-dn= "${result.reference_name}" data-dt= "${result.reference_type}" data-item= "${result.service}"
            data-rate = ${result.rate}
            data-income-account = "${result.income_account}"
            data-qty = ${result.qty}
            data-description = "${result.description}">
            </div>`).append($row);
	return $row
};

var add_to_item_line = function(frm, checked_values){
    console.log(frm.doc);
    frappe.call({
        doc: frm.doc,
        method: "set_legal_services",
        args:{ checked_values: checked_values },
        callback: function() {
            frm.trigger("validate");
            frm.refresh_fields();
        }
    });
};