// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt


frappe.ui.form.on('Live Shiftwise Dashboard', {
	refresh(frm) {
		frappe.call({
			method: 'johoku.johoku.doctype.live_shiftwise_dashboard.live_shiftwise_dashboard.get_shift',
			args:{
				'attendance_date':frm.doc.attendance_date
			},
			callback(r){
				if(r.message){
					console.log(r.message)
					if (r.message > "16:40"){
						frm.set_value('shift',2);
					}
					else if (r.message < "07:50" ){
						frm.set_value('shift',3);
					}
					else if (r.message > "07:50"){
						frm.set_value('shift',1);
					}
				}
			}
		})
		frm.disable_save()
	},
	attendance_date(frm){
		frm.trigger('livedata')
	},
	shift(frm){
		frm.trigger('livedata')
	},
	livedata(frm){
				frappe.call({
					method: 'johoku.johoku.doctype.live_shiftwise_dashboard.live_shiftwise_dashboard.live_data',
					args:{
						'attendance_date':frm.doc.attendance_date,
						'shift':frm.doc.shift,
					},
					callback(r) {
						if (r.message) {
							frm.fields_dict.live_shiftwise_dashboard.$wrapper.empty().append("<h2>Live Shiftwise Dashboard</h2><ul>" + r.message + "</ul>")
						}
					}
				}
				)}

	
});

