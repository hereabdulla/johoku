# Copyright (c) 2022, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from csv import writer
from inspect import getfile
from unicodedata import name
import frappe
from frappe.utils import cstr, add_days, date_diff, getdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file, upload
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from numpy import unicode_


class ShiftSchedule(Document):

	def on_submit(self): 
		if self.attach:
			self.create_shift_assignment()

	def create_shift_assignment(self):
		filepath = get_file(self.attach)
		pps = read_csv_content(filepath[1])
		dates = self.get_dates(self.from_date,self.to_date)
		for date in dates:
			for pp in pps:
				if pp[2] != 'Shift':
					if pp[1]:
						if not frappe.db.exists("Shift Assignment",{'employee':pp[0],'start_date':date,'end_date':date,'docstatus':['in',[0,1]]}):
							doc = frappe.new_doc('Shift Assignment')
							doc.employee = pp[0]
							doc.shift_type = pp[2]
							doc.department = pp[3]
							doc.employee_type = pp[4]
							doc.route_no = pp[5]
							doc.boarding_point = pp[6]
							doc.start_date = date
							doc.end_date = date
							doc.schedule = self.name
							doc.save(ignore_permissions=True)
							doc.submit()
							frappe.db.commit()
	
	def on_cancel(self):
		frappe.db.sql("""delete from `tabShift Assignment` where schedule=%s """, (self.name))

	def get_dates(self,from_date,to_date):
		no_of_days = date_diff(add_days(to_date, 1), from_date)
		dates = [add_days(from_date, i) for i in range(0, no_of_days)]
		return dates

	@frappe.whitelist()
	def validate(self):
		shift_assignment = frappe.db.sql("""select name from `tabShift Assignment` where department = '%s' and start_date between '%s' and '%s' """ % (self.department, self.from_date, self.to_date), as_dict=True)
		if shift_assignment:
				self.upload = ''
				return 'Shift Schedule already submitted for the selected date'
		  
@frappe.whitelist()
def get_template():
	args = frappe.local.form_dict

	if getdate(args.from_date) > getdate(args.to_date):
		frappe.throw(_("To Date should be greater than From Date"))

	w = UnicodeWriter()
	w = add_header(w)
	w = add_data(w, args)

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Shift Assignment"

def add_header(w):
	w.writerow(['Employee ID','Employee Name','Shift','Department','Employement Type','Route No','Boarding Point'])
	return w

def add_data(w, args):
	data = get_data(args)
	writedata(w, data)
	return w

@frappe.whitelist()
def get_data(args):
	if args.department == "All Departments":
		employees = frappe.db.get_all('Employee',{'status':'Active'},['*'])
		data = []
		for emp in employees:
			row = [
				emp.name,emp.employee_name,emp.default_shift or '',emp.department,emp.employee_type or '',emp.route_no or '',emp.boarding_point or ''
			]
			data.append(row)
	else:
		employees = frappe.db.get_all('Employee',{'status':'Active','department':args.department},['*'])
		data = []
		for emp in employees:
			row = [
				emp.name,emp.employee_name,emp.default_shift or '',emp.department,emp.employee_type or '',emp.route_no or '',emp.boarding_point or ''
			]
			data.append(row)
	return data

@frappe.whitelist()
def writedata(w, data):
	for row in data:
		w.writerow(row)




