from __future__ import print_function
from pickle import TRUE
from time import strptime
from traceback import print_tb
import frappe
from frappe.utils.data import ceil, get_time, get_year_start
import pandas as pd
import json
import datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours
import requests
from datetime import date, timedelta,time
from frappe.utils import get_url_to_form
import math
import dateutil.relativedelta

status_map = {    
	"Earned Leave": "EL",
	"Casual Leaave": "CL",
	"Sick Leave": "SL",
	"Privilege Leave": "PL",
	"Leave Without Pay": "LWP",
	"Medical Leave": "MdL",
	"Maternity Leave": "MaL",
	"Compensatory Off": "CO",
	}

def mark_att_aug():
	# from_date = add_days(today(),-1)  
	# to_date = today()
	from_date = '2024-08-13'
	to_date = '2024-08-13'
	checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where skip_auto_attendance = 0 and date(time) between '%s' and '%s' order by time  """%(from_date,to_date),as_dict=True)
	for c in checkins:
		employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
		if employee:
			mark_attendance_from_checkin(c.name,c.employee,c.time,c.log_type)
	mark_absent(from_date,to_date)
	mark_wh_ot(from_date,to_date)   
	get_ot_compensation(from_date,to_date)   
	att_shift_status(from_date,to_date)
	assigned_shift(from_date,to_date) 
	shift_matched(from_date,to_date)
	return "ok" 

def mark_att():
	from_date = add_days(today(),-1)  
	to_date = today()
	# from_date = '2023-10-31'
	# to_date = '2023-11-06'
	checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where skip_auto_attendance = 0 and date(time) between '%s' and '%s' order by time  """%(from_date,to_date),as_dict=True)
	for c in checkins:
		employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
		if employee:
			mark_attendance_from_checkin(c.name,c.employee,c.time,c.log_type)
	mark_absent(from_date,to_date)
	mark_wh_ot(from_date,to_date)   
	get_ot_compensation(from_date,to_date)   
	att_shift_status(from_date,to_date)
	assigned_shift(from_date,to_date) 
	shift_matched(from_date,to_date)
	mark_att_present(from_date,to_date)
	return "ok" 
	
