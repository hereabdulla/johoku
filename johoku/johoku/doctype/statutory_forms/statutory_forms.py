# Copyright (c) 2022, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta,date
# from dateutil import relativedelta
import datetime
from frappe.utils import today,flt,add_days,date_diff,getdate,cint,formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname

class StatutoryForms(Document):
    
    @frappe.whitelist()
    def get_employees_form_5(self):
        datalist = []
        data = {}
        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
        employee = frappe.db.sql("""select name,employee_name,age,date_of_birth,gender from `tabEmployee` where status = 'Active' and date_of_joining between '%s' and '%s' """%(start_day_of_prev_month,last_day_of_prev_month),as_dict=1)
        if employee:
            # frappe.errprint(employee)
            for emp in employee:
                data.update({
                    'employee':emp['name'],
                    'employee_name':emp['employee_name'],
                    'age':emp['age'],
                    'date_of_birth':emp['date_of_birth'],
                    'gender':emp['gender']
                })
                datalist.append(data.copy())
                frappe.errprint(data)
        # frappe.errprint(datalist)
            return datalist
        
    @frappe.whitelist()
    def get_employees_form_10(self):
        datalist = []
        data = {}
        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
        employee = frappe.db.sql("""select name,employee_name,relieving_date,reason_for_leaving,feedback from `tabEmployee` where status = 'Left' and relieving_date between '%s' and '%s' """%(start_day_of_prev_month,last_day_of_prev_month),as_dict=1)
        if employee:
            frappe.errprint(employee)
            for emply in employee:
                data.update({
                    'employee':emply['name'],
                    'employee_name':emply['employee_name'],
                    'relieving_date':emply['relieving_date'],
                    'reason_for_leaving':emply['reason_for_leaving'],
                    'feedback':emply['feedback'],
                })
                datalist.append(data.copy())
                frappe.errprint(data)
            frappe.errprint(datalist)
            return datalist
    
    
    