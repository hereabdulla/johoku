// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Attendance Register"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.nowdate()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.nowdate()
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
		},
		{
			"fieldname": "work_station",
			"label": __("Work Station"),
			"fieldtype": "Link",
			"options": "Work Station"
		},
		{
			"fieldname": "employee_category",
			"label": __("Employee Category"),
			"fieldtype": "Link",
			"options":"Employee Category"
			// "options": " \nStaff\nDT\nITI\nGT\nTT\nCL\nNaps",
			// "default": ["Staff", "DT", "ITI", "GT", "TT", "CL", "Naps"]
			// "default" : " "
		},
	]	
};
