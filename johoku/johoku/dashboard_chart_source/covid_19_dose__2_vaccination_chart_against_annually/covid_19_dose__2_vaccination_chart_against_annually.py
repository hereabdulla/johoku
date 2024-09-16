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
    timespan=None,
    time_interval=None,
    heatmap_year=None,
) -> dict[str, list]:
    if filters:
        filters = frappe.parse_json(filters)

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    if not to_date:
        to_date = getdate()

    dose2 = get_records(from_date, to_date, "dose_2_vaccinated_date", filters.get("company"))

    return {
    "labels": [get_period(r[0], filters.get("time_interval")) for r in dose2],
    "datasets": [   
    {"name": _("Dose2 Count"), "values": [r[1] for r in dose2]},
    ],
    }

def get_records(
    from_date: str, to_date: str, datefield: str, company: str
) -> tuple[tuple[str, float, int]]:
    filters = [
        ["Employee", "company", "=", company],
        ["Employee", datefield, ">=", from_date, False],
        ["Employee", datefield, "<=", to_date, False],
    ]

    data = frappe.db.sql(
    """SELECT
    dose_2_vaccinated_date,
    sum(count(*)) OVER (PARTITION BY d2v ORDER BY dose_2_vaccinated_date)
    FROM tabEmployee
    where status='Active' and dose_2_vaccinated_date is not null
    GROUP BY d2v, dose_2_vaccinated_date
    ORDER BY d2v, dose_2_vaccinated_date"""
    )
    return data