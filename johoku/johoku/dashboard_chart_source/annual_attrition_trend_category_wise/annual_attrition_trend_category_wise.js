frappe.provide("frappe.dashboards.chart_sources");
frappe.dashboards.chart_sources["Annual Attrition Trend Category wise"] = {
	method: "johoku.johoku.dashboard_chart_source.annual_attrition_trend_category_wise.annual_attrition_trend_category_wise.get_data",
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
			default: frappe.defaults.get_user_default("month_start_date"),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default:  frappe.defaults.get_user_default("month_end_date"),
		},
		{
			fieldname: "time_interval",
			label: __("Time Interval"),
			fieldtype: "Select",
			// options: ["Monthly", "Quarterly", "Yearly"],
			// default:  "Monthly",
			reqd: 1
		},
        {
			fieldname: "employee_category",
			label: __("Employee Category"),
			fieldtype: "link",
			options: "Employee Category",
			reqd: 1
		},
	]
};
