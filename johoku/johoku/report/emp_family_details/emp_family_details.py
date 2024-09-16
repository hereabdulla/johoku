# Copyright (c) 2022, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = []
    employee = get_data(filters)
    for emp in employee:
        data.append(emp)
    return columns, data

def get_columns():
    return[
        _("Employee") + ":Link/Employee:120",
        _("Name") + ":Data:100",
        _("Date of Joining") + ":Date:100",
        _("Date of Birth") + ":Date:100",
        _("Father Name") + ":Data:80",
        _("Mother Name")  + ":Data:80",
        _("Department") + ":Link/Department:120",
        _("Designation") + ":Link/Designation:120",
        _("Gender") + ":Data:100",
        _("Blood Group") + ":Data:80"  
    ]
    
    
def get_data(filters):
    data = []
    if  filters.employee:
        employee = frappe.db.get_all('Employee',{'status':'Active','name':filters.employee},['*'])
        for emp in employee:
            row = [emp.name,emp.employee_name,emp.date_of_joining,emp.date_of_birth,emp.father_name,emp.mother_name,emp.department,emp.designation,emp.gender,emp.blood_group]
            data.append(row) 
    else:
        employee = frappe.db.get_all('Employee',{'status':'Active'},['*'])
        for emp in employee:
            row = [emp.name,emp.employee_name,emp.date_of_joining,emp.date_of_birth,emp.father_name,emp.mother_name,emp.department,emp.designation,emp.gender,emp.blood_group]
            data.append(row) 
    return data