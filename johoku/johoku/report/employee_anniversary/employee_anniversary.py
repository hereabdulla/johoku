# Copyright (c) 2022, TEAMPRO and contributors
# For license information, please see license.txt
import frappe
from frappe import _
import datetime
from datetime import datetime,timedelta
import dateutil.relativedelta
from dateutil.relativedelta import relativedelta
import frappe.utils
from frappe.utils import (
	add_days,
	add_months,
	add_years,
	cint,
	cstr,
	date_diff,
    today,
	flt,
	formatdate,
	get_last_day,
	get_timestamp,
	getdate,
	nowdate,
)


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_employees(filters)
    # year = get_workeryear(filters)
    frappe.errprint(data)
    return columns, data

def get_columns():
    return[
        _("Employee") + ":Link/Employee:120",
        _("Name") + ":Data:200",
        _("Date of Joining") + ":Date:100",
        _("Department") + ":Link/Department:120",
        _("Designation") + ":Link/Designation:120",
        _("Gender") + ":Data:60",
        _("Anniversary") + ":Data:270",
    ]
def get_employees(filters):
    data = []
    frappe.errprint('experience')
    employee = frappe.db.get_all('Employee',{'status':'Active'},['*'])
    for emp in employee:
        
        date_2 = datetime.now()
        diff = relativedelta.relativedelta(date_2, emp.date_of_joining)
        yos = cstr(diff.years) + ' years, ' + cstr(diff.months) +' months and ' + cstr(diff.days) + ' days'
        current_day = today()
        date = emp.date_of_joining
        curr = datetime.strptime(str(current_day),'%Y-%m-%d').date()
        experience = date_diff(curr,date)
        
        row = [emp.name,emp.employee_name,emp.date_of_joining,emp.department,emp.designation,emp.gender,yos]
        data.append(row) 
    return data 


def get_conditions(filters):
    conditions= ""
    if filters.get("month"):
        month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec",
        ].index(filters["month"]) + 1
        conditions += " and month(date_of_joining) = '%s'" % month 
    return conditions


    
    # def get_data(filters):
    # data = []
    # if  filters.employee:
    #     employee = frappe.db.get_all('Employee',{'status':'Active','name':filters.employee},['*'])
    #     for emp in employee:
    #         row = [emp.name,emp.employee_name,emp.date_of_joining,emp.date_of_birth,emp.father_name,emp.mother_name,emp.department,emp.designation,emp.gender,emp.blood_group]
    #         data.append(row) 
    # else:
    #     employee = frappe.db.get_all('Employee',{'status':'Active'},['*'])
    #     for emp in employee:
    #         row = [emp.name,emp.employee_name,emp.date_of_joining,emp.date_of_birth,emp.father_name,emp.mother_name,emp.department,emp.designation,emp.gender,emp.blood_group]
    #         data.append(row) 
    # return data