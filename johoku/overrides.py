from datetime import datetime
from email import message
import frappe
from frappe.frappeclient import FrappeException
from frappe.utils.data import add_days, date_diff
from hrms.hr.doctype.employee_checkin.employee_checkin import EmployeeCheckin
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
from hrms.hr.doctype.leave_allocation.leave_allocation import LeaveAllocation
from erpnext.setup.doctype.employee.employee import Employee
from hrms.hr.doctype.compensatory_leave_request.compensatory_leave_request import CompensatoryLeaveRequest
from datetime import date
from frappe import _
from hrms.hr.utils import throw_overlap_error


@frappe.whitelist()
def get_employee():
    emp_details = frappe.db.get_value('Employee',{'user_id':frappe.session.user},['user_id'])
    return emp_details

#Employee Checkin
class CustomEmployeeCheckin(EmployeeCheckin):
    def after_save(self):
        get_date = datetime.strptime(str(self.time),'%Y-%m-%d %H:%M:%S').date()
        self.checkin_log_date = get_date 

#Leave Application
class CustomLeaveApplication(LeaveApplication):
    # def before_save(self):
    #     if self.leave_type == 'Casual Leave':
    #         yesterday = add_days(self.from_date,-1)
    #         before_leave = frappe.db.exists('Leave Application',{'employee':self.employee,'from_date':yesterday,'leave_type':'Sick Leave','docstatus':('!=','2')})
    #         if before_leave:
    #             frappe.throw(_('Casual Leave Cannot be Applied After Sick Leave'))
    #         else:
    #             message = ('Casual Leave cannot be applied before Sick Levae')    
    #             frappe.log_error('Casual Leave',message)  

    #     elif self.leave_type == 'Sick Leave':
    #         yesterday = add_days(self.from_date,-1)
    #         before_leave = frappe.db.exists('Leave Application',{'employee':self.employee,'from_date':yesterday,'leave_type':'Casual Leave','docstatus':('!=','2')})
    #         if before_leave:
    #             frappe.throw(_('Sick Leave Cannot be Applied After Casual Leave'))
    #         else:
    #             message = ('Sick Leave can be applied before Earned Leave and not Casual Leave')    
    #             frappe.log_error('Sick Leave',message)  

    #     elif self.leave_type == 'Earned Leave':
    #         yesterday = add_days(self.from_date,-1)
    #         before_leave = frappe.db.exists('Leave Application',{'employee':self.employee,'from_date':yesterday,'leave_type':'Casual Leave','docstatus':('!=','2')})
    #         if before_leave:
    #             frappe.throw(_('Earned Leave Cannot be Applied After Casual Leave'))
    #         else:
    #             message = ('Earned Leave can be applied before Sick Leave and not Casual Leave')    
    #             frappe.log_error('Earned Leave',message)         

    #     self.notice_period_leave()   
    #     self.leave_type_validation()     

    def notice_period_leave(self):
        employee = frappe.db.get_value('Employee',{'status':'Active','employee':self.employee},['resignation_letter_date'])
        if employee:
            if self.leave_type == 'Casual Leave' or self.leave_type == 'Earned Leave':
                frappe.throw(_('Employee %s %s cannot be availed during the Notice period'%(self.employee,self.leave_type)))
            else:
                message = ('Employee %s to check only Casual and Earned Leave'%(self.employee))
                frappe.log_error('Leave Applcation',message)      
        else:
            message = ('Employee %s has no Resignation Letter Date'%(self.employee))
            frappe.log_error('Notice Period Leave Apply',message) 
            
    def leave_type_validation(self):
        if self.employee:
            if self.leave_type == 'Maternity Leave':
                emp = frappe.db.get_value('Employee',{'status':'Active','name':self.employee},['gender'])
                if emp == 'Male':
                    frappe.throw(_('%s type only allowed for female employees'%(self.leave_type)))
                    
class CustomCompensatoryLeaveRequest(CompensatoryLeaveRequest):
    def before_save(self):
        self.validation_total_hours()
        avail_days = date_diff(self.posting_date,self.work_from_date)
        if avail_days > 30 :
            frappe.throw(_('%s Leave Request cannot be Applied After 30 Days'%(self.leave_type)))
        else:
            message = ('Leave Applied Less than 30 Days')
            frappe.log_error('%s Leave Type'%(self.leave_type),message)  

    def validation_total_hours(self):
        att = frappe.db.get_value('Attendance',{'employee':self.employee,'attendance_date':self.work_from_date,'docstatus':('!=','2')},['total_working_hours'])
        if att < 6:
            frappe.throw(_('Employee %s Working Hours Should be Greater than 6 Hours'%(self.employee)))
        else:
            message = ('Employee %s Working Hours Greater than 6'%(self.employee)) 
            frappe.log_error('Compensatory Leave Request',message)  
             
class CustomEmployee(Employee):
    def before_save(self):
        print("HI")
        # if self.grade != 'G-1':
        #     if self.ctc_amount:
        #         spl_allow = self.basic + self.house_rent_allowance + self.conveyance_allowance + self.education_allowance + self.food_allowance + self.attire_allowance + self.mobile_allowance + self.medical_allowance 
        #         overall_amount = spl_allow + self.pf_amount
        #         self.special_allowance = self.ctc_amount - overall_amount
        #         self.fixed_earning = spl_allow + self.special_allowance

class CustomLeaveAllocation(LeaveAllocation):
    def before_save(self):
        if self.employee:
            if self.leave_type == 'Maternity Leave':
                emp = frappe.db.get_value('Employee',{'status':'Active','name':self.employee},['gender'])
                if emp == 'Male':
                    frappe.throw(_('%s type only allowed for female employees'%(self.leave_type)))
                            
        
   

