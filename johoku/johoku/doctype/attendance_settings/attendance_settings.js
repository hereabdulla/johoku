// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Settings', {
	refresh: function(frm) {
		frm.disable_save()
	},
	process_attendance(frm){
		// console.log("HI");
		frappe.call({
			"method": "johoku.mark_attendance.mark_att_process",
			"args":{
				from_date  : frm.doc.date,
			},
			freeze: true,
			freeze_message: 'Processing Attendance....',
			callback(r){
				console.log("HI");
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Attendance is Marking in the Background. Kindly check after sometime")
				}
			}
		})
	},
	process_checkin(frm){
		// console.log("HI");
		frappe.call({
			"method": "johoku.custom.get_urc_to_ec",
			"args":{
				from_date  : frm.doc.date,
			},
			freeze: true,
			freeze_message: 'Processing Checkin....',
			callback(r){
				console.log("HI");
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Checkin is Marking in the Background. Kindly check after sometime")
				}
			}
		})
	},
	process_checkin_2(frm){
		// console.log("HI");
		frappe.call({
			"method": "johoku.custom.push_punch",
			"args":{
				from_date  : frm.doc.date,
			},
			freeze: true,
			freeze_message: 'Processing Checkin Easytimepro to HRPRO....',
			callback(r){
				console.log("HI");
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Checkin is Marking in the Background. Kindly check after sometime")
				}
			}
		})
	},
});