def mark_attendance_from_checkin(checkin,employee,time,log_type):
	att_date = time.date()
	att_time = time.time()
	shift = ''
	if log_type == 'IN':
		min_in_time = ''
		max_in_time = ''
		min_in_time1 = datetime.strptime('07:00', '%H:%M').time()
		max_in_time1 = datetime.strptime('13:00', '%H:%M').time()
		min_in_time2 = datetime.strptime('13:00', '%H:%M').time()
		max_in_time2 = datetime.strptime('19:00', '%H:%M').time()
		min_in_time3 = datetime.strptime('01:00', '%H:%M').time()
		max_in_time3 = datetime.strptime('05:00', '%H:%M').time()
		if max_in_time1 >= att_time >= min_in_time1:
			shift = '1'
			min_in_time = datetime.strptime('07:00', '%H:%M').time()
			max_in_time = datetime.strptime('13:00', '%H:%M').time()
		elif max_in_time2 >= att_time >= min_in_time2:
			shift = '2' 
			min_in_time = datetime.strptime('13:00', '%H:%M').time()
			max_in_time = datetime.strptime('19:00', '%H:%M').time()
		elif max_in_time3 > att_time >= min_in_time3:
			shift = '3'  
			min_in_time = datetime.strptime('01:00', '%H:%M').time()
			max_in_time = datetime.strptime('05:00', '%H:%M').time()  
			add_date = add_days(att_date,-1)
		if min_in_time and max_in_time:
			att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
			if not att:
				if shift != '3':
					checkins = frappe.db.sql(""" select name,time from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and time(time) between '%s' and '%s'  order by time """%(employee,att_date,min_in_time,max_in_time),as_dict=True)
				else:
					yesterday = add_days(att_date,1) 
					checkins = frappe.db.sql(""" select name,time from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and time(time) between '%s' and '%s' order by time """%(employee,yesterday,min_in_time,max_in_time),as_dict=True)
				if checkins:
					try:
						if not frappe.db.exists('Restriction',{'employee':employee,'restricted_date':att_date,'docstatus':1}):
							att = frappe.new_doc("Attendance")
							att.employee = employee
							att.attendance_date = att_date
							att.shift = shift
							att.status = 'Absent'
							att.in_time = checkins[0].time
							att.working_total_hours = '00:00'
							att.extra_hours = '00:00'
							att.save(ignore_permissions=True)
							frappe.db.commit()
							frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
							frappe.db.set_value('Employee Checkin',checkins[0].name,'attendance',att.name)
							return att
					except:
						frappe.log_error(title="Restriction",message="Please Check Restriction on %s that Employee %s"%(att_date,employee))    
			else:
				if shift != '3':
					checkins = frappe.db.sql("select name,time from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and time(time) between '%s' and '%s' order by time "%(employee,att_date,min_in_time,max_in_time),as_dict=True)
				else:
					yesterday = add_days(att_date,1)
					checkins = frappe.db.sql("select name,time from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and time(time) between '%s' and '%s' order by time "%(employee,yesterday,min_in_time,max_in_time),as_dict=True)
				if checkins:
					att = frappe.get_doc("Attendance",att)
					if att.docstatus == 0:
						att.employee = employee
						att.attendance_date = att_date
						att.shift = shift
						att.status = 'Absent'
						att.in_time = checkins[0].time
						att.working_total_hours = '00:00'
						att.extra_hours = '00:00'
						att.save(ignore_permissions=True)
						frappe.db.commit()
						frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
						return att
	if log_type == 'OUT':
		max_out = datetime.strptime('11:30','%H:%M').time()
		if att_time < max_out:
			yesterday = add_days(att_date,-1)
			checkins = frappe.db.sql("select name,time from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and time(time) < '%s' order by time "%(employee,att_date,max_out),as_dict=True)
			att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':yesterday})
			if att:
				att = frappe.get_doc("Attendance",att)
				if att.docstatus == 0:
					if not att.out_time:
						if len(checkins) > 0:
							att.out_time = checkins[-1].time
						else:
							att.out_time = checkins[-1].time
						att.status = 'Present'    
						att.save(ignore_permissions=True)
						frappe.db.commit()
						frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
						return att
					else:
						return att
			else:
				try: 
					if not frappe.db.exists('Restriction',{'employee':employee,'restricted_date':yesterday,'docstatus':1}):
						att = frappe.new_doc("Attendance")
						att.employee = employee
						att.attendance_date = yesterday
						att.status = 'Absent'
						if len(checkins) > 0:
							att.out_time = checkins[-1].time
							att.shift = get_actual_shift(get_time(checkins[-1].time))
						else:
							att.out_time = checkins[-1].time
							att.shift = get_actual_shift(get_time(checkins[-1].time))
						att.save(ignore_permissions=True)
						frappe.db.commit()
						frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
						return att
				except:
					frappe.log_error(title="Restriction",message="Please Check Restriction on %s that Employee %s"%(yesterday,employee))
	 
		else:
			checkins = frappe.db.sql("select name,time,docstatus from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' order by time "%(employee,att_date),as_dict=True)
			att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date})
			if att:
				att = frappe.get_doc("Attendance",att)
				if att.docstatus == 0:
					if not att.out_time:
						if len(checkins) > 0:
							att.out_time = checkins[-1].time
						else:
							att.out_time = checkins[-1].time
						att.status = 'Present'    
						att.save(ignore_permissions=True)
						frappe.db.commit()
						frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
						return att
					else:
						return att
			else:
				try: 
					if not frappe.db.exists('Restriction',{'employee':employee,'restricted_date':att_date,'docstatus':1}):
						att = frappe.new_doc("Attendance")
						att.employee = employee
						att.attendance_date = att_date
						att.shift = shift
						att.status = 'Absent'
						if len(checkins) > 0:
							att.out_time = checkins[-1].time
							att.shift = get_actual_shift(get_time(checkins[-1].time))
						else:
							att.out_time = checkins[-1].time
							att.shift = get_actual_shift(get_time(checkins[-1].time))
						att.save(ignore_permissions=True)
						frappe.db.commit()
						frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance','1')
						frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
						return att  
				except:
					frappe.log_error(title="Restriction",message="Please Check Restriction on %s that Employee %s"%(att_date,employee))
	 

def is_between(time, time_range):
	if time_range[1] < time_range[0]:
		return time >= time_range[0] or time <= time_range[1]
	return time_range[0] <= time <= time_range[1]

def get_actual_shift(get_shift_time):
	from datetime import datetime
	from datetime import date, timedelta,time
	nowtime = datetime.now()
	shift_1_time = [time(hour=14, minute=0, second=0),time(hour=17, minute=30, second=0)]
	shift_2_time = [time(hour=12, minute=0, second=0),time(hour=2, minute=0, second=0)]
	shift_3_time = [time(hour=6, minute=50, second=0),time(hour=8, minute=50, second=0)]
	shift = ''
	if is_between(get_shift_time,shift_1_time):
		shift = '1'
	if is_between(get_shift_time,shift_2_time):
		shift = '2'
	if is_between(get_shift_time,shift_3_time):
		shift = '3'
	return shift   

@frappe.whitelist()
def mark_absent(from_date,to_date):
	dates = [from_date,to_date]
	for date in dates:
		employee = frappe.db.get_all('Employee',{'status':'Active','date_of_joining':['<=',from_date]})
		for emp in employee:
			hh = check_holiday(date,emp.name)
			if not hh:
				if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
					try:
						if not frappe.db.exists('Restriction',{'employee':emp.name,'restricted_date':date,'docstatus':1}):
							att = frappe.new_doc("Attendance")
							att.employee = emp.name
							att.status = 'Absent'
							att.attendance_date = date
							# att.total_working_hours = "0.0"
							# att.over_time_hours = "0.0"
							# att.working_total_hours = "00:00:00"
							# att.over_time_hours = "0.0"
							# att.extra_hours = "00:00:00"
							# att.att_in_time = "00:00:00"
							# att.att_out_time = "00:00:00"
							att.save(ignore_permissions=True)
							frappe.db.commit()
					except:
						frappe.log_error(title="Restriction",message="Please Check Restriction on %s that Employee %s"%(date,emp.name))
	absent_for_unmatched_shift()


