// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Birthday Anniversary"] = {
	"filters": [
		{
			"fieldname": "date_of_birth",
			"label": __("Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		}

	]
};
