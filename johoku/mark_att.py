# from os import name

# # from pandas.core.tools.datetimes import to_datetime
# from os import name
# import frappe
# from numpy import empty
# import pandas as pd
# import json
# import datetime
# from frappe.permissions import check_admin_or_system_manager
# from frappe.utils.csvutils import read_csv_content
# from six.moves import range
# from six import string_types
# from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
# 	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
# from datetime import datetime
# from calendar import monthrange
# from frappe import _, msgprint
# from frappe.utils import flt
# from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours
# import requests

# from datetime import date, timedelta,time
# from frappe.utils.background_jobs import enqueue
# from frappe.utils import get_url_to_form
# import math

# frappe.whitelist()
# def mark_att():
# 	to_date = "2023-01-24"
# 	from_date= "2022-12-25"
# 	to_date = today()
# 	from_date= get_first_day(today())
# 	employee_checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where  date(time) between '%s' and '%s' order by time """%(from_date,to_date),as_dict=True) 
   
# 	if employee_checkins:
# 		date = employee_checkins[0].time
# 		from_date = datetime.strftime(date,'%Y-%m-%d')
		
# 		for c in employee_checkins:
# 			mark_attendance_from_checkin(c.employee,c.time,c.device_id)

# def mark_attendance_from_checkin(employee,time,device):
# 	att_time = time.time()
# 	att_date = time.date()
# 	in_time = ''
# 	out_time = ''
# 	checkins = frappe.db.sql(""" select name,time from `tabEmployee Checkin` where employee = '%s' and date(time)  = '%s' order by time """%(employee,att_date),as_dict=True)
# 	# ending_time = frappe.db.sql(""" select time from `tabShift Type` where name ='%s' and end_time ='%s' order by time"""(name,end_time),as_dict=True)
# 	if checkins:
# 		if device in ['Silvasa']:
# 				if datetime.strptime('04:30:00','%H:%M:%S').time() < att_time < datetime.strptime('08:15:00','%H:%M:%S').time():
# 					if len(checkins) >= 2:
# 						in_time = checkins[0].time
# 						out_time = checkins[-1].time
# 					elif len(checkins) == 1:
# 						in_time = checkins[0].time
# 						out_time = checkins[-1].time
# 					attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
# 					print(attn)
# 					status = ""
# 					if in_time and out_time:
# 						if in_time == out_time:
# 							status = 'Absent'
# 						elif in_time != out_time:	
# 							status = 'Present'
# 					else:
# 						status = 'Absent'
# 					if not attn:
# 						att = frappe.new_doc('Attendance')
# 						att.employee = employee
# 						att.attendance_date = att_date
# 						att.status = status
# 						att.in_time = in_time
# 						att.out_time = out_time
# 						att.save(ignore_permissions=True)
# 						frappe.db.commit()
# 					else:
# 						if in_time:
# 							frappe.db.set_value('Attendance',attn,'in_time',in_time)
# 						if out_time:
# 							frappe.db.set_value('Attendance',attn,'out_time',out_time)

# 						# frappe.db.set_value("Attendance",attn,'shift','Office Shift A')
# 						frappe.db.set_value("Attendance",attn,'status',status)
# 					for c in checkins:
# 						print(c)
# 						frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
# 						frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
# 					if in_time and out_time:
# 						str_working_hours = out_time - in_time
# 						time_d_float = str_working_hours.total_seconds()
# 						whrs = time_d_float/3600
# 						working_hours = "{:.2f}".format(whrs)
# 						# # end_timing = frappe.get_all("Shift Type",{'name':'A'},['end_time'])	
# 						# end_timing = frappe.get_value("Shift Type",{"name":},["end_time"])  
# 						frappe.db.set_value('Attendance',attn,'working_hours',working_hours)


# 					if float(working_hours) > 8:
# 						ot = float(working_hours) - 8
# 						print(ot)
# 						frappe.db.set_value('Attendance',attn,'ot',ot)
# 					else:
# 						return '0'
	
						
# 							# frappe.db.set_value('Attendance',attn,'ot',ot)
# 	elif checkins:
# 		if device in ['Mumbai']:
# 				if datetime.strptime('05:30:00','%H:%M:%S').time() < att_time < datetime.strptime('09:15:00','%H:%M:%S').time():
# 					if len(checkins) >= 2:
# 						in_time = checkins[0].time
# 						out_time = checkins[-1].time
# 					elif len(checkins) == 1:
# 						in_time = checkins[0].time
# 						out_time = checkins[-1].time
# 					attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
# 					print(attn)
# 					status = ""
# 					if in_time and out_time:
# 						if in_time == out_time:
# 							status = 'Absent'
# 						elif in_time != out_time:	
# 							status = 'Present'
# 					else:
# 						status = 'Absent'
# 					if not attn:
# 						att = frappe.new_doc('Attendance')
# 						att.employee = employee
# 						att.attendance_date = att_date
# 						att.status = status
# 						att.in_time = in_time
# 						att.out_time = out_time
# 						att.save(ignore_permissions=True)
# 						frappe.db.commit()
# 					else:
# 						if in_time:
# 							frappe.db.set_value('Attendance',attn,'in_time',in_time)
# 						if out_time:
# 							frappe.db.set_value('Attendance',attn,'out_time',out_time)

