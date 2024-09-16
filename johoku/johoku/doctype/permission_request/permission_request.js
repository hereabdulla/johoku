// Copyright (c) 2022, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Permission Request', {
    refresh: function (frm) {
        frappe.breadcrumbs.add("HR", "Permission Request");
    },
    employee_id(frm) {
        if (frm.doc.employee_id) {
            frappe.call({
                "method": "johoku.johoku.doctype.permission_request.permission_request.get_employee_approver",
                "args": {
                    "dept":frm.doc.department
                },
                callback(r) {
                    frm.set_value('permission_approver', r.message)
                }
            })
        }  
    },
    // permission_date(frm) {
    //     if (!frappe.user.has_role('HR GM')) {
    //         if (frm.doc.permission_date) {
    //             var date = frappe.datetime.add_days(frm.doc.permission_date, 3)
    //             frappe.call({
    //                 "method":"johoku.utils.get_server_date" ,
    //                 callback(r){
    //                     if (r.message > date) {
    //                         frappe.msgprint("Permission should be applied within 3 days")
    //                         frappe.validated = false;
    //                     }
    //                 }
    //             })
    //         }
    //     }
    // },
    // validate(frm) {
    //     if (!frappe.user.has_role('HR GM')) {
    //         if (frm.doc.permission_date) {
    //             var date = frappe.datetime.add_days(frm.doc.permission_date, 3)
    //             frappe.call({
    //                 "method":"johoku.utils.get_server_date" ,
    //                 callback(r){
    //                     if (r.message > date) {
    //                         frappe.msgprint("Permission should be applied within 3 days")
    //                         frappe.validated = false;
    //                     }
    //                 }
    //             })
    //         }
    //     }
    // },
    permission_hour(frm){
        if (frm.doc.session){
            frappe.call({
                "method": "johoku.johoku.doctype.permission_request.permission_request.get_endtime1",
                "args": {
                    "shift":frm.doc.shift,
                    "session":frm.doc.session,
                    "per_hour":frm.doc.permission_hour,	
                },	
                callback(r){
                    $.each(r.message,function(i,v){
                        if (frm.doc.permission_hour == '1'){
                            frm.set_value('from_time',v.get_shift_time)
                            frm.set_value('to_time',v.one_hour)
                        }
                        else if (frm.doc.permission_hour == '2'){
                            frm.set_value('from_time',v.get_shift_time)
                            frm.set_value('to_time',v.two_hour)
                        }
                        else{
                            frm.set_value('from_time','00:00')
                            frm.set_value('to_time','00:00')
                        }
                    })
                }
            })
        }
		else {
			frm.trigger('shift')
		}
    }
    // after_save(frm){
    // 	console.log('ok')
        
    // },	
    // session(frm) {
    // 	if (frm.doc.shift) {
    // 		frappe.call({
    // 			"method": "johoku.johoku.doctype.permission_request.permission_request.get_endtime1",
    // 			"args": {
    // 				"shift":frm.doc.shift,
    // 				"session":frm.doc.session,
    // 				"per_hour":frm.doc.permission_hour,	
    // 			},
    // 			callback(r) {
    // 				// frm.set_value("session", 'First Half')
    // 				// frm.set_value("from_time", r.message.start_time)
    // 				// frm.call('get_endtime1', {
    // 				// 	start_time: r.message.start_time
    // 				// }).then((d) => {
    // 				// 	frm.set_value("to_time", d.message)
    // 				// })
    // 			}
    // 		})
    // 	}
    // },
    // session(frm) {
    // 	if (frm.doc.shift) {
    // 		if (frm.doc.session == 'Second Half') {
    // 			frappe.call({
    // 				"method": "frappe.client.get",
    // 				"args": {
    // 					doctype: "Shift Type",
    // 					fieldname: ["name", "start_time", "end_time"],
    // 					filters: {
    // 						name: frm.doc.shift
    // 					}
    // 				},
    // 				callback(r) {
    // 					frm.set_value("to_time", r.message.end_time)
    // 					frm.call('get_endtime2', {
    // 						end_time: r.message.end_time
    // 					}).then((d) => {
    // 						frm.set_value("from_time", d.message)
    // 					})
    // 				}
    // 			})
    // 		}
    // 		else {
    // 			frm.trigger('shift')
    // 		}
    // 	}
    //  }
});


