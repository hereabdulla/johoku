# Copyright (c) 2022, TEAMPRO and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
from itertools import count
from pickle import FALSE
from stat import FILE_ATTRIBUTE_REPARSE_POINT
import frappe
from frappe.model.document import Document
from frappe.model.document import Document
from datetime import datetime, timedelta, date, time
from frappe.utils import get_first_day, get_last_day, format_datetime, get_url_to_form
from frappe import msgprint


class PermissionRequest(Document):

    def validate(self):
        if self.docstatus == 0:
            month_start = get_first_day(self.permission_date)
            month_end = get_last_day(self.permission_date)

            # count = frappe.db.count("Permission Request",{"employee_id":self.employee_id,"permission_date":self.permission_date})
            # if count >= 1:
            # 	frappe.throw("Only 1 permission are allowed for a day")
                
            # monthly_permission_count = frappe.db.count("Permission Request",{"employee_id":self.employee_id,"permission_date": ('between',(month_start,month_end)) }) 
            # if monthly_permission_count >=2:
            # 	frappe.throw("Only 2 permissions are allowed for a month")

            # per_exists = frappe.db.exists('Permission Request',{'employee_id':self.employee_id,"permission_date": ('between',(month_start,month_end))})    
            # if per_exists:
            # 	per_count = frappe.db.get_value('Permission Request',{'name':per_exists},['permission_hour'])
            # 	hours = int(per_count) + int(self.permission_hour)
            # 	if hours > 2:
            # 		frappe.throw("Only 2 Hours permissions are allowed for a month")
            # 	else:
            # 		message = ('Employee %s Permission Count Less than 2 Hours'%(self.employee_id))    
            # 		frappe.error_log('Permission Request',message)
            # else:
            # 	message = ('Employee %s Permission Request is not there')        
            # 	frappe.log_error('Permission Request',message)
                              
    # if count[0].count >= 1:
    # 	    # frappe.errprint('today')
    #     frappe.throw("Only 1 permission are allowed for a day")
    #     # count = frappe.db.sql("select count(*) as count from `tabPermission Request` where employee_id = '%s' and permission_date between '%s' and '%s' and employee_name != '%s' and workflow_state != 'Rejected' "%(self.employee_id, month_start, month_end, self.employee_name), as_dict=True)
    #     if count[0].count >= 2:
    #         frappe.throw("Only 2 permissions are allowed for a month")

@frappe.whitelist()
def get_employee_approver(dept):
    get_approver = frappe.db.get_value('Department', {'name': dept}, ['hod'])
    return get_approver

@frappe.whitelist()
def get_endtime1(shift,session,per_hour):
    datalist = []
    data = {}
    if session == 'First Half':
        get_shift_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
        if per_hour == '1':
            one_hour = timedelta(hours=1) + get_shift_time
            data.update({
                'get_shift_time':get_shift_time,
                'one_hour':one_hour
            })
            datalist.append(data.copy())
        elif per_hour == '2':
            two_hour = timedelta(hours=2) + get_shift_time     
            data.update({
                'get_shift_time':get_shift_time,
                'two_hour':two_hour
            })
            datalist.append(data.copy())   
        # else:
        # 	frappe.throw("Not Allowed for 1.5 Hours Permission")   
    elif session == 'Second Half':
        get_shift_time = frappe.db.get_value('Shift Type',{'name':shift},['end_time'])
        if per_hour == '1':
            one_hour = get_shift_time - timedelta(hours=1) 
            data.update({
                'get_shift_time':one_hour,
                'one_hour':get_shift_time
            })
            datalist.append(data.copy())
        elif per_hour == '2':
            # shift_type = frappe.db.get_value('Shift Type',{'name':shift},['name'])
            if shift == "2":
                get_shift_time_str =str(get_shift_time)
                get_shift_time_new = datetime.strptime(get_shift_time_str, "%H:%M:%S")
                two_hour_time = get_shift_time_new - timedelta(hours=2)
                two_hour = two_hour_time.time()  
                data.update({
                'get_shift_time':two_hour,
                'two_hour':get_shift_time })
            else:
                two_hour = get_shift_time - timedelta(hours=2)   
                data.update({
                'get_shift_time':two_hour,
                'two_hour':get_shift_time
            })
            datalist.append(data.copy())
        # else:
        # 	frappe.throw("Not Allowed for 1.5 Hours Permission")                 
    return datalist        

