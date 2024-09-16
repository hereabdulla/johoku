# Copyright (c) 2022, TEAMPRO and contributors
# For license information, please see license.txt
import fractions
from frappe.model.document import Document
import frappe
import datetime
from datetime import date, datetime,time
from frappe.utils import add_days,today
import datetime as dt
import pandas as pd
from frappe.utils import (
	add_days,
	add_to_date,
	cint,
	flt,
	get_datetime,
	get_link_to_form,
	get_time,
	getdate,
	time_diff,
	time_diff_in_hours,
	time_diff_in_seconds,
)


class OvertimeRequest(Document):

# @frappe.whitelist()
# def get_employee_code(user):
#     employee = frappe.db.get_value('Employee', {'user_id': user}, "name")
#     return employee

    @frappe.whitelist()
    def roundoff_time(time):
            time = datetime.strptime(time, '%H:%M:%S')
            if time.minute not in (0, 30):
                if time.minute < 30:
                    roundoff_time = time.replace(minute=0)
                elif time.minute >= 30:
                    roundoff_time = time.replace(minute=30)
                roundoff_time = roundoff_time.time()
                return str(roundoff_time)

    @frappe.whitelist()
    def check_holiday(self):
        data = []
        if self.ot_date:
            holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
            left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = 'Johoku Holiday List 2022' and holiday_date = '%s' """%(self.ot_date),as_dict=True)
            if holiday:
                 data.append('Yes')
            else:
                data.append('No')
        return data    

@frappe.whitelist()
def get_att_bio_checkin(emp,ot_date):
    datalist = []
    data = {}
    if frappe.db.exists('Attendance',{'employee':emp,'attendance_date':ot_date}):
        attendance = frappe.get_all('Attendance',{'employee':emp,'attendance_date':ot_date},['*'])
        for att in attendance:
            if att.in_time and att.out_time:
                bio_in = att.in_time
                bio_out = att.out_time
                total_wh = att.working_total_hours
                shift = att.shift
                ot_hours = att.over_time_hours
                data.update({
                    'bio_in':bio_in,
                    'bio_out':bio_out,
                    'total_wh':total_wh,
                    'shift':shift,
                    'ot_hours':ot_hours
                })
                datalist.append(data.copy())
            else:
                data.update({
                    'bio_in':'',
                    'bio_out':'',
                    'total_wh':'',
                    'shift':'',
                    'ot_hours':''
                })
                datalist.append(data.copy())
                frappe.msgprint('Overtime Cannot be applied without Biometric In time and Out time')
    else:
        data.update({
            'bio_in':'',
            'bio_out':'',
            'total_wh':'',
            'shift':'',
            'ot_hours':''
        })
        datalist.append(data.copy())
        frappe.msgprint('Overtime Cannot be applied without Attendance')
    return datalist    
       
@frappe.whitelist()
def get_time(emp,ot_date,shift):
    datalist = []
    data = {}
    attendance = frappe.db.get_all('Attendance',{'employee':emp,'attendance_date':ot_date},['*'])
    for att in attendance:
        if att.shift == shift:
            if att.in_time:
                in_time = datetime.strptime(str(att.in_time),'%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
                data.update({
                    'in_time':in_time
                })
                datalist.append(data.copy())
                if att.out_time:
                    out_time = datetime.strptime(str(att.out_time),'%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
                    data.update({
                        'out_time':out_time
                    })
                    datalist.append(data.copy())
                else:
                    data.update({
                        'out_time':''
                    })
                    datalist.append(data.copy())
                    frappe.msgprint('Employee has no Out Time')
            else:
                data.update({
                    'in_time':''
                })
                datalist.append(data.copy())
                frappe.msgprint('Employee has no Out Time')
        else:
            data.update({
                'in_time':'',
                'out_time':''
            })
            datalist.append(data.copy())
            frappe.msgprint('Employee could Apply for the same Shift')
        return datalist    

# @frappe.whitelist()
# def ot_calculation(ot_date,shift,from_time,to_time,ot_hours,employee_grade):
#     ot_date = datetime.strptime(ot_date, "%Y-%m-%d").date()
#     from_time = datetime.strptime(from_time, "%H:%M:%S").time()
#     to_time = datetime.strptime(to_time, "%H:%M:%S").time()
#     if shift == '3':
#         ot_date = add_days(ot_date,1)
#         from_datetime = datetime.combine(ot_date,from_time)
#         to_datetime = datetime.combine(ot_date,to_time)
#     elif shift == '2':
#         if to_time > time(16,40,0):
#             from_datetime = datetime.combine(ot_date,from_time)
#             to_datetime = datetime.combine(ot_date,to_time)
#         else:
#             from_datetime = datetime.combine(ot_date,from_time)
#             ot_date = add_days(ot_date,1)
#             to_datetime = datetime.combine(ot_date,to_time)
#     else:
#         from_datetime = datetime.combine(ot_date,from_time)
#         to_datetime = datetime.combine(ot_date,to_time)
#     if from_datetime > to_datetime:
#         frappe.throw('From Time should be lesser that To Time')

@frappe.whitelist()
def overtime_grade(ot_date,shift,from_time,to_time,employee_grade,ot_hours,emp):
    data = []
    if ot_date:
        holiday = check_holiday(ot_date,emp)
        if holiday:
            if holiday == 'WW':
                if employee_grade == 'G-0':
                    grade_g0 = 'Double Wages'
                    data.append(grade_g0)
                elif employee_grade in ['MG-0','MG-1','MG-2','MG-3']:
                    grade_mg_1_to_3 = 'Double Wages'  
                    data.append(grade_mg_1_to_3) 
                elif employee_grade in ['MG-4','MG-5','MG-6','MG-7','MG-8','MG-9','MG-10','MG-11']:
                    grade_mg_4_to_11 = 'Compensatory Off'
                    data.append(grade_mg_4_to_11) 
            elif holiday == 'HH':
                if employee_grade == 'G-0':
                    grade_g0 = 'Double Wages + Compensatory Off or Triple Wages'   
                    data.append(grade_g0) 
                elif employee_grade in ['MG-0','MG-1','MG-2','MG-3']:
                    grade_mg_1_to_3 = 'Double Wages + Compensatory Off'
                    data.append(grade_mg_1_to_3) 
                elif employee_grade in ['MG-4','MG-5','MG-6','MG-7','MG-8','MG-9','MG-10','MG-11']:
                    grade_mg_4_to_11 = 'Compensatory Off' 
                    data.append(grade_mg_4_to_11) 
            else:
                message = ('No Holiday') 
                frappe.log_error('Holiday List Condition',message)       
        else:
            if shift == '1':
                shift_time = frappe.db.get_value('Shift Type',{'name':shift},['start_time'])
                shift_start_time = pd.to_datetime(str(shift_time)).time()
                ot_date_str = datetime.strptime(str(ot_date),'%Y-%m-%d').date()
                shift_start_datetime = datetime.combine(ot_date_str,shift_start_time)
                att_in_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':ot_date},['in_time'])
                total_hours = shift_start_datetime - att_in_time
                ftr = [3600,60,1]
                hr = sum([a*b for a,b in zip(ftr, map(int,str(total_hours).split(':')))])
                wh = round(hr/3600,1)
                if wh >= 2 :
                    if employee_grade == 'G-0':
                        grade_g0 = 'Double Wages'
                        data.append(grade_g0)
                    elif employee_grade in ['MG-0','MG-1','MG-2','MG-3']:
                        grade_mg_1_to_3 = 'Double Wages'  
                        data.append(grade_mg_1_to_3) 
                    else:
                        grade_nil = 'NIL'      
                        data.append(grade_nil) 
                elif frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':ot_date},['over_time_hours']) >=2 :
                    if employee_grade == 'G-0':
                        grade_g0 = 'Double Wages'
                        data.append(grade_g0)
                    elif employee_grade in ['MG-0','MG-1','MG-2','MG-3']:
                        grade_mg_1_to_3 = '200 Rupees Allowance'  
                        data.append(grade_mg_1_to_3)   
                    else:
                        grade_nil = 'NIL'      
                        data.append(grade_nil)      
            elif shift == '2':
                if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':ot_date},['over_time_hours']) >=2 :
                    if employee_grade == 'G-0':
                        grade_g0 = 'Double Wages'
                        data.append(grade_g0)
                    elif employee_grade in ['MG-0','MG-1','MG-2','MG-3']:
                        grade_mg_1_to_3 = 'Double Wages'  
                        data.append(grade_mg_1_to_3) 
                    else:
                        grade_nil = 'NIL'      
                        data.append(grade_nil)    
            else:
                message = ('Shift Based Overtime closed')
                frappe.log_error('Overtime Request',message)
            if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':ot_date},['over_time_hours']) >=3 :
                if shift != '3':
                    if employee_grade == 'G-0':
                        grade_g0 = 'Double Wages'
                        data.append(grade_g0)
                    elif employee_grade in ['MG-0','MG-1','MG-2','MG-3']:
                        grade_mg_1_to_3 = 'Double Wages'  
                        data.append(grade_mg_1_to_3)    
                    elif frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':ot_date},['over_time_hours']) >=4 and frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':ot_date},['over_time_hours']) <8 :
                        if employee_grade in ['MG-4','MG-5','MG-6','MG-7','MG-8','MG-9','MG-10','MG-11']:
                            grade_mg_4_to_11 = 'Half Day Compensatory Off' 
                            data.append(grade_mg_4_to_11) 
                        else:
                            message = ('Grade over less than MG-11')
                            frappe.log_error('Overtime Request',message)
                    elif frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':ot_date},['over_time_hours']) >=8:
                        if employee_grade in ['MG-4','MG-5','MG-6','MG-7','MG-8','MG-9','MG-10','MG-11']:
                            grade_mg_4_to_11 = 'Full Day Compensatory Off' 
                            data.append(grade_mg_4_to_11) 
                        else:
                            message = ('Grade over less than MG-11')
                            frappe.log_error('Overtime Request',message)   
            else:
                message = ('Overtime Hours lesser than 3 is not run')
                frappe.log_error('Overtime Request',message) 
    # return data   
    return ", ".join(data) if data else "NIL"             
           
@frappe.whitelist()    
def check_holiday(date,emp):
    holiday_list = frappe.db.get_value('Employee',emp,'holiday_list')
    holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
    left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
    if holiday:
        if holiday[0].weekly_off == 1:
            return "WW"
        else:
            return "HH"