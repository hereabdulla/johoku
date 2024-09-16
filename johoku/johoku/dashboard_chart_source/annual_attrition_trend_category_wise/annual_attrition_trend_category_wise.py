# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.desk.doctype.dashboard_chart.dashboard_chart import get_result
from frappe.utils import getdate
from frappe.utils.dashboard import cache_source
from frappe.utils.dateutils import get_period

@frappe.whitelist()
@cache_source
def get_data(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
    employee_category= None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
) -> dict[str, list]:
	if filters:
		filters = frappe.parse_json(filters)

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
    # employee_category = filters.get("employee_category")

	if not to_date:
		to_date = getdate()

	data = get_records(from_date, to_date, employee_category, "relieving_date", filters.get("company"), filters.get("employee_category"))

	re_data = get_result(data, filters.get("time_interval"), from_date, to_date, employee_category, "Count")

	return {
		"labels": [get_period(r[0], filters.get("time_interval")) for r in re_data],
		"datasets": [
			{"name": _("Attrition Count"), "values": [r[1] for r in re_data]},
		],
	}


def get_records(
	from_date: str, to_date: str, datefield: str, company: str, employee_category: str
) -> tuple[tuple[str, float, int]]:
	filters = [
		["Employee", "company", "=", company],
		["Employee", datefield, ">=", from_date, False],
		["Employee", datefield, "<=", to_date, False],
        ["Employee", "employee_category", "=", employee_category],
	]

	data = frappe.db.get_list(
		"Employee",
		fields=[f"{datefield} as _unit", "SUM(1)", "COUNT(*)"],
		filters=filters,
		group_by="_unit",
		order_by="_unit asc",
		as_list=True,
		ignore_ifnull=True,
	)
	return data
