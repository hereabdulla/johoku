// Copyright (c) 2022, TEAMPRO and contributors
// For license information, please see license.txt


frappe.ui.form.on('Statutory Forms', {
    refresh(frm) {
        frm.add_custom_button(__("Print Preview"), function () {
            if (frm.doc.select_the_form == "PF-Form 5") {
                var print_format = "Statutory PF Form-5"
            }
            if (frm.doc.select_the_form == "PF-Form 10") {
                var print_format = "Statutory PF Form-10"
            }
            var f_name = frm.doc.name
            // var print_format = "Statutory PF Form-5";
            window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                + "doctype=" + encodeURIComponent("Statutory Forms")
                + "&name=" + encodeURIComponent(f_name)
                + "&trigger_print=1"
                + "&format=" + print_format
                + "&no_letterhead=0"


            ));

        });

        if (frm.doc.docstatus == 0) {
            frm.add_custom_button(__('Get Employees'), function () {
                if (frm.doc.select_the_form == "PF-Form 5") {
                    frm.call('get_employees_form_5').then((r) => {
                        frm.clear_table('employees')
                        $.each(r.message, function (i, v) {
                            frm.add_child('employees', {
                                'employee': v.employee,
                                'employee_name': v.employee_name,
                                'age': v.age,
                                'date_of_birth': v.date_of_birth,
                                'gender': v.gender,

                            })



                        })
                        frm.refresh_field('employees')
                    })
                }

                else if (frm.doc.select_the_form == "PF-Form 10") {
                    console.log('hi')
                    frm.call('get_employees_form_10').then((r) => {
                        console.log('r.message')
                        frm.clear_table('emp_details')
                        $.each(r.message, function (i, f) {
                            frm.add_child('emp_details', {
                                'employee': f.employee,
                                'employee_name': f.employee_name,
                                'relieving_date': f.relieving_date,
                                'reason_for_leaving': f.reason_for_leaving,
                                'feedback': f.feedback,
                            })

                            frm.refresh_field('emp_details')
                        })


                    })
                }




            })


        }
    }


});
