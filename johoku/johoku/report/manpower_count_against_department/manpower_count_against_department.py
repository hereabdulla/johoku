# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import erpnext
from datetime import date


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Department") + ":Link/Department:200",
		_("Count") + ":Data:200",
	]
	return columns


def get_data(filters):
	data = []
	dept = frappe.db.sql(""" select * from `tabDepartment` """,as_dict=True)
	for i in dept:
		frappe.errprint(i.name)
		# count = frappe.db.sql(""" select count(*) as count from `tabEmployee` where status ='Active' and department = '%s' """%(i.name),as_dict=True)
		count_i = frappe.db.count("Employee",{'status':'Active','department':i.name})
		frappe.errprint(count_i)
		row = [i.name,count_i]
		data.append(row)
	return data