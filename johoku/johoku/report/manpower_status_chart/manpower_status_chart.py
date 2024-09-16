# Copyright (c) 2013, teampro and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six import string_types
import frappe
from datetime import datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,format_date)
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate
from itertools import count
import pandas as pd
import datetime as dt


def execute(filters=None):
    data = []
    columns = get_columns()
    manpower = get_details(filters)
    for mp in manpower:
        data.append(mp)
    return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Data:100",
        _("Employee Name") + ":Data:150",
        _("Department") + ":Data:150",
        _("Employment Type") + ":Data:150",
        _("Employee Category") + ":Data:100",
        _("Grade") + ":Data:100",
    ]
    return columns

def get_details(filters):
    data = []
    manpower = frappe.db.get_all('Employee',{'status':'Active'},['*'])
    for mp in manpower:
        row = [mp.employee,mp.employee_name,mp.department,mp.employment_type,mp.employee_category,mp.grade]
        data.append(row)
    return data