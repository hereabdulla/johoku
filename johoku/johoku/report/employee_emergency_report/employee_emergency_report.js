// Copyright (c) 2016, TeamPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Emergency Report"] = {
	"filters": [
		{
			"fieldname":"date",
			"label": __("Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.nowdate())
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		}
	]
};

