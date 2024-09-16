// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Live Shift-wise Manpower Count Report"] = {
	"filters": [
		{
			"fieldname": "attendance_date",
			"label": __("Attendance Date"),
			"fieldtype": "Date",
			"width": "100",
			"default": frappe.datetime.nowdate(),
		},
		{
			"fieldname": "shift",
			"label": __("Shift Type"),
			"fieldtype": "Link",
			"options": "Shift Type",
		},
	],
	onload(frm){
		frappe.call({
			method: 'johoku.johoku.doctype.live_shiftwise_dashboard.live_shiftwise_dashboard.get_shift',
			callback(r){
				if(r.message){
					console.log(r.message)
					if (r.message > "16:40"){
						frappe.query_report.set_filter_value('shift', 2);
					}
					else if (r.message < "07:50" ){
						frappe.query_report.set_filter_value('shift', 3);
					}
					else if (r.message > "07:50"){
						frappe.query_report.set_filter_value('shift', 1);	
					}
				}
			}
		})
	}
};
