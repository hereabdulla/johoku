from __future__ import unicode_literals
from csv import writer
from email import message
from inspect import getfile
from unicodedata import name
import frappe
from frappe.utils import cstr, add_days, date_diff, getdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file, upload
from frappe.model.document import Document
from datetime import datetime, timedelta, date, time
from frappe.utils import cint, today, flt, date_diff, add_days, add_months, date_diff, getdate, formatdate, cint, cstr
from numpy import unicode_


class OvertimePlan(Document):

    def on_submit(self): 
        if self.upload:
            self.create_overtime_list()
        else:
            frappe.throw(_('Please Attach the File'))    

    def create_overtime_list(self):
        filepath = get_file(self.upload)
        pps = read_csv_content(filepath[1])
        dates = self.get_dates(self.ot_from_date,self.ot_to_date)
        for date in dates:
            for pp in pps:
                if pp[0] == 'ID':
                    pass
                else: 
                    ol = frappe.db.exists("Overtime List",{'employee':pp[0],'ot_from_date':date,'ot_to_date':date,'docstatus':['in',[0,1]]})
                    if not ol:
                        doc = frappe.new_doc('Overtime List')
                        doc.employee = pp[0]
                        doc.ot_hours = pp[2]
                        doc.department = pp[3]
                        doc.shift = pp[4]
                        doc.ot_from_date = date
                        doc.ot_to_date = date
                        doc.overtime_plan = self.name
                        doc.save(ignore_permissions=True)
                        doc.submit()
                        frappe.db.commit()

    def get_dates(self,ot_from_date,ot_to_date):
        """get list of dates in between from date and to date"""
        no_of_days = date_diff(add_days(ot_to_date, 1),ot_from_date)
        dates = [add_days(ot_from_date, i) for i in range(0, no_of_days)]
        return dates

    @frappe.whitelist()
    def validate_employees(self):
        err_list = ""
        filepath = get_file(self.upload)
        pps = read_csv_content(filepath[1])
        dates = self.get_dates(self.ot_from_date,self.ot_to_date)
        shift_list = []
        for pp in pps:
            if pp[0] != ' Employee ':
                shift_list.append(pp[0])
        for pp in pps:
            if shift_list.count(pp[0]) > 1:
                err_list += '<li> Employee  - <font color="red"> %s</font> appears multiple times in the list. </li>' % pp[0]
        if err_list:
            return err_list
        for pp in pps:
            if pp[0] != ' Employee ':
                if pp[0]:
                    if not pp[1]:
                        err_list += '<li>Employe Name should not be Empty. </li>'
                    if not pp[2]:
                        err_list += '<li>Overtime should not be Empty. </li>'
                    if not pp[3]:
                        err_list += '<li>Department Code should not be Empty. </li>'
                    if not pp[4]:
                        err_list += '<li>Shift Type should not be Empty. </li>'
                    if not frappe.db.exists("Employee", {'name': pp[0], 'status': 'Active'}):
                        err_list += '<li><font color="red"><b>%s</b></font> is not an Active Employee. </li>' % (pp[0])
                    else:
                        if self.department != frappe.db.get_value("Employee", pp[0], "department"):
                            err_list += '<li><font color="red"><b>%s</b></font> doesnot belongs to <b>%s</b> department. </li>' % (pp[0], self.department)
                        else:
                            if pp[2]:
                                for date in dates:
                                    sa = frappe.db.exists('Overtime List', {'employee': pp[0], 'start_date': date, 'docstatus': ['!=', '2']})
                                    if sa:
                                        err_list += '<li>%s department have already allocated shift for <font color="red"><b>%s</b></font> for the date %s </li>' % (
                                            frappe.db.get_value("Overtime List", sa, "department"), pp[0], date)
                            else:
                                err_list += '<li>Overtime value missing for <font color="red"><b>%s</b></font> in the upload sheet.</li>' % (
                                    pp[0])
                else:
                    li = [pp[1], pp[2], pp[3], pp[4]]
                    if len(li) != 5:
                        err_list += '<li>Employee should not be Empty.</li>'
        return err_list

    @frappe.whitelist()
    def check(self):
        overtime_list = frappe.db.sql("""select name from `tabOvertime List` where department = '%s' and ot_from_date between '%s' and '%s' """ % (self.department, self.ot_from_date, self.ot_to_date), as_dict=1)
        if overtime_list:
            self.upload = ''
            return 'Overtime Plan already submitted for the selected date'

    @frappe.whitelist()
    def show_csv_data(self):
        filepath = get_file(self.upload)
        pps = read_csv_content(filepath[1])
        data_list = ''
        for pp in pps:
            if pp[0] == 'Employee':
                data_list += "<tr><td style='background-color:#1dbaba; border: 1px solid black'>%s</td><td style='background-color:#1dbaba; border: 1px solid black'>%s</td><td style='background-color:#1dbaba; border: 1px solid black'>%s</td><td style='background-color:#1dbaba; border: 1px solid black'>%s</td><td style='background-color:#1dbaba; border: 1px solid black'>%s</td></tr>" % (pp[0], pp[1], pp[2], pp[3], pp[4])
            else:
                data_list += "<tr><td style = 'border: 1px solid black'>%s</td><td style = 'border: 1px solid black'>%s</td><td style = 'border: 1px solid black'>%s</td><td style = 'border: 1px solid black'>%s</td><td style = 'border: 1px solid black'>%s</td></tr>" % (pp[0], pp[1], pp[2], pp[3], pp[4])
        return data_list

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
    w.writerow(['ID', 'Employee Name', 'Overtime Hours','Department', 'Shift Type'])
    return w

def add_data(w, args):
    data = get_data(args)
    writedata(w, data)
    return w

@frappe.whitelist()
def get_data(args):
    shifts = frappe.get_all('Shift Assignment', {'status': 'Active', 'department': args.department, 'start_date': args.ot_from_date}, ['*'])
    data = []
    for shift in shifts:
        row = [
            shift.employee, shift.employee_name, shift.default_overtime or '', shift.department, shift.shift_type
        ]
        data.append(row)
    return data

@frappe.whitelist()
def writedata(w, data):
    for row in data:
        w.writerow(row)

@frappe.whitelist()
def check_shift(dept,from_date,to_date):
    data = []
    message = ''
    shift = frappe.db.exists('Shift Assignment',{'start_date':('between',(from_date,to_date)),'department':dept})
    if shift:
        data.append('Shift Assigned')
    else:
        data.append('No Shift Assigned')
    return data
    