# 						# frappe.db.set_value("Attendance",attn,'shift','Office Shift A')
# 						frappe.db.set_value("Attendance",attn,'status',status)
# 					for c in checkins:
# 						print(c)
# 						frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
# 						frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
# 					if in_time and out_time:
# 						str_working_hours = out_time - in_time
# 						time_d_float = str_working_hours.total_seconds()
# 						whrs = time_d_float/3600
# 						working_hours = "{:.2f}".format(whrs)
# 						# # end_timing = frappe.get_all("Shift Type",{'name':'A'},['end_time'])	
# 						# end_timing = frappe.get_value("Shift Type",{"name":},["end_time"])  
# 						frappe.db.set_value('Attendance',attn,'working_hours',working_hours)


# 					if float(working_hours) > 8:
# 						ot = float(working_hours) - 8
# 						print(ot)
# 						frappe.db.set_value('Attendance',attn,'ot',ot)
# 					else:
# 						return '0'
# 	elif checkins:
# 		if device in ['CHENNAI']:
# 				if datetime.strptime('04:30:00','%H:%M:%S').time() < att_time < datetime.strptime('08:15:00','%H:%M:%S').time():
# 					if len(checkins) >= 2:
# 						in_time = checkins[0].time
# 						out_time = checkins[-1].time
# 					elif len(checkins) == 1:
# 						in_time = checkins[0].time
# 						out_time = checkins[-1].time
# 					attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
# 					print(attn)
# 					status = ""
# 					if in_time and out_time:
# 						if in_time == out_time:
# 							status = 'Absent'
# 						elif in_time != out_time:	
# 							status = 'Present'
# 					else:
# 						status = 'Absent'
# 					if not attn:
# 						att = frappe.new_doc('Attendance')
# 						att.employee = employee
# 						att.attendance_date = att_date
# 						att.status = status
# 						att.in_time = in_time
# 						att.out_time = out_time
# 						att.save(ignore_permissions=True)
# 						frappe.db.commit()
# 					else:
# 						if in_time:
# 							frappe.db.set_value('Attendance',attn,'in_time',in_time)
# 						if out_time:
# 							frappe.db.set_value('Attendance',attn,'out_time',out_time)

# 						# frappe.db.set_value("Attendance",attn,'shift','Office Shift A')
# 						frappe.db.set_value("Attendance",attn,'status',status)
# 					for c in checkins:
# 						print(c)
# 						frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
# 						frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
# 					if in_time and out_time:
# 						str_working_hours = out_time - in_time
# 						time_d_float = str_working_hours.total_seconds()
# 						whrs = time_d_float/3600
# 						working_hours = "{:.2f}".format(whrs)
# 						# # end_timing = frappe.get_all("Shift Type",{'name':'A'},['end_time'])	
# 						# end_timing = frappe.get_value("Shift Type",{"name":},["end_time"])  
# 						frappe.db.set_value('Attendance',attn,'working_hours',working_hours)


# 					if float(working_hours) > 8:
# 						ot = float(working_hours) - 8
# 						print(ot)
# 						frappe.db.set_value('Attendance',attn,'ot',ot)
# 					else:
# 						return '0'
# 	elif checkins:
# 		if device in ['SRICITY']:
# 				if datetime.strptime('05:30:00','%H:%M:%S').time() < att_time < datetime.strptime('09:15:00','%H:%M:%S').time():
# 					if len(checkins) >= 2:
# 						in_time = checkins[0].time
# 						out_time = checkins[-1].time
# 					elif len(checkins) == 1:
# 						in_time = checkins[0].time
# 						out_time = checkins[-1].time
# 					attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
# 					print(attn)
# 					status = ""
# 					if in_time and out_time:
# 						if in_time == out_time:
# 							status = 'Absent'
# 						elif in_time != out_time:	
# 							status = 'Present'
# 					else:
# 						status = 'Absent'
# 					if not attn:
# 						att = frappe.new_doc('Attendance')
# 						att.employee = employee
# 						att.attendance_date = att_date
# 						att.status = status
# 						att.in_time = in_time
# 						att.out_time = out_time
# 						att.save(ignore_permissions=True)
# 						frappe.db.commit()
# 					else:
# 						if in_time:
# 							frappe.db.set_value('Attendance',attn,'in_time',in_time)
# 						if out_time:
# 							frappe.db.set_value('Attendance',attn,'out_time',out_time)

