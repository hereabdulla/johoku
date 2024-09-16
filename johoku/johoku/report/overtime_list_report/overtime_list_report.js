// Copyright (c) 2022, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Overtime List Report"] = {
	"filters": [

		{
			"fieldname":"ot_from_date",
			"label": __("OT From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.nowdate())

		},
		{
			"fieldname":"ot_to_date",
			"label": __("OT To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.nowdate())
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
		},	
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		}

	]
};
