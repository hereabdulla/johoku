// Copyright (c) 2022, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Overtime List', {
	onload(frm) {
		if(frm.doc.shift == '1'){
			frm.set_value("ot_starting_time","16:40:00");
		}
		else if(frm.doc.shift == '2')
		{
			frm.set_value("ot_starting_time","01:30:00");
		}
		else
		{
			frm.set_value("ot_starting_time","07:50:00");
		}
	},
});
