# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

import frappe
from frappe import _
from frappe.utils import getdate, formatdate

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		_('Employee ID') + ':Data:100',
		_('Employee Name') + ':Data:100',
		_('Date of Birth') + ':Date:100',
		_('Department') + ':Data/:100',
		_('Designation') + ':Data/:100',
		_('Grade') + ':Data/:100',
		_('Branch') + ':Data/:100',
		_('Work Station') + ':Data/:100',
		_('Employee Category') + ':Data/:100'
		
	]
	return columns

def get_data(filters):
	data = []
	employees = get_employees(filters)
	today = getdate()
	for emp in employees:
		dob = getdate(emp.date_of_birth)
		
		
		if dob and today.month == dob.month and today.day == dob.day:
			row = [
				emp.employee_number,
				emp.employee_name,
				formatdate(dob),
				emp.department,
				emp.designation,
				emp.grade,
				emp.branch,
				emp.work_station,
				emp.employee_category,
				_('Birthday')
			]
			data.append(row)
	
	
	return data

def get_employees(filters):
	employees = frappe.get_all(
		'Employee',
		filters={'status': 'Active'},
		fields=['employee_number', 'employee_name', 'date_of_birth','department' or '','designation' or '','grade' or '','branch' or '','work_station'or '','employee_category' or '']
	)
	return employees
