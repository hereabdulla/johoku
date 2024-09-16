# -*- coding: utf-8 -*-
# Copyright (c) 2018, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from ast import Gt
from email import message
import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta,date
from frappe import _
from frappe.utils import today,flt,add_days,date_diff,getdate,cint,formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname
from frappe.utils import get_first_day, get_last_day, format_datetime,get_url_to_form

class LeaveApproverIdentityError(frappe.ValidationError): pass
class OverlapError(frappe.ValidationError): pass
class AttendanceAlreadyMarkedError(frappe.ValidationError): pass    

class OnDutyApplication(Document):

    def on_submit(self):
        if self.status == "Applied":
            frappe.throw(_("Only Applications with status 'Approved' and 'Rejected' can be submitted"))
        if self.workflow_state == "Approved":
            no_of_days = date_diff(add_days(self.to_date, 1),self.od_date )
            dates = [add_days(self.od_date, i) for i in range(0, no_of_days)]
            for emp in self.multi_employee:
                for date in dates:
                    att = frappe.db.exists("Attendance",{"attendance_date":date,"employee":emp.employee,"docstatus":["!=","2"]})
                    if att:
                        doc = frappe.get_doc("Attendance",att)
                        if doc.docstatus == 0:
                            doc.status = 'Present'
                            doc.on_duty_application = self.name
                            doc.save(ignore_permissions=True)
                            doc.submit()
                            frappe.db.commit()
                        elif doc.docstatus == 1:
                            doc.cancel()
                            doc = frappe.new_doc("Attendance")
                            doc.employee = emp.employee
                            doc.attendance_date = date
                            doc.status = 'Present'
                            doc.on_duty_application = self.name
                            doc.save(ignore_permissions=True)
                            doc.submit()
                            frappe.db.commit()

    # def before_save(self):
    #     current_date = today()
    #     previous_date = add_days(current_date,1)
    #     if previous_date:
    #         frappe.throw(_('On Duty Cannot be marked as Future Dates'))

    def after_insert(self):
        if self.workflow_state == 'Pending for HOD':
            table = ''
            link = get_url_to_form("On Duty Application", self.name)
            content="""<p>Dear Sir,<br>Kindly find the below On Duty Application from %s (%s).</p><br>"""%(self.employee,self.employee_name)
            for idx,emp in enumerate(self.multi_employee):
                header = """<table class=table table-bordered><tr><td style = 'border: 1px solid black'>Serial No</td><th colspan='7' style = 'border: 1px solid black;background-color:#ffedcc;'><center>On Duty Application</center></th><tr>"""
                table += """<tr><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Employee ID</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Employee Name</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Department</th><td style = 'border: 1px solid black'>%s</td></tr>
                """%(idx+1,emp.employee,emp.employee_name,emp.department)
            data = """ </table><br><table class=table table-bordered><th colspan='6' style = 'border: 1px solid black;background-color:#ffedcc;'><center>On Duty Application Details</center></th><tr>
            <tr><th style = 'border: 1px solid black'>From Date</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>To Date</th><td style = 'border: 1px solid black'>%s</td></tr>
            <tr><th style = 'border: 1px solid black'>From Time</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>To Time</th><td style = 'border: 1px solid black'>%s</td></tr>
            <tr><th style = 'border: 1px solid black'>Total Number of Days</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Session</th><td style = 'border: 1px solid black'>%s</td></tr>
            <tr><th colspan='4' style = 'border: 1px solid black;background-color:#ffedcc;'><center><a href='%s'>VIEW</a></center></th></tr>
            </table><br>"""%(format_datetime(self.od_date),format_datetime(self.to_date),format_datetime(self.from_time),format_datetime(self.to_time),self.total_number_of_days,self.session,link)
            regards = "Thanks & Regards,<br>HR"
            # frappe.sendmail(
            # recipients=[self.approver,'abdulla.pi@groupteampro.com'],
            # subject='Reg.On Duty Application Approval' ,
            # message = content+header+table+data+regards)
        
    @frappe.whitelist()
    def show_html(self):
        if self.vehicle_request:
            html = "<h2><center>ON DUTY APPLICATION WITH VEHICLE</center></h2><table class='table table-bordered'><tr><th>From Date</th><th>To Date</th></tr><tr><td><h2>%s</h2></td><td><h2>%s</h2></td></tr><tr><th>From Time</th><th>To Time</th></tr><tr><td><h2>%s</h2></td><td><h2>%s</h2></td></tr></table>"%(frappe.utils.format_date(self.od_date),frappe.utils.format_date(self.od_date),self.from_time,self.to_time)
        else:
            html = "<h2><center>ON DUTY APPLICATION</center></h2><table class='table table-bordered'><tr><th>From Date</th><th>To Date</th></tr><tr><td><h2>%s</h2></td><td><h2>%s</h2></td></tr><tr><th>From Time</th><th>To Time</th></tr><tr><td><h2>%s</h2></td><td><h2>%s</h2></td></tr></table>"%(frappe.utils.format_date(self.od_date),frappe.utils.format_date(self.od_date),self.from_time,self.to_time)
        return html

    @frappe.whitelist()
    def throw_overlap_error(self, d):
        msg = _("Employee {0} has already applied for {1} between {2} and {3}").format(self.employee,
            d['on_duty_type'], formatdate(d['od_date']), formatdate(d['to_date'])) \
            + """ <br><b><a href="#Form/On Duty Application/{0}">{0}</a></b>""".format(d["name"])
        frappe.throw(msg, OverlapError)
        leave_count_on_half_day_date = frappe.db.sql("""select count(name) from `tabOn Duty Application`
            where employee = %(employee)s
            and docstatus < 2
            and status in ("Open","Applied", "Approved")
            and half_day = 1
            and half_day_date = %(half_day_date)s
            and name != %(name)s""", {
                "employee": self.employee,
                "half_day_date": self.half_day_date,
                "name": self.name
            })[0][0]
        return leave_count_on_half_day_date * 0.5

    @frappe.whitelist()
    def get_ceo(self,department):
        ceo = frappe.db.get_value('Department',department,"ceo")
        return ceo
    
    @frappe.whitelist()
    def get_gm(self,department):
        gm = frappe.db.get_value('Department',department,"gm")
        return gm

    @frappe.whitelist()
    def get_hod(self,department):
        hod = frappe.db.get_value('Department',department,"hod")
        return hod

