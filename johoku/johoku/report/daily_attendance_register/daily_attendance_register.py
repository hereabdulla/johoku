# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
from math import floor
from frappe import msgprint, _
from calendar import month, monthrange
from datetime import date, timedelta, datetime
import pandas as pd

status_map = {
    "Absent": "AA",
	"Half Day": "HD",
	"Holiday": "HH",
	"Weekly Off": "WW",
    "Present": "P",
    "None" : ""
}

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = []
    columns += [
        _("Emp ID") + ":Data/:120",
        _("Employee Name") + ":Data/:180",
        _("Department") + ":Data/:150",
        _("Work Station") + ":Data/:150",
        _("Employee Category") + ":Data/:150",
        _("DOJ") + ":Date/:100",
        _("Attendance Date") + ":Date/:100",
        _("In Time") + ":Data/:100",
        _("Out Time") + ":Data/:100",
        _("Assigned Shift ") + ":Data/:80",
        _("Attended Shift ") + ":Data/:80",
        _("Shift Status") + ":Data/:80",
        _("TWH") + ":Data/:80",
        _("OT") + ":Data/:80"
    ]
    return columns

def get_data(filters):
    data = []
    emp_status_map = []
    dates = get_dates(filters.from_date,filters.to_date)
    for date in dates:
        employees = get_employees(filters)
        for emp in employees:
            row = [emp.name,
                   emp.employee_name,
                   emp.department or "-",
                   emp.work_station or "-",
                   emp.employee_category or "-",
                   emp.date_of_joining]
            row.append(date)
            att = frappe.db.get_value("Attendance",{'attendance_date':date,'employee':emp.name},['status',
                                                                                                 'in_time',
                                                                                                 'out_time',
                                                                                                 'assigned_shift',
                                                                                                 'shift',
                                                                                                 'shift_status',
                                                                                                 'attendance_date',
                                                                                                 'total_working_hours',
                                                                                                 'over_time_hours']) or ''
            # twh = 0
            # ot = 0
            if att:
                status = status_map.get(att[0], "")
                if att[1] is not None:
                    row.append(att[1].strftime('%H:%M:%S'))
                else:
                    row.append('-')
                if att[2] is not None:
                    row.append(att[2].strftime('%H:%M:%S'))
                else:
                    row.append('-')
                if att[3] == 'No Shift Assigned':
                    row.append("NS")
                else:
                    row.append(att[3])
                if att[4]:
                    row.append(att[4])
                else:
                    row.append("-")
                if att[5] not in ["1","2","3","NS/P"]:
                    row.append(att[5])
                else: 
                    row.append("P")
                # frappe.errprint(type(att[6]))
                # frappe.errprint(att[7])
                if att[7]:
                    frappe.errprint("-")
                    row.append(att[7])
                else:
                    row.append('-')
                if att[8]:
                    frappe.errprint('-')
                    row.append(att[8])
                else:
                    row.append('-')
                # row.append(att[6])
                # row.append(att[7])
            else:
                row += ['-','-','-','-','-','-','-','-','-']
            data.append(row)
    return data

def get_dates(from_date,to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]
    return dates

def get_employees(filters):
    conditions = ''
    if filters.department:
        conditions += "and department = '%s' " % filters.department
    if filters.employee:
        conditions += "and employee = '%s' " % filters.employee
    if filters.work_station:
        conditions += "and work_station = '%s' " % filters.work_station
    if filters.employee_category:
        conditions += "and employee_category = '%s' " % filters.employee_category
    employees = frappe.db.sql("""select name, employee_name, department,work_station,employee_category, date_of_joining from `tabEmployee` where status = 'Active' %s"""%(conditions),as_dict=True)
    return employees
