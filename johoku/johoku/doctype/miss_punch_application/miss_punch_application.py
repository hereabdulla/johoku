# Copyright (c) 2022, teampro and contributors
# For license information, please see license.txt
from re import S
from time import strftime, strptime
import frappe
import math
import pandas as pd
from frappe.model.document import Document
import frappe,os,base64
import requests
import datetime
import json,calendar
from datetime import datetime,timedelta,date,time
import datetime as dt
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe.desk.notifications import delete_notification_count_for
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today,get_datetime
from frappe import _


class MissPunchApplication(Document):

    def on_submit(self):
        total_working_hr = self.validate()
        total_working_hours = total_working_hr[0]['working_hours']
        total_wh = self.validate()
        total_work_hours = total_wh[0]['wh']
        extra_hours = self.validate()
        extra_hr = extra_hours[0]['extra_hours']
        ot_hours = self.validate()
        ot_hr = ot_hours[0]['overtime_hours']
        att = frappe.get_doc('Attendance',self.attendance_marked)
        att.status = 'Present'
        att.in_time = self.in_time
        att.out_time = self.out_time
        att.working_total_hours = total_working_hours
        att.total_working_hours = total_work_hours
        att.extra_hours = extra_hr
        att.over_time_hours = ot_hr
        att.miss_punch = self.name
        att.save(ignore_permissions=True)
        frappe.db.commit()
              
    def validate(self):
        datalist = []
        data = {}
        in_time = datetime.strptime(str(self.in_time),'%Y-%m-%d %H:%M:%S')
        out_time = datetime.strptime(str(self.out_time),'%Y-%m-%d %H:%M:%S')
        working_hours = out_time - in_time
        ftr = [3600,60,1]
        hr = sum([a*b for a,b in zip(ftr, map(int,str(working_hours).split(':')))])
        wh = round(hr/3600,1)
        shift_end_time = frappe.db.get_value('Shift Type',self.shift,'end_time')
        shift_end_time = pd.to_datetime(str(shift_end_time)).time() 
        get_date_time = get_datetime(self.out_time)
        get_date = get_date_time.date()
        shift_end_datetime = datetime.combine(get_date,shift_end_time)
        get_shift_hours = frappe.db.get_value('Shift Type',{'name':self.shift},['total_shift_hours'])
        total_shift_hours = (get_datetime(get_shift_hours)).time()
        total_working_hours = datetime.strptime(str(working_hours),'%H:%M:%S').time()
        if shift_end_datetime:
            extra_hours = pd.to_datetime('00:00:00').time()  
            overtime_hours = 0 
            if get_date_time > shift_end_datetime:
                if total_working_hours > total_shift_hours:
                    extra_hours = get_date_time - shift_end_datetime
                    hr = sum([a*b for a,b in zip(ftr, map(int,str(extra_hours).split(':')))])
                    extras = round(hr/3600,1)
                    if extras > 1:
                        overtime_hours = math.floor(extras * 2) / 2
        data.update({
            'working_hours':working_hours,
            'wh':wh,
            'extra_hours':extra_hours,
            'overtime_hours':overtime_hours  
        })   
        datalist.append(data.copy())         
        return datalist    
    
    def on_cancel(self):
        att = frappe.db.exists('Attendance',{'attendance_date':self.date,'employee':self.employee})
        if att:
            frappe.db.set_value('Attendance',att,'miss_punch','')             
                    
                
                
        
    
    
    
       