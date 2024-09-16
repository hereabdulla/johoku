# Copyright (c) 2022, teampro and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from email import message
import re
from frappe import _
import frappe
from frappe.model.document import Document
from datetime import date, timedelta, datetime,time
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,today, format_date)
import pandas as pd
from dateutil.relativedelta import relativedelta
import math
from datetime import datetime
from frappe.utils import add_months, cint, flt, getdate, time_diff_in_hours

class AttendanceRegularize(Document):

	def on_submit(self):
		status = self.validate_total_wh()
		att_status = status[0]['status']
		att_working_hours = self.validate_total_wh()
		working_hours = att_working_hours[0]['att_wh']
		att_total_wh = self.validate_total_wh()
		total_wh = att_total_wh[0]['total_wh_att']
		att_extra_hours = self.validate_extra_hour()
		extra_hours = att_extra_hours[0]['extra_hrs_time']
		att_ot_hr = self.validate_extra_hour()
		ot_hr = att_ot_hr[0]['ot_hr']
		update_shift_in_time = self.updated_shift()
		shift_in_time = update_shift_in_time[0]['get_shift_start_time']
		update_shift_out_time = self.updated_shift()
		shift_out_time = update_shift_out_time[0]['get_shift_end_time']
		hh = self.validate_check_holiday()
		if not hh:
			att = frappe.db.exists('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date,'docstatus':('!=','2')})
			if att:
				attendance = frappe.get_doc('Attendance',{'name':att})
				attendance.status = att_status
				attendance.in_time = self.corrected_in
				attendance.out_time = self.corrected_out
				attendance.shift = self.corrected_shift
				attendance.total_working_hours = working_hours
				attendance.working_total_hours = total_wh
				attendance.extra_hours = extra_hours
				attendance.over_time_hours = ot_hr
				attendance.attended_shift = self.corrected_shift
				attendance.att_in_time = self.corrected_in
				attendance.att_out_time = self.corrected_out
				attendance.shift_status = self.corrected_shift
				attendance.save(ignore_permissions=True)
				frappe.db.commit()
				frappe.db.set_value('Attendance',att,'shift_matched_or_unmatched','Matched')
				frappe.db.set_value('Attendance',att,'attendance_regularize',self.name)
		else:
			att = frappe.db.exists('Attendance',{'name':self.attendance_marked})
			if att:
				total_working_hour = self.validate_total_wh()
				total_wh = total_working_hour[0]['total_wh']
				ftr = [3600,60,1]
				hr = sum([a*b for a,b in zip(ftr, map(int,str(total_wh).split(':')))])
				wh = round(hr/3600,1)
				if wh > 0:
					none_time =pd.to_datetime('00:00:00').time()
					holiday_ot_hr = (math.floor(wh * 2) / 2) - 0.5
					attendance = frappe.get_doc('Attendance',{'name':self.attendance_marked})
					attendance.status = 'Present'
					attendance.in_time = self.corrected_in
					attendance.out_time = self.corrected_out
					attendance.shift = self.corrected_shift
					attendance.total_working_hours = working_hours
					attendance.working_total_hours = total_wh
					attendance.extra_hours = total_wh
					attendance.over_time_hours = holiday_ot_hr
					attendance.attended_shift = self.corrected_shift
					attendance.att_in_time = self.corrected_in
					attendance.att_out_time = self.corrected_out
					attendance.shift_status = self.corrected_shift
					attendance.save(ignore_permissions=True)
					frappe.db.commit()
					# frappe.db.set_value('Attendance',self.attendance_marked,'status','Present')
					frappe.db.set_value('Attendance',self.attendance_marked,'shift_matched_or_unmatched','Matched')
					frappe.db.set_value('Attendance',self.attendance_marked,'attendance_regularize',self.name)
			else:
				frappe.throw(_("Employee has Attendance for the date %s"%(self.attendance_date)))

	def on_cancel(self):
		att = frappe.db.exists('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date})
		if att:
			att_reg = frappe.db.get_value('Attendance',{'name':att},['attendance_regularize'])
			if att_reg == self.name:
				frappe.db.sql(""" update `tabAttendance` set attendance_regularize = '' where name = '%s' and docstatus != 2 """%(att))
				frappe.db.sql(""" update `tabAttendance` set shift_matched_or_unmatched = 'Unmatched' where name = '%s' and docstatus != 2 """%(att))
	 
	def updated_shift(self):
		datalist = []
		data = {}
		get_shift_start_time = frappe.db.get_value('Shift Type',{'name':self.corrected_shift},['start_time'])
		get_shift_end_time = frappe.db.get_value('Shift Type',{'name':self.corrected_shift},['end_time'])
		data.update({
			'get_shift_start_time':get_shift_start_time,
			'get_shift_end_time':get_shift_end_time
		})
		datalist.append(data.copy())
		return datalist


	def validate_total_wh(self):
		datalist = []
		data = {}
		work_hour = time_diff_in_hours(self.corrected_out,self.corrected_in)
		str_in_time = datetime.strptime(str(self.corrected_in),'%Y-%m-%d %H:%M:%S')
		str_out_time = datetime.strptime(str(self.corrected_out),'%Y-%m-%d %H:%M:%S')
		total_wh = str_out_time - str_in_time
		if work_hour < 4.0:
			status = 'Absent'
		elif work_hour >= 4.0 and work_hour < 8.0:
			status = 'Half Day'
		elif work_hour >= 8.0:
			status = 'Present'	
		total_wh_att = datetime.strptime(str(total_wh),'%H:%M:%S').strftime('%H:%M')
		ftr = [3600,60,1]
		hr = sum([a*b for a,b in zip(ftr, map(int,str(total_wh).split(':')))])
		att_wh = round(hr/3600,1)
		data.update({
			'status':status,
			'total_wh':total_wh,
			'att_wh':att_wh,
			'total_wh_att':total_wh_att,
		})
		datalist.append(data.copy())
		return datalist  

	def validate_extra_hour(self):
		datalist = []
		data = {}
		ftr = [3600,60,1]
		shift_end_time = frappe.db.get_value('Shift Type',self.corrected_shift,'end_time')
		shift_end_time = pd.to_datetime(str(shift_end_time)).time()
		total_shift_hours = frappe.db.get_value('Shift Type',self.corrected_shift,'total_hours')
		att_out_time = datetime.strptime(str(self.corrected_out),'%Y-%m-%d %H:%M:%S')
		str_out_date = att_out_time.date()
		previous_day = add_days(str_out_date,-1)
		if getdate(str_out_date) > getdate(self.attendance_date):
			if self.corrected_shift == '3':
				shift_end_date_time = datetime.combine(previous_day,shift_end_time)
				if shift_end_date_time:
					extra_hrs = pd.to_datetime('00:00:00').time()
					ot_hr = 0 
					if att_out_time > shift_end_date_time:
						total_wh_method = self.validate_total_wh()
						total_wh = total_wh_method[0]['total_wh']
						if total_wh > total_shift_hours:
							extra_hrs = att_out_time - shift_end_date_time
							hr = sum([a*b for a,b in zip(ftr, map(int,str(extra_hrs).split(':')))])
							extras = round(hr/3600,1)
							if extras >= 1:
								ot_hr = math.floor(extras * 2) / 2
			elif self.corrected_shift == '2':  
				shift_end_date_time = datetime.combine(previous_day,shift_end_time)
				if shift_end_date_time:
					extra_hrs = pd.to_datetime('00:00:00').time()
					ot_hr = 0 
					if att_out_time > shift_end_date_time:
						total_wh_method = self.validate_total_wh()
						total_wh = total_wh_method[0]['total_wh']
						if total_wh > total_shift_hours:
							extra_hrs = att_out_time - shift_end_date_time
							hr = sum([a*b for a,b in zip(ftr, map(int,str(extra_hrs).split(':')))])
							extras = round(hr/3600,1)
							if extras >= 1.0:
								ot_hr = math.floor(extras * 2) / 2     
			elif self.corrected_shift == '1':  
				shift_end_date_time = datetime.combine(previous_day,shift_end_time)
				if shift_end_date_time:
					extra_hrs = pd.to_datetime('00:00:00').time()
					ot_hr = 0 
					if att_out_time > shift_end_date_time:
						total_wh_method = self.validate_total_wh()
						total_wh = total_wh_method[0]['total_wh']
						if total_wh > total_shift_hours:
							extra_hrs = att_out_time - shift_end_date_time
							hr = sum([a*b for a,b in zip(ftr, map(int,str(extra_hrs).split(':')))])
							extras = round(hr/3600,1)
							if extras >= 1:
								ot_hr = math.floor(extras * 2) / 2                                      
			else:
				shift_end_date_time = datetime.combine(str_out_date,shift_end_time)
				if shift_end_date_time:
					extra_hrs = pd.to_datetime('00:00:00').time()
					ot_hr = 0 
					if att_out_time > shift_end_date_time:
						total_wh_method = self.validate_total_wh()
						total_wh = total_wh_method[0]['total_wh']
						if total_wh > total_shift_hours:
							frappe.errprint(att_out_time)
							frappe.errprint(shift_end_date_time)
							extra_hrs = att_out_time - shift_end_date_time
							hr = sum([a*b for a,b in zip(ftr, map(int,str(extra_hrs).split(':')))])
							extras = round(hr/3600,1)
							if extras >= 1:
								frappe.errprint(shift_end_date_time)
								ot_hr = math.floor(extras * 2) / 2
		else:
			shift_end_date_time = datetime.combine(str_out_date,shift_end_time)
			if shift_end_date_time:
				extra_hrs = pd.to_datetime('00:00:00').time()
				ot_hr = 0 
				if att_out_time > shift_end_date_time:
					total_wh_method = self.validate_total_wh()
					total_wh = total_wh_method[0]['total_wh']
					if total_wh > total_shift_hours:
						extra_hrs = att_out_time - shift_end_date_time
						hr = sum([a*b for a,b in zip(ftr, map(int,str(extra_hrs).split(':')))])
						extras = round(hr/3600,1)
						if extras >= 1:
							ot_hr = math.floor(extras * 2) / 2
	
									
		extra_hrs_time = datetime.strptime(str(extra_hrs),'%H:%M:%S').strftime('%H:%M')                
		data.update({
			'extra_hrs_time':extra_hrs_time,
			'ot_hr':ot_hr
		})     
		datalist.append(data.copy()) 
		return datalist    

	def validate_check_holiday(self):
		holiday_list = frappe.db.get_value('Employee',self.employee,'holiday_list')
		holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
		left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,self.attendance_date),as_dict=True)
		if holiday:
			if holiday[0].weekly_off == 1:
				return "WW"
			else:
				return "HH"