def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',emp,'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	if holiday:
		if holiday[0].weekly_off == 1:
			return "WW"
		else:
			return "HH"

def mark_wh_ot(from_date,to_date):
	attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':('!=','2')},['name','shift','in_time','out_time','employee'])
	for att in attendance:
		if att.in_time and att.out_time:
			hh = check_holiday(att.attendance_date,att.employee)
			if not hh:
				total_wh = att.out_time - att.in_time
				ftr = [3600,60,1]
				wh = time_diff_in_hours(att.out_time,att.in_time)
				if wh < 4:
					frappe.db.set_value('Attendance',att.name,'status','Absent')
				elif wh >= 4 and wh < 8:
					frappe.db.set_value('Attendance',att.name,'status','Half Day')
				elif wh >= 8:
					frappe.db.set_value('Attendance',att.name,'status','Present')   
				shift_start_time = frappe.db.get_value('Shift Type',{'name':att.shift},['start_time'])
				shift_start_time = pd.to_datetime(str(shift_start_time)).time()

				shift_end_time = frappe.db.get_value('Shift Type',{'name':att.shift},['end_time'])
				shift_end_time = pd.to_datetime(str(shift_end_time)).time()

				in_date = att.in_time.date()
				out_date = att.out_time.date()
				get_shift_hours = frappe.db.get_value('Shift Type',{'name':att.shift},['total_shift_hours'])
				total_shift_hours = datetime.strptime(str(get_shift_hours),'%Y-%m-%d %H:%M:%S').time()
				shift_hr = sum([a*b for a,b in zip(ftr, map(int,str(total_shift_hours).split(':')))])
				shift_wh = round(shift_hr/3600,1) 
				shift_start_datetime = datetime.combine(in_date,shift_start_time)
				shift_end_datetime = datetime.combine(out_date,shift_end_time)
				
				if int(wh) > int(shift_wh):
					extra_hrs =pd.to_datetime('00:00:00').time()
					ot_hr = 0
					try:
						extra_hrs = att.out_time - shift_end_datetime
						hr = sum([a*b for a,b in zip(ftr, map(int,str(extra_hrs).split(':')))])
						extras = round(hr/3600,1)
					except:
						extra_hrs = '00:00' 
						extras = 0 
					if extras > 1:
							ot_hr = math.floor(extras * 2) / 2  
					frappe.db.set_value('Attendance',att.name,'working_total_hours',total_wh)             
					frappe.db.set_value('Attendance',att.name,'total_working_hours',wh)                
					frappe.db.set_value('Attendance',att.name,'extra_hours',extra_hrs)
					frappe.db.set_value('Attendance',att.name,'over_time_hours',ot_hr)
				else:
					none_time = pd.to_datetime('00:00:00').time()
					frappe.db.set_value('Attendance',att.name,'working_total_hours','00:00')
					frappe.db.set_value('Attendance',att.name,'total_working_hours',0)  
					frappe.db.set_value('Attendance',att.name,'extra_hours','00:00')
					frappe.db.set_value('Attendance',att.name,'over_time_hours',0)
			else:
				total_wh = att.out_time - att.in_time
				ftr = [3600,60,1]
				hr = sum([a*b for a,b in zip(ftr, map(int,str(total_wh).split(':')))])
				wh = round(hr/3600,1)
				if wh < 4:
					frappe.db.set_value('Attendance',att.name,'status','Absent')
				elif wh >= 4 and wh < 8:
				   	frappe.db.set_value('Attendance',att.name,'status','Half Day')   
				else:
					frappe.db.set_value('Attendance',att.name,'status','Present') 
				if wh > 0:
					ot_hr = (math.floor(wh * 2) / 2) - 0.5
					frappe.db.set_value('Attendance',att.name,'over_time_hours',ot_hr)
					none_time =pd.to_datetime('00:00:00').time()
					frappe.db.set_value('Attendance',att.name,'extra_hours','00:00')
					frappe.db.set_value('Attendance',att.name,'working_total_hours',total_wh)
					frappe.db.set_value('Attendance',att.name,'total_working_hours',wh)
				else:
					none_time =pd.to_datetime('00:00:00').time()
					frappe.db.set_value('Attendance',att.name,'over_time_hours',0)
					frappe.db.set_value('Attendance',att.name,'extra_hours','00:00')
					frappe.db.set_value('Attendance',att.name,'working_total_hours','00:00')
					frappe.db.set_value('Attendance',att.name,'total_working_hours',0)   
		else:
			none_time =pd.to_datetime('00:00:00').time()
			frappe.db.set_value('Attendance',att.name,'extra_hours','00:00')
			frappe.db.set_value('Attendance',att.name,'working_total_hours','00:00')

