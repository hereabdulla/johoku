# Copyright (c) 2013, TEAMPRO and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
from math import floor
from frappe import msgprint, _
from calendar import month, monthrange
from datetime import date, timedelta, datetime

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = []
    columns += [
        _("Employee") + ":Data:100",_("Employee Name") + ":Data:200",_("Department") + ":Data:150"
    ]
    dates = get_dates(filters.from_date,filters.to_date)
    for date in dates:
        date = datetime.strptime(date,'%Y-%m-%d')
        day = datetime.date(date).strftime('%d')
        month = datetime.date(date).strftime('%m')
        columns.append(_(day + '/' + month) + ":Data:70")
    columns.append(_("Total") + ":Data/:70")
    return columns

def get_data(filters):
    data = []
    employees = get_employees(filters)
    for emp in employees:
        dates = get_dates(filters.from_date,filters.to_date)
        row1 = [emp.name,emp.employee_name,emp.department]
        total_ot = 0
        for date in dates:
            att = frappe.db.get_value("Attendance",{'attendance_date':date,'employee':emp.name},['over_time_hours'])
            if att:
                row1.append(att)
                total_ot += att
            else:
                row1.append('-')
        row1.extend([total_ot])
        data.append(row1)
    return data
    
def get_dates(from_date,to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]
    return dates

def get_employees(filters):
    conditions = ''
    if filters.department:
        conditions += "and department = '%s' "%filters.department
    elif filters.employee:
        conditions += "and employee = '%s' "%filters.employee
    employees = frappe.db.sql("""select name, employee_name, department from `tabEmployee` where status = 'Active' %s """%(conditions),as_dict=True)
    left_employees = frappe.db.sql("""select name, employee_name, department from `tabEmployee` where status = 'Left' and relieving_date >= '%s' %s """ %(filters.from_date,conditions),as_dict=True)
    employees.extend(left_employees)
    return employees