def validate_if_attendance_not_applicable(employee, attendance_date):
    # Check if attendance_date is a Holiday
    if is_holiday(employee, attendance_date):
        frappe.msgprint(_("Attendance not submitted for {0} as it is a Holiday.").format(attendance_date), alert=1)
        return True
    # Check if employee on Leave
    leave_record = frappe.db.sql("""select half_day from `tabLeave Application`
            where employee = %s and %s between od_date and to_date
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if leave_record:
        frappe.msgprint(_("Attendance not submitted for {0} as {1} on leave.").format(attendance_date, employee), alert=1)
        return True
    return False

def get_holiday_list_for_employee(employee, raise_exception=True):
    if employee:
        holiday_list, company = frappe.db.get_value("Employee", employee, ["holiday_list", "company"])
    else:
        holiday_list=''
        company=frappe.db.get_value("Global Defaults", None, "default_company")

    if not holiday_list:
        holiday_list = frappe.get_cached_value('Company',  company,  "default_holiday_list")

    if not holiday_list and raise_exception:
        frappe.throw(_('Please set a default Holiday List for Employee {0} or Company {1}').format(employee, company))
    return holiday_list

def is_holiday(employee, date=None):
    '''Returns True if given Employee has an holiday on the given date
    :param employee: Employee `name`
    :param date: Date to check. Will check for today if None'''
    holiday_list = get_holiday_list_for_employee(employee)
    if not date:
        date = today()
    if holiday_list:
        return frappe.get_all('Holiday List', dict(name=holiday_list, holiday_date=date)) and True or False

@frappe.whitelist()
def get_number_of_leave_days(employee, od_date, to_date,session=None,  to_date_session=None, date_dif=None):
    number_of_days = 0
    if od_date == to_date:
        if session != 'Full Day':
            number_of_days = 0.5
        else:
            number_of_days = 1
    else:
        if session == "Full Day" and to_date_session == "Full Day":
            number_of_days = flt(date_dif)
        if session == "Full Day" and to_date_session == "First Half":
            number_of_days = flt(date_dif) - 0.5
        if session == "Second Half" and to_date_session == "Full Day":
            number_of_days = flt(date_dif) - 0.5
        if session == "Second Half" and to_date_session == "First Half":
            number_of_days = flt(date_dif) - 1
    return number_of_days

@frappe.whitelist()
def check_attendance(employee, od_date, to_date):
    if employee:
        attendance = frappe.db.sql("""select status,attendance_date from `tabAttendance`
                    where employee = %s and attendance_date between %s and %s
                    and docstatus = 1""", (employee, od_date, to_date), as_dict=True)
        return attendance

@frappe.whitelist()
def validate_cutoff(od_date):
    cur_mon = datetime.strptime(today(), "%Y-%m-%d").strftime("%B")
    frappe.errprint(cur_mon)
    c = frappe.get_value("Application Cut Off Date",{'month':cur_mon},['cut_off_date','od_date','to_date'])
    curday = date.today()
    fromdate = datetime.strptime(str(od_date),"%Y-%m-%d").date()
    if fromdate < c[1]:
        return 'Expired'
    if fromdate > c[1] and fromdate < c[2]:
        frappe.errprint('true')

@frappe.whitelist()
def get_employees():
    # frappe.error_log(frappe.session.user)
    data = []
    employee_id = frappe.db.get_value('Employee',{'status':'Active','user_id':frappe.session.user},["name", "employee_name", "department", "designation"])
    data.append(employee_id[0])
    data.append(employee_id[1])
    data.append(employee_id[2])
    data.append(employee_id[3])    
    return data

@frappe.whitelist()
def get_time(shift,session):
    datalist = []
    data = {}
    if shift == '1':
        get_session_st_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        get_session_ed_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if session == 'Full Day':
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':get_session_ed_time    
            })
            datalist.append(data.copy())
        elif session == 'First Half' :
            gt = get_session_st_time + timedelta(hours=4,minutes=25)
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':gt
            })
            datalist.append(data.copy())
        elif session == 'Second Half' :
            gc =  get_session_ed_time - timedelta(hours=4,minutes=25)
            data.update({
                'get_session_st_time':gc,
                'get_session_ed_time':get_session_ed_time
            })
            datalist.append(data.copy()) 
    elif shift == '2':
        get_session_st_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        get_session_ed_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if session == 'Full Day':
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':get_session_ed_time    
            })
            datalist.append(data.copy())
        elif session == 'First Half' :
            gt = get_session_st_time + timedelta(hours=4,minutes=25)
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':gt
            })
            datalist.append(data.copy())
        elif session == 'Second Half' :
            gc =  get_session_st_time + timedelta(hours=4,minutes=25)
            data.update({
                'get_session_st_time':gc,
                'get_session_ed_time':get_session_ed_time
            })
            datalist.append(data.copy())     
    else: 
        get_session_st_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        get_session_ed_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if session == 'Full Day':
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':get_session_ed_time,    
            })
            datalist.append(data.copy())
        elif session == 'First Half' :
            gt = get_session_st_time + timedelta(hours=3,minutes=10) 
            data.update({
                'get_session_st_time':get_session_st_time,
                'get_session_ed_time':gt
            })
            datalist.append(data.copy())
        elif session == 'Second Half' :
            gc = get_session_ed_time - timedelta(hours=3,minutes=10)
            data.update({
                'get_session_st_time':gc,
                'get_session_ed_time':get_session_ed_time
            })
            datalist.append(data.copy())   
    return datalist