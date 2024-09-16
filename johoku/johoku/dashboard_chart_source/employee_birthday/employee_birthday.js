frappe.provide("frappe.dashboards.chart_sources");
frappe.dashboards.chart_sources["Employee Birthday"] = {
    method: "johoku.johoku.dashboard_chart_source.employee_birthday.employee_birthday.get_data",
    filters: [
        {
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("Date of Birth")
		},
    ]
}