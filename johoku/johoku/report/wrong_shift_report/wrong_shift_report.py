# Copyright (c) 2013, teampro and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.utils import get_first_day, today, get_last_day, format_datetime, add_years, date_diff, add_days, getdate, cint, format_date,get_url_to_form



def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        _('Employee ID') +':Data:100',
        _('Employee Name') +':Data:200',
        _("Department") + ":Data/:150",
        _("Work Station") + ":Data/:150",
        _("Employee Category") + ":Data/:150",
        _('Attendance Date') +':Data:150',
        _('Assigned Shift') +':Data:150',
        _('Attended Shift') +':Data:150'
    ]
    return columns

def get_data(filters):
    data = []
    employees = get_employees(filters)
    for emp in employees: 
        attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(filters.from_date,filters.to_date)),'employee':emp.name},['*'])
        for att in attendance:
            if att.status == "Absent":
                if att.shift_matched_or_unmatched == "Unmatched":
                    row = [emp.name,
                        emp.employee_name,
                        emp.department or "-",
                        emp.work_station or "-",
                        emp.employee_category or "-",
                        format_date(att.attendance_date),
                        att.assigned_shift,
                        att.attended_shift
                        ]
                    data.append(row)
    return data	


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
    employees = frappe.db.sql("""select name, employee_name,employee_category, department, date_of_joining,work_station from `tabEmployee` where status = 'Active' %s"""%(conditions),as_dict=True)
    return employees