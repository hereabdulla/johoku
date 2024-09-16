from datetime import date
from frappe import _
from frappe.utils.dashboard import cache_source
from frappe.utils import getdate, formatdate
import frappe

@frappe.whitelist()
@cache_source
def get_data(chart_name=None, chart=None, no_cache=None, filters=None, from_date=None, to_date=None, timespan=None, time_interval=None, heatmap_year=None):
	if filters:
		filters = frappe.parse_json(filters)
		company = filters.get("company")

		if not company:
			frappe.throw(_("Please provide the company filter."))

		today = date.today()
		current_month = today.month
		current_day = today.day

		employees = frappe.get_list(
			"Employee",
			filters={"company": company, "status": "Active"},
			fields=["employee_number", "employee_name", "date_of_birth", "marriage_date"],
		)
		today_birthdays = []
		month_birthdays = []
		today_anniversaries = []
		month_anniversaries = []

		for employee in employees:
			dob = employee.get("date_of_birth")
			dom = employee.get("marriage_date")

			if dob:
				dob_date = getdate(dob)
				dob_month = dob_date.month
				dob_day = dob_date.day

				if dob_month == current_month and dob_day == current_day:
					today_birthdays.append({
						"employee_number": employee.get("employee_number"),
						"employee_name": employee.get("employee_name"),
						"date_of_birth": formatdate(dob_date, "MMMM d")
					})

				if dob_month == current_month:
					month_birthdays.append({
						"employee_number": employee.get("employee_number"),
						"employee_name": employee.get("employee_name"),
						"date_of_birth": formatdate(dob_date, "MMMM d")
					})

			if dom:
				dom_date = getdate(dom)
				dom_month = dom_date.month
				dom_day = dom_date.day

				if dom_month == current_month and dom_day == current_day:
					today_anniversaries.append({
						"employee_number": employee.get("employee_number"),
						"employee_name": employee.get("employee_name"),
						"marriage_date": formatdate(dom_date, "MMMM d")
					})

				if dom_month == current_month:
					month_anniversaries.append({
						"employee_number": employee.get("employee_number"),
						"employee_name": employee.get("employee_name"),
						"marriage_date": formatdate(dom_date, "MMMM d")
					})

		return {
			"labels": [_("Today's Birthdays"),  _("Today's Anniversaries")],
			"datasets": [
				{
					"name": _("Employees"),
					"values": [len(today_birthdays),len(today_anniversaries)],
					"details": [today_birthdays, today_anniversaries],
					"colors": ["#0F4C75"]
				},
			],
		}
