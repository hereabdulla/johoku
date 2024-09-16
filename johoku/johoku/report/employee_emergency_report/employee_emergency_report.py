# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six import string_types
import frappe
import json
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate
from itertools import count
from datetime import datetime
from datetime import datetime, timedelta
		

def execute(filters=None):
	# current_time = datetime.now()
	# frappe.errprint(max_in_time)
	# frappe.errprint(current_time)
	if not filters:
		filters = {}
	columns = get_columns()
	data = []
	attendance = get_emergency(filters)
	for att in attendance:
		data.append(att)
	return columns, data

def get_columns():
	columns = []
	columns += [
	    _("Employee") + ":Data:120",
	    _("Employee Name") + ":Data:150",
	    _("In Time") + ":Data:120"
	]
	return columns

def get_emergency(filters):
	data = []
	if filters.employee:
		max_in_time = datetime.strptime('07:00:00', '%H:%M:%S').time()
		current_time = datetime.now()
		# frappe.errprint(max_in_time)
		# frappe.errprint(current_time)
		# frappe.errprint(type(max_in_time))
		# frappe.errprint(type(current_time))
		datetime_obj = datetime.strptime(str(current_time), "%Y-%m-%d %H:%M:%S.%f")
		time = datetime_obj.time()
		time_str = time.strftime("%H:%M:%S")
		time_str_tt = datetime.strptime(time_str, '%H:%M:%S').time()
		# frappe.errprint(time_str_tt)
		# frappe.errprint(type(time_str_tt))
		if max_in_time > time_str_tt :
			# frappe.errprint("HI")
			from_date = filters.date
			to_date = filters.date
		else:
			# frappe.errprint("HII")
			from_date = add_days(filters.date,-1) 
			to_date = filters.date
		emergency_co = frappe.db.sql(""" select count(*) as count from `tabEmployee Checkin` where log_type = "IN" and employee = '%s' and date(time) between '%s' and '%s' """%(filters.employee,from_date,to_date),as_dict=True)[0]
		# frappe.errprint(emergency_co['count'])
		row = []
		if emergency_co['count'] > 0 :
			emergency = frappe.db.sql(""" select * from `tabEmployee Checkin` where log_type = "IN" and employee = '%s' and date(time) between '%s' and '%s' ORDER BY time ASC LIMIT 1 """%(filters.employee,from_date,to_date),as_dict=True)
			# frappe.errprint(emergency)
			for egy in emergency:
				ey_time = datetime.strptime(str(egy.time),'%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
				frappe.errprint(ey_time)
				new_datetime = egy.time + timedelta(hours=24)
				emergency_out = frappe.db.sql(""" select count(*) as count from `tabEmployee Checkin` where log_type = "OUT" and employee = '%s' and time between '%s' and '%s' """%(filters.employee,egy.time,new_datetime),as_dict=True)[0]
				# frappe.errprint(emergency_out['count'])
				if emergency_out['count'] == 0:
					row = [egy.employee,egy.employee_name,ey_time]
					data.append(row)
	else:
		employees = frappe.get_all("Employee",{'status':"Active"},["*"])
		for e in employees:
			max_in_time = datetime.strptime('07:00:00', '%H:%M:%S').time()
			current_time = datetime.now()
			# frappe.errprint(max_in_time)
			# frappe.errprint(current_time)
			# frappe.errprint(type(max_in_time))
			# frappe.errprint(type(current_time))
			datetime_obj = datetime.strptime(str(current_time), "%Y-%m-%d %H:%M:%S.%f")
			time = datetime_obj.time()
			time_str = time.strftime("%H:%M:%S")
			time_str_tt = datetime.strptime(time_str, '%H:%M:%S').time()
			# frappe.errprint(time_str_tt)
			# frappe.errprint(type(time_str_tt))
			if max_in_time > time_str_tt :
				# frappe.errprint("HI")
				from_date = filters.date
				to_date = filters.date
			else:
				# frappe.errprint("HII")
				from_date = add_days(filters.date,-1) 
				to_date = filters.date
			emergency_co = frappe.db.sql(""" select count(*) as count from `tabEmployee Checkin` where log_type = "IN" and employee = '%s' and date(time) between '%s' and '%s' """%(e.name,from_date,to_date),as_dict=True)[0]
			# frappe.errprint(emergency_co['count'])
			row = []
			if emergency_co['count'] > 0 :
				emergency = frappe.db.sql(""" select * from `tabEmployee Checkin` where log_type = "IN" and employee = '%s' and date(time) between '%s' and '%s' ORDER BY time ASC LIMIT 1 """%(e.name,from_date,to_date),as_dict=True)
				# frappe.errprint(emergency)
				for egy in emergency:
					ey_time = datetime.strptime(str(egy.time),'%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
					frappe.errprint(ey_time)
					new_datetime = egy.time + timedelta(hours=24)
					emergency_out = frappe.db.sql(""" select count(*) as count from `tabEmployee Checkin` where log_type = "OUT" and employee = '%s' and time between '%s' and '%s' """%(e.name,egy.time,new_datetime),as_dict=True)[0]
					# frappe.errprint(emergency_out['count'])
					if emergency_out['count'] == 0:
						row = [egy.employee,egy.employee_name,ey_time]
						data.append(row)
	return data