@frappe.whitelist()
def get_assigned_shift_details(emp,att_date):
	datalist = []
	data = {}
	if frappe.db.exists('Shift Assignment',{'start_date':att_date,'employee':emp}):
		shift_assign = frappe.db.get_value('Shift Assignment',{'start_date':att_date,'employee':emp},['shift_type'])
		shift_start_time = frappe.db.get_value('Shift Type',{'name':shift_assign},['start_time'])
		shift_end_time = frappe.db.get_value('Shift Type',{'name':shift_assign},['end_time'])
		data.update({
			'shift_assign':shift_assign,
			'shift_start_time':shift_start_time,
			'shift_end_time':shift_end_time
		})
		datalist.append(data.copy())
	# else:
	#     shift_assign = "G"
	#     shift_start_time = frappe.db.get_value('Shift Type',{'name':shift_assign},['start_time'])
	#     shift_end_time = frappe.db.get_value('Shift Type',{'name':shift_assign},['end_time'])
	#     data.update({
	#         'shift_assign':shift_assign,
	#         'shift_start_time':shift_start_time,
	#         'shift_end_time':shift_end_time
	#     })
	#     datalist.append(data.copy())
	return datalist		


@frappe.whitelist()
def get_attendance(emp,att_date):
	datalist = []
	data = {}
	if frappe.db.exists('Attendance',{'employee':emp,'attendance_date':att_date}):
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time']):
			in_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time']).strftime('%H:%M:%S') 
		else:
			in_time = '-'    
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time']):
			out_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time']).strftime('%H:%M:%S')   
		else:
			out_time = '-'
		data.update({
			'in_time':in_time,
			'out_time':out_time,
		})
		datalist.append(data.copy())
	else:
		frappe.throw(_("Employee has No Checkins for the day"))
		data.update({
			'in_time':'No In Time',
			'out_time':'',
		})
		datalist.append(data.copy())
	return datalist    