def permission_request(from_date,to_date):
	year_start = date(date.today().year, 1, 1)
	year_end = date(date.today().year, 12, 31)
	month_start_date =  from_date + dateutil.relativedelta.relativedelta(months=-1)
	payroll_start_date = add_days(get_first_day(month_start_date),20)
	payroll_end_date = add_days(get_first_day(from_date),19)
	attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':('!=','2')},['in_time','shift','employee','attendance_date'])  
	if attendance:
		for att in attendance:
			if frappe.db.exists('Permission Request',{'permission_date':('between',(payroll_start_date,payroll_end_date)),'employee_id':att.employee,'docstatus':('!=','2')}):
				per_count = frappe.db.count('Permission Request',{'permission_date':('between',(payroll_start_date,payroll_end_date)),'employee_id':att.employee,'docstatus':('!=','2')})
				if per_count >= 2:
					if att.in_time:
						shift_start_time = frappe.db.get_value('Shift Type',{'name':att.shift},['start_time'])
						shift_start_time = pd.to_datetime(str(shift_start_time)).time()
						in_date = att.in_time.date()
						shift_start_datetime = datetime.combine(in_date,shift_start_time)
						att_in_time = datetime.strptime(str(att.in_time),'%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
						att_shift_time = datetime.strptime(str(shift_start_time),'%H:%M:%S').strftime('%H:%M:%S')
						if  att_in_time > att_shift_time:
							late = att.in_time - shift_start_datetime
							late_5_mins = timedelta(hours=0,minutes=5,seconds=0)
							late_5_hr = timedelta(hours=5,minutes=0,seconds=0)
							leave_allocation = frappe.db.exists('Leave Allocation',{'employee':att.employee,'from_date':('between',(year_start,year_end)),'docstatus':('!=','2')})
							if leave_allocation:
								leave_type = frappe.db.get_value('Leave Allocation',{'name':leave_allocation,'docstatus':('!=','2')},['leave_type'])
								leave_allocation_count = frappe.db.get_value('Leave Allocation',{'name':leave_allocation,'docstatus':('!=','2')},['new_leaves_allocated'])
								leave_application_count = frappe.db.count('Leave Application',{'employee':att.employee,'from_date':('between',(year_start,year_end)),'leave_type':leave_type,'docstatus':('!=','2') })
								balance_leaves = leave_allocation_count - leave_application_count
								leave_approver = ''
								if late > late_5_mins and late < late_5_hr:
									leave_approver = frappe.db.get_value('Employee',{'status':'Active','employee':att.employee},['leave_approver'])
									if leave_type == "Casual Leave" and balance_leaves > 0:
										new_leave_application = frappe.new_doc('Leave Application')
										new_leave_application.employee = att.employee
										new_leave_application.leave_type = 'Casual Leave'
										new_leave_application.from_date = att.attendance_date
										new_leave_application.to_date = att.attendance_date
										new_leave_application.half_day = 1
										new_leave_application.status = 'Open'
										new_leave_application.description = 'Late By %s'%late
										new_leave_application.leave_approver = leave_approver
										new_leave_application.save(ignore_permissions=TRUE)
										new_leave_application.submit()
										frappe.db.commit()
									elif leave_type == 'Sick Leave' and balance_leaves > 0 :
										new_leave_application = frappe.new_doc('Leave Application')
										new_leave_application.employee = att.employee
										new_leave_application.leave_type = 'Sick Leave'
										new_leave_application.from_date = att.attendance_date
										new_leave_application.to_date = att.attendance_date
										new_leave_application.half_day = 1
										new_leave_application.status = 'Open'
										new_leave_application.description = 'Late By %s'%late
										new_leave_application.leave_approver = leave_approver
										new_leave_application.save(ignore_permissions=TRUE)
										new_leave_application.submit()
										frappe.db.commit()
									elif leave_type == 'Earned Leave' and balance_leaves > 0:
										new_leave_application = frappe.new_doc('Leave Application')
										new_leave_application.employee = att.employee
										new_leave_application.leave_type = 'Earned Leave'
										new_leave_application.from_date = att.attendance_date
										new_leave_application.to_date = att.attendance_date
										new_leave_application.half_day = 1
										new_leave_application.status = 'Open'
										new_leave_application.description = 'Late By %s'%late
										new_leave_application.leave_approver = leave_approver
										new_leave_application.save(ignore_permissions=TRUE)
										new_leave_application.submit()
										frappe.db.commit()
									else:
										new_leave_application = frappe.new_doc('Leave Application')
										new_leave_application.employee = att.employee
										new_leave_application.leave_type = 'Leave Without Pay'
										new_leave_application.from_date = att.attendance_date
										new_leave_application.to_date = att.attendance_date
										new_leave_application.half_day = 1
										new_leave_application.status = 'Open'
										new_leave_application.description = 'Late By %s'%late
										new_leave_application.leave_approver = leave_approver
										new_leave_application.save(ignore_permissions=TRUE)
										new_leave_application.submit()
										frappe.db.commit()
								elif late > late_5_hr:
									leave_approver = frappe.db.get_value('Employee',{'status':'Active','employee':att.employee},['leave_approver'])
									if leave_type == "Casual Leave" and balance_leaves > 0:
										new_leave_application = frappe.new_doc('Leave Application')
										new_leave_application.employee = att.employee
										new_leave_application.leave_type = 'Casual Leave'
										new_leave_application.from_date = att.attendance_date
										new_leave_application.to_date = att.attendance_date
										new_leave_application.half_day = 1
										new_leave_application.status = 'Open'
										new_leave_application.description = 'Late By %s'%late
										new_leave_application.leave_approver = leave_approver
										new_leave_application.save(ignore_permissions=TRUE)
										new_leave_application.submit()
										frappe.db.commit()
									elif leave_type == 'Sick Leave' and balance_leaves > 0 :
										new_leave_application = frappe.new_doc('Leave Application')
										new_leave_application.employee = att.employee
										new_leave_application.leave_type = 'Sick Leave'
										new_leave_application.from_date = att.attendance_date
										new_leave_application.to_date = att.attendance_date
										new_leave_application.half_day = 1
										new_leave_application.status = 'Open'
										new_leave_application.description = 'Late By %s'%late
										new_leave_application.leave_approver = leave_approver
										new_leave_application.save(ignore_permissions=TRUE)
										new_leave_application.submit()
										frappe.db.commit()
									elif leave_type == 'Earned Leave' and balance_leaves > 0:
										new_leave_application = frappe.new_doc('Leave Application')
										new_leave_application.employee = att.employee
										new_leave_application.leave_type = 'Earned Leave'
										new_leave_application.from_date = att.attendance_date
										new_leave_application.to_date = att.attendance_date
										new_leave_application.half_day = 1
										new_leave_application.status = 'Open'
										new_leave_application.description = 'Late By %s'%late
										new_leave_application.leave_approver = leave_approver
										new_leave_application.save(ignore_permissions=TRUE)
										new_leave_application.submit()
										frappe.db.commit()
									else:
										new_leave_application = frappe.new_doc('Leave Application')
										new_leave_application.employee = att.employee
										new_leave_application.leave_type = 'Leave Without Pay'
										new_leave_application.from_date = att.attendance_date
										new_leave_application.to_date = att.attendance_date
										new_leave_application.half_day = 1
										new_leave_application.status = 'Open'
										new_leave_application.description = 'Late By %s'%late
										new_leave_application.leave_approver = leave_approver
										new_leave_application.save(ignore_permissions=TRUE)
										new_leave_application.submit()
										frappe.db.commit()    
						else:
							frappe.log_error('Employee has no late')                
					else:
						frappe.log_error ('Employee has no INTIME')                            
				else:
					if att.in_time:
						shift_start_time = frappe.db.get_value('Shift Type',{'name':att.shift},['start_time'])
						shift_start_time = pd.to_datetime(str(shift_start_time)).time()
						in_date = att.in_time.date()
						shift_start_datetime = datetime.combine(in_date,shift_start_time)
						att_in_time = datetime.strptime(str(att.in_time),'%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
						att_shift_time = datetime.strptime(str(shift_start_time),'%H:%M:%S').strftime('%H:%M:%S')
						if  att_in_time > att_shift_time:
							late = att.in_time - shift_start_datetime
							late_time_15_mins = timedelta(hours=0,minutes=15,seconds=0)
							late_time_1_hr = timedelta(hours=1,minutes=0,seconds=0)
							if late > late_time_15_mins and late < late_time_1_hr:
								if att.shift == '1':
									from_time = frappe.db.get_value('Shift Type',{'name':'1'},['start_time'])
									to_time = timedelta(hours=1) + from_time
									permission = frappe.new_doc('Permission Request')
									permission.employee_id = att.employee
									permission.permission_date = att.attendance_date
									permission.shift = att.shift
									permission.reason = 'Late By %s'%late
									permission.session = 'First Half'
									permission.permission_hour = '1'
									permission.from_time = from_time
									permission.to_time = to_time
									permission.save(ignore_permissions=True)
									permission.submit()
									frappe.db.commit()
								elif att.shift == '2':
									from_time = frappe.db.get_value('Shift Type',{'name':'2'},['start_time'])
									to_time = timedelta(hours=1) + from_time
									permission = frappe.new_doc('Permission Request')
									permission.employee_id = att.employee
									permission.permission_date = att.attendance_date
									permission.shift = att.shift
									permission.reason = 'Late By %s'%late
									permission.session = 'First Half'
									permission.permission_hour = '1'
									permission.from_time = from_time
									permission.to_time = to_time
									permission.save(ignore_permissions=True)
									permission.submit()
									frappe.db.commit()
								elif att.shift == '3':
									from_time = frappe.db.get_value('Shift Type',{'name':'3'},['start_time'])
									to_time = timedelta(hours=1) + from_time
									permission = frappe.new_doc('Permission Request')
									permission.employee_id = att.employee
									permission.permission_date = att.attendance_date
									permission.shift = att.shift
									permission.reason = 'Late By %s'%late
									permission.session = 'First Half'
									permission.permission_hour = '1'
									permission.from_time = from_time
									permission.to_time = to_time
									permission.save(ignore_permissions=True)
									permission.submit()
									frappe.db.commit()
								else:
									frappe.error_log("No Shift ") 
							elif  late > late_time_1_hr:
								if att.shift == '1':
									from_time = frappe.db.get_value('Shift Type',{'name':'1'},['start_time'])
									to_time = timedelta(hours=2) + from_time
									permission = frappe.new_doc('Permission Request')
									permission.employee_id = att.employee
									permission.permission_date = att.attendance_date
									permission.shift = att.shift
									permission.reason = 'Late By %s'%late
									permission.session = 'First Half'
									permission.permission_hour = '1.5'
									permission.from_time = from_time
									permission.to_time = to_time
									permission.save(ignore_permissions=True)
									permission.submit()
									frappe.db.commit()
								elif att.shift == '2':
									from_time = frappe.db.get_value('Shift Type',{'name':'2'},['start_time'])
									to_time = timedelta(hours=2) + from_time
									permission = frappe.new_doc('Permission Request')
									permission.employee_id = att.employee
									permission.permission_date = att.attendance_date
									permission.shift = att.shift
									permission.reason = 'Late By %s'%late
									permission.session = 'First Half'
									permission.permission_hour = '1.5'
									permission.from_time = from_time
									permission.to_time = to_time
									permission.save(ignore_permissions=True)
									permission.submit()
									frappe.db.commit()
								elif att.shift == '3':
									from_time = frappe.db.get_value('Shift Type',{'name':'3'},['start_time'])
									to_time = timedelta(hours=2) + from_time
									permission = frappe.new_doc('Permission Request')
									permission.employee_id = att.employee
									permission.permission_date = att.attendance_date
									permission.shift = att.shift
									permission.reason = 'Late By %s'%late
									permission.session = 'First Half'
									permission.permission_hour = '1.5'
									permission.from_time = from_time
									permission.to_time = to_time
									permission.save(ignore_permissions=True)
									permission.submit()
									frappe.db.commit()    
								else:
									frappe.log_error("No Shift")  
							else:
								error_msg = [att.employee.att.attendance_date,att.shift,att.in_time]
								frappe.log_error("No Records",error_msg)   

def get_ot_compensation(from_date,to_date):
	attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':('!=','2')},['*'])
	for att in attendance:
		hh = check_holiday(att.attendance_date,att.employee)
		if hh:
			if hh == "WW":
				if att.grade == 'G-0':
					grade_g0 = 'Double Wages'
					frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_g0)
				elif att.grade in ['MG-0','MG-1','MG-2','MG-3']:
					grade_mg_1_to_3 = 'Double Wages'  
					frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_mg_1_to_3) 
				elif att.grade in ['MG-4','MG-5','MG-6','MG-7','MG-8','MG-9','MG-10','MG-11']:
					grade_mg_4_to_11 = 'Compensatory Off'
					frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_mg_4_to_11) 
			elif hh == 'HH':
				if att.grade == 'G-0':
					grade_g0 = 'Double Wages + Compensatory Off or Triple Wages'   
					frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_g0)
				elif att.grade in ['MG-0','MG-1','MG-2','MG-3']:
					grade_mg_1_to_3 = 'Double Wages + Compensatory Off'
					frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_mg_1_to_3)
				elif att.grade in ['MG-4','MG-5','MG-6','MG-7','MG-8','MG-9','MG-10','MG-11']:
					grade_mg_4_to_11 = 'Compensatory Off' 
					frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_mg_4_to_11)
			else:
				message = ('No Holiday') 
				frappe.log_error('Holiday List Condition',message)   
		else:
			if att.shift == '1':
				shift_time = frappe.db.get_value('Shift Type',{'name':att.shift},['start_time'])
				shift_start_time = pd.to_datetime(str(shift_time)).time()
				att_date_str = datetime.strptime(str(att.attendance_date),'%Y-%m-%d').date()
				shift_start_datetime = datetime.combine(att_date_str,shift_start_time)
				total_hours = shift_start_datetime - att.in_time
				ftr = [3600,60,1]
				try:
					hr = sum([a*b for a,b in zip(ftr, map(int,str(total_hours).split(':')))])
					ot_hour = round(hr/3600,1)   
				except:
					ot_hour = 0     
				if ot_hour >= 2 :
					if att.grade == 'G-0':
						grade_g0 = 'Double Wages'
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_g0)
					elif att.grade in ['MG-0','MG-1','MG-2','MG-3']:
						grade_mg_1_to_3 = 'Double Wages'  
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_mg_1_to_3)
					else:
						grade_nil = 'NIL'      
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_nil)
				elif att.over_time_hours >=2 :
					if att.grade == 'G-0':
						grade_g0 = 'Double Wages'
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_g0)
					elif att.grade in ['MG-0','MG-1','MG-2','MG-3']:
						grade_mg_1_to_3 = '200 Rupees Allowance'  
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_mg_1_to_3)   
					else:
						grade_nil = 'NIL'      
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_nil)       
			elif att.shift == '2':
				if att.over_time_hours >=2 :
					if att.grade == 'G-0':
						grade_g0 = 'Double Wages'
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_g0)
					elif att.grade in ['MG-0','MG-1','MG-2','MG-3']:
						grade_mg_1_to_3 = 'Double Wages'  
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_mg_1_to_3)
					else:
						grade_nil = 'NIL'      
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_nil)   
			else:
				message = ('Shift Based Overtime closed')
				frappe.log_error('Overtime Request',message)
			if att.over_time_hours >=3 :
				if att.shift != '3':
					if att.grade == 'G-0':
						grade_g0 = 'Double Wages'
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_g0)  
					elif att.grade in ['MG-0','MG-1','MG-2','MG-3']:
						grade_mg_1_to_3 = 'Double Wages'  
						frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_mg_1_to_3)
					elif att.over_time_hours >=4 and att.over_time_hours <8 :
						if att.grade in ['MG-4','MG-5','MG-6','MG-7','MG-8','MG-9','MG-10','MG-11']:
							grade_mg_4_to_11 = 'Half Day Compensatory Off' 
							frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_mg_4_to_11) 
						else:
							message = ('Grade over less than MG-11')
							frappe.log_error('Overtime Request',message)
					elif att.over_time_hours >=8:
						if att.grade in ['MG-4','MG-5','MG-6','MG-7','MG-8','MG-9','MG-10','MG-11']:
							grade_mg_4_to_11 = 'Full Day Compensatory Off' 
							frappe.db.set_value('Attendance',att.name,'ot_compensation',grade_mg_4_to_11)  
						else:
							message = ('Grade over less than MG-11')
							frappe.log_error('Overtime Request',message)   
			else:
				message = ('Overtime Hours lesser than 3 is not run')
				frappe.log_error('Overtime Request',message)  


