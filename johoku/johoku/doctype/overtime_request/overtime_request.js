// Copyright (c) 2022, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Overtime Request', {
	// refresh: function (frm) {
	// 	if (frm.doc.__islocal) {
	// 		frappe.call({
	// 			method: 'johoku.johoku.doctype.overtime_request.overtime_request.get_employee_code',
	// 			args: {
	// 				user: frappe.session.user
	// 			},
	// 			callback(r) {
	// 				if (r.message) {
	// 					frm.set_value('employee', r.message)
	// 				}
	// 			}
	// 		})
	// 	}
	// },
	validate(frm) {
		if (!frm.doc.employee) {
			frappe.throw("Please enter Employee ")
		}
		if (!frm.doc.shift) {
			frappe.throw("Please enter Shift")
		}
		if (!frm.doc.to_time) {
			frappe.throw("Overtime Cannot be applied without Biometric In Time and Out Time")
		}
	},
	employee(frm) {
		if (frm.doc.employee) {
			frappe.call({
				method: "frappe.client.get_value",
				args:{
					doctype : "Employee",
					filters:{
						name : frm.doc.employee
					},
					fieldname : ['department']
				},
				callback(r){
					frm.set_value('department',r.message.department)
				}				
			})
		}
	},
	ot_date(frm) {
		if(frm.doc.employee){
			frappe.call({
				'method':'johoku.johoku.doctype.overtime_request.overtime_request.get_att_bio_checkin',
				'args':{
					emp:frm.doc.employee,
					ot_date:frm.doc.ot_date
				},
				callback(r){
					$.each(r.message,function(i,v){
						frm.set_value('bio_in',v.bio_in)
						frm.set_value('bio_out',v.bio_out)
						frm.set_value('total_wh',v.total_wh)
						frm.set_value('shift',v.shift)
						frm.set_value('ot_hours',v.ot_hours)
					})
				}
			})
		}
	},
	shift(frm) {
		if (frm.doc.bio_in && frm.doc.bio_out){
			frappe.call({
				'method':'johoku.johoku.doctype.overtime_request.overtime_request.get_time',
				'args':{
					emp:frm.doc.employee,
					ot_date:frm.doc.ot_date,
					shift:frm.doc.shift,
				},
				callback(r){
					$.each(r.message,function(i,v){
						frm.set_value('from_time',v.in_time)
						frm.set_value('to_time',v.out_time)
					})
				}
			})
		}
	},
	to_time(frm){
		if (frm.doc.to_time){
			frm.trigger('overtime_grade')
		}
	},
	overtime_grade(frm){
		if (frm.doc.ot_date){
			if (frm.doc.from_time && frm.doc.to_time && frm.doc.ot_hours){
				frappe.call({
					"method": "johoku.johoku.doctype.overtime_request.overtime_request.overtime_grade",
					args: {
						'ot_date': frm.doc.ot_date,
						'shift': frm.doc.shift,
						'from_time': frm.doc.from_time,
						'to_time': frm.doc.to_time,
						'employee_grade': frm.doc.employee_grade,
						'ot_hours':frm.doc.ot_hours,
						'emp':frm.doc.employee
					},
					callback(r) {
						console.log(r.message)
						frm.set_value('ot_compensation',r.message)
					}
				})
			}
		}
	},
});