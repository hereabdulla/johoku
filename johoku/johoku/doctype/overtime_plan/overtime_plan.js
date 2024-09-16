// Copyright (c) 2022, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Overtime Plan', {
	refresh: function (frm) {
		frm.fields_dict.error_preview.$wrapper.empty()
		frm.fields_dict.csv_preview.$wrapper.empty()
		frm.trigger('show_csv_data')
	},
	get_template: function (frm) {
		if (frm.doc.ot_to_date) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&ot_from_date=%(ot_from_date)s&ot_to_date=%(ot_to_date)s&department=%(department)s', {
				cmd: "johoku.johoku.doctype.overtime_plan.overtime_plan.get_template",
				ot_from_date: frm.doc.ot_from_date,
				ot_to_date: frm.doc.ot_to_date,
				department: frm.doc.department,
			})
		}
		else {
			frappe.throw("Please enter OT To Date")
		}
	},
	ot_from_date(frm) {
		if (frm.doc.ot_from_date) {
			if (frm.doc.ot_from_date < frappe.datetime.now_date()) {
				frappe.msgprint(" OT From Date should not be a Past Date")
				frm.set_value('ot_from_date', '')
			}
			// if (frm.doc.ot_from_date > frappe.datetime.add_days(frappe.datetime.now_date(), 7)) {
			// 	frappe.msgprint("OT From Date should be within 7 days from Today")
			// 	frm.set_value('ot_from_date', '')
			// }
		}
	},
	ot_to_date(frm) {
		if (frm.doc.ot_to_date) {
			if (frm.doc.ot_to_date < frappe.datetime.now_date()) {
				frappe.msgprint(" OT To Date should not be a Past Date")
				frm.set_value('ot_to_date', '')
			}
			else if (frm.doc.ot_to_date < frm.doc.ot_from_date) {
				frappe.msgprint("OT To Date should not be greater than OT From Date")
				frm.set_value('ot_to_date', '')
			}
			else if (frm.doc.department && frm.doc.ot_from_date && frm.doc.ot_to_date)
				frm.call('check').then(r => {
					frappe.msgprint(r.message)
				})
		frappe.call({
			'method': 'johoku.johoku.doctype.overtime_plan.overtime_plan.check_shift',
			'args': {
				dept: frm.doc.department,
				from_date: frm.doc.ot_from_date,
				to_date: frm.doc.ot_to_date
			},
			callback(r){
				if (r.message[0] == 'No Shift Assigned'){
					frm.disable_save()
					frappe.throw(__("Shift Schedule not submitted for the selected date"))
				}
			}
		})
			// else if (frm.doc.ot_to_date > frappe.datetime.add_days(frm.doc.from_date, 7)) {
			// 	frappe.msgprint(" OT To Date should be within 8 days from From Date")
			// 	frm.set_value('ot_to_date', '')
			// }
		}
	},
	upload(frm) {
		frm.trigger('show_csv_data')
		if (frm.doc.upload) {
			frm.call('validate_employees').then(r => {
				if (r.message) {
					frm.fields_dict.error_preview.$wrapper.empty().append("<h2>Error Preview</h2><ul>" + r.message + "</ul>")
					frm.disable_save()
					frm.set_value('upload', '')
					frm.fields_dict.error_preview.$wrapper.empty()
					frm.fields_dict.csv_preview.$wrapper.empty()
				}
			})
		}
	},
	validate(frm) {
		frm.trigger('show_csv_data')
		frm.trigger('upload')
	},
	show_csv_data(frm) {
		if (frm.doc.upload) {
			frm.call('show_csv_data').then(r => {
				if (r.message) {
					frm.fields_dict.csv_preview.$wrapper.empty().append("<h2>Upload Preview</h2><table class='table table-bordered'>" + r.message + "</table>")
				}
			})
		}
	},	
});