def att_shift_status(from_date,to_date):
	attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':('!=','2')},['*'])  
	for att in attendance:
		shift_status = ''
		if att.status == 'Absent':
			if att.in_time and not att.out_time:
				if att.shift:
					shift_status = str(att.shift) + 'M'
					frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
				else:
					shift_status = 'NS/' + 'M'
					frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
			elif att.out_time and not att.in_time:
				if att.shift:
					shift_status = 'M' + str(att.shift)
					frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
				else:
					shift_status = 'M' + '/NS'
					frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
			elif att.out_time and att.in_time:
				if att.shift:
					shift_status = 'AA'
					frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
				else:
					shift_status = 'AA'
					frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
			else:
				shift_status = 'AA'
				frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
		elif att.status == 'Present':
			if att.shift:
				shift_status = str(att.shift)
				frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
			else:
				if att.on_duty_application:
					shift_status = 'OD'
					frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
				else:
					shift_status = 'NS/P'
					frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
		elif att.status == 'Work From Home':
			shift_status = 'WFH'
			frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
		elif att.status == 'Half Day':
			if att.leave_type:
				shift_status = 'HD/' + status_map.get(att.leave_type)
				frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
			else:
				shift_status = 'HD'
				frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
		elif att.status == 'On Leave':
			if att.leave_type:
				shift_status = status_map.get(att.leave_type)
				frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
			else:
				shift_status = 'L'
				frappe.db.set_value('Attendance',att.name,'shift_status',shift_status)
	return 'ok'
	