#         shift = frappe.db.get_value('Shift Type', {'name': shift}, ['start_time'])
#         str_time = datetime.strptime(shift, '%H:%M:%S')

# @frappe.whitelist()
# def get_endtime1(Self, start_time):
#         time = datetime.strptime(start_time, "%H:%M:%S")
#         end_time = timedelta(hours=2) + time
#         return str(end_time.time())

# @frappe.whitelist()
# def get_endtime2(Self, end_time):
#         time = datetime.strptime(end_time, "%H:%M:%S")
#         start_time = time - timedelta(hours=2)
#         return str(start_time.time())

# @frappe.whitelist()
# def get_ceo(self):
#     	ceo = frappe.db.get_value('Department',self.department,"ceo")
#     	return ceo

# @frappe.whitelist()
#     def get_gm(self):
#     	gm = frappe.db.get_value('Department',self.department,"gm")
#     	return gm

@frappe.whitelist()
def get_hod(self):
        hod = frappe.db.get_value('Department', self.department, "hod")
        return hod

def after_insert(self):
        if self.workflow_state == 'Pending for HOD':
            link = get_url_to_form("Permission Request", self.name)
            content = """<p>Dear Sir,</p>
            Kindly find the below Permission Request from %s (%s).<br>""" % (self.employee_id, self.employee_name)
            table = """<table class=table table-bordered><tr><th colspan='4' style = 'border: 1px solid black;background-color:#ffedcc;'><center>PERMISSION REQUEST</center></th><tr>
            <tr><th style = 'border: 1px solid black'>Employee ID</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Department</th><td style = 'border: 1px solid black'>%s</td></tr>
            <tr><th style = 'border: 1px solid black'>Employee Name</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Designation</th><td style = 'border: 1px solid black'>%s</td></tr>
            <tr><th style = 'border: 1px solid black'>Permission Date</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Session</th><td style = 'border: 1px solid black'>%s</td></tr>
            <tr><th style = 'border: 1px solid black'>Shift</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>From Time</th><td style = 'border: 1px solid black'>%s</td></tr>
            <tr><th rowspan='2' style = 'border: 1px solid black'>Reason</th><td rowspan='2' style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>To Time</th><td style = 'border: 1px solid black'>%s</td></tr>
            <tr><th style = 'border: 1px solid black'>Hours</th><td style = 'border: 1px solid black'>%s</td></tr>
            <tr><th colspan='4' style = 'border: 1px solid black;background-color:#ffedcc;'><center><a href='%s'>VIEW</a></center></th></tr>
            </table><br>"""%(self.employee_id, self.department, self.employee_name, self.designation, format_datetime(self.permission_date),self.session,self.shift,self.from_time,self.reason,self.to_time,self.hours,link)
            regards = "Thanks & Regards,<br>HR"
            # frappe.sendmail(
            # recipients=[self.permission_approver,'abdulla.pi@groupteampro.com'],
            # subject='Reg.Permission Request Approval' ,
            # message = content+table+regards)


@frappe.whitelist()
def get_shift_assignment(employee_id, start_date):
    shift_assignment = frappe.get_all(
        "Shift Assignment",
        filters={
            "employee": employee_id,
            "start_date": start_date,
            "docstatus" :1
        },
        fields=["shift_type"],
        limit=1
    )

    if shift_assignment:
        return {"shift_type": shift_assignment[0].shift_type}

    return {}