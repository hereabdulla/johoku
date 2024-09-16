frappe.provide("frappe.dashboards.chart_sources");
frappe.dashboards.chart_sources["Covid 19 Vaccination Chart"] = {
    method: "johoku.johoku.dashboard_chart_source.covid_19_vaccination_chart.covid_19_vaccination_chart.get_data",
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
			default: frappe.defaults.get_user_default("year_start_date"),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default:  frappe.defaults.get_user_default("year_end_date"),
		},
        {
            fieldname: "time_interval",
            label: __("Time Interval"),
            fieldtype: "Select",
            options: ["Monthly", "Quarterly", "Yearly"],
            default: "Monthly",
            reqd: 1
        },
    ]
};