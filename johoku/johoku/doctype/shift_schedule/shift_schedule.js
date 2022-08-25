// Copyright (c) 2022, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Schedule', {
	get_template: function (frm) {
        window.location.href = repl(frappe.request.url +
            '?cmd=%(cmd)s&from_date=%(from_date)s&to_date=%(to_date)s&department=%(department)s', {
            cmd: "johoku.doctype.shift_schedule.shift_schedule.get_template",
            from_date: frm.doc.from_date,
            to_date: frm.doc.to_date,
            department:frm.doc.department,
        })
	}	
	// from_date(frm) {
	// 	if (frm.doc.from_date) {
	// 		if (frm.doc.from_date < frappe.datetime.now_date()) {
	// 			frappe.msgprint("From Date should not be a Past Date")
	// 			frm.set_value('from_date', '')
	// 		}
	// 		if (frm.doc.from_date > frappe.datetime.add_days(frappe.datetime.now_date(), 7)) {
	// 			frappe.msgprint("From Date should be within 7 days from Today")
	// 			frm.set_value('from_date', '')
	// 		}
	// 	}
	// },
	// to_date(frm) {
	// 	if (frm.doc.to_date) {
	// 		if (frm.doc.to_date < frappe.datetime.now_date()) {
	// 			frappe.msgprint("To Date should not be a Past Date")
	// 			frm.set_value('to_date', '')
	// 		}
	// 		else if (frm.doc.to_date < frm.doc.from_date) {
	// 			frappe.msgprint("To Date should not be greater than From Date")
	// 			frm.set_value('to_date', '')
	// 		}
	// 		else if (frm.doc.to_date > frappe.datetime.add_days(frm.doc.from_date, 7)) {
	// 			frappe.msgprint("To Date should be within 8 days from From Date")
	// 			frm.set_value('to_date', '')
	// 		}
	// 	}
	// },
// 	validate(frm) {
// 		frm.trigger('show_csv_data')
// 		frm.trigger('upload')
// 	},
// 	upload(frm) {
// 		frm.trigger('show_csv_data')
// 		if (frm.doc.upload) {
// 			frm.fields_dict.error_preview.$wrapper.empty()
// 			frm.call('validate_employees').then(r => {
// 				if (r.message) {
// 					frappe.msgprint(r.message)
// 					frm.disable_save()
// 					frm.set_value('upload','')
// 					frm.fields_dict.summary.$wrapper.empty()
// 					frm.fields_dict.error_preview.$wrapper.empty()
// 					frm.fields_dict.csv_preview.$wrapper.empty()

// 				}
// 			})
// 		}
// 	},
// 	show_csv_data(frm) {
// 		if (frm.doc.upload) {
// 			frm.fields_dict.csv_preview.$wrapper.empty()
// 			frm.call('show_csv_data').then(r => {
// 				if (r.message) {
// 					frm.fields_dict.csv_preview.$wrapper.empty().append("<h2>Upload Preview</h2><table class='table table-bordered'>" + r.message + "</table>")
// 				}
// 			})
// 		}
// 	},
// 	after_save(frm){
// 		frappe.call({
// 			"method": "johoku.johoku.doctype.shift_schedule.shift_schedule.enqueue_shift_assignment",
// 			"args":{
// 				"file" : frm.doc.upload,
// 				"from_date" : frm.doc.from_date,
// 				"to_date" : frm.doc.to_date,
// 				"name" : frm.doc.name
// 			},
// 			freeze: true,
// 			freeze_message: 'Submitting Shift Schedule....',
// 		})
// 	},
});
