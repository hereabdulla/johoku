// Copyright (c) 2022, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Overtime Schedule', {
	get_template: function (frm) {
        window.location.href = repl(frappe.request.url +
            '?cmd=%(cmd)s&ot_from_date=%(ot_from_date)s&ot_to_date=%(ot_to_date)s&department=%(department)s', {
            cmd: "johoku.johoku.doctype.overtime_schedule.overtime_schedule.get_template",
            ot_from_date: frm.doc.ot_from_date,
            ot_to_date: frm.doc.ot_to_date,
            department:frm.doc.department,
        })
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
			// else if (frm.doc.ot_to_date > frappe.datetime.add_days(frm.doc.from_date, 7)) {
			// 	frappe.msgprint(" OT To Date should be within 8 days from From Date")
			// 	frm.set_value('ot_to_date', '')
			// }
		}
	},
});