@frappe.whitelist()
def attendance_marked(emp,att_date):
	datalist = []
	data = {}
	assigned_shift = ''
	att_id = ''
	if frappe.db.exists('Attendance',{'employee':emp,'attendance_date':att_date}):
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time']):
			in_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time'])
			assigned_shift = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['assigned_shift'])
			att_id = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['name'])
		else:
			in_time = ''   
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time']):
			out_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time'])
			assigned_shift = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['assigned_shift'])
			att_id = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['name'])
		else:
			out_time = ''
		data.update({
			'in_time':in_time,
			'out_time':out_time,
			'assigned_shift':assigned_shift,
			'att_id':att_id
		})
		datalist.append(data.copy())
	else:
		data.update({
			'in_time':'-',
			'out_time':'-',
			'assigned_shift':'-',
		})
		datalist.append(data.copy())
	return datalist 


# @frappe.whitelist()
# def date_of_joining(doj):

# 	# Current date in Python
# 	current_date = getdate(datetime.now())
# 	# frappe.errprint(current_date)

# 	#  Date of joining in Python
# 	nod = datetime.strptime(str(current_date),'%Y-%m-%d').date()
# 	# frappe.errprint(nod)
# 	jd = datetime.strptime(str(doj),'%Y-%m-%d').date()
# 	# frappe.errprint(jd)
 
# 	# Calculate the employee's experience in Python
# 	if nod.year != jd.year:
# 		jo_exp = str(nod.year - jd.year) + " " + "Years"
# 	if nod.year == jd.year:
# 		if nod.month != jd.month:
# 			jo_exp = str(nod.month - jd.month) + " " + "Months"
# 		if nod.month == jd.month:
# 			jo_exp = str(nod.day - jd.day) + " " +"Days"
 
#     #  Print the result
# 	# frappe.errprint(jo_exp)
# 	return jo_exp




	