def assigned_shift(from_date,to_date):
	datalist = []
	data = {}
	attendance = frappe.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':('!=','2')},['*'])
	for att in attendance:
		check_shift = frappe.db.exists('Shift Assignment',{'employee':att.employee,'start_date':att.attendance_date,'docstatus':1})  
		if check_shift:
			get_shift = frappe.get_value('Shift Assignment',{'name':check_shift},['shift_type'])  
			shift_start_time = frappe.get_value('Shift Type',{'name':get_shift},['start_time'])
			shift_end_time = frappe.get_value('Shift Type',{'name':get_shift},['end_time'])
			data.update({
				'get_shift':get_shift,
				'shift_start_time':shift_start_time,
				'shift_end_time':shift_end_time 
			})
			datalist.append(data.copy())
		else: 
			get_shift = 'No Shift Assigned'  
			shift_start_time = datetime.strptime(str('00:00:00'),'%H:%M:%S').strftime('%H:%M')
			shift_end_time = datetime.strptime(str('00:00:00'),'%H:%M:%S').strftime('%H:%M')
			data.update({
				'get_shift':get_shift,
				'shift_start_time':shift_start_time,
				'shift_end_time':shift_end_time 
			})
			datalist.append(data.copy())  
			
		if att.in_time and att.out_time:
			att_in_time = att.in_time
			att_out_time = att.out_time
			att_shift = att.shift or ' '
			data.update({
				'att_shift':att.shift or '-',
				'att_in_time':att_in_time,
				'att_out_time':'att_out_time',
			}) 
			datalist.append(data.copy())  
			frappe.db.set_value('Attendance',att.name,'attended_shift',att_shift or '')
			frappe.db.set_value('Attendance',att.name,'att_in_time',att_in_time)
			frappe.db.set_value('Attendance',att.name,'att_out_time',att_out_time)    
		elif att.in_time:
			att_in_time = att.in_time 
			att_out_time = datetime.combine(getdate(att.attendance_date),get_time('00:00:00'))
			att_shift = att.shift or '-'
			data.update({
				'att_shift':att.shift,
				'att_in_time':att_in_time,
				'att_out_time':att_out_time
			})
			datalist.append(data.copy())
			frappe.db.set_value('Attendance',att.name,'attended_shift',att_shift or '')
			frappe.db.set_value('Attendance',att.name,'att_in_time',att_in_time)
			frappe.db.set_value('Attendance',att.name,'att_out_time',att_out_time)    
		elif att.out_time:
			att_in_time = datetime.combine(getdate(att.attendance_date),get_time('00:00:00'))
			att_out_time = att.out_time
			att_shift = att.shift or '-'
			data.update({
				'att_shift':att.shift,
				'att_in_time':att_in_time,
				'att_out_time':att_out_time
			})
			datalist.append(data.copy()) 
			frappe.db.set_value('Attendance',att.name,'attended_shift',att_shift or '')
			frappe.db.set_value('Attendance',att.name,'att_in_time',att_in_time)
			frappe.db.set_value('Attendance',att.name,'att_out_time',att_out_time)          
		frappe.db.set_value('Attendance',att.name,'assigned_shift',get_shift)
		frappe.db.set_value('Attendance',att.name,'shift_in_time',shift_start_time)
		frappe.db.set_value('Attendance',att.name,'shift_out_time',shift_end_time)
		# frappe.db.set_value('Attendance',att.name,'attended_shift',att_shift or '')
		# frappe.db.set_value('Attendance',att.name,'att_in_time',att_in_time)
		# frappe.db.set_value('Attendance',att.name,'att_out_time',att_out_time)  
	return "ok"
	   
def shift_matched(from_date,to_date):
	data = {}
	datalist = []
	# from_date = '2023-01-02'
	# to_date = '2023-02-11'
	status = ''
	attendance = frappe.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':('!=','2')},['*'])
	for att in attendance:
		if att.assigned_shift and att.attended_shift:
			if att.assigned_shift == att.attended_shift:
				status = 'Matched'
			else:
				status = 'Unmatched'  
		else:
			status = 'Unmatched'
		data.update({
			'status':status
		}) 
		datalist.append(data.copy())  
		frappe.db.set_value('Attendance',att.name,'shift_matched_or_unmatched',status)   

def mark_att_present(from_date, to_date):
    attendance_docstatus_0 = frappe.db.get_all('Attendance', {
        'attendance_date': ('between', (from_date, to_date)),'docstatus': 0}, ['*'])
    
    for att in attendance_docstatus_0:
        if att.get('status') == 'Present':
            frappe.db.set_value('Attendance', att.get('name'), 'docstatus', 1)
		  
					  
@frappe.whitelist()
def mark_att_process(from_date):
	frappe.errprint("Hi")
	to_date = from_date
	checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where skip_auto_attendance = 0 and date(time) between '%s' and '%s' order by time  """%(from_date,to_date),as_dict=True)
	frappe.errprint("Hi")
	for c in checkins:
		frappe.errprint("Hi")
		employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
		if employee:
			mark_attendance_from_checkin(c.name,c.employee,c.time,c.log_type)
			frappe.errprint("Hi")  
	mark_absent(from_date,to_date)  
	mark_wh_ot(from_date,to_date)   
	get_ot_compensation(from_date,to_date)   
	att_shift_status(from_date,to_date) 
	assigned_shift(from_date,to_date)
	shift_matched(from_date,to_date)
	return "ok"       



@frappe.whitelist()
def push_punch():
	from cgi import print_environ
	import mysql.connector
	import requests,json
	from datetime import date
	from datetime import time,datetime

	mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd="Pa55w0rd@",
	database="easytimepro"
	)

	from_date = add_days(today(),-1)  
	to_date = today()

	mycursor = mydb.cursor(dictionary=True)
	query = "SELECT  * FROM iclock_transaction where date(punch_time) between '%s'  and '%s' "%(from_date,to_date)
	mycursor.execute(query)
	attlog = mycursor.fetchall()
	if attlog:
		for a in attlog:
			# print(len(attlog))
			url = "http://157.245.101.198/api/method/johoku.biometric_checkin.mark_checkin?employee=%s&time=%s&device_id=%s" % (a['emp_code'],a['punch_time'],a['terminal_alias'])
			print(url)
			headers = { 'Content-Type': 'application/json','Authorization': 'token b3df19e9615e0dc:b499d47b3041f94'}
			print(headers)
			response = requests.request('GET',url,headers=headers,verify=False)
			print(response)
			res = json.loads(response.text)
			print(res)
			if res:
				if res['message'] == 'Checkin Marked':
					mycursor = mydb.cursor()
					sql = "UPDATE iclock_transaction SET checkin_marked = 1 WHERE id = %s " % a['id']
					mycursor.execute(sql)
					mydb.commit()   
		return "OK"

@frappe.whitelist()
def delete_urc_automatically():
	from_date = add_days(today(),-35)  
	to_date = add_days(today(),-34)  
	urc = frappe.db.sql("""delete from `tabUnregistered Employee Checkin` where date(biometric_time) between '%s' and '%s'  """%(from_date,to_date),as_dict = True)
	print(urc)

@frappe.whitelist()
def absent_for_unmatched_shift():
	from_date = get_first_day(today())
	to_date = today()
	frappe.db.sql("""UPDATE `tabAttendance` SET status = 'Absent' WHERE assigned_shift != 'No Shift Assigned' AND status = 'Present' AND shift_matched_or_unmatched = 'Unmatched' AND attendance_date BETWEEN '%s' AND '%s' """ % (from_date, to_date), as_dict=1)
	frappe.db.sql("""UPDATE `tabAttendance` SET attended_shift = NULL,  att_in_time = NULL, att_out_time = NULL 
			   		 WHERE in_time IS NULL AND out_time IS NULL AND attendance_date BETWEEN '%s' AND '%s' """ % (from_date, to_date), as_dict=1)




