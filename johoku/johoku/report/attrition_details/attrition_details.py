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
    attrition = get_attrition(filters)
    for att in attrition:
        data.append(att)
    return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Data:100",
		_("Employee Name") + ":Data:150",
		_("Department") + ":Data:110",
        _("Employment Type") + ":Data:110",
        _("Designation") + ":Data:110",
		_("Date of Exit") + ":Date:140",
    ]
    return columns

def get_attrition(filters):
    data = []
    attrition = frappe.get_all('Employee',{'status':'Left','relieving_date':('between',(filters.from_date,filters.to_date))},['*'])
    for att in attrition:
        row = [att.employee,att.employee_name,att.department,att.employment_type,att.designation,att.relieving_date]
        data.append(row)
    return data
