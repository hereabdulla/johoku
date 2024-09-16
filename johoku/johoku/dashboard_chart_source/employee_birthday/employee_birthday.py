# from dateutil.relativedelta import relativedelta
# import frappe
# from frappe import _
# from frappe.utils import getdate
# from frappe.utils.dashboard import cache_source

# @frappe.whitelist()
# @cache_source
# def get_data(
#     chart_name=None,
#     chart=None,
#     no_cache=None,
#     filters=None,
#     from_date=None,
#     timespan=None,
#     time_interval=None,
#     heatmap_year=None,
# ) -> dict[str, list]:
#     if filters:
#         filters = frappe.parse_json(filters)
		
#         # Get today's date
#         today = getdate()

#         # Calculate the range of dates for the upcoming 30 days
#         from_date = today
		
#         # Retrieve employees with upcoming birthdays within the date range
#         employees = frappe.get_list(
#             "Employee",
#             filters=[
#                 ["company", "=", filters.get("company")],
#                 ["status", "=", "Active"],
#                 ["date_of_birth", ">=", from_date],
			   
#             ],
#             pluck="name"
#         )

#         # Construct the data for the dashboard chart
#         data = {
#             "labels": [_("Upcoming Birthdays")],
#             "datasets": [
#                 {
#                     "name": _("Employees"),
#                     "values": [len(employees)],
#                     "chartType": "bar"
#                 }
#             ]
#         }

#         return data


# from datetime import date
# from frappe import _
# from frappe.utils.dashboard import cache_source
# from frappe.utils import getdate, formatdate
# import frappe

# @frappe.whitelist()
# @cache_source
# def get_data(chart_name=None, chart=None, no_cache=None, filters=None, from_date=None, to_date=None, timespan=None, time_interval=None, heatmap_year=None):
# 	if filters:
# 		filters = frappe.parse_json(filters)
# 		company = filters.get("company")

# 		if not company:
# 			frappe.throw(_("Please provide the company filter."))

# 		today = date.today()
# 		current_month = today.month
# 		current_day = today.day

# 		employees = frappe.get_list(
# 			"Employee",
# 			filters={"company": company, "status": "Active"},
# 			fields=["date_of_birth"],
# 		)
# 		today_birthdays = 0
# 		month_birthdays = 0

# 		for employee in employees:
# 			dob = employee.get("date_of_birth")
# 			if dob:
# 				dob_date = getdate(dob)
# 				dob_month = dob_date.month
# 				dob_day = dob_date.day

# 				if dob_month == current_month and dob_day == current_day:
# 					today_birthdays += 1

# 				if dob_month == current_month:
# 					month_birthdays += 1

# 		return {
# 			"labels": [_("Today's Birthdays"), _("This Month's Birthdays")],
# 			"datasets": [
# 				{"name": _("Employees"), "values": [today_birthdays, month_birthdays]},
# 			],
# 		}
# from datetime import date
# from frappe import _
# from frappe.utils.dashboard import cache_source
# from frappe.utils import getdate, formatdate
# import frappe

# @frappe.whitelist()
# @cache_source
# def get_data(chart_name=None, chart=None, no_cache=None, filters=None, from_date=None, to_date=None, timespan=None, time_interval=None, heatmap_year=None):
# 	if filters:
# 		filters = frappe.parse_json(filters)
# 		company = filters.get("company")

# 		if not company:
# 			frappe.throw(_("Please provide the company filter."))

# 		today = date.today()
# 		current_month = today.month
# 		current_day = today.day

# 		employees = frappe.get_list(
# 			"Employee",
# 			filters={"company": company, "status": "Active"},
# 			fields=["employee_name", "date_of_birth"],
# 		)
# 		today_birthdays = []
# 		month_birthdays = []

# 		for employee in employees:
# 			dob = employee.get("date_of_birth")
# 			if dob:
# 				dob_date = getdate(dob)
# 				dob_month = dob_date.month
# 				dob_day = dob_date.day

# 				if dob_month == current_month and dob_day == current_day:
# 					today_birthdays.append((employee.get("employee_name"), formatdate(dob_date, "MMMM d")))

# 				if dob_month == current_month:
# 					month_birthdays.append((employee.get("employee_name"), formatdate(dob_date, "MMMM d")))

# 		return {
# 			"labels": [_("Today's Birthdays"), _("This Month's Birthdays")],
# 			"datasets": [
# 				{"name": _("Employees"), "values": [len(today_birthdays), len(month_birthdays)], "details": [today_birthdays, month_birthdays]},
# 			],
# 		}


# from datetime import date
# from frappe import _
# from frappe.utils.dashboard import cache_source
# from frappe.utils import getdate, formatdate
# import frappe

# @frappe.whitelist()
# @cache_source
# def get_data(chart_name=None, chart=None, no_cache=None, filters=None, from_date=None, to_date=None, timespan=None, time_interval=None, heatmap_year=None):
# 	if filters:
# 		filters = frappe.parse_json(filters)
# 		company = filters.get("company")

# 		if not company:
# 			frappe.throw(_("Please provide the company filter."))

# 		today = date.today()
# 		current_month = today.month
# 		current_day = today.day

# 		employees = frappe.get_list(
# 			"Employee",
# 			filters={"company": company, "status": "Active"},
# 			fields=["employee_number", "employee_name", "date_of_birth"],
# 		)
# 		today_birthdays = []
# 		month_birthdays = []

# 		for employee in employees:
# 			dob = employee.get("date_of_birth")
# 			if dob:
# 				dob_date = getdate(dob)
# 				dob_month = dob_date.month
# 				dob_day = dob_date.day

# 				if dob_month == current_month and dob_day == current_day:
# 					today_birthdays.append({
# 						"employee_number": employee.get("employee_number"),
# 						"employee_name": employee.get("employee_name"),
# 						"date_of_birth": formatdate(dob_date, "MMMM d")
# 					})

# 				if dob_month == current_month:
# 					month_birthdays.append({
# 						"employee_number": employee.get("employee_number"),
# 						"employee_name": employee.get("employee_name"),
# 						"date_of_birth": formatdate(dob_date, "MMMM d")
# 					})

# 		return {
# 			"labels": [_("Today's Birthdays"), _("This Month's Birthdays")],
# 			"datasets": [
# 				{
# 					"name": _("Employees"),
# 					"values": [len(today_birthdays), len(month_birthdays)],
# 					"details": [today_birthdays, month_birthdays]
# 				},
# 			],
# 		}



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
