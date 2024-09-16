# Copyright (c) 2022, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _
from frappe.utils import formatdate


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = []
    columns += [
        _("Employee ID") + ":Data/:150",_("Employee Name") + ":Data/:200",_("Department") + ":Data/:150",_("OT From Date") + ":Data/:150",_("OT To Date") + ":Data/:150",_("Shift") + ":Data/:100",_("OT Hours") + ":Data/:150",_("OT Starting Time") + ":Data/:150",_("Document Status") + ":Data/:200"
    ]
    return columns

def get_data(filters):
    data = []
    docstatus = ''
    if filters.employee:
        shifts = frappe.db.sql("""select * from `tabOvertime List` where ot_from_date between '%s' and '%s' and employee = '%s' and docstatus != '2' """%(filters.ot_from_date,filters.ot_to_date,filters.employee),as_dict=True)
        for s in shifts:
            if s.docstatus == 1:
               docstatus = 'Submitted'
            elif s.docstatus == 0:
                docstatus = 'Draft'
            data.append([s.employee,s.employee_name,s.department,formatdate(s.ot_from_date),formatdate(s.ot_to_date),s.shift,s.ot_hours,s.ot_starting_time,docstatus]) 
    elif filters.department:
        shifts = frappe.db.sql("""select * from `tabOvertime List` where ot_from_date between '%s' and '%s' and department = '%s' and docstatus != '2' """%(filters.ot_from_date,filters.ot_to_date,filters.department),as_dict=True)
        for s in shifts:
            if s.docstatus == 1:
               docstatus = 'Submitted'
            elif s.docstatus == 0:
                docstatus = 'Draft'
            data.append([s.employee,s.employee_name,s.department,formatdate(s.ot_from_date),formatdate(s.ot_to_date),s.shift,s.ot_hours,s.ot_starting_time,docstatus])           
    else: 
        shifts = frappe.db.sql("""select * from `tabOvertime List` where ot_from_date between '%s' and '%s' and docstatus != '2' """%(filters.ot_from_date,filters.ot_to_date),as_dict=True)
        for s in shifts:
            if s.docstatus == 1:
                docstatus = 'Submitted'
            elif s.docstatus == 0:
                docstatus = 'Draft'
            data.append([s.employee,s.employee_name,s.department,formatdate(s.ot_from_date),formatdate(s.ot_to_date),s.shift,s.ot_hours,s.ot_starting_time,docstatus])
    return data

