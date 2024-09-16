# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import erpnext
from datetime import date


def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data

def get_columns():
	columns = []
	columns += [
		_("Grade") + ":Link/Employee Grade:200",
		_("Count") + ":Data:200",
	]
	return columns

def get_data():
	data = []
	grade = frappe.db.sql(""" select * from `tabEmployee Grade` """,as_dict=True)
	for i in grade:
		frappe.errprint(i.name)
		count = frappe.db.count("Employee",{'status':'Active','grade':i.name})
		frappe.errprint(count)
		row = [i.name,count]
		data.append(row)
	return data