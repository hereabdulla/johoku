# Copyright (c) 2022, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, add_days, date_diff, getdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter
from frappe.model.document import Document

class ShiftSchedule(Document):
    
@frappe.whitelist()
def get_template():
    args = frappe.local.form_dict

    if getdate(args.from_date) > getdate(args.to_date):
        frappe.throw(_("To Date should be greater than From Date"))

    w = UnicodeWriter()
    w = add_header(w)
    w = add_data(w, args)

    frappe.response['result'] = cstr(w.getvalue())
    frappe.response['type'] = 'csv'
    frappe.response['doctype'] = "Shift Assignment"

def add_header(w):
    w.writerow(["Emplyoee ID",'Employee Name','Department','Employment Type','Shift Type','Route No','Boarding Point'])
    return w

def add_data(w, args):
    data = get_data(args)
    writedata(w, data)
    return w

@frappe.whitelist()
def get_data(args):
    employees = frappe.get_all('Employee',{'status':'Active','department':args.department,},['*'])
    data = []
    for emp in employees:
        row = [
            emp.name,emp.first_name,emp.department,emp.employment_type,'',emp.route_no,emp.boarding_point
        ]
        data.append(row)    
    return data

@frappe.whitelist()
def writedata(w, data):
    for row in data:
        w.writerow(row)


