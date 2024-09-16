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

def execute(filters=None):
    data = []
    columns = get_columns()
    attendance = get_attendance(filters)
    for att in attendance:
        data.append(att)
    return columns, data

def get_columns():
    columns = [
         _("Employee") + ":Data:100",_("Employee Name") + ":Data:170",_("Department") + ":Data:150",_("Attendance Date") + ":Data:140",_("Shift") + ":Data:60",_("OT Hours") + ":Data:100",
    ]
    return columns

def get_attendance(filters):
    data = []
    if filters.employee:
        attendance = frappe.db.get_all('Attendance',{'status':'Present','attendance_date':('between',(filters.from_date,filters.to_date)),'employee':filters.employee},['*'])
        for att in attendance:
            if att.over_time_hours > 0:
                row = [att.employee,att.employee_name,att.department,format_date(att.attendance_date),att.shift,att.over_time_hours]
                data.append(row)
    elif filters.department:
        attendance = frappe.db.get_all('Attendance',{'status':'Present','attendance_date':('between',(filters.from_date,filters.to_date)),'department':filters.department},['*'])
        for att in attendance:
            if att.over_time_hours > 0:
                row = [att.employee,att.employee_name,att.department,format_date(att.attendance_date),att.shift,att.over_time_hours]
                data.append(row)
    else:
        attendance = frappe.db.get_all('Attendance',{'status':'Present','attendance_date':('between',(filters.from_date,filters.to_date))},['*'])
        for att in attendance:
            if att.over_time_hours > 0:
                row = [att.employee,att.employee_name,att.department,format_date(att.attendance_date),att.shift,att.over_time_hours]
                data.append(row)
    return data
