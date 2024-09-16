from __future__ import unicode_literals
from csv import writer
from inspect import getfile
from unicodedata import name
import frappe
from frappe.utils import cstr, add_days, date_diff, getdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file, upload
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from numpy import unicode_


class OvertimeSchedule(Document):

    def on_submit(self): 
        if self.attach:
            self.create_overtime_plan()

    def create_overtime_plan(self):
        filepath = get_file(self.attach)
        pps = read_csv_content(filepath[1])
        dates = self.get_dates(self.ot_from_date,self.ot_to_date)
        for date in dates:
            for pp in pps:
                frappe.errprint(pp[2])
                if pp[2] != 'Overtime':
                    if pp[1]:
                        if not frappe.db.exists("Overtime Plan",{'employee':pp[0],'ot_start_date':date,'ot_end_date':date,'docstatus':['in',[0,1]]}):
                            doc = frappe.new_doc('Overtime Plan')
                            doc.employee = pp[0]
                            doc.ot_hours = pp[2]
                            doc.department = pp[3]
                            doc.employee_type = pp[4]
                            doc.designation = pp[5]
                            doc.employee_garde = pp[6]
                            doc.shift = pp[7]
                            doc.ot_from_date = date
                            doc.ot_to_date = date
                            doc.ot_starting_time = ''
                            doc.ot_ending_time = ''
                            doc.overtime_plan = self.name
                            doc.save(ignore_permissions=True)
                            doc.submit()
                            frappe.db.commit()

    def get_dates(self,ot_from_date,ot_to_date):
        no_of_days = date_diff(add_days(ot_to_date, 1), ot_from_date)
        dates = [add_days(ot_from_date, i) for i in range(0, no_of_days)]
        return dates

                        
               
@frappe.whitelist()
def get_template():
    args = frappe.local.form_dict

    if getdate(args.ot_from_date) > getdate(args.ot_to_date):
        frappe.throw(_(" OT To Date should be greater than From Date"))

    w = UnicodeWriter()
    w = add_header(w)
    w = add_data(w, args)

    frappe.response['result'] = cstr(w.getvalue())
    frappe.response['type'] = 'csv'
    frappe.response['doctype'] = "Overtime Plan"

def add_header(w):
    w.writerow(['Employee ID','Employee Name','Overtime','Department','Employement Type','Designation','Employee Grade','Shift','Start Date'])
    return w

def add_data(w, args):
    data = get_data(args)
    writedata(w, data)
    return w

@frappe.whitelist()
def get_data(args):
    # employees = frappe.get_all('Employee',{'status':'Active','department':args.department,},['*'])
    # data = []
    # for emp in employees:
    #         row = [
    #             emp.name,emp.employee_name,emp.default_overtime or '',emp.department,emp.employee_type or '',emp.designation or '',emp.grade or ''
    #         ] 

    shifts = frappe.get_all('Shift Assignment',{'status':'Active','department':args.department,'start_date':args.ot_from_date},['*'])
    data = []
    for shift in shifts:
        row = [
            shift.employee,shift.employee_name,shift.overtime or '',shift.department,shift.employee_type or '',shift.designation or '',shift.employee_grade or '',shift.shift_type,shift.start_date
        ]
        data.append(row)    
    return data
    
@frappe.whitelist()
def writedata(w, data):
    for row in data:
        w.writerow(row)