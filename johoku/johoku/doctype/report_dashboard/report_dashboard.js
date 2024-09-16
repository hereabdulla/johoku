// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Report Dashboard', {
	
	download:function(frm){
		if(frm.doc.report == 'Daily Manpower Report'){
			var path = "johoku.johoku.doctype.report_dashboard.man_power_vs_actual_report.download"
			var args = 'att_date=%(att_date)s&shift=%(shift)s&dept=%(dept)s'
		}
		if(path){
			window.location.href = repl(frappe.request.url+
				'?cmd=%(cmd)s&%(args)s',{
					cmd:path,
					args:args,
					shift:frm.doc.shift,
					dept:frm.doc.department,
					att_date:frm.doc.attendance_date,

				}
			)
		}
		
	}
});
