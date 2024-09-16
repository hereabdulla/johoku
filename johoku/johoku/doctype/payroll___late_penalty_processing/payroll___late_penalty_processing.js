// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll - Late Penalty Processing', {
	refresh(frm){
		frm.set_value('end_date',frappe.datetime.add_days(frappe.datetime.month_start(), 19))

		var d = frappe.datetime.add_months(frappe.datetime.month_start(), -1)
		frm.set_value('start_date',frappe.datetime.add_days(d, 20))
		frm.disable_save()
	},
	process_late(frm){
		frappe.call({
			"method": "johoku.johoku.doctype.payroll___late_penalty_processing.payroll___late_penalty_processing.attendance_calc",
			"args":{
				"from_date" : frm.doc.start_date,
				"to_date" : frm.doc.end_date,
			},
			freeze: true,
			freeze_message: 'Processing late....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Late Penalty Created Successfully")
				}
			}
		})
	},
	create_late_penalty(frm){
		frappe.call({
			"method": "johoku.johoku.doctype.payroll___late_penalty_processing.payroll___late_penalty_processing.additional_salary",
			"args":{
				"from_date" : frm.doc.start_date,
				"to_date" : frm.doc.end_date,
			},
			freeze: true,
			freeze_message: 'Processing additional salary....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Late Penalty - Additional Created Successfully")
				}
			}
		})
	}
});