# 						# frappe.db.set_value("Attendance",attn,'shift','Office Shift A')
# 						frappe.db.set_value("Attendance",attn,'status',status)
# 					for c in checkins:
# 						print(c)
# 						frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
# 						frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
# 					if in_time and out_time:
# 						str_working_hours = out_time - in_time
# 						time_d_float = str_working_hours.total_seconds()
# 						whrs = time_d_float/3600
# 						working_hours = "{:.2f}".format(whrs)
# 						# # end_timing = frappe.get_all("Shift Type",{'name':'A'},['end_time'])	
# 						# end_timing = frappe.get_value("Shift Type",{"name":},["end_time"])  
# 						frappe.db.set_value('Attendance',attn,'working_hours',working_hours)


# 					if float(working_hours) > 8:
# 						ot = float(working_hours) - 8
# 						print(ot)
# 						frappe.db.set_value('Attendance',attn,'ot',ot)
# 					else:
# 						return '0'

# def mark_absent_employee():
# 	to_date = '2023-01-24'
# 	from_date= '2022-12-25'
	
# 	att_date = today()
# 	yesterday = add_days(att_date,-1)
# 	employee = frappe.db.sql("""select * from `tabEmployee` where status = 'Active'""",as_dict =1)
# 	for emp in employee:
# 		dates = get_dates(from_date,to_date)
# 		# dates = get_dates(yesterday,att_date)
# 		for date in dates:
# 			date = datetime.strptime(date,'%Y-%m-%d')
# 			day = date.date()
# 			emp_doj = frappe.get_value('Employee',emp.name,'date_of_joining')
# 			if day >= emp_doj:
# 				emp_holiday_list = frappe.get_value('Employee',emp.name,'holiday_list')
# 				holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
# 				left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(emp_holiday_list,day),as_dict=True)
# 				if not holiday:
# 					att = frappe.db.exists("Attendance",{'employee':emp.name,'attendance_date':day})
# 					if not att:
# 						att_doc = frappe.new_doc('Attendance')
# 						att_doc.employee = emp.name
# 						att_doc.attendance_date = day
# 						att_doc.status = 'Absent'
# 						att_doc.save(ignore_permissions=True)


# def create_hooks_mark_ot():
# 	job = frappe.db.exists('Scheduled Job Type', 'mark_att')
# 	if not job:
# 		sjt = frappe.new_doc("Scheduled Job Type")
# 		sjt.update({
# 			"method": 'hunter_douglas.mark_attendance.mark_att',
# 			"frequency": 'Cron',
# 			"cron_format": '00 11 * * *'
# 		})
# 		sjt.save(ignore_permissions=True)


# def get_dates(from_date,to_date):
# 	no_of_days = date_diff(add_days(to_date, 1), from_date)
# 	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
# 	return dates




# # @frappe.whitelist()
# # def get_working_hours_on_attendance(in_time,out_time):
# # #     in_time = datetime.strptime(in_time,"%Y-%m-%d %H:%M:%S")

# #     out_time = datetime.strptime(out_time,"%Y-%m-%d %H:%M:%S")
# #     working_hours = out_time - in_time
# #     return working_hours
# #     frappe.db.set_value('Attendance',attn,'working_hours',working_hours)
# #         # att.working_hours = working_hours

# # @frappe.whitelist()
# # def del_att():
# #     # att = frappe.db.sql("""delete from `tabAttendace` where attendance_date = '2022-08-0
# #     att = frappe.db.sql(""" update `tabEmployee Checkin` set skip_auto_attendance = 0 where date(time) between  '2022-09-01' and '2022-09-19'  """)
# #     # print(att)
# #     att = frappe.db.sql(""" update `tabEmployee Checkin` set attendance = '' where date(time) between  '2022-09-01' and '2022-09-19'""")
# #     # # print(att)
# #     att = frappe.db.sql(""" delete from `tabAttendance` where attendance_date between  '2022-09-01' and '2022-09-19'  """)










# # return working_hours
# 	# if working_hours: