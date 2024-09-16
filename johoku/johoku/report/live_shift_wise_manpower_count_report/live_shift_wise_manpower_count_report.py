# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils import flt
import erpnext
import time
import pytz
from datetime import datetime
from datetime import timedelta
import pandas as pd

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = []
	columns += [
		_('Date') + ":Date/:100",
		_("Employee ID") + ":Data/:90",
		_("Employee Name") + ":Data/:150",
		_("Assigned Shift") + ":Data/:70",
		# _("Attended Shift") + ":Data/:70",
		_("Department") + ":Data/:100",
		_("Designation") + ":Data/:100",
		_("Category") + ":Data/:90",
		_("Check In Time") + ":Data/:100",
		_("Status") + ":Data/:100",
	]
	
	return columns

# def get_conditions(filters):
# 	conditions = ""
# 	if filters.get("attendance_date"):
# 		conditions += "  attendance_date = %(attendance_date)s"
# 	if filters.get("shift_type"):
# 		conditions += " and shift = %(shift_type)s"
# 	return conditions, filters

def get_data(filters):
	data = []
	# conditions, filters = get_conditions(filters)
	sa = frappe.db.sql("""select * from `tabAttendance` where attendance_date = '%s' and shift='%s'"""%(filters.attendance_date,filters.shift),as_dict=True)
	if sa:
		for i in sa:
			ass = ''
			at_time =''
			status = ''

			if i.status=='On Leave':
				ass = "Leave"
				status="On Leave"
				at_time='-'
			elif i.in_time and i.status == 'Absent' or 'Present' and i.shift == filters.shift:
				ass = i.shift
				status='Present'
				at_time = i.in_time.strftime('%H:%M:%S')
			elif i.assigned_shift in ['1','2','3']:
				if not i.in_time and i.status == 'Absent' and i.assigned_shift == filters.shift:
					ass = i.assigned_shift
					status='Absent'
					at_time = '-'
			elif i.assigned_shift not in ['1','2','3']:
				if not i.in_time and i.status == 'Absent':
					ass = "NSA"
					status='Absent'
					at_time = '-'

			row=[i.attendance_date,i.employee,i.employee_name,ass,i.department,i.designation,i.category,at_time,status]
			data.append(row)
	return data



@frappe.whitelist()
def get_shift(attendance_date):
	frappe.errprint("Hi")
	timez = pytz.timezone('Asia/Kolkata')
	nowtime = datetime.now(timez)
	curtime = nowtime.strftime('%H:%M')
	frappe.errprint(curtime)
	return curtime



		

